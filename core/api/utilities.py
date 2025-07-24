import random
import string

import io, csv, pandas as pd
from core.api.serializers import *
from core.api.permissions import *
# # import models
from core.models import *
from django.contrib.auth import get_user_model
# from django.db.models import Q, Sum, Avg, Max, Min
from django.db import transaction, models
from django.shortcuts import get_object_or_404
# # from rest_framework import mixins
from rest_framework import generics, status
# # import validation errors
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import *
# # import Response
from rest_framework.response import Response
# # import here below used for class based views
from rest_framework.views import APIView

from rest_framework.parsers import MultiPartParser,FormParser

import openpyxl



User = get_user_model()


def processTerminalResult(classObj, termObj, sessionObj, classteacher):
    # Get all students with scores in this class/term/session
    students_scores = (
        Scores.objects
        .filter(session=sessionObj, term=termObj, studentclass=classObj)
        .values('user')
        .annotate(subject_total=Sum('subjecttotal'))
    )

    # Get existing results for this class/term/session
    existing_results = {
        (r.student_id): r
        for r in Result.objects.filter(studentclass=classObj, term=termObj, session=sessionObj)
    }

    results_to_update = []
    results_to_create = []

    for entry in students_scores:
        student_id = entry['user']
        total = entry['subject_total']
        if student_id in existing_results:
            result = existing_results[student_id]
            result.termtotal = total
            results_to_update.append(result)
        else:
            results_to_create.append(Result(
                termtotal=total,
                classteacher=classteacher,
                session=sessionObj,
                studentclass=classObj,
                term=termObj,
                student_id=student_id
            ))

    # Bulk update and create
    if results_to_update:
        Result.objects.bulk_update(results_to_update, ['termtotal'])
    if results_to_create:
        Result.objects.bulk_create(results_to_create, batch_size=1000)

    # Update averages and positions in bulk
    terminalAverage(classObj, termObj, sessionObj)
    terminalPosition(classObj, termObj, sessionObj)

# 
# find subject and class average
def subjectAverage(subj, classroom, termObj, sessionObj):
    scores = Scores.objects.filter(
        subject=subj, studentclass=classroom, term=termObj, session=sessionObj
    ).aggregate(scoresav=Avg('subjecttotal'))
    return scores['scoresav']

#  subject positioning
def subjectPosition(subject, classroom,termObj,sessionObj):

    # activeTerm = Term.objects.get(status='True')
    # activeSession = Session.objects.get(status='True')

    # Get all scores ordered by subjecttotal descending
    scores = list(
        Scores.objects.filter(
            subject=subject, studentclass=classroom, term=termObj, session=sessionObj
        ).order_by('-subjecttotal', 'user_id').values('id', 'subjecttotal')
    )

    # Assign positions (handle ties)
    position = 1
    repeated_counter = 0
    previous_score = None
    positions = {}

    for idx, score in enumerate(scores):
        if previous_score is not None and score['subjecttotal'] == previous_score:
            repeated_counter += 1
        else:
            position = idx + 1
            repeated_counter = 0
        positions[score['id']] = position
        previous_score = score['subjecttotal']

    # Bulk update positions
    if positions:
        cases = [models.When(id=pk, then=models.Value(pos)) for pk, pos in positions.items()]
        Scores.objects.filter(id__in=positions.keys()).update(
            subjectposition=models.Case(*cases, output_field=models.IntegerField())
        )


# update ratings
def scoresRating(subject, classroom, termObj, sessionObj):

    # activeTerm = Term.objects.get(status='True')
    # activeSession = Session.objects.get(status='True')

    
    # TODO: Use select for update because of transaction
    # Fetch all relevant scores
    scores = Scores.objects.filter(
        subject=subject, studentclass=classroom, term=termObj, session=sessionObj
    )

    updates = []
    for score in scores:
        total = score.subjecttotal or 0
        if total <= 39:
            grade, rating = 'F', 'Failed'
        elif 40 <= total <= 44.9:
            grade, rating = 'E', 'Poor'
        elif 45 <= total <= 54.9:
            grade, rating = 'D', 'Fair'
        elif 55 <= total <= 64.9:
            grade, rating = 'C', 'Good'
        elif 65 <= total <= 74.9:
            grade, rating = 'B', 'Very Good'
        elif 75 <= total <= 100:
            grade, rating = 'A', 'Excellent'
        else:
            grade, rating = 'NA', 'NA'
        score.subjectgrade = grade
        score.subjectrating = rating
        updates.append(score)
    if updates:
        Scores.objects.bulk_update(updates, ['subjectgrade', 'subjectrating'])


# Minimum and Maximum scores
def minMaxScores(subject, classroom, termObj, sessionObj):
    min_max = Scores.objects.filter(
        subject=subject, studentclass=classroom, term=termObj, session=sessionObj
    ).aggregate(min_scores=Min('subjecttotal'), max_scores=Max('subjecttotal'))

    Scores.objects.filter(
        subject=subject, studentclass=classroom, term=termObj, session=sessionObj
    ).update(
        highest_inclass=min_max['max_scores'],
        lowest_inclass=min_max['min_scores']
    )
    
    
#  process scores
def processScores(subjectObj, classroomObj, termObj, sessionObj):
   

    subjavg = subjectAverage(subjectObj, classroomObj, termObj, sessionObj)

    Scores.objects.filter(
        subject=subjectObj, studentclass=classroomObj, term=termObj, session=sessionObj
    ).update(subjaverage=subjavg)

    #update position and grading
    subjectPosition(subjectObj, classroomObj, termObj, sessionObj)

    #Update  grades
    scoresRating(subjectObj, classroomObj, termObj, sessionObj)

    # update min and max
    minMaxScores(subjectObj, classroomObj, termObj, sessionObj)

 
#    
def processPsycho(classroom, session, term):
    # Prefetch all psychomotor skills and ratings
    psycho_skills = list(Psychomotor.objects.all())
    rating = Rating.objects.get(pk=3)

    # Get all students who should have psychomotor traits
    studentsResultList = Result.objects.filter(
        studentclass=classroom,
        session=session,
        term=term
    ).select_related('student').distinct('student')

    # Get all existing Studentpsychomotor records for this class/session/term
    existing_psycho = set(
        Studentpsychomotor.objects.filter(
            studentclass=classroom,
            term=term,
            session=session
        ).values_list('student_id', flat=True)
    )

    new_psychos = []
    for student_result in studentsResultList:
        student_id = student_result.student.pk
        if student_id in existing_psycho:
            continue
        # Select two random psychomotor skills for each student
        selected_skills = random.sample(psycho_skills, min(2, len(psycho_skills)))
        for skill in selected_skills:
            new_psychos.append(
                Studentpsychomotor(
                    session=session,
                    studentclass=classroom,
                    term=term,
                    student=student_result.student,
                    psychomotor=skill,
                    rating=rating,
                )
            )
    if new_psychos:
        Studentpsychomotor.objects.bulk_create(new_psychos, batch_size=1000)

# 
def processAffective(classroom, session, term):
    # Prefetch all affective skills and ratings
    affective_skills = list(Affective.objects.all())
    rating = Rating.objects.get(pk=3)

    # Get all students who should have affective traits
    studentsResultList = Result.objects.filter(
        studentclass=classroom,
        session=session,
        term=term
    ).select_related('student').distinct('student')

    # Get all existing Studentaffective records for this class/session/term
    existing_affective = set(
        Studentaffective.objects.filter(
            studentclass=classroom,
            term=term,
            session=session
        ).values_list('student_id', flat=True)
    )

    new_affectives = []
    for student_result in studentsResultList:
        student_id = student_result.student.pk
        if student_id in existing_affective:
            continue
        # Select two random affective skills for each student
        selected_skills = random.sample(affective_skills, min(2, len(affective_skills)))
        for skill in selected_skills:
            new_affectives.append(
                Studentaffective(
                    session=session,
                    studentclass=classroom,
                    term=term,
                    student=student_result.student,
                    affective=skill,
                    rating=rating,
                )
            )
    if new_affectives:
        Studentaffective.objects.bulk_create(new_affectives, batch_size=1000)

    

def terminalAverage(classroom, term, session):
    # Get number of subjects per class
    try:
        no_subj_per_class = SubjectPerClass.objects.get(sch_class=classroom, term=term, session=session).no_subject
    except SubjectPerClass.DoesNotExist:
        no_subj_per_class = 1  # Avoid division by zero

    # Update all results in bulk
    Result.objects.filter(studentclass=classroom, term=term, session=session).update(
        termaverage=models.F('termtotal') / no_subj_per_class
    )

# assign terminal result position
def terminalPosition(classroom, term, session):
    # Get all results ordered by termtotal descending
    results = Result.objects.filter(studentclass=classroom, term=term, session=session).order_by('-termtotal', 'student_id').values('id', 'termtotal')

    # Assign positions (handle ties)
    position = 1
    repeated_counter = 0
    previous_score = None
    positions = {}

    for idx, result in enumerate(results):
        if previous_score is not None and result['termtotal'] == previous_score:
            repeated_counter += 1
        else:
            position = idx + 1
            repeated_counter = 0
        positions[result['id']] = position
        previous_score = result['termtotal']

    # Bulk update positions
    if positions:
        cases = [models.When(id=pk, then=models.Value(pos)) for pk, pos in positions.items()]
        Result.objects.filter(id__in=positions.keys()).update(
            termposition=models.Case(*cases, output_field=models.IntegerField())
        )


def autoAddComment(classroom, session, term):
    # select result
    resultFilter = Result.objects.select_for_update().filter(
        studentclass=classroom.pk,
        session=session.pk,
        term=term.pk
    )

    results_to_update = []
    for resultObj in resultFilter:
        if resultObj.termaverage is None:
            comment = 'NA'
        elif resultObj.termaverage <= 39.99:
            comment = 'Failed'
        elif 40 <= resultObj.termaverage <= 44.99:
            comment = 'A Fair Result'
        elif 45 <= resultObj.termaverage <= 54.99:
            comment = 'A Passed Result'
        elif 55 <= resultObj.termaverage <= 64.99:
            comment = 'A Good Result'
        elif 65 <= resultObj.termaverage <= 74.99:
            comment = 'A Very Good Result'
        elif 75 <= resultObj.termaverage <= 100:
            comment = 'An Excellent Result'
        else:
            comment = 'NA'

        resultObj.classteachercomment = comment
        resultObj.headteachercomment = comment
        results_to_update.append(resultObj)

    if results_to_update:
        Result.objects.bulk_update(results_to_update, ['classteachercomment', 'headteachercomment'])

# Annual Average
def annualAverage(studentid,classroom,session):


    sessionResult = AnnualResult.objects.filter(student=studentid,studentclass=classroom,session=session).aggregate(annual_sum=Sum('annualtotal'))

    session_sum = sessionResult['annual_sum']
    # get subject per class
    no_subj_per_class = SubjectPerClass.objects.get(sch_class=classroom)
    session_subject_total = no_subj_per_class.no_subject*3

    session_av = session_sum/session_subject_total

    # TODO MOVE CODE TO UPDATE TERMINAL AVERAGE HERE
    result = AnnualResult.objects.filter(student=studentid,studentclass=classroom,session=session).update(annualaverage=session_av)


# annual position
# Assign annual Postion
def annualPosition(session,classroom):


    # activeTerm = Term.objects.get(status='True')
    # activeSession = Session.objects.get(status='True')

    results = AnnualResult.objects.filter(studentclass=classroom,session=session)
    ordered_scores = []
    counter = 1
    repeated_counter = 0

    previous_score = AnnualResult.objects.none()
    for result in results.order_by("-annualtotal"):
        # repeated_counter = 0
        if counter == 1:
            #this is the first iteration, just assign the first position
            position = counter
            #update the database
            result_entity = AnnualResult.objects.get(pk=result.pk)
            result_entity.annualposition = position
            result_entity.save()


            # ordered_scores.append({
            # "position": position,
            # "id": score.pk,
            # "subjecttotal": score.subjecttotal
            # })
            previous_score = result
            counter += 1
        else:

            # check for duplicate
            if result.annualtotal == previous_score.annualtotal:
                # update database
                result_entity = AnnualResult.objects.get(pk=result.pk)
                result_entity.annualposition = position
                result_entity.save()

                # position = counter
                # ordered_scores.append({
                # "position": position,
                # "id": score.pk,
                # "subjecttotal": score.subjecttotal
                # })
                # position = previous_score.position
                repeated_counter +=1

            else:
                position = counter + repeated_counter
                # update database
                result_entity = AnnualResult.objects.get(pk=result.pk)
                result_entity.annualposition = position
                result_entity.save()

                # ordered_scores.append({
                # "position": position,
                # "id": score.pk,
                # "subjecttotal": score.subjecttotal
                # })

                previous_score = result
                # previous_position = position
                # repeated_counter = position
                counter += 1


# process annual result
def processAnnualResult(scoresObj):


    # Find record in the annual result table
    Annualresult = AnnualResult.objects.filter(student=scoresObj.student,studentclass=scoresObj.studentclass,session=scoresObj.session)

    result = Result.objects.filter(student=scoresObj.student,studentclass=scoresObj.studentclass,session=scoresObj.session).aggregate(annual_total=Sum('termtotal'))

    # print(scores['subject_total'])

    # check for existence of record
    if Annualresult:

        # update the record
        Annualresult.update(annualtotal=result['annual_total'])

        # update annual average
        annualAverage(scoresObj.student,scoresObj.studentclass,scoresObj.session)
        # update  annual position
        annualPosition(scoresObj.session,scoresObj.studentclass)
    else:

        # create a new anual result record
        newAnnualresultObj = AnnualResult.objects.create(
                                 annualtotal = result['annual_total'],
                                 session = scoresObj.session,
                                 studentclass = scoresObj.studentclass,
                                 client = scoresObj.client,
                                 student = scoresObj.student
                                     )
        newAnnualresultObj.save()



        # update term average
        annualAverage(scoresObj.student,scoresObj.studentclass,scoresObj.session)

        # update  term position
        annualPosition(scoresObj.session,scoresObj.studentclass)

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
def subjectAverage(subj,classroom,termObj,sessionObj):
    
    # get scores based on subject
    # scores = Scores.objects.filter(subject=subj,studentclass=classroom,term=activeTerm,session=activeSession).distinct('student').aggregate(Sum('subjAverage'))

    scores = Scores.objects.filter(subject=subj,studentclass=classroom,term=termObj,session=sessionObj).aggregate(scoresav=Avg('subjecttotal'))

    av = scores['scoresav']

    return av

#  subject positioning
def subjectPosition(subject, classroom,termObj,sessionObj):

    # activeTerm = Term.objects.get(status='True')
    # activeSession = Session.objects.get(status='True')

    scores = Scores.objects.filter(subject=subject,studentclass=classroom,term=termObj,session=sessionObj)
    ordered_scores = []
    counter = 1
    repeated_counter = 0
    # index_counter = 0
    previous_score = Scores.objects.none()
    for score in scores.order_by("-subjecttotal"):
        # repeated_counter = 0
        if counter == 1:
            # this is the first iteration, just assign the first position
            position = counter
             # update the database
            score_entity = Scores.objects.get(pk=score.pk)
            score_entity.subjectposition = position
            score_entity.save()
            # ordered_scores.append({
            # "position": position,
            # "id": score.pk,
            # "subjecttotal": score.subjecttotal
            # })
            previous_score = score
            counter += 1

        else:

            # check for duplicate
            if score.subjecttotal == previous_score.subjecttotal:
                # update database
                score_entity = Scores.objects.get(pk=score.pk)
                score_entity.subjectposition = position
                score_entity.save()

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
                score_entity = Scores.objects.get(pk=score.pk)
                score_entity.subjectposition = position
                score_entity.save()

                # ordered_scores.append({
                # "position": position,
                # "id": score.pk,
                # "subjecttotal": score.subjecttotal
                # })

                previous_score = score
                # previous_position = position
                # repeated_counter = position

                counter += 1
    # return render(request, "template.html", {"players": ordered_players})
    # return ordered_scores


# update ratings
def scoresRating(subject,classroom,termObj,sessionObj):

    # activeTerm = Term.objects.get(status='True')
    # activeSession = Session.objects.get(status='True')

    
    # TODO: Use select for update because of transaction
    scores = Scores.objects.filter(subject=subject,studentclass=classroom,term=termObj,session=sessionObj)

    for scoresObj in scores:

        if scoresObj.subjecttotal <= 39:
            scoresObj.subjectgrade = 'F'
            scoresObj.subjectrating = 'Failed'
            scoresObj.save()
        elif scoresObj.subjecttotal >= 40 and scoresObj.subjecttotal <= 44.9:
            scoresObj.subjectgrade = 'E'
            scoresObj.subjectrating = 'Poor'
            scoresObj.save()
        elif scoresObj.subjecttotal >= 45 and scoresObj.subjecttotal <= 54.9:
            scoresObj.subjectgrade = 'D'
            scoresObj.subjectrating = 'Fair'
            scoresObj.save()
        elif scoresObj.subjecttotal >= 55 and scoresObj.subjecttotal <= 64.9:
            scoresObj.subjectgrade = 'C'
            scoresObj.subjectrating = 'Good'
            scoresObj.save()
        elif scoresObj.subjecttotal >= 65 and scoresObj.subjecttotal <= 74.9:
            scoresObj.subjectgrade = 'B'
            scoresObj.subjectrating = 'Very Good'
            scoresObj.save()
        elif scoresObj.subjecttotal >= 75 and scoresObj.subjecttotal <= 100:

            scoresObj.subjectgrade = 'A'
            scoresObj.subjectrating = 'Excellent'
            scoresObj.save()
        else:
            scoresObj.subjectgrade = 'NA'
            scoresObj.subjectrating = 'NA'
            scoresObj.save()


# Minimum and Maximum scores
def minMaxScores(subject,classroom,termObj,sessionObj):
 
    min_max = Scores.objects.filter(subject=subject,studentclass=classroom,term=termObj,session=sessionObj).aggregate(min_scores=Min('subjecttotal'),max_scores=Max('subjecttotal'))

    scores = Scores.objects.filter(subject=subject,studentclass=classroom,term=termObj,session=sessionObj).update(highest_inclass=min_max['max_scores'],lowest_inclass=min_max['min_scores'])
    
    
#  process scores
def processScores(subjectObj,classroomObj,termObj,sessionObj):
   

    subjavg = subjectAverage(subjectObj,classroomObj,termObj,sessionObj)

    scores = Scores.objects.filter(subject=subjectObj,studentclass=classroomObj,term=termObj,session=sessionObj).update(subjaverage=subjavg)

    #update position and grading
    subjectPosition(subjectObj,classroomObj,termObj,sessionObj)

    #Update  grades
    scoresRating(subjectObj,classroomObj,termObj,sessionObj)

    # update min and max
    minMaxScores(subjectObj,classroomObj,termObj,sessionObj)

 
#    
def processPsycho(classroom,session,term):

 
    # list psycho items
    # psychoList = Studentpsychomotor.objects.filter(studentclass=classroom.pk,term=term.pk,session=session.pk)
    psychoList = Studentpsychomotor.objects.filter(
    studentclass=classroom,
    term=term,
    session=session
    ).select_related('studentclass', 'term', 'session')
    
    if not psychoList:
        # select Distinct students from result table
        # studentsResultList = Result.objects.filter(studentclass=classroom.pk,session=session.pk,term=term.pk).distinct('student')
        studentsResultList = Result.objects.filter(
        studentclass=classroom,
        session=session,
        term=term
        ).select_related('studentclass', 'session', 'term').distinct('student')
        # Get class teacher
  
        for student in studentsResultList:
            
            # check for existence of record
            if psychoList.filter(student=student.student.pk).exists():
                pass
            else:
                # select three random random skills
                psycho_skills = Psychomotor.objects.all().order_by("?")[:2]
                # select rating
                rating = Rating.objects.get(pk=3)

            for i in  psycho_skills:
                
                studentPsycho = Studentpsychomotor.objects.create(
                    session = session,
                    studentclass = classroom,
                    term = term,
                    student = student.student,
                    psychomotor = Psychomotor.objects.get(pk=i.pk),
                    rating= rating,
                                     )
                studentPsycho.save()

# 
def processAffective(classroom,session,term):
    
    # list affetive items
    # affective = Studentaffective.objects.filter(studentclass=classroom.pk,term=term.pk,session=session.pk)
    affective = Studentaffective.objects.filter(
    studentclass=classroom,
    term=term,
    session=session
    ).select_related('studentclass', 'term', 'session')
    
    if not affective:
        
        # select Distinct students from result table
        # studentsResultList = Result.objects.filter(studentclass=classroom,session=session,term=term).distinct('student')
        
        studentsResultList = Result.objects.filter(
        studentclass=classroom,
        session=session,
        term=term
        ).select_related('student', 'studentclass', 'session', 'term').distinct('student')

    
        for student in studentsResultList:
        
            # check for existence of record
            if affective.filter(student=student.student.pk).exists():
                pass
            else:
                # select three random affective skills
                affective_skills = Affective.objects.all().order_by("?")[:2]
                # select rating
                rating = Rating.objects.get(pk=3)

            for i in affective_skills:

                # create a new record
                studentAffective = Studentaffective.objects.create(
                        session = session,
                        studentclass = classroom,
                        term = term,
                        student = student.student,
                        affective = Affective.objects.get(pk=i.pk),
                        rating= rating,
                        )
                studentAffective.save()

    

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


def autoAddComment(classroom,session,term):

    # select result
    resultFilter = Result.objects.select_for_update().filter(studentclass=classroom.pk,session=session.pk,term=term.pk)

    for resultObj in resultFilter:

        if resultObj.termaverage <= 39.99:
            resultObj.classteachercomment = 'Failed'
            resultObj.headteachercomment = 'Failed'
            resultObj.save()
            
        elif resultObj.termaverage >= 40 and resultObj.termaverage <= 44.99:
            resultObj.classteachercomment = 'A Fair Result'
            resultObj.headteachercomment = 'A Fair Result'
            resultObj.save()
            
        elif resultObj.termaverage >= 45 and resultObj.termaverage <= 54.99:
            resultObj.classteachercomment = 'A Passed Result'
            resultObj.headteachercomment = 'A Passed Result'
            resultObj.save()
            
        elif resultObj.termaverage >= 55 and resultObj.termaverage <= 64.99:
            resultObj.classteachercomment = 'A Good Result'
            resultObj.headteachercomment = 'A Good Result'
            resultObj.save()
            
        elif resultObj.termaverage >= 65 and resultObj.termaverage <= 74.99:
            resultObj.classteachercomment = 'A Very Good Result'
            resultObj.headteachercomment = 'A Very Good Result'
            resultObj.save()
            
        elif resultObj.termaverage >= 75 and resultObj.termaverage <= 100:
            resultObj.classteachercomment = 'An Excellent Result '
            resultObj.headteachercomment = 'An Excellent Result'
            resultObj.save()
            
        else:
            resultObj.classteachercomment = 'NA'
            resultObj.headteachercomment = 'NA'
            resultObj.save()

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

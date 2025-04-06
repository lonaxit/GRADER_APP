import random
import string
import math
import json
from io import BytesIO

import pandas as pd
from users.serializers import *
from core.api.serializers import *
# from profiles.api.serializers import *
from core.api.permissions import *
# from core.api.utilities import *
from django.http import HttpResponse,JsonResponse
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404

import csv

# # import models
from core.models import *
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum, Avg, Max, Min
from django.db import transaction
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
from openpyxl import Workbook
from rest_framework.renderers import JSONRenderer
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer

from core.tasks import migrate_academic_session,migrate_school_class,migrate_subjects,migrate_subjectsperclass,migrate_users_task,migrate_subject_teachers,migrate_class_teachers,migrate_scores,migrate_result,migrate_enrollment,migrate_admissionnumber,migrate_studentaffective,migrate_studentpsychomotor,migrate_student_profile

User = get_user_model()

from core.api.utilities import *


class TermListCreateAPIView(generics.ListCreateAPIView):
    # ListCreateAPIView gives us both the get and post methods
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
class TermDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset =Term.objects.all()
    serializer_class = TermSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    

class SessionListCreateAPIView(generics.ListCreateAPIView):
    # ListCreateAPIView gives us both the get and post methods
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
class SessionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset =Session.objects.all()
    serializer_class = SessionSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
class SchoolClassCreateAPIView(generics.ListCreateAPIView):
    # ListCreateAPIView gives us both the get and post methods
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
class SchoolClassDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset =SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    

class SubjectCreateAPIView(generics.ListCreateAPIView):
    # ListCreateAPIView gives us both the get and post methods
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
class SubjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset =Subject.objects.all()
    serializer_class = SubjectSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    

class SubjectPerClassCreateAPIView(generics.ListCreateAPIView):
    # ListCreateAPIView gives us both the get and post methods
    queryset = SubjectPerClass.objects.all()
    serializer_class = SubjectPerClassSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
class SubjectPerClassDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset =SubjectPerClass.objects.all()
    serializer_class = SubjectPerClassSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    
    
class AttendanceSettingsCreateAPIView(generics.ListCreateAPIView):
    # ListCreateAPIView gives us both the get and post methods
    queryset = AttendanceSetting.objects.all()
    serializer_class = AttendanceSettingSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
class AttendanceSettingsClassDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset =AttendanceSetting.objects.all()
    serializer_class = AttendanceSettingSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    


class ResumptionSettingsCreateAPIView(generics.ListCreateAPIView):
    # ListCreateAPIView gives us both the get and post methods
    queryset = ResumptionSetting.objects.all()
    serializer_class = ResumptionSettingSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    
# get resumption date by sesstion and curren term
# error for this code is object of type ResumeSetting is not JSON serializable
# not in use
# class GetResumptionDate(APIView):
#     serializer_class = ResumptionSettingSerializer
#     # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get(self,request):
        
#         termid = request.query_params.get('term')
#         sessionid = request.query_params.get('session')
      
#         queryset = ResumptionSetting.objects.filter(current_term=termid,session=sessionid).first()
        
#         if not queryset:
#             raise ValidationError("No records available")
#         return Response(queryset)
    
    
    
class ResumptionSettingsClassDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ResumptionSetting.objects.all()
    serializer_class = ResumptionSettingSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    

class StudentProfileListAPIView(generics.ListAPIView):
    # ListCreateAPIView gives us both the get and post methods
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
# class FilteredRecordListView(generics.ListAPIView):
#     serializer_class = RecordSerializer

#     def get_queryset(self):
#         return Record.objects.filter(status__isnull=True)  # Fi

# get scores based on subject, term, session and class
class StudentsWithNoNumber(APIView):
    def get(self, request):
        
        queryset = StudentProfile.objects.filter(admission_number__isnull=True)
        if not queryset:
            raise ValidationError("No records matching your criteria")
        
        # Serialize the data and return the response
        serializer = StudentProfileSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
class AssignNumberAPIView(generics.RetrieveUpdateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
 

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        adm_number = AdmissionNumber.objects.filter(status='No').first()
        session = Session.objects.get(pk=instance.session_admitted.pk)
        if adm_number:
            numberItem = adm_number.serial_no
            admissionstring ='SKY/ADM/'+session.name+'/'+ str(numberItem)
            instance.admission_number = numberItem
            instance.admission_numberstring = admissionstring
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            raise ValidationError({"message":"No assigned number available"})
    

# create student profile
class StudentProfileCreate(generics.CreateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    
    def get_queryset(self):
        return StudentProfile.objects.all()
    
    def perform_create(self, serializer):
        try:
            pk = self.kwargs.get('pk')
            
            # get user instance
            user = User.objects.get(pk=pk)
            
            # get the instance of admission number
            adm_number = serializer.validated_data['admission_number']
            adm_num_obj = AdmissionNumber.objects.get(serial_no=adm_number)
            
            sess_admitted = serializer.validated_data['session_admitted']
            session = Session.objects.get(pk=sess_admitted.pk)
            
            # admissionstring = 'SKY/STDM/'
            
            guardian = serializer.validated_data['guardian']
            local_govt = serializer.validated_data['local_govt']
            admission_number = adm_number
            admission_numberstring = serializer.validated_data['admission_numberstring']
            address = serializer.validated_data['address']
            session_admitted = serializer.validated_data['session_admitted']
            term_admitted = serializer.validated_data['term_admitted']
            class_admitted = serializer.validated_data['class_admitted']
            
            serializer.save(user=user)
            
            adm_num_obj.status = 'Yes'
            adm_num_obj.save()
            
        except User.DoesNotExist:
            raise NotFound("User with the provided ID does not exist.")
        except AdmissionNumber.DoesNotExist:
            raise NotFound("AdmissionNumber with the provided ID does not exist.")
        except Session.DoesNotExist:
            raise NotFound("Session with the provided ID does not exist.")
        except Exception as e:
            # Handle other exceptions here
            raise e  # You might want to log the exception or handle it differently
        
        
# create student profile using user id
# class StudentProfileCreate(generics.CreateAPIView):
#     queryset = StudentProfile.objects.all()
#     serializer_class = StudentProfileSerializer
#     # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    
#     def get_queryset(self):
#         # just return the subjectteacher object
#         return StudentProfile.objects.all()
     
    
#     def perform_create(self,serializer):
        
#         pk = self.kwargs.get('pk')
        
#         # get user instance
#         user= User.objects.get(pk=pk)
        
#         # get the instance of admission number
#         adm_numObj = AdmissionNumber.objects.get(pk=serializer.validated_data['admission_number'])
        
#         session = Session.objects.get(pk=serializer.validated_data['session_admitted'])
    
#         admissionstring ='SKY/ADM/'+session.name+'/'+ str(serializer.validated_data['admission_number'])
        
#         guardian = serializer.validated_data['guardian']
#         local_govt = serializer.validated_data['local_govt']
#         admission_number = serializer.validated_data['admission_number']
#         admission_numberstring = admissionstring
#         address = serializer.validated_data['address']
#         session_admitted = serializer.validated_data['session_admitted']
#         term_admitted = serializer.validated_data['term_admitted']
#         class_admitted = serializer.validated_data['class_admitted']
        
        
#         serializer.save(user=user)
        
#         adm_numObj.status='Yes'
#         adm_numObj.save()
        

    
class StudentProfileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    

# class TeacherProfileCreateAPIView(generics.ListCreateAPIView):
#     # ListCreateAPIView gives us both the get and post methods
#     queryset = TeacherProfile.objects.all()
#     serializer_class = TeacherProfileSerializer
#     # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]

class TeacherProfileCreateAPIView(generics.CreateAPIView):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    
    def get_queryset(self):
        # just return the subjectteacher object
        return TeacherProfile.objects.all()
     
    
    def perform_create(self,serializer):
        
        pk = self.kwargs.get('pk')
        
        # get movie
        user= User.objects.get(pk=pk)
        
        qualification = serializer.validated_data['qualification']
        local_govt = serializer.validated_data['local_govt']
        address = serializer.validated_data['address']
        
        serializer.save(user=user)
    
class TeacherProfileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    

class SubjectTeacherListAPIView(generics.ListAPIView):
    queryset = SubjectTeacher.objects.all()
    serializer_class = SubjectTeacherSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    
# create a subject teacher given a userid
class SubjectTeacherCreateAPIView(generics.CreateAPIView):
    
    serializer_class = SubjectTeacherSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    
    def get_queryset(self):
        # just return the subjectteacher object
        return SubjectTeacher.objects.all()
     
    #  we need to overwrite the current function becos we need to pass the current movie ID for which review is being created
    
    def perform_create(self,serializer):
        
        pk = self.kwargs.get('pk')
        
        # get movie
        user= User.objects.get(pk=pk)
        
        # subject = serializer.validated_data.get('subject')
        # classroom = serializer.validated_data.get('classroom')
        # sessionId = serializer.validated_data.get('session')
        subject = self.request.data.get("subject")
        classroom = self.request.data.get("classroom")
        session = self.request.data.get("session")
        # subject = serializer.validated_data['subject']
        # classroom = serializer.validated_data['classroom']
        # sessionId = serializer.validated_data['session']
        print(subject)
        subj = Subject.objects.get(pk=subject)
        class_ = SchoolClass.objects.get(pk=classroom)
        session_ = Session.objects.get(pk=session)
        # subject = serializer.validated_data['subject']
        # classroom = serializer.validated_data['classroom']
        # sessionId = serializer.validated_data['session']
        
        # subject = Subject.objects.get(pk=subject_id)
        # classroom = SchoolClass.objects.get(pk = classroom_id)
        
        # logic to prevent multple creation of subjectteacher by a user
        _queryset = SubjectTeacher.objects.filter(teacher=user,subject=subject,classroom=classroom,session=session)
        
        if _queryset.exists():
            
            raise ValidationError("You are already a subject teacher")
        # custom calculations
        # check if rating is 0 
        # if movie.number_rating == 0:
        #     movie.avg_rating = serializer.validated_data['rating']
        # else:
        #     movie.avg_rating = (movie.avg_rating + serializer.validated_data['rating'])/2
        
        # # increase the rating  
        # movie.number_rating = movie.number_rating + 1
        
        # # save
        # movie.save()
        
        # save together with related watchlist and user
        serializer.save(teacher=user,subject=subj,classroom=class_,session=session_)


class ToggleSubjectTeacherAPIView(generics.RetrieveUpdateAPIView):
    queryset = SubjectTeacher.objects.all()
    serializer_class = SubjectTeacherSerializer
    # lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = not instance.status # Toggle the status
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SubjectTeacherClassDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubjectTeacher.objects.all()
    serializer_class = SubjectTeacherSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]



# create class teacher using userid
class ClassTeacherListAPIView(generics.ListAPIView):
    queryset = ClassTeacher.objects.all()
    serializer_class = ClassTeacherSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    
# create a class teacher given a userid
class ClassTeacherCreateAPIView(generics.CreateAPIView):
    queryset = ClassTeacher.objects.all()
    serializer_class = ClassTeacherSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    
    def get_queryset(self):
        # just return the subjectteacher object
        return ClassTeacher.objects.all()
     
    #  we need to overwrite the current function becos we need to pass the current movie ID for which review is being created
    
    def perform_create(self,serializer):
        
        pk = self.kwargs.get('pk')
        
        # get movie
        user= User.objects.get(pk=pk)
        
        term = serializer.validated_data['term']
        classroom = serializer.validated_data['classroom']
        session = serializer.validated_data['session']
        
        # logic to prevent multple creation of class teacher by a user
        _queryset = ClassTeacher.objects.filter(tutor=user,term=term,classroom=classroom,session=session)
        
        if _queryset.exists():
            
            raise ValidationError("Record already exist")
        
        serializer.save(tutor=user)


class ToggleClassTeacherAPIView(generics.RetrieveUpdateAPIView):
    queryset = ClassTeacher.objects.all()
    serializer_class = ClassTeacherSerializer
    

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
   
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = not instance.status # Toggle the status
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ClassTeacherDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassTeacher.objects.all()
    serializer_class = ClassTeacherSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]


# scores
class ScoresListAPIView(generics.ListAPIView):
    queryset = Scores.objects.all()
    serializer_class = ScoresSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]

# create individual score
class ScoresCreateAPIView(generics.CreateAPIView):
    queryset = Scores.objects.all()
    serializer_class = ScoresSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    
    def get_queryset(self):
        # just return the subjectteacher object
        return Scores.objects.all()
     
    
    def perform_create(self,serializer):
        
        pk = self.kwargs.get('pk')
        
        # get user
        user= User.objects.get(pk=pk)
        
        term = serializer.validated_data['term']
        studentclass = serializer.validated_data['studentclass']
        session = serializer.validated_data['session']
        subject = serializer.validated_data['subject']
        firstscore = serializer.validated_data['firstscore']
        secondscore = serializer.validated_data['secondscore']
        thirdscore = serializer.validated_data['thirdscore']
        examscore = serializer.validated_data['examscore']
        
        totalca = 0
        subjecttotal =0
        
        if math.isnan(firstscore):
            firstscore = 0
        else:
            firstscore = firstscore
        
        if math.isnan(secondscore):
            secondscore = 0
        else:
            secondscore = secondscore
        
        if math.isnan(thirdscore):
            firstscore = 0
        else:
            thirdscore = thirdscore
        
        if math.isnan(examscore):
            examscore = 0
        else:
            examscore = examscore
        
        totalca = firstscore + secondscore + thirdscore
        subjecttotal = totalca + examscore
        
        teacher = self.request.user
        
        # _isteacher = SubjectTeacher.objects.filter(teacher_id=teacher.pk,classroom=studentclass.pk,session=session.pk,subject=subject.pk)
        # if not _isteacher:
        #     raise ValidationError("You are not a subject teacher for this class")
            
        
        # logic to prevent multple creation of record
        _queryset = Scores.objects.filter(user=user,term=term,studentclass=studentclass,session=session,subject=subject)
        
        if _queryset.exists():
            
            raise ValidationError("Record already exist")
        
        serializer.save(user=user,subjectteacher=SubjectTeacher.objects.filter(teacher=teacher).first(),firstscore=firstscore,secondscore=secondscore,thirdscore=thirdscore,totalca=totalca,subjecttotal=subjecttotal)
        processScores(subject,studentclass,term,session)
        
        
# get scores based on subject, term, session and class
class FindScoresAPIView(APIView):
    def get(self, request):
        payload = request.query_params
        
        subjObj = Subject.objects.get(pk=payload.get('subject'))
        classObj = SchoolClass.objects.get(pk=payload.get('studentclass'))
        termObj = Term.objects.get(pk=payload.get('term'))
        sessionObj = Session.objects.get(pk=payload.get('session'))

        # Example usage: filtering queryset based on payload parameters
        queryset = Scores.objects.filter(subject=subjObj,studentclass=classObj,session=sessionObj,term=termObj)
        if not queryset:
            raise ValidationError("No records matching your criteria")
        
        # Serialize the data and return the response
        serializer = ScoresSerializer(queryset, many=True)
        return Response(serializer.data)
    
# new optimize code



class FindScoresAPIView(APIView):
    def get(self, request):
        payload = request.query_params

        subjObj = get_object_or_404(Subject, pk=payload.get('subject'))
        classObj = get_object_or_404(SchoolClass, pk=payload.get('studentclass'))
        termObj = get_object_or_404(Term, pk=payload.get('term'))
        sessionObj = get_object_or_404(Session, pk=payload.get('session'))

        # Optimize the queryset by selecting related foreign key objects
        queryset = Scores.objects.select_related(
            'user',
            'term',
            'session',
            'studentclass',
            'subject',
            'subjectteacher'
        ).filter(
            subject=subjObj,
            studentclass=classObj,
            term=termObj,
            session=sessionObj
        )

        if not queryset.exists():
            raise ValidationError("No records matching your criteria")

        serializer = ScoresSerializer(queryset, many=True)
        return Response(serializer.data)

    
# get scores based on term, session and class
class FilterTerminalScoresAPIView(APIView):
    def get(self, request):
        
        payload = request.query_params
        print(payload)
        myterm = payload.get('term')
        mysession = payload.get('session')
        myclass= payload.get('classroom')
        
        # subjObj = Subject.objects.get(pk=payload.get('subject'))
        classObj = SchoolClass.objects.get(pk=myclass)
        termObj = Term.objects.get(pk=myterm)
        sessionObj = Session.objects.get(pk=mysession)
        

        # Example usage: filtering queryset based on payload parameters
        queryset = Scores.objects.filter(studentclass=classObj,session=sessionObj,term=termObj)
        if not queryset:
            raise ValidationError("No records matching your criteria")
        
        # Serialize the data and return the response
        serializer = ScoresSerializer(queryset, many=True)
        return Response(serializer.data)
        

# score detail
class ScoresDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Scores.objects.all()
    serializer_class = ScoresSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]

# user scores for term
class UserScoresList(generics.ListAPIView):
    serializer_class = ScoresSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        
        userid = self.kwargs.get('userid')
        termid = self.kwargs.get('term')
        sessionid = self.kwargs.get('session')
        classid = self.kwargs.get('class')
        
        # 
        user = User.objects.get(pk=userid)
        term = Term.objects.get(pk=termid)
        session = Session.objects.get(pk=sessionid)
        classroom = SchoolClass.objects.get(pk=classid)
        
        
        # Example: Fetching data based on a filter field named 'filter_field'
        queryset = Scores.objects.filter(user=userid,term=termid,session=sessionid,studentclass=classid)
        
        if not queryset:
            raise ValidationError("No records available")
        return queryset

# code to build and process scores after uploading
class BuidScores(generics.CreateAPIView):
    serializer_class = ScoresSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        # just return the review object
        return Scores.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        
        with transaction.atomic():
            
            try:
                # Access form values from the request object
                _class = request.data.get('studentclass')
                # term = request.data.get('term')
                # session = request.data.get('session')
                subj = request.data.get('subj')
                
                classObj = SchoolClass.objects.get(pk=_class)
                # termObj = Term.objects.get(pk=term)
                # sessionObj = Session.objects.get(pk=session)
                
                
                subjectObj = Subject.objects.get(pk=subj)   
                activeTerm = Term.objects.get(status='True')
                activeSession = Session.objects.get(status='True')
                
                # loggedInUser = request.user
                
                # _isteacher = ClassTeacher.objects.filter(tutor=loggedInUser,classroom=classObj)
                # if not _isteacher:
                #     raise ValidationError("You are not a class teacher for this class")
                
                
                # process terminal scores
                processScores(subjectObj,classObj,activeTerm,activeSession)

            except Exception as e:
                raise ValidationError(e)
           
        return Response(
                {'msg':'Scores build/processed successfully'},
                status = status.HTTP_201_CREATED
                )



 
class CreateResult(generics.CreateAPIView):
    serializer_class = ResultSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        # just return the review object
        return Result.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        
        with transaction.atomic():
            
            try:
                # Access form values from the request object
                _class = request.data.get('studentclass')
                term = request.data.get('term')
                session = request.data.get('session')
                
                classObj = SchoolClass.objects.get(pk=_class)
                termObj = Term.objects.get(pk=term)
                sessionObj = Session.objects.get(pk=session)
                
                loggedInUser = request.user
                
                _isteacher = ClassTeacher.objects.filter(tutor=loggedInUser,classroom=classObj)
                if not _isteacher:
                    raise ValidationError("You are not a class teacher for this class")
                
                
                # process terminal result
                processTerminalResult(request,classObj,termObj,sessionObj)

                    # process terminal result
                    # processAnnualResult(score)

                    # Add auto comment
                    # autoAddComment(score.studentclass,score.session,score.term)

                    # proccess Affective domain
                    # processAffective(score)

                    # process Psychomotor domain
                    # processPsycho(score)
                
            except Exception as e:
                raise ValidationError(e)
           
        return Response(
                {'msg':'Result created successfully'},
                status = status.HTTP_201_CREATED
                )
    
# List all result based on term, class, session
# class ExportSheet(APIView):
#     # serializer_class = ClassroomSerializer
#     # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
#     renderer_classes = [XLSXRenderer, JSONRenderer]
    
#     def get(self,request):
#         try:
#             payload = request.query_params
            
#             activeTerm = Term.objects.get(status='True')
#             activeSession = Session.objects.get(status='True')
            
#             classObj = SchoolClass.objects.get(pk=payload.get('classroom'))
#             subjObj = Subject.objects.get(pk=payload.get('subject'))

            
#             teacher = self.request.user
        
#             # _isteacher = SubjectTeacher.objects.filter(teacher_id=teacher.pk,classroom=classObj.pk,session=activeSession.pk,subject=subjObj.pk)
#             # if not _isteacher:
#             #     raise ValidationError("You are not a subject teacher for this class")

#             response = Response(content_type='text/csv')
#             response['Content-Disposition'] = 'attachment; filename=CA_SHEET_'+subjObj.name+'_'+classObj.class_name+'_'+activeTerm.name+'_'+activeSession.name+'.csv'
#             writer = csv.writer(response)
            
#             writer.writerow(['StudentID','Name','Class','Subject','FirstCA','SecondCA','ThirdCA','Exam'])
            
#             rollcall = Classroom.objects.filter(Q(session=activeSession) & Q(class_room=classObj) & Q(term=activeTerm)).order_by('student__sur_name')
#             # subject = Subject.objects.get(pk=subject)
            
#             for item in rollcall:
#                 writer.writerow([item.student.pk,item.student.sur_name + "  " + item.student.first_name,classObj.class_name,subjObj.subject_code,0,0,0,0])

#             return response
    
#         except Exception as e:
            
#             raise ValidationError("Unable to download the sheet")

# export sheet 
class ExportSheet(APIView):
    # 1 this works Adopt this one
    def get(self, request):
        
        payload = request.query_params
        
        classname = payload.get('classname')
        subjname = payload.get('subjname')
        classid = payload.get('classid')
        subjectid = payload.get('subjectid')
        
        classObj = SchoolClass.objects.get(pk=classid)    
        activeTerm = Term.objects.get(status='True')
        activeSession = Session.objects.get(status='True')
        
        rollcall = Classroom.objects.filter(Q(session=activeSession) & Q(class_room=classObj) & Q(term=activeTerm)).order_by('student__sur_name')

        # Create an in-memory Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active

        # Write headers to the worksheet
        headers = ['STDID', 'NAME', 'CLASS','CLASSID','SUBJNAME','SUBJID','TRM','SESS','CA1','CA2','CA3','EXAM']
        ws.append(headers)

        # Write data to the worksheet
        for item in rollcall:
            row = [item.student.id,item.student.sur_name +' '+ item.student.first_name, classname,classid,subjname, subjectid, activeTerm.name,activeSession.name,0,0,0,0]
            ws.append(row)

        # Create a response object with the appropriate content type and headers
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=your_data.xlsx'

        # Save the workbook to the response
        wb.save(response)

        return response
    
     # 2 works as well 
    # def get(self, request):
        
    #     custom_header = ['Product1', 'Price2','Product3', 'Price4','Product5', 'Price6','Product7', 'Price8']
    #     userObj = Classroom.objects.all()
    #     serializer = ClassroomSerializer(userObj, many=True)
    #     df = pd.DataFrame(serializer.data)
    #     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    #     response['Content-Disposition'] = 'attachment; filename="out.xlsx"'
    #     df.to_excel(response, na_rep='N/A', header=custom_header, index=False)

    #     return response
    
    
    
# export attendance sheet
class ExportAttendanceSheet(APIView):
    # 1 this works Adopt this one
    def get(self, request):
        
        payload = request.query_params
        
        classroom_id = payload.get('classroom')
        term_id = payload.get('term')
        session_id = payload.get('session')
        
        classObj = SchoolClass.objects.get(pk=classroom_id)    
        termObj = Term.objects.get(pk=term_id)
        sessObj = Session.objects.get(pk=session_id)
        
        rollcall = Result.objects.filter(Q(session=sessObj) & Q(studentclass=classObj) & Q(term=termObj)).order_by('student__sur_name')

        # Create an in-memory Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active

        # Write headers to the worksheet
        headers = ['RSLTID', 'NAME', 'CLASS','TRM','SESS','POS','ATT']
        ws.append(headers)

        # Write data to the worksheet
        for item in rollcall:
            row = [item.id,item.student.sur_name +' '+ item.student.first_name, classObj.class_name, termObj.name,sessObj.name,item.termposition,]
            ws.append(row)

        # Create a response object with the appropriate content type and headers
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=your_data.xlsx'

        # Save the workbook to the response
        wb.save(response)

        return response
    
# upload attendance
class UploadTerminalAttendance(generics.CreateAPIView):
    serializer_class = ResultSerializer
    parser_classes = (MultiPartParser, FormParser,)
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # just return the review object
        return Result.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        with transaction.atomic():
              
            try:
                 if 'file' not in request.FILES:
                     raise ValidationError({"msg":"no file chosen"})
                 else:
                    data = request.FILES['file']
                   
                    reader = pd.read_excel(data)
                    reader = reader.where(pd.notnull(reader), None)
                    dtframe = reader
                  
                
                    for row in dtframe.itertuples():
                        resultObj = Result.objects.get(pk=row.RSLTID)
                        resultObj.attendance = row.ATT
                        resultObj.save()
            except Exception as e:
                
                raise ValidationError(e)
           
        return Response(
                {'msg':'Attendance created successfully'},
                status = status.HTTP_201_CREATED
                )





# upload/import CA EXCEL SHEET
class ImportAssessment(generics.CreateAPIView):
    serializer_class = ScoresSerializer
    parser_classes = (MultiPartParser, FormParser,)
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    permission_classes = [IsAuthenticated]
    
    # def get_queryset(self):
        # just return the review object
        # return Scores.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        with transaction.atomic():
              
            try:
                 if 'file' not in request.FILES:
                    
                     raise ValidationError({"msg":"no file chosen"})
                 else:
                    data = request.FILES['file']
                   
                    reader = pd.read_excel(data)
                    # reader = reader.where(pd.notnull(reader), None)
                    dtframe = reader.fillna(0)
                  
                
                    for dtframe in dtframe.itertuples():
                        studentObj=User.objects.get(pk=dtframe.STDID)
                        classObj = SchoolClass.objects.get(pk=dtframe.CLASSID) 
                        subjectObj = Subject.objects.get(pk=dtframe.SUBJID)   
                        activeTerm = Term.objects.get(status='True')
                        activeSession = Session.objects.get(status='True')
                     
                    
                        # check for subject teacher
                        teacher = self.request.user
                        
                        # _isteacher = SubjectTeacher.objects.filter(teacher=teacher.pk,classroom=int(dtframe.CLASSID),session=activeSession.pk,subject=dtframe.SUBJID)
                        
                        # for use this term
                        subjteacher = SubjectTeacher.objects.filter(classroom=dtframe.CLASSID,session=activeSession.pk,subject=dtframe.SUBJID).first()
                        
                        # if not _isteacher:
                        #     raise ValidationError("You are not a subject teacher for this class")
                        # else:
                            # check if studentexist in class
                        isEnrolled = Classroom.objects.filter(session=activeSession,term=activeTerm,class_room = classObj,student=dtframe.STDID).exists()
                        if  not isEnrolled:
                            pass
                        else:
                            
                            # check for existence of scores
                            scoresExist = Scores.objects.filter(session=activeSession.pk,term=activeTerm.pk,subject=dtframe.SUBJID,studentclass=dtframe.CLASSID,user=dtframe.STDID).exists()
                    
                            if scoresExist:
                                
                                pass
                            else:
                                
                                    
                                # ca1 = 0
                                # ca2 = 0
                                # ca3 = 0
                                # exam = 0
                
                                # if not math.isnan(dtframe.CA1):
                                #     ca1 = dtframe.CA1
                                # elif not math.isnan(dtframe.CA2):
                                #     ca2 = dtframe.CA2
                                # elif not math.isnan(dtframe.CA3):
                                #     ca3 = dtframe.CA3
                                # elif not math.isnan(dtframe.EXAM):
                                #     exam = dtframe.EXAM
                    
                                obj = Scores.objects.create(
                                        firstscore=dtframe.CA1,
                                        secondscore=dtframe.CA2,
                                        thirdscore=dtframe.CA3,
                                        totalca=dtframe.CA1 + dtframe.CA2 + dtframe.CA3,
                                        examscore=dtframe.EXAM,
                                        subjecttotal=dtframe.EXAM + dtframe.CA1 + dtframe.CA2 + dtframe.CA3,
                                        session=activeSession,
                                        term=activeTerm,
                                        user=studentObj,
                                        studentclass=classObj,
                                        subjectteacher= SubjectTeacher.objects.get(teacher=subjteacher.teacher.pk,classroom=dtframe.CLASSID,session=activeSession.pk,subject=dtframe.SUBJID),
                                        subject=subjectObj,
                                    )
                                    
                                obj.save()
                    
                    # process scores -moved this to a different view BuildScores
                    # processScores(subjectObj,classObj,activeTerm,activeSession)
                  
            except Exception as e:
                
                raise ValidationError(e)
           
        return Response(
                {'msg':'Assessment created successfully'},
                status = status.HTTP_201_CREATED
                )
        

# List all result based on term, class, session
class GetResult(generics.ListAPIView):
    serializer_class = ResultSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        # _class = self.request.data.get('classroom')
        # _session = self.request.data.get('session')
        # _term = self.request.data.get('term')
        payload = self.request.query_params
        
        # myclass = payload.get('classroom')
        # classObj = SchoolClass.objects.get(pk=myclass)
        # termObj = Term.objects.get(pk=payload.get('term'))
        # sessionObj = Session.objects.get(pk=payload.get('session'))
       
        classObj = get_object_or_404(SchoolClass, pk=payload.get('classroom'))
        termObj = get_object_or_404(Term, pk=payload.get('term'))
        sessionObj = get_object_or_404(Session, pk=payload.get('session'))
        
    
        
        # Example: Fetching data based on a filter field named 'filter_field'
        queryset = Result.objects.select_related(
            'student',
            'term',
            'session',
            'studentclass',
            'classteacher',
        ).filter(studentclass=classObj,session=sessionObj,term=termObj)
        
        if not queryset.exists():
            raise ValidationError("No records matching your criteria")
        return queryset

# Detail Result
class ResultDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    

# retrieve all result given a student id
class UserResultList(generics.ListAPIView):
    serializer_class = ResultSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        
        pk = self.kwargs.get('pk')
        
        # Example: Fetching data based on a filter field named 'filter_field'
        queryset = Result.objects.filter(student=pk)
        
        if not queryset:
            raise ValidationError("No records available")
        return queryset
    

class CreateStudentAffectiveTraits(generics.CreateAPIView):
    serializer_class = StudentaffectiveSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        # just return the review object
        return Studentaffective.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        
        with transaction.atomic():
            
            try:
                # Access form values from the request object
                _class = request.data.get('studentclass')
                term = request.data.get('term')
                session = request.data.get('session')
                
                classObj = SchoolClass.objects.get(pk=_class)
                termObj = Term.objects.get(pk=term)
                sessionObj = Session.objects.get(pk=session)
                
                loggedInUser = request.user
                
                # _isteacher = ClassTeacher.objects.filter(tutor=loggedInUser,classroom=classObj,session=sessionObj,term=termObj)
                # if not _isteacher:
                #     raise ValidationError("You are not a class teacher for this class")
                
                
               # proccess Affective domain
                processAffective(classObj,sessionObj,termObj)

            except Exception as e:
                raise ValidationError(e)
           
        return Response(
                {'msg':'Student affective traits created successfully'},
                status = status.HTTP_201_CREATED
                )
        
class CreateStudentPsychoTraits(generics.CreateAPIView):
    serializer_class = StudentpsychomotorSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        # just return the review object
        return Studentpsychomotor.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        
        with transaction.atomic():
            
            try:
                # Access form values from the request object
                _class = request.data.get('studentclass')
                term = request.data.get('term')
                session = request.data.get('session')
                
                classObj = SchoolClass.objects.get(pk=_class)
                termObj = Term.objects.get(pk=term)
                sessionObj = Session.objects.get(pk=session)
                
                loggedInUser = request.user
                
                # _isteacher = ClassTeacher.objects.filter(tutor=loggedInUser,classroom=classObj,session=sessionObj,term=termObj)
                # if not _isteacher:
                #     raise ValidationError("You are not a class teacher for this class")

                # process Psychomotor domain
                processPsycho(classObj,sessionObj,termObj)

                    
            except Exception as e:
                raise ValidationError(e)
           
        return Response(
                {'msg':'Student psycho traits created successfully'},
                status = status.HTTP_201_CREATED
                )
        
        
        
class AddAutoComents(generics.CreateAPIView):
    serializer_class = ResultSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        # just return the review object
        return Result.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        
        with transaction.atomic():
            
            try:
                # Access form values from the request object
                _class = request.data.get('studentclass')
                term = request.data.get('term')
                session = request.data.get('session')
                
                classObj = SchoolClass.objects.get(pk=_class)
                termObj = Term.objects.get(pk=term)
                sessionObj = Session.objects.get(pk=session)
                
                loggedInUser = request.user
                
                # _isteacher = ClassTeacher.objects.filter(tutor=loggedInUser,classroom=classObj,session=sessionObj,term=termObj)
                
                # if not _isteacher:
                #     raise ValidationError("You are not a class teacher for this class")
                
                scores = Scores.objects.filter(session=sessionObj,term=termObj,studentclass=classObj).exists()

                if not scores:
                    raise ValidationError("You are not a class teacher for this class")
                    # Add auto comment
                autoAddComment(classObj,sessionObj,termObj)

            except Exception as e:
                raise ValidationError(e)
           
        return Response(
                {'msg':'comments created successfully'},
                status = status.HTTP_201_CREATED
                )    

# ratings
class RatingCreateAPIView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
class RatingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
# Psychomotor
class PsychomotorCreateListAPIView(generics.ListCreateAPIView):
    queryset = Psychomotor.objects.all()
    serializer_class = PsychomotorSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
class PyschomotorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Psychomotor.objects.all()
    serializer_class = PsychomotorSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    
class AffectiveCreateListAPIView(generics.ListCreateAPIView):
    queryset = Affective.objects.all()
    serializer_class = AffectiveSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
class AffectiveDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Affective.objects.all()
    serializer_class = AffectiveSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
    
# List all student affective traits based on term, class, session
class GetStudentAffectiveTraits(generics.ListAPIView):
    serializer_class = StudentaffectiveSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        userid = self.kwargs.get('userid')
        _class = self.kwargs.get('classroom')
        _term = self.kwargs.get('term')
        _session = self.kwargs.get('session')
        
        classObj = SchoolClass.objects.get(pk=_class)
        termObj = Term.objects.get(pk=_term)
        sessionObj = Session.objects.get(pk=_session)
        user = User.objects.get(pk=userid)
        
        
        # Example: Fetching data based on a filter field named 'filter_field'
        queryset = Studentaffective.objects.filter(studentclass=classObj,session=sessionObj,term=termObj,student=user)
        
        if not queryset:
            raise ValidationError("No records matching your criteria")
        return queryset
    

# List all student affective traits based on term, class, session
class GetStudentPsychoTraits(generics.ListAPIView):
    serializer_class = StudentpsychomotorSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        userid = self.kwargs.get('userid')
        _class = self.kwargs.get('classroom')
        _term = self.kwargs.get('term')
        _session = self.kwargs.get('session')
        
        classObj = SchoolClass.objects.get(pk=_class)
        termObj = Term.objects.get(pk=_term)
        sessionObj = Session.objects.get(pk=_session)
        user = User.objects.get(pk=userid)
        
        
        # Example: Fetching data based on a filter field named 'filter_field'
        queryset = Studentpsychomotor.objects.filter(studentclass=classObj,session=sessionObj,term=termObj,student=user)
        
        if not queryset:
            raise ValidationError("No records matching your criteria")
        return queryset
    
# Enroll newly admitted students in their class
class NewStudentsMassEnrollStudent(generics.CreateAPIView):
    serializer_class = ClassroomSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        # just return the review object
        return Classroom.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        
        with transaction.atomic():
            
            try:
                new_class = request.data.get('newclass')
                new_term = request.data.get('newterm')
                new_session = request.data.get('newsession')
                
                newlyadmittedstudents = StudentProfile.objects.filter(Q(term_admitted=new_term) & Q(session_admitted=new_session) & Q (class_admitted=new_class)).distinct('user')
                
                if not newlyadmittedstudents:
                    raise ValidationError("No records available for your selection")
                
                else:
                    for row in newlyadmittedstudents:
                        std_obj = Classroom.objects.filter(student=row.user.pk,class_room=new_class,session=new_session,term=new_term)
                        if std_obj:
                            continue
                            
                        enrollObj = Classroom.objects.create(
                        class_room=SchoolClass.objects.get(pk=new_class),
                        ession = Session.objects.get(pk=new_session),
                        erm = Term.objects.get(pk=new_term),
                        student = User.objects.get(pk=row.user.pk)
                        )
                    enrollObj.save()
  
            except Exception as e:
                raise ValidationError(e)
           
        return Response(
                {'msg':'Enrollment created successfully'},
                status = status.HTTP_201_CREATED
                )  


# Enroll individual student in class room
class EnrollStudent(generics.CreateAPIView):
    serializer_class = ClassroomSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        # just return the review object
        return Classroom.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        
        with transaction.atomic():
            
            try:
                activeTerm = Term.objects.get(status='True')
                activeSession = Session.objects.get(status='True')
                # Access form values from the request object
                _class = request.data.get('class_room')
                admission_number = request.data.get('student')
            
                student = StudentProfile.objects.get(admission_number=admission_number)
                
                classObj = SchoolClass.objects.get(pk=_class)
                
                
                # check if student is already enrolled
                studentEnrolled = Classroom.objects.filter(Q(term=activeTerm) & Q(session=activeSession) & Q (class_room=classObj.pk) & Q(student=student.user.pk))
                
                if studentEnrolled:
                    raise ValidationError("You are already enrolled")
                
                enrollObj = Classroom.objects.create(
                        class_room=classObj,
                        session = activeSession,
                        term = activeTerm,
                        student = student.user
                        )
                enrollObj.save()
  
            except Exception as e:
                raise ValidationError(e)
           
        return Response(
                {'msg':'Enrollment created successfully'},
                status = status.HTTP_201_CREATED
                )
        

# Mass enrollment
class MassEnrollStudent(generics.CreateAPIView):
    serializer_class = ClassroomSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    def get_queryset(self):
        # just return the review object
        return Classroom.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        
        with transaction.atomic():
            
            try:
                
                from_class = request.data.get('oldclass')
                from_term = request.data.get('oldterm')
                from_session = request.data.get('oldsession')
                
                to_class = request.data.get('nextclassroom')
                to_term = request.data.get('nextterm')
                to_session = request.data.get('nextsession')
                
               
                
                
                studentEnrolled = Classroom.objects.filter(Q(term=from_term) & Q(session=from_session) & Q (class_room=from_class)).distinct('student')
                
                if not studentEnrolled:
                    raise ValidationError("No records available for your selection")
                
                else:
                
                    for row in studentEnrolled:
                        # check for students duplicate in class
                        stud_obj = Classroom.objects.filter(student=row.student.pk,class_room=to_class,session=to_session,term=to_term)
                        if stud_obj:
                            continue
                            
                        enrollObj = Classroom.objects.create(
                            class_room=SchoolClass.objects.get(pk=to_class),
                            session = Session.objects.get(pk=to_session),
                            term = Term.objects.get(pk=to_term),
                            student = User.objects.get(pk=row.student.pk)
                        )
                        enrollObj.save()
  
            except Exception as e:
                raise ValidationError(e)
           
        return Response(
                {'msg':'Enrollment created successfully'},
                status = status.HTTP_201_CREATED
                )
        
# # List all student in classroom based on term, class, session
# class RollCall(generics.ListAPIView):
#     serializer_class = ClassroomSerializer
#     # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
        
#         _class = self.request.data.get('classroom')
#         _term = self.request.data.get('term')
#         _session = self.request.data.get('session')
#         # classObj = SchoolClass.objects.get(pk=_class)
#         termObj = Term.objects.get(pk=_term)
#         sessionObj = Session.objects.get(pk=_session)
        
#         queryset = Classroom.objects.filter(session=sessionObj,term=termObj)
        
#         if not queryset:
#             raise ValidationError("No records matching your criteria")
#         return queryset
    
class RollCallAPIView(APIView):
    def get(self, request):
        payload = request.query_params
        # Access the query parameters
        # Use payload to filter and retrieve the desired records
        classObj = SchoolClass.objects.get(pk=payload.get('classroom'))
        termObj = Term.objects.get(pk=payload.get('term'))
        sessionObj = Session.objects.get(pk=payload.get('session'))

        # Example usage: filtering queryset based on payload parameters
        queryset = Classroom.objects.filter(class_room=classObj,session=sessionObj,term=termObj)
        if not queryset:
            raise ValidationError("No records matching your criteria")
        
        # Serialize the data and return the response
        serializer = ClassroomSerializer(queryset, many=True)
        return Response(serializer.data)

# roll call for assessment sheet
class AssessmentSheetRollCallAPIView(APIView):
    def get(self, request):
        payload = request.query_params
        # Access the query parametersF
        # Use payload to filter and retrieve the desired records
        activeTerm = Term.objects.get(status='True')
        activeSession = Session.objects.get(status='True')
        classObj = SchoolClass.objects.get(pk=payload.get('classroom'))

        # Example usage: filtering queryset based on payload parameters
        queryset = Classroom.objects.filter(class_room=classObj,session=activeSession,term=activeTerm)
        if not queryset:
            raise ValidationError("No records matching your criteria")
        
        # Serialize the data and return the response
        serializer = ClassroomSerializer(queryset, many=True)
        return Response(serializer.data)
    
# Detail Classroom
class ClassroomDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    
# endpoint to get first unassigned number  
class FirstAdmNumberView(APIView):
    def get(self, request, format=None):
        adm_number = AdmissionNumber.objects.filter(status='No').first()
        serializer = AdmissionNumberSerializer(adm_number,many=False)
        return Response(serializer.data) 


#Search student user by name
class SearchEnroll(generics.ListAPIView):
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]

    def get_queryset(self):
        name = self.request.query_params.get('name')

        if not name:
            raise ValidationError("The 'name' parameter is required.")

        
        queryset = User.objects.filter(sur_name__icontains=name)

        if not queryset.exists():
            raise ValidationError("No records matching your criteria.")

        return queryset
    
#Enroll by search 
class EnrollBySearch(generics.CreateAPIView):
    serializer_class = EnrollBySearchSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
    # def get_queryset(self):
        # just return the review object
        # return Classroom.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        user_id = request.data.get('user_id')
        class_id = request.data.get('class_id')
        
        # used only when the endpoint has parameters as part of it
        # user_id = self.request.query_params.get('user_id')

        
        with transaction.atomic():
            
            try:
                activeTerm = Term.objects.get(status='True')
                activeSession = Session.objects.get(status='True')
                
                userObj = User.objects.get(pk=user_id)
                
                classObj = SchoolClass.objects.get(pk=class_id)
                
                # get admission number
                # This code was used to initially enroll students
                # adm_number = AdmissionNumber.objects.filter(status='No').first()
                # string_number = str(adm_number.serial_no)
                # admissionstring = 'SKY/STDM/'+activeSession.name+'/'+string_number
                
                # check if student is already enrolled
                studentEnrolled = Classroom.objects.filter(Q(term=activeTerm.pk) & Q(session=activeSession.pk) & Q (class_room=classObj.pk) & Q(student=userObj.pk))
                
                if studentEnrolled:
                    raise ValidationError("You are already enrolled")
                
                # Create StudentProfile
                # myProfile = StudentProfile.objects.create(
                #     guardian = userObj.sur_name,
                #     user_id= userObj.pk,
                #     class_admitted_id =classObj.pk,
                #     session_admitted_id=activeSession.pk,
                #     term_admitted_id=activeTerm.pk,
                #     admission_number =adm_number.serial_no,
                #     admission_numberstring = admissionstring
                # )
                # myProfile.save()
                
                enrollObj = Classroom.objects.create(
                        class_room=classObj,
                        session_id = activeSession.pk,
                        term_id = activeTerm.pk,
                        student_id = userObj.pk
                        )
                enrollObj.save()
                
                # adm_number.status='Yes'
                # adm_number.save()
                
  
            except Exception as e:
                raise ValidationError(e)
           
        return Response(
                {'msg':'Enrollment created successfully'},
                status = status.HTTP_201_CREATED
                )
        
        
    
  
class FetchNewEnrollment(generics.ListAPIView):
    serializer_class = ClassroomSerializer
    # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]

    def get_queryset(self):
        class_id = self.request.query_params.get('class_id')
        activeTerm = Term.objects.get(status='True')
        activeSession = Session.objects.get(status='True')
        classObj = SchoolClass.objects.get(pk=class_id)

        if not class_id:
            raise ValidationError("The 'class id' parameter is required.")

        queryset = Classroom.objects.filter(Q(term=activeTerm.pk) & Q(session=activeSession.pk) & Q (class_room=classObj.pk))

        if not queryset.exists():
            raise ValidationError("No records matching your criteria.")

        return queryset
  
# class SearchEnroll(generics.ListAPIView):
#     serializer_class = UserSerializer
#     # permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # _class = self.request.data.get('classroom')
#         # _session = self.request.data.get('session')
#         # _term = self.request.data.get('term')
#         payload = self.request.query_params
        
#         name = payload.get('name')
        
#         # classObj = SchoolClass.objects.get(pk=myclass)
#         # termObj = Term.objects.get(pk=payload.get('term'))
#         # sessionObj = Session.objects.get(pk=payload.get('session'))
        
#         # Example: Fetching data based on a filter field named 'filter_field'
#         queryset = User.objects.filter(sur_name=name)
        
#         if not queryset:
#             raise ValidationError("No records matching your criteria")
#         return queryset






# # Migration with Celery

# class migrateSessionsCelery(generics.CreateAPIView):
#     serializer_class = SessionSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return Session.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         dtframe = reader
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_academic_session.delay(json_data)
#         return Response(
#                 {'msg':'Session Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED
#                 )

# class migrateClassCelery(generics.CreateAPIView):
#     serializer_class = SessionSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return Session.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         dtframe = reader
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_school_class.delay(json_data)
#         return Response(
#                 {'msg':'class Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED
#                 )
        
#         # migrate_subjects
        
# class migrateSubjectsCelery(generics.CreateAPIView):
#     serializer_class = SubjectSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return Subject.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         dtframe = reader
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_subjects.delay(json_data)
#         return Response(
#                 {'msg':'subjects Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED
#                 )
        
# # migrate subject per class
# class migrateSubjectPerClasssCelery(generics.CreateAPIView):
#     serializer_class = SubjectPerClassSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return SubjectPerClass.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         dtframe = reader
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_subjectsperclass.delay(json_data)
#         return Response(
#                 {'msg':'subjects per class Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED
#                 )
        
# # migrate students users
# class migrateUserCelery(generics.CreateAPIView):
#     serializer_class = UserSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return User.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         dtframe = reader
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_users_task.delay(json_data)
#         return Response(
#                 {'msg':'users Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED
#                 )
        
        
# # subject teachers

# class migrateSubjectTeachersCelery(generics.CreateAPIView):
#     serializer_class = SubjectTeacherSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return SubjectTeacher.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         dtframe = reader
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_subject_teachers.delay(json_data)
#         return Response(
#                 {'msg':'subject teachers Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED
#                 )
        
# # class teachers 
# class migrateClassTeachersCelery(generics.CreateAPIView):
#     serializer_class = ClassTeacherSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return ClassTeacher.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         dtframe = reader
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_class_teachers.delay(json_data)
#         return Response(
#                 {'msg':'class teachers Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED
#                 )
        

# # scores
# class migrateScoresCelery(generics.CreateAPIView):
#     serializer_class = ScoresSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return Scores.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
        
       
        
#         # value_to_replace = None
#         # reader.fillna(0, inplace=True)
#         # reader[['subjaverage', 'subjectposition','highest_inclass','lowest_inclass']] = reader[['subjaverage', 'subjectposition','highest_inclass','lowest_inclass']].apply(pd.to_numeric, errors='coerce')
#         # reader = reader.where(pd.notnull(reader), None)
#         dtframe = reader
        
     
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_scores.delay(json_data)
#         return Response(
#                 {'msg':'Scores Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED
#                 )
        
# # results
# class migrateResultCelery(generics.CreateAPIView):
#     serializer_class = ResultSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return Result.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         reader = reader.where(pd.notnull(reader), None)
#         dtframe = reader
        
     
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_result.delay(json_data)
#         return Response(
#                 {'msg':'result Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED)
        
# # enrollment
# class migrateEnrollmentCelery(generics.CreateAPIView):
#     serializer_class = ClassroomSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return Classroom.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         reader = reader.where(pd.notnull(reader), None)
#         dtframe = reader
        
     
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_enrollment.delay(json_data)
#         return Response(
#                 {'msg':'result Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED)
        



# # admission number
# class migrateAdNumberCelery(generics.CreateAPIView):
#     serializer_class = ClassroomSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return AdmissionNumber.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         reader = reader.where(pd.notnull(reader), None)
#         dtframe = reader
        
     
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_admissionnumber.delay(json_data)
#         return Response(
#                 {'msg':'number Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED)
        
        

# # students affective

# class migrateStudentsAffectiveCelery(generics.CreateAPIView):
#     serializer_class = StudentaffectiveSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return Affective.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         reader = reader.where(pd.notnull(reader), None)
#         dtframe = reader
        
     
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_studentaffective.delay(json_data)
#         return Response(
#                 {'msg':'affective Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED)
        

# # migrate student psychomotor
# class migrateStudentsPyschoCelery(generics.CreateAPIView):
#     serializer_class = StudentpsychomotorSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return Psychomotor.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         reader = reader.where(pd.notnull(reader), None)
#         dtframe = reader
        
     
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_studentpsychomotor.delay(json_data)
#         return Response(
#                 {'msg':'psycho Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED)
        
        
        

# # migrate student psychomotor
# class migrateStudentProfileCelery(generics.CreateAPIView):
#     serializer_class = StudentProfileSerializer
#     parser_classes = (MultiPartParser, FormParser,)
#     permission_classes = [IsAuthenticated & IsAuthOrReadOnly]
    
#     def get_queryset(self):
#         # just return the review object
#         return StudentProfile.objects.all()
    
#     def post(self, request, *args, **kwargs):
        
#         data = request.FILES['file']
#         reader = pd.read_excel(data)
#         reader = reader.where(pd.notnull(reader), None)
#         dtframe = reader
        
     
        
#         json_data = dtframe.to_json()
#         # data = json.loads(json_data)

#         with transaction.atomic():
#             migrate_student_profile.delay(json_data)
#         return Response(
#                 {'msg':'student profile Successfuly Uploaded'},
#                 status = status.HTTP_201_CREATED)
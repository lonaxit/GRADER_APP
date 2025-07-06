from dataclasses import fields
from rest_framework import serializers
# import models
from core.models import *
from django.db.models import Q, Sum, Avg, Max, Min, Count
from django.db.models import F
User = get_user_model()
from users.serializers import *


# user app
class UserSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = User
        # fields = ('id','username','first_name')
        # fields = '__all__'
        exclude=('password','last_login','is_superuser','user_permissions','groups','avatar','dob','phone',)

class TermSerializer(serializers.ModelSerializer):

    class Meta:
        model = Term
        fields = ('id','name','status',)


# subject teacher serializer
class SubjectTeacherSerializer(serializers.ModelSerializer):  
    # 
    teacher = UserSerializer(read_only=True)


    class Meta:
        model = SubjectTeacher
        # fields = "__all__"
        exclude = ('status','date_created','date_modified',)
    
    
class SessionSerializer(serializers.ModelSerializer):
    # sessions = SubjectTeacherSerializer(many=True,read_only=True)
    class Meta:
        model = Session
        fields = ('id','name','status',)

class SchoolClassSerializer(serializers.ModelSerializer):
    # classrooms = SubjectTeacherSerializer(many=True, read_only=True)

    class Meta:
        model = SchoolClass
        fields = ('id','class_name',)
       
class SubjectSerializer(serializers.ModelSerializer):
    # subjects = SubjectTeacherSerializer(many=True,read_only=True)

    class Meta:
        model = Subject
        fields = ('id','name','subject_code',)
        
        
class SubjectPerClassSerializer(serializers.ModelSerializer):
    term_name = serializers.SerializerMethodField()
    session_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = SubjectPerClass
        fields = "__all__"
        
    def get_term_name(self,object):
               
        term = Term.objects.get(pk=object.term.pk)
        return term.name
    
    def get_session_name(self,object):
               
        session = Session.objects.get(pk=object.session.pk)
        return session.name
    
    def get_class_name(self,object):
               
        classObj = SchoolClass.objects.get(pk=object.sch_class.pk)
        return classObj.class_name
    
    
class AttendanceSettingSerializer(serializers.ModelSerializer):
    
    term_name = serializers.SerializerMethodField()
    session_name = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSetting
        fields = "__all__"
        
    def get_term_name(self,object):
               
        term = Term.objects.get(pk=object.term.pk)
        return term.name
    
    def get_session_name(self,object):
               
        session = Session.objects.get(pk=object.session.pk)
        return session.name
        

class ResumptionSettingSerializer(serializers.ModelSerializer):
    term_current = serializers.SerializerMethodField()
    session_name = serializers.SerializerMethodField()

    class Meta:
        model = ResumptionSetting
        fields = "__all__"
    
    def get_term_current(self,object):
               
        term = Term.objects.get(pk=object.current_term.pk)
        return term.name
    
    def get_session_name(self,object):
               
        session = Session.objects.get(pk=object.session.pk)
        return session.name






# class teacher serializer
class ClassTeacherSerializer(serializers.ModelSerializer):
    tutor = UserSerializer(read_only=True)
    # tutor = serializers.StringRelatedField(read_only=True)
    # teacher_name = serializers.SerializerMethodField()
    # session_name = serializers.SerializerMethodField()
    # class_name = serializers.SerializerMethodField()
    # term_name = serializers.SerializerMethodField()

    class Meta:
        model = ClassTeacher
        exclude = ('date_created','date_modified',)
    
    # def get_teacher_name(self,object):
               
    #     teacherObj = User.objects.get(pk=object.tutor.pk)
    #     return teacherObj.sur_name + ' ' + teacherObj.first_name
    
    # def get_session_name(self,object):
               
    #     session = Session.objects.get(pk=object.session.pk)
    #     return session.name
    
    # def get_term_name(self,object):
               
    #     term = Term.objects.get(pk=object.term.pk)
    #     return term.name
    
    # def get_class_name(self,object):
               
    #     _class = SchoolClass.objects.get(pk=object.classroom.pk)
    #     return _class.class_name
    
#score
class ScoreSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    subjectteacher = serializers.StringRelatedField()
    
    class Meta:
        model = Scores 
        fields = "__all__"


class ScoresSerializer(serializers.ModelSerializer):
    # Use model property methods for these fields
    student_full_name = serializers.CharField(read_only=True)
    term_code = serializers.CharField(read_only=True)
    session_name = serializers.CharField(read_only=True)
    subject_code = serializers.CharField(read_only=True)
    class_name = serializers.CharField(read_only=True)
    subject_teacher_name = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    # Optionally, keep the nested serializers if you want full related objects
    # user = UserSerializer(read_only=True)
    # term = TermSerializer(read_only=True)
    # session = SessionSerializer(read_only=True)
    # studentclass = SchoolClassSerializer(read_only=True)
    # subject = SubjectSerializer(read_only=True)
    # subjectteacher = SubjectTeacherSerializer(read_only=True)

    class Meta:
        model = Scores
        fields = (
            'id', 'user', 'user_id', 'student_full_name',
            'term', 'term_code',
            'session', 'session_name',
            'studentclass', 'class_name',
            'subject', 'subject_code',
            'subjectteacher', 'subject_teacher_name',
            'firstscore', 'secondscore', 'thirdscore', 'totalca', 'examscore', 'subjecttotal',
            'subjaverage', 'subjectposition', 'subjectgrade', 'subjectrating', 'highest_inclass',
            'lowest_inclass',
        )
  

class ResultSerializer(serializers.ModelSerializer):
    # Use model property methods for these fields
    student_full_name = serializers.CharField(read_only=True)
    term_code = serializers.CharField(read_only=True)
    session_name = serializers.CharField(read_only=True)
    class_name = serializers.CharField(read_only=True)
    classteacher_name = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    admission_number = serializers.CharField(source='admission_numberstring', read_only=True)

    # Optionally, keep the nested serializers if you want full related objects
    # student = UserSerializer(read_only=True)
    # term = TermSerializer(read_only=True)
    # session = SessionSerializer(read_only=True)
    # studentclass = SchoolClassSerializer(read_only=True)
    # classteacher = ClassTeacherSerializer(read_only=True)

    class Meta:
        model = Result
        fields = (
            'id', 'student', 'user_id', 'student_full_name',
            'term', 'term_code',
            'session', 'session_name',
            'studentclass', 'class_name',
            'classteacher', 'classteacher_name',
            'admission_number',
            'termtotal', 'termaverage', 'termposition',
            'classteachercomment', 'headteachercomment', 'attendance',
            'date_created', 'date_modified',
        )

class TerminalSummaryResultSerializer(serializers.ModelSerializer):
    # Use model property methods for these fields
    student_full_name = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Result
        fields = (
            'user_id', 'student_full_name', 'termtotal', 'termaverage', 'termposition'
        )


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"


class PsychomotorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Psychomotor
        fields = "__all__"
        
class AffectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affective
        fields = "__all__"
        


class StudentaffectiveSerializer(serializers.ModelSerializer):
    affective = serializers.StringRelatedField(read_only=True)
    rating = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Studentaffective
        fields = "__all__"
        
        

class StudentpsychomotorSerializer(serializers.ModelSerializer):
    psychomotor = serializers.StringRelatedField(read_only=True)
    rating = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Studentpsychomotor
        fields = "__all__"


class ClassroomSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_adm_no = serializers.SerializerMethodField()
    session = serializers.StringRelatedField()
    term = serializers.StringRelatedField()
    class_room = serializers.StringRelatedField()

    class Meta:
        model = Classroom
        fields = "__all__"
    
    def get_student_name(self,object):
        user = User.objects.get(pk=object.student.pk)
        return user.sur_name + ' ' + user.first_name
    
    def get_student_adm_no(self,object):
        obj = StudentProfile.objects.get(user_id=object.student.pk)
        return obj.admission_numberstring
    
# admission number serialiser
class AdmissionNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdmissionNumber
        fields = "__all__"

class TerminalScoresSummarySerializer(serializers.ModelSerializer):
    # Use model property methods for these fields
    student_full_name = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Scores
        fields = (
            'user_id', 'student_full_name', 'subjecttotal', 'subjectposition', 'subjectgrade'
        )
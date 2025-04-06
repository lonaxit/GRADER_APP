from dataclasses import fields
from rest_framework import serializers
# import models
from core.models import *
from django.db.models import Q, Sum, Avg, Max, Min, Count
from django.db.models import F
User = get_user_model()
from users.serializers import *

class TermSerializer(serializers.ModelSerializer):

    class Meta:
        model = Term
        fields = ('id','name','status',)


# subject teacher serializer
class SubjectTeacherSerializer(serializers.ModelSerializer):  
    # 
    teacher = serializers.StringRelatedField(read_only=True)
    subject = serializers.StringRelatedField(read_only=True)
    classroom = serializers.StringRelatedField(read_only=True)
    session = serializers.StringRelatedField(read_only=True)
    # teacher_name = serializers.SerializerMethodField()
    # session_name = serializers.SerializerMethodField()
    # subject_name = serializers.SerializerMethodField()
    # class_name = serializers.SerializerMethodField()
    # teacherid = serializers.SerializerMethodField()

    class Meta:
        model = SubjectTeacher
        # fields = "__all__"
        exclude = ('status','date_created','date_modified',)
    
    # def get_teacher_name(self,object):
               
    #     teacherObj = User.objects.get(pk=object.teacher.pk)
    #     return teacherObj.sur_name + ' ' + teacherObj.first_name
    # def get_teacherid(self,object):
               
    #     teacherObj = User.objects.get(pk=object.teacher.pk)
    #     return teacherObj.pk
    
    # def get_session_name(self,object):
               
    #     session = Session.objects.get(pk=object.session.pk)
    #     return session.name
    
    # def get_class_name(self,object):
               
    #     _class = SchoolClass.objects.get(pk=object.classroom.pk)
    #     return _class.class_name
    
    # def get_subject_name(self,object):
               
    #     _subject = Subject.objects.get(pk=object.subject.pk)
    #     return _subject.name
    
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
    tutor = serializers.StringRelatedField(read_only=True)
    teacher_name = serializers.SerializerMethodField()
    session_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    term_name = serializers.SerializerMethodField()

    class Meta:
        model = ClassTeacher
        fields = "__all__"
    
    def get_teacher_name(self,object):
               
        teacherObj = User.objects.get(pk=object.tutor.pk)
        return teacherObj.sur_name + ' ' + teacherObj.first_name
    
    def get_session_name(self,object):
               
        session = Session.objects.get(pk=object.session.pk)
        return session.name
    
    def get_term_name(self,object):
               
        term = Term.objects.get(pk=object.term.pk)
        return term.name
    
    def get_class_name(self,object):
               
        _class = SchoolClass.objects.get(pk=object.classroom.pk)
        return _class.class_name
    
#score
class ScoreSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Scores 
        fields = ("id",)


class ScoresSerializer(serializers.ModelSerializer):
    # new
    student = UserSerializer(many=True, read_only=True)  # Nested serializer for User
    # term = TermSerializer(many=True, read_only=True)  # Nested serializer for Term
    # session = SessionSerializer(many=True, read_only=True)  # Nested serializer for Session
    # studentclass = SchoolClassSerializer(many=True, read_only=True)  # Nested serializer for SchoolClass
    # subject = SubjectSerializer(many=True, read_only=True)  # Nested serializer for Subject
    # subjectteacher = SubjectTeacherSerializer(many=True, read_only=True)  # Nested serializer for SubjectTeacher
    
    # 2
    
    # user = serializers.StringRelatedField(read_only=True)
    # subjectteacher = serializers.StringRelatedField(read_only=True)
    # student_name = serializers.SerializerMethodField()
    # session_name = serializers.SerializerMethodField()
    # class_name = serializers.SerializerMethodField()
    # term_name = serializers.SerializerMethodField()
    # subject_name = serializers.SerializerMethodField()
    # subject_code = serializers.SerializerMethodField()
    # user_id = serializers.SerializerMethodField()

    class Meta:
        model = Scores
        fields = ('id', 'user', 'term', 'session', 'studentclass', 'subject', 'subjectteacher',
            'firstscore', 'secondscore', 'thirdscore', 'totalca', 'examscore', 'subjecttotal',
            'subjaverage', 'subjectposition', 'subjectgrade', 'subjectrating', 'highest_inclass',
            'lowest_inclass','student',)
    
    # def get_student_name(self,object):
               
    #     studentObj = User.objects.get(pk=object.user.pk)
    #     return studentObj.sur_name + ' ' + studentObj.first_name
    
    # def get_session_name(self,object):
               
    #     session = Session.objects.get(pk=object.session.pk)
    #     return session.code
    
    # def get_term_name(self,object):
               
    #     term =  Term.objects.get(pk=object.term.pk)
    #     return term.code
    
    # def get_class_name(self,object):
               
    #     _class = SchoolClass.objects.get(pk=object.studentclass.pk)
    #     return _class.code
    
    # def get_subject_name(self,object):
               
    #     _subj = Subject.objects.get(pk=object.subject.pk)
    #     return _subj.name
    
    # def get_subject_code(self,object):
               
    #     _subj = Subject.objects.get(pk=object.subject.pk)
    #     return _subj.subject_code
    
    # def get_user_id(self,object):
               
    #     _userobj = User.objects.get(pk=object.user.pk)
    #     return _userobj.pk

class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    classteacher_name = serializers.SerializerMethodField()
    session_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    term_name = serializers.SerializerMethodField()
    admission_number = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Result
        fields = "__all__"
    
    def get_student_name(self,object):
               
        studentObj = User.objects.get(pk=object.student.pk)
        return studentObj.sur_name + ' ' + studentObj.first_name
    
    def get_classteacher_name(self,object):
               
        teacherObj = User.objects.get(pk=object.classteacher.tutor.pk)
        return teacherObj.sur_name
    
    def get_session_name(self,object):
               
        session = Session.objects.get(pk=object.session.pk)
        return session.code
    
    def get_term_name(self,object):
               
        term =  Term.objects.get(pk=object.term.pk)
        return term.code
    
    def get_class_name(self,object):
               
        _class = SchoolClass.objects.get(pk=object.studentclass.pk)
        return _class.code
    
    def get_admission_number(self,object):
               
         std = StudentProfile.objects.get(user=object.student.pk)
         return std.admission_numberstring
     
    def get_user_id(self,object):
               
        _userobj = User.objects.get(pk=object.student.pk)
        return _userobj.pk

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
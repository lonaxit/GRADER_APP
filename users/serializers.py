from dataclasses import fields
import profile
from rest_framework import serializers
from core.api.serializers import *


# IMPORT CUSTOM USER
from django.contrib.auth import get_user_model

User = get_user_model()

# other serializers
class StdProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    
    class Meta:
        model = StudentProfile
        fields = ('id','user',)
        
class StudentProfileSerializer(serializers.ModelSerializer): #child model
    
    user = serializers.StringRelatedField()
    term_name = serializers.SerializerMethodField()
    session_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    studentid = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = "__all__"
    
    def get_term_name(self,object):
               
        term = Term.objects.get(pk=object.term_admitted.pk)
        return term.name
    
    def get_session_name(self,object):
               
        session = Session.objects.get(pk=object.session_admitted.pk)
        return session.name
    
    def get_class_name(self,object):
               
        classObj = SchoolClass.objects.get(pk=object.class_admitted.pk)
        return classObj.class_name
    
    def get_student_name(self,object):
        std = User.objects.get(pk=object.user.pk)
        
        return std.sur_name + ' ' + std.first_name
    
    def get_studentid(self,object):
        return object.user.pk
   
class EnrollBySearchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StudentProfile
        fields = "__all__"
    
# user app
class UserSerializer(serializers.ModelSerializer):
    # studentprofile = StudentProfileSerializer(read_only=True) #parent model
  
   
    class Meta:
        model = User
        # fields = ('id','username','first_name')
        # fields = '__all__'
        exclude=('password','last_login','is_superuser','user_permissions','groups','avatar','dob','phone',)
 

class TeacherProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = TeacherProfile
        fields = "__all__"       
   
   
        
class UserTeacherSerializer(serializers.ModelSerializer):
    # teacherprofile = TeacherProfileSerializer(read_only=True) #parent model
   
    
    class Meta:
        model = User
        # fields = ('id','username','first_name')
        # fields = '__all__'
        exclude=('password','last_login','is_superuser','user_permissions','groups',)
        
        
        



# 
class UpdateUserPasswordSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id','password')


class UpdatePasswordWithUsernameSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id','password','username')
        



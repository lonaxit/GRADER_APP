from django.db import models

from django.utils import timezone
from datetime import date
import datetime
from django.utils.timezone import now

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomUserManager(BaseUserManager):
    
    def create_user(self, username, sur_name,first_name,gender,dob,other_name=None,phone=None,password=None):
        
        if not username:
            raise ValueError('User must have a username and must be unique')
        if not first_name:
            raise ValueError('User must have a firstname')
        if not sur_name:
            raise ValueError('User must have a surname')
        if not dob:
            raise ValueError('User must have a date of birth')
      
             
        

        user = self.model(
            username=username,
            sur_name=sur_name,
            first_name = first_name,
            other_name=other_name,
            gender = gender,
            phone = phone,
            dob = dob,
        )

        user.set_password(password)
        
        # when using multple databases
        # user.save(using=self._db)
        user.save()
        return user

    # method to create other roles
    def create_student(self, username, sur_name,first_name,gender,dob,other_name=None,phone=None,password=None):
        user = self.create_user(username,sur_name,first_name,gender,dob,other_name,phone,password)
        user.is_student=True
        user.save()
        
        return user
    
    def create_teacher(self, username, sur_name,first_name,gender,dob,other_name=None,phone=None,password=None):
        user = self.create_user(username,sur_name,first_name,gender,dob,other_name,phone,password)
        user.is_staff=True
        user.save()
        
        return user
    
    
    def create_superuser(self, username, sur_name,first_name,gender,dob,other_name=None,phone=None,password=None):
        user = self.create_user(username,sur_name,first_name,gender,dob,other_name,phone,password)
        user.is_superuser = True
        user.is_staff =True
        user.save()
        return user
    
      

class CustomUser(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=255,unique=True)
    sur_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    other_name = models.CharField(max_length=255,blank=True,null=True)
    gender = models.CharField(max_length=255)
    phone = models.CharField(max_length=200,blank=True,null=True)
    dob = models.DateField()
    avatar = models.ImageField(null=True,blank=True)
    # date_joined = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)
    created_on = models.DateField(default=now) 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
 
    
    
    objects = CustomUserManager()
    
    USERNAME_FIELD ='username'
    REQUIRED_FIELDS = ['sur_name','first_name', 'gender','dob']
    
    def __str__(self):
        return self.sur_name






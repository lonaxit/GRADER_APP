from urllib import response
from xml.dom import ValidationErr
from django.shortcuts import render


from django.db import transaction

from rest_framework.views import APIView
# from rest_framework import status,permissions

from rest_framework import generics, status
# from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response

# IMPORT CUSTOM USER
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import timezone
from datetime import datetime,timedelta


from .serializers  import *

# using permissions 
from rest_framework.permissions import *
# from core.api.permissions import *
from django.contrib.auth.hashers import make_password

from rest_framework.parsers import MultiPartParser,FormParser
from users.pagination import UserPagination

import openpyxl
import pandas as pd


import random
import string

# user creation view 
class RegistrationView(APIView):
    
    # permission_classes = [IsAuthenticated,IsAuthOrReadOnly]
    
    def post(self, request):
        
        try:
            data = request.data
            username = data['username']
            first_name = data['first_name']
            sur_name = data['sur_name']
            other_name = data['other_name']
            phone = data['phone']
            gender = data['gender']
            dob = data['dob']
            password = data['password']
            re_password = data['re_password']
            is_staff = data['is_staff']
         
       
            if is_staff == True:
                is_staff=True
            else: 
                is_staff = False
                
           
                
            if not password:
                 return Response(
                        {'msg':'Provide a password'},
                        status = status.HTTP_400_BAD_REQUEST
                        )
            
            if password == re_password:
                if len(password) >=8:
                    
                    
                    if not User.objects.filter(username=username).exists():
                        
                        
                        if not is_staff:
                            # username,sur_name,first_name,gender,dob,other_name,phone,password
                            User.objects.create_student(username=username,sur_name=sur_name,first_name=first_name,gender=gender,dob=dob,other_name=other_name,phone=phone,password=password)
                            
                            return Response(
                            {'msg':'User created successfuly'},
                            status = status.HTTP_201_CREATED
                            )
                             
                        else:
                            
                            User.objects.create_teacher(username=username,sur_name=sur_name,first_name=first_name,gender=gender,dob=dob,other_name=other_name,phone=phone,password=password)
                            
                            return Response(
                            {'msg':'User created successfuly'},
                            status = status.HTTP_201_CREATED
                            )
                         
                    else:
                        
                        return Response(
                        {'msg':'User already exist'},
                        status = status.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response(
                    {'msg':'Password must be at least 8 characters'},
                    status = status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                {'msg':'Password mismatch'},
                status = status.HTTP_400_BAD_REQUEST
                )    
        except Exception as e:
            print(e)
            return Response(
                {'msg':e},
                status =status.HTTP_500_INTERNAL_SERVER_ERROR
            )



#  get logged in user info  
class RetrieveUserView(APIView):
    
    # permission_classes = [IsAuthenticated,IsAuthOrReadOnly]
    
    def get(self,request):
        
        # try:
        user = request.user
        user = UserSerializer(user)
        return Response(
                {'user':user.data},
                status= status.HTTP_200_OK
            )
 
# #  get logged in user info
    
class GetUserWithUsername(APIView):
    
    # permission_classes = [IsAuthenticated,IsAuthOrReadOnly]
    
    def get(self,request,username):
        
        # try:
        user = User.objects.get(username=username)
        # user = request.user
        user = UserSerializer(user)
        return Response(
                {'user':user.data},
                status= status.HTTP_200_OK
            )      
            
# New but not in use again
# class retrieveAllUsers(APIView):
#     # permission_classes = [IsAuthenticated, IsAuthOrReadOnly]
    
#     def get(self, request):
#         try:
#             # today = timezone.now().date()  # Ensure we use timezone-aware date
#             # last_week = today - timedelta(days=7)
            
#             # users = User.objects.filter(created_on__range=(last_week, today))
#             # users = User.objects.filter(created_on__gte=today)
            
#             today = timezone.now()
          
#             one_days_ago = today - timedelta(days=3)
#             users = User.objects.filter(date_joined__gte=one_days_ago)
#             serializer = UserSerializer(users, many=True)
#             return Response({'users': serializer.data}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class retrieveAllUsers(APIView):
    # permission_classes = [IsAuthenticated,IsAuthOrReadOnly]
    pagination_class = UserPagination
    
    def get(self,request):
        try:
            user = User.objects.all()
            user = UserSerializer(user,many=True)
            return Response(
                {'user':user.data},
                status= status.HTTP_200_OK
            )
        except:
            return Response(
                {'error':'Unable to retrieve data'},
                status =status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# fetch staff profile
class retrieveAllStaff(APIView):
    # permission_classes = [IsAuthenticated,IsAuthOrReadOnly]
    
    
    def get(self,request):
        try:
            user = User.objects.all()
            user = UserTeacherSerializer(user,many=True)
            return Response(
                {'user':user.data},
                status= status.HTTP_200_OK
            )
        except:
            return Response(
                {'error':'Unable to retrieve data'},
                status =status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

# User details
class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class =UserSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
             
# update user
class UpdateUser(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class =UserSerializer
    # permission_classes =[IsAuthenticated & IsAuthOrReadOnly]
    

# Update password for user given a user id
class UpdateUserPassword(APIView):
    
    # permission_classes=[IsAuthenticated & IsAuthOrReadOnly]
    # throttle_classes= [AnonRateThrottle]
    
    # def get(self,request,pk):
        
    #     try:
    #         user = User.objects.get(pk=pk)
    #     except User.DoesNotExist:
            
    #         # creating a custom message
    #         return Response({'Error': 'Not Found'},
    #                status=status.HTTP_404_NOT_FOUND
    #                )
             
    #     serializer = UpdateUserPasswordSerializer(user)
    #     return Response(serializer.data)
    
    
    def put(self,request,pk):
        
        
        user = User.objects.get(pk=pk)
        password = make_password(request.data['password'])
        user.password = password
        user.save()
        return Response('Password Reset Successful!')
    
    

# Update password for user given a username
class UpdatePasswordUsername(APIView):
    
    """
    put method
    update a password given a user name
    """
    # permission_classes=[IsAuthOnly]
    # throttle_classes= [AnonRateThrottle]
    
    def put(self,request):
        
        username = request.data['username']
        try:
            user = User.objects.get(username=username)
            password = make_password(request.data['password'])
            
            user.password = password
            user.save()
            return Response('Password Reset Successful!')
        
        except User.DoesNotExist:
            raise ValidationErr('Username does not exist')
        
        
      
        
    


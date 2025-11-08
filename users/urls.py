from django.urls import path
from .views import *

urlpatterns=[
    path('register/',RegistrationView.as_view(), name="register"),
    path('me/', RetrieveUserView.as_view(), name="me"),
    path('user-detail/<int:pk>/', UserDetail.as_view(), name="user-detail"),
    path('get-user/<str:username>/', GetUserWithUsername.as_view(), name="get-user"),
    path('all/users/',retrieveAllUsers.as_view(), name="all-users"),
    path('all/staff/',retrieveAllStaff.as_view(), name="all-staff"),
    path('<int:pk>/user-update/',UpdateUser.as_view(), name="update-user"),
    
    # change login detail using userid
    path('<int:pk>/update-password/',UpdateUserPassword.as_view(), name="update-password"),
    
    # Change password using username
    path('username-update-password/',UpdatePasswordUsername.as_view(), name="username-update-password"),     
    path('unlinked-students/', UnlinkedStudents.as_view(), name='unlinked-students'),
]
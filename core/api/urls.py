from django.urls import path,include

from core.api.views import *

urlpatterns =[
    path("term/", TermListCreateAPIView.as_view(), name="term"),
    path("term-detail/<int:pk>/", TermDetailAPIView.as_view(), name="term-detail"),
    
    path("session/", SessionListCreateAPIView.as_view(), name="session"),
    path("session-detail/<int:pk>/", SessionDetailAPIView.as_view(), name="session-detail"),
    
    path("school_class/", SchoolClassCreateAPIView.as_view(), name="schoolclass"),
    path("schoolclass-detail/<int:pk>/", SchoolClassDetailAPIView.as_view(), name="schoolclass-detail"),
    
    path("subject/", SubjectCreateAPIView.as_view(), name="subject"),
    path("subject-detail/<int:pk>/", SubjectDetailAPIView.as_view(), name="subject-detail"),
    
    path("subject-perclass/", SubjectPerClassCreateAPIView.as_view(), name="subject-perclass"),
    path("subjectperclass-detail/<int:pk>/", SubjectPerClassDetailAPIView.as_view(), name="subjectperclass-detail"),
    
    path("attendance-setting/", AttendanceSettingsCreateAPIView.as_view(), name="attendance-setting"),
    path("attendancesetting-detail/<int:pk>/", AttendanceSettingsClassDetailAPIView.as_view(), name="attendancesetting-detail"),
    
    
    path("resumption-setting/", ResumptionSettingsCreateAPIView.as_view(), name="resumption-setting"),
    
    # not working refactor
    # path("get-resumption-date/", GetResumptionDate.as_view(), name="get-resumption-date"),
    
    path("resumptionsetting-detail/<int:pk>/", ResumptionSettingsClassDetailAPIView.as_view(), name="resumptionsetting-detail"),
    
    path("student-profile/<int:pk>/", StudentProfileCreate.as_view(), name="studentprofile"),
    path("student-profile/", StudentProfileListAPIView.as_view(), name="student-profile"),
    
    path("student-profile-nonumber/", StudentsWithNoNumber.as_view(), name="student-profile-nonumber"),

    path("assign_number/<int:pk>/", AssignNumberAPIView.as_view(), name="assign_number"),
    
    path("studentprofile-detail/<int:pk>/", StudentProfileDetailAPIView.as_view(), name="studentprofile-detail"),

    path("teacher-profile/<int:pk>/", TeacherProfileCreateAPIView.as_view(), name="teacher-profile"),
    
    #  path("teacher-profile/", TeacherProfileCreateAPIView.as_view(), name="teacher-profile"),
    path("teacherprofile-detail/<int:pk>/", TeacherProfileDetailAPIView.as_view(), name="teacherprofile-detail"),
    
    
     path("create-subject-teacher/<int:pk>/", SubjectTeacherCreateAPIView.as_view(), name="create-subject-teacher"),
     
    path("list-subjectteacher/", SubjectTeacherListAPIView.as_view(), name="list-subjectteacher"),
    
    path("subjectteacher-detail/<int:pk>/", SubjectTeacherClassDetailAPIView.as_view(), name="subjectteacher-detail"),
    
    path("toggle-subjectteacher/<int:pk>/", ToggleSubjectTeacherAPIView.as_view(), name="toggle-subjectteacher"),
    
    
    # url for class teacher
    path("list-classteacher/", ClassTeacherListAPIView.as_view(), name="list-classteacher"),
    
    path("new-class-teacher/<int:pk>/", ClassTeacherCreateAPIView.as_view(), name="new-class-teacher"),
    
    path("classteacher-detail/<int:pk>/", ClassTeacherDetailAPIView.as_view(), name="classteacher-detail"),
    
    path("toggle-classteacher/<int:pk>/", ToggleClassTeacherAPIView.as_view(), name="toggle-classteacher"),
    
    # endpoints for scores
    path("list-scores/", ScoresListAPIView.as_view(), name="list-scores"),
    #  create new sccores using user id
    path("new-score/<int:pk>/", ScoresCreateAPIView.as_view(), name="new-score"),
    path("filter-scores/", FindScoresAPIView.as_view(), name="filter-scores"),
    # NEW API ENDPOINT
    path("filter-terminal-scores/", FilterTerminalScoresAPIView.as_view(), name="filter-terminal-scores"),
    
    path("scores-detail/<int:pk>/", ScoresDetailAPIView.as_view(), name="scores-detail"),
    
    # user scores given userid, term, session, class
    path("user-scores/<int:userid>/<int:term>/<int:session>/<int:class>/",UserScoresList.as_view(),name='user-scores'),
    
    path("export-sheet/",ExportSheet.as_view(),name="export-sheet"),
    path("import-sheet/",ImportAssessment.as_view(),name="import-sheet"),
    
    path("export-attendance-sheet/",ExportAttendanceSheet.as_view(),name="export-attendance-sheet"),
    
    path("upload-attendance/",UploadTerminalAttendance.as_view(),name="upload-attendance"),
    
    # endpoint for creating result
    path("create-result/",CreateResult.as_view(), name="create-result"),
    
    # get result passing in term, session and class
    path("get-result/",GetResult.as_view(), name="get-result"),
    
    # get result detail using result id
    path("detail-result/<int:pk>/",ResultDetailAPIView.as_view(), name="detail-result"),
    path("userresult-list/<int:pk>/",UserResultList.as_view(), name="userresult-list"),
    
    # rating
     path("create-rating/",RatingCreateAPIView.as_view(), name="create-rating"),
     path("rating-detail/<int:pk>/",RatingDetailAPIView.as_view(), name="rating-detail"),
     
    #  psychomotor
    path("create-pyschomotor/", PsychomotorCreateListAPIView.as_view(), name="create-psychomotor"),
    path("pyschomotor-detail/<int:pk>/", PyschomotorDetailAPIView.as_view(), name="psychomotor-detail"),
    
    # affective
    path("create-affective/", AffectiveCreateListAPIView.as_view(), name="create-affective"),
    path("affective-detail/<int:pk>/", AffectiveDetailAPIView.as_view(), name="affective-detail"),
    
    # create traits
    path("createaffective-traits/",CreateStudentAffectiveTraits.as_view(), name="createaffective-traits"),
    path("createpsycho-traits/",CreateStudentPsychoTraits.as_view(), name="createpsycho-traits"),

    # auto comments
    path("auto-comments/", AddAutoComents.as_view(), name="auto-coments"),
    
    # fetch traits using term, session, class and userid 
    path("student/affectivetraits/<int:userid>/<int:session>/<int:classroom>/<int:term>/",GetStudentAffectiveTraits.as_view(), name="get-studentaffective"),
    
    path("student/psychotraits/<int:userid>/<int:session>/<int:classroom>/<int:term>/",GetStudentPsychoTraits.as_view(), name="get-studentpsycho"),
    
    # Enrollment
    path("new-enrollment/",EnrollStudent.as_view(), name="new-enrollment"),
    path("mass-enrollment/",MassEnrollStudent.as_view(), name="mass-enrollment"),
    path("new-admission-enrollment/",NewStudentsMassEnrollStudent.as_view(), name="new-admission-enrollment"),
    
    path("roll-call/",RollCallAPIView.as_view(), name="roll-call"),
    
    path("rollcall-detail/<int:pk>/",ClassroomDetailAPIView.as_view(), name="roll-call"),
    
    path("ca-roll-call/",AssessmentSheetRollCallAPIView.as_view(), name="ca-roll-call"),
    path("get-adm-number/",FirstAdmNumberView.as_view(), name="get-adm-number"),
     
    
    
    
    
    # celery migration
    # path("migrate-session/",migrateSessionsCelery.as_view(), name="migrate-session"),
    # path("migrate-class/",migrateClassCelery.as_view(), name="migrate-class"),
    
    
    # path("migrate-subjects/",migrateSubjectsCelery.as_view(), name="migrate-subjects"),
    # path("migrate-subjectsperclass/",migrateSubjectPerClasssCelery.as_view(), name="migrate-subjectsperclass"),
    #  path("migrate-students/",migrateUserCelery.as_view(), name="migrate-students"),
    #  path("migrate-subject-teachers/",migrateSubjectTeachersCelery.as_view(), name="migrate-subject-teachers"),
     
    #   path("migrate-class-teachers/",migrateClassTeachersCelery.as_view(), name="migrate-class-teachers"),
      
    #   path("migrate-scores/",migrateScoresCelery.as_view(), name="migrate-scores"),
    #   path("migrate-result/",migrateResultCelery.as_view(), name="migrate-result"),
    #   path("migrate-enrollment/",migrateEnrollmentCelery.as_view(), name="migrate-enrollment"),
    #   path("migrate-enrollment/",migrateEnrollmentCelery.as_view(), name="migrate-enrollment"),
    #   path("migrate-number/",migrateAdNumberCelery.as_view(), name="migrate-number"),
    #   path("migrate-studentaffective/",migrateStudentsAffectiveCelery.as_view(), name="migrate-studentaffective"),
      
    #   path("migrate-studentpsycho/",migrateStudentsPyschoCelery.as_view(), name="migrate-studentpsycho"),
      
    #   path("migrate-studentprofile/",migrateStudentProfileCelery.as_view(), name="migrate-studentprofile"),

]
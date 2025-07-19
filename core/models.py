from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()

class Term(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    code = models.CharField(max_length=100,null=True,blank=True)
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    

class Session(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    code = models.CharField(max_length=100,null=True,blank=True)
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    
    
class SchoolClass(models.Model):
    class_name = models.CharField(max_length=100,null=True,blank=True)
    code = models.CharField(max_length=100,null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.class_name
    
# subject model
class Subject(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    subject_code = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name


# subject per class
class SubjectPerClass(models.Model):
    sch_class = models.ForeignKey(SchoolClass,on_delete=models.CASCADE)
    term = models.ForeignKey(Term,on_delete=models.CASCADE)
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    no_subject = models.IntegerField(null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.sch_class.class_name


class AttendanceSetting(models.Model):
    session = models.ForeignKey(Session,on_delete=models.DO_NOTHING)
    term = models.ForeignKey(Term,on_delete=models.DO_NOTHING)
    days_open = models.DecimalField(max_digits=5,decimal_places=2, null=True, blank=True)
    days_closed = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.days_open
    

class ResumptionSetting(models.Model):
    session = models.ForeignKey(Session,on_delete=models.DO_NOTHING)
    current_term = models.ForeignKey(Term,on_delete=models.DO_NOTHING)
    current_term_ends = models.DateField(null=True,blank=True)
    next_term_begins = models.DateField(blank=True,null=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.current_term

class StudentProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='studentprofile')
    guardian = models.CharField(max_length=200,null=True,blank=True)
    local_govt = models.CharField(max_length=200,null=True,blank=True)
    admission_number = models.IntegerField(null=True,blank=True)
    admission_numberstring = models.CharField(max_length=200,null=True,blank=True)
    address = models.CharField(max_length=200,null=True,blank=True)
    session_admitted = models.ForeignKey(Session,on_delete=models.DO_NOTHING)
    term_admitted = models.ForeignKey(Term,on_delete=models.DO_NOTHING)
    class_admitted = models.ForeignKey(SchoolClass,on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.sur_name

    
    
class TeacherProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='teacherprofile')
    local_govt = models.CharField(max_length=200,null=True,blank=True)
    address = models.CharField(max_length=200,null=True,blank=True)
    qualification = models.CharField(max_length=200,null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.sur_name

# assign subject teacher  
class SubjectTeacher(models.Model):
    subject = models.ForeignKey(Subject,on_delete=models.DO_NOTHING,related_name='subjects')
    classroom = models.ForeignKey(SchoolClass,on_delete=models.DO_NOTHING,related_name='classrooms')
    session = models.ForeignKey(Session,on_delete=models.DO_NOTHING,related_name='sessions')
    teacher = models.ForeignKey(User,on_delete=models.CASCADE,related_name='teachersubjects')
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.teacher.sur_name
   
# assign class teacher
class ClassTeacher(models.Model):
    session = models.ForeignKey(Session,on_delete=models.DO_NOTHING)
    term = models.ForeignKey(Term,on_delete=models.DO_NOTHING)
    classroom = models.ForeignKey(SchoolClass,on_delete=models.DO_NOTHING, related_name='classes')
    tutor = models.ForeignKey(User,on_delete=models.CASCADE,related_name='formmaster')
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.tutor.sur_name

    @property
    def session_name(self):
        return self.session.name if self.session else None

    @property
    def term_name(self):
        return self.term.name if self.term else None

    @property
    def classroom_name(self):
        return self.classroom.class_name if self.classroom else None

    @property
    def tutor_name(self):
        return f"{self.tutor.sur_name} {self.tutor.first_name}" if self.tutor else None
    
    
class Scores(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='student')
    term = models.ForeignKey(Term,on_delete=models.DO_NOTHING, related_name="scores_terms")
    session = models.ForeignKey(Session,on_delete=models.DO_NOTHING, related_name="scores_sessions")
    studentclass = models.ForeignKey(SchoolClass,on_delete=models.DO_NOTHING,related_name="scores_class")
    subject = models.ForeignKey(Subject,on_delete=models.DO_NOTHING,related_name="scores_subjects")
    subjectteacher = models.ForeignKey(SubjectTeacher,on_delete=models.DO_NOTHING,related_name="scores_teacher")
    firstscore = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    secondscore = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    thirdscore = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    totalca = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    examscore = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    subjecttotal = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    subjaverage = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    subjectposition = models.IntegerField(null=True)
    subjectgrade = models.CharField(max_length=10,null=True)
    subjectrating = models.CharField(max_length=10,null=True)
    highest_inclass = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    lowest_inclass =  models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.sur_name

    @property
    def student_full_name(self):
        return f"{self.user.sur_name} {self.user.first_name}"

    @property
    def term_code(self):
        return self.term.code if self.term else None

    @property
    def session_name(self):
        return self.session.name if self.session else None

    @property
    def subject_code(self):
        return self.subject.subject_code if self.subject else None

    @property
    def class_name(self):
        return self.studentclass.class_name if self.studentclass else None

    @property
    def subject_teacher_name(self):
        # Assumes subjectteacher.teacher is a User instance
        if self.subjectteacher and self.subjectteacher.teacher:
            return f"{self.subjectteacher.teacher.sur_name} {self.subjectteacher.teacher.first_name}"
        return None

    @property
    def user_id(self):
        return self.user.id if self.user else None

class Result(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    term = models.ForeignKey(Term,on_delete=models.DO_NOTHING)
    session = models.ForeignKey(Session,on_delete=models.DO_NOTHING)
    studentclass = models.ForeignKey(SchoolClass,on_delete=models.DO_NOTHING)
    classteacher = models.ForeignKey(ClassTeacher,on_delete=models.DO_NOTHING)
    termtotal = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    termaverage = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    termposition = models.IntegerField(null=True)
    classteachercomment = models.CharField(max_length=200,null=True,blank=True)
    headteachercomment = models.CharField(max_length=200,null=True,blank=True)
    attendance = models.CharField(max_length=20,null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student.sur_name

    @property
    def admission_numberstring(self):
        if hasattr(self.student, 'studentprofile'):
            return self.student.studentprofile.admission_numberstring
        return None

    @property
    def student_full_name(self):
        return f"{self.student.sur_name} {self.student.first_name}"

    @property
    def term_code(self):
        return self.term.code if self.term else None

    @property
    def session_name(self):
        return self.session.name if self.session else None

    @property
    def class_name(self):
        return self.studentclass.class_name if self.studentclass else None

    @property
    def classteacher_name(self):
        if self.classteacher and self.classteacher.tutor:
            return f"{self.classteacher.tutor.sur_name} {self.classteacher.tutor.first_name}"
        return None

    @property
    def user_id(self):
        return self.student.id if self.student else None

class AnnualResult(models.Model):
    
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    session = models.ForeignKey(Session,on_delete=models.DO_NOTHING)
    studentclass = models.ForeignKey(SchoolClass,on_delete=models.DO_NOTHING)
    annualtotal = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    annualaverage = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    annualposition = models.IntegerField(null=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.student.sur_name
    
class Rating(models.Model):
    description = models.CharField(max_length=100,null=True)
    scores = models.IntegerField(null=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.description
    

class Psychomotor(models.Model):

    skill = models.CharField(max_length=200,null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.skill

class Affective(models.Model):
    domain = models.CharField(max_length=200,null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.domain
    
    
class Studentaffective(models.Model):

    student = models.ForeignKey(User,on_delete=models.CASCADE)
    term = models.ForeignKey(Term,on_delete=models.DO_NOTHING)
    session = models.ForeignKey(Session,on_delete=models.DO_NOTHING)
    studentclass = models.ForeignKey(SchoolClass,on_delete=models.DO_NOTHING)
    affective = models.ForeignKey(Affective,on_delete=models.CASCADE)
    rating = models.ForeignKey(Rating,on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.student.sur_name
    

class Studentpsychomotor(models.Model):

    student = models.ForeignKey(User,on_delete=models.CASCADE)
    term = models.ForeignKey(Term,on_delete=models.DO_NOTHING)
    session = models.ForeignKey(Session,on_delete=models.DO_NOTHING)
    studentclass = models.ForeignKey(SchoolClass,on_delete=models.DO_NOTHING)
    psychomotor = models.ForeignKey(Psychomotor,on_delete=models.CASCADE)
    rating = models.ForeignKey(Rating,on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.student.sur_name
    
    
# my classroom
class Classroom(models.Model):
    session = models.ForeignKey(Session,on_delete=models.DO_NOTHING)
    term = models.ForeignKey(Term,on_delete=models.DO_NOTHING)
    class_room = models.ForeignKey(SchoolClass,on_delete=models.DO_NOTHING)
    student = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.class_room

    @property
    def student_name(self):
        return f"{self.student.sur_name} {self.student.first_name}"

    @property
    def student_adm_no(self):
        if hasattr(self.student, 'studentprofile'):
            return self.student.studentprofile.admission_numberstring
        return None

# Admission number list
class AdmissionNumber(models.Model):
    serial_no = models.IntegerField(null=True)
    status = models.CharField(max_length=20,default='No')
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.serial_no
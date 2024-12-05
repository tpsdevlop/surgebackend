from datetime import date, datetime, time, timedelta
from djongo import models

class Attendance (models.Model):
    Login_id        = models.AutoField(primary_key=True)
    SID             = models.CharField(max_length=15)
    Login_time      = models.DateTimeField()
    Last_update     = models.DateTimeField()
    Status          = models.TextField(default="in")
    Duration        = models.IntegerField(default=0)
class ErrorLogs(models.Model):
    Error_id        = models.AutoField(primary_key=True)
    StudentId       = models.CharField(max_length=15)
    Email           = models.EmailField()
    Name            = models.CharField(max_length=25)
    Occurred_time    = models.DateTimeField()####################
    Error_msg       = models.TextField()
    Stack_trace     = models.TextField()
    User_agent      = models.TextField()
    Operating_sys   = models.TextField()

class login_data(models.Model):
    User_ID         = models.CharField(max_length=25,primary_key=True)
    User_name       = models.CharField(max_length=25)
    User_emailID    = models.EmailField(unique=True,null=False)
    User_category   = models.CharField(max_length=5)############

class CourseDetails(models.Model):
    SubjectId       = models.CharField(max_length=5, primary_key=True)
    SubjectName     = models.CharField(max_length=20)
    path            = models.CharField(max_length=500)
    Description     = models.CharField(max_length=500,default='')#name of the course############
    
class StudentDetails(models.Model):
    StudentId       = models.CharField(max_length=15, primary_key=True)
    firstName       = models.CharField(max_length=20)
    lastName        = models.CharField(max_length=20)
    college_Id      = models.CharField(max_length=20)
    CollegeName     = models.CharField(max_length=20)
    Center          = models.CharField(max_length=20)
    email           = models.EmailField(unique=True)
    whatsApp_No     = models.IntegerField()
    mob_No          = models.IntegerField()
    sem             = models.CharField(max_length=3)
    branch          = models.CharField(max_length=10) 
    status          = models.CharField(max_length=3)
    user_category   = models.CharField(max_length=3)
    reg_date        = models.DateField()
    exp_date        = models.DateField()
    score           = models.FloatField()
    progress_Id     = models.JSONField(default=dict)
    Assignments_test= models.JSONField(default=dict)
    Courses         = models.JSONField(default=list)
    Course_Time     = models.JSONField(default=dict)
    CGPA            = models.FloatField()
    user_Type       = models.CharField(max_length=3, default="SW")

# class InternshipDetails(models.Model):
#     sl_id           = models.AutoField(primary_key=True)
#     Student_id      = models.CharField(max_length=25)
#     Name            = models.CharField(max_length=55)
#     email           = models.EmailField(unique=True)
#     Project_name    = models.CharField(max_length=50)
    
#     HTML_Code       = models.JSONField(default=dict)
#     HTML_Score      = models.JSONField(default=dict)

#     CSS_Code        = models.JSONField(default=dict)
#     CSS_Score       = models.JSONField(default=dict)

#     JS_Code         = models.JSONField(default=dict)
#     JS_Score        = models.JSONField(default=dict)

#     Python_Code     = models.JSONField(default=dict)
#     Python_Score    = models.JSONField(default=dict)

#     AppPy_Code      = models.JSONField(default=dict)
#     AppPy_Score     = models.JSONField(default=dict)

#     Database_Code   = models.JSONField(default=dict)
#     Database_Score  = models.JSONField(default=dict)

#     Score           = models.IntegerField(default=0)

class InternshipsDetails(models.Model):###
    ID             = models.AutoField( primary_key=True)
    StudentId      = models.CharField(max_length=25,unique=True)
    ProjectName    = models.JSONField(default=list)
    ProjectStatus  = models.JSONField(default=dict)
    SubmissionDates = models.JSONField(default=dict)
    ProjectDateAndTime = models.JSONField(default=dict)
    
    HTMLCode       = models.JSONField(default=dict)
    HTMLScore      = models.JSONField(default=dict)

    CSSCode        = models.JSONField(default=dict)
    CSSScore       = models.JSONField(default=dict)

    JSCode         = models.JSONField(default=dict)
    JSScore        = models.JSONField(default=dict)

    PythonCode     = models.JSONField(default=dict)
    PythonScore    = models.JSONField(default=dict)

    AppPyCode      = models.JSONField(default=dict)
    AppPyScore     = models.JSONField(default=dict)

    DatabaseCode   = models.JSONField(default=dict)
    DatabaseScore  = models.JSONField(default=dict)

    InternshipScores = models.JSONField(default=dict)
class QuestionDetails_Days(models.Model):
    sl_no           = models.AutoField(primary_key=True)
    Student_id      = models.CharField(max_length=25)
    Subject         = models.CharField(max_length=25)
    Attempts        = models.IntegerField()
    DateAndTime     = models.DateTimeField()
    Score           = models.FloatField()
    Qn              = models.TextField(max_length=25)
    Ans             = models.TextField()
    Result          = models.JSONField(default=dict)

class StudentDetails_Days_Questions(models.Model):
    Student_id      = models.CharField(max_length=25,primary_key=True)
    Days_completed  = models.JSONField(default=dict)
    Qns_lists       = models.JSONField(default=dict)
    Qns_status      = models.JSONField(default=dict)
    Ans_lists       = models.JSONField(default=dict)
    Score_lists     = models.JSONField(default=dict)
    Start_Course    = models.JSONField(default=dict)
    End_Course      = models.JSONField (default=dict)
    
 
class BugDetails(models.Model):
    sl_id           = models.AutoField(primary_key=True)
    Student_id      = models.CharField(max_length=25)
    Img_path        = models.TextField()
    BugDescription  = models.TextField()
    BugStatus       = models.CharField(max_length=50,default='Pending')
    Issue_type      = models.CharField(max_length=50)
    Reported        = models.DateTimeField()
    Resolved        = models.DateTimeField(null=True)
    Comments        = models.JSONField(default=dict)

#PKGS models

class CoursePackages(models.Model):
    CourseId        = models.CharField(max_length=9, primary_key=True)
    CourseName      = models.CharField(max_length=20)
    CourseDescription = models.CharField(max_length=500)
    Price           = models.IntegerField()
    Course_content  = models.JSONField(default=list)

class Login(models.Model):
    id              = models.AutoField(primary_key=True)
    username        = models.CharField(max_length=100)
    category        = models.CharField(max_length=5)
    email           = models.EmailField(max_length=100,unique=True)
    timestamp       = models.DateTimeField()

class Switches(models.Model):
    id              = models.AutoField(primary_key=True)
    Key             = models.CharField(max_length=100)
    Value           = models.CharField(max_length=100)

class StudentProfile(models.Model):
    id              = models.AutoField(primary_key=True)
    profileimage    = models.TextField()
    name            = models.CharField(max_length=100)
    college         = models.TextField()
    branch          = models.CharField(max_length=100)
    contact         = models.CharField(max_length=10)
    emailid         = models.EmailField(max_length=100)
    cgpa            = models.FloatField(null=True, blank=True)
    skills          = models.TextField()
    otherskills     = models.TextField()
    entranceTest    = models.CharField(max_length=10)
    python          = models.CharField(max_length=10)
    sql             = models.CharField(max_length=10)
    dsa             = models.CharField(max_length=10)
    aptitude        = models.CharField(max_length=10)
    rank            = models.IntegerField()
    resumeLink      = models.TextField()
    communicationVideo = models.TextField()
    hackerrankLink  = models.TextField()
    leetcodeLink    = models.TextField()
    githubLink      = models.TextField()
    isSelected      = models.BooleanField(default=False)
    financialaid    = models.TextField()
    placed          = models.TextField(default='No')

    def __str__(self):
        return self.name
    
class ContactInfo(models.Model):
    ROLE_CHOICES = (
        ('hiringManager', 'Hiring Manager'),
        ('volunteer', 'Volunteer'),
    )

    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    designation = models.CharField(max_length=255, blank=True)
    contactNumber = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=255, blank=True)
    loc = models.CharField(max_length=255, blank=True)
    openings = models.CharField(max_length=255, blank=True)
    employmentType = models.CharField(max_length=50, blank=True)
    duration = models.CharField(max_length=50, blank=True)
    hasBond = models.CharField(max_length=10, blank=True)
    bondDuration= models.CharField(max_length=50, blank=True)
    packageInLPA = models.CharField(max_length=50, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.role})"
    
class Chatbox(models.Model):
    Message_Id = models.CharField(max_length=5,null=False)
    From_User = models.CharField(max_length=100 ,null=False)
    To_User = models.CharField(max_length=100,null=False)
    Timestamp = models.DateTimeField()
    Subject = models.CharField(max_length=100,null=False)
    Content = models.TextField()
    Seen = models.BooleanField(default=False)
    Attachments = models.TextField( )

class userdetails(models.Model):
    userID = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    category = models.CharField(max_length=100,default="")
    expiry_date = models.DateField()
    status = models.CharField(max_length=50)
    register_date = models.DateField(auto_now_add=True)
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)


class Rankings(models.Model):
    Rank_id      = models.AutoField(primary_key=True)
    StudentId   = models.CharField(max_length=15)
    Rank        = models.IntegerField()
    Course      = models.CharField(max_length=100)
    Score       = models.FloatField()
    DateTime    = models.DateTimeField()
    Delay       = models.FloatField()

class ActiveUserCounts(models.Model):
    Sl_id = models.AutoField(primary_key=True)
    StatDateTime = models.DateTimeField()
    ActiveUsers = models.IntegerField()
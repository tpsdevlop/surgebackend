from django.contrib import admin

from .models import *

admin.site.register(login_data)
admin.site.register(StudentDetails)
admin.site.register(CourseDetails)
# admin.site.register(InternshipDetails)
admin.site.register(QuestionDetails_Days)
admin.site.register(StudentDetails_Days_Questions)
admin.site.register(BugDetails)
admin.site.register(Rankings)
admin.site.register(InternshipsDetails)

admin.site.register(CoursePackages)
admin.site.register(StudentProfile)
admin.site.register(ContactInfo)
admin.site.register(Login)
admin.site.register(Switches)
admin.site.register(Attendance)
admin.site.register(ErrorLogs)
admin.site.register(Chatbox)
admin.site.register(userdetails)
admin.site.register(ActiveUserCounts)
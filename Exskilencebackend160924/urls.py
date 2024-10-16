"""Exskilencebackend160924 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from Exskilence import views as ex,sqlviews as sql,pythonrun as ex_py,HTML_CSS_views as html_css,js_views as js , frontend_views as frontend
from Exskilence import coursecreatiton as pkgs,trainerflowQn as tech ,ENYCRP as enc, Chatbox as chat ,adminflow as adminflow ,internship as intr

urlpatterns = [
    path('admin/', admin.site.urls),
    # Swapnodayaplacements
    path ('placement/', include('Exskilence.placements_urls')),
    path ('internshipreport/', include('Exskilence.urls')),
    path ('Questions/<str:course>',tech.Questions), 
    # ADMIN Flow
    path ('getadminflow/', adminflow.adminflow),
    # path('active-users/', adminflow.get_active_users, name='active_users'),
    # path('bugs/reported/<str:period>/', adminflow.get_bugs_reported_by_period, name='get_bugs_reported'),
    # path('bugs/resolved/<str:period>/', adminflow.get_bugs_resolved_by_period, name='get_bugs_resolved'),
    #test
    # path ('test/', ex.updateScore),
    path('encode/', enc.EncodeView , name='encode'),
    path('decode/', enc.DecodeView , name='decode'),
    path ('testcourse/', enc.getcourse),
    path ('activeuser/', enc.activeUsers),
    # Exskilence
    path ('', ex.home),
    path ('fetch/', ex.fetch),
    path ('logout/', ex.logout),
    path ('duration/', ex.get_duration),
    path ('courseInfo/', ex.courseInfo),
    path ('get/course/',ex.getcourse ),
    path ('getdays/',ex.getdays ),
    path ('days/qns/',ex.getQnslist ),
    path ('get/qn/data/',ex.getQn ),
    path ('submit/',ex.submit ),
    path ('nav/qn/',ex.nextQn ),
    path ('daycomplete/',ex.daycomplete ),
    # Sql
    path ('runsql/',sql.sql_query ),
    # Python
    path ('runpy/',ex_py.submit_python ),
    # Frontend
    
    path ('html/',html_css.html_page ),
    path ('css/',html_css.css_compare ),
    # path ('js/',js.run_test_js ),
    path ('js/',js.js_Score ),
    path ('frontend/qns/',frontend.frontend_Questions_page ),
    path ('frontend/qns/data/',frontend.frontend_getQn ),
    path ('frontend/nav/qn/',frontend.frontend_nextQn ),

    path ('createpkgs/', pkgs.createpkgs),
    path ('coursepackages/', pkgs.coursepackages),
    path ('setusercourse/time', pkgs.assigncoursetime),
    path ('getcourselist/', pkgs.allCourses),
    path ('setusercourse/', pkgs.assigncourse),
    path ('studentlist/', pkgs.getallstudents),

    path ('filter/', pkgs.filteringStudents),

    path ('getranking/', ex.getRanks),

    # chatbox
    path ('chatbox/', chat.chatbox),
    path ('upload/', chat.file_upload),
    path ('sendemail/', chat.send_email),
    path('sent/<str:id>', chat.Sent, name='Sent'),
    path('inbox/<str:id>', chat.Inbox, name='Inbox'),
    #for both
      path ('send_email_to_tutor/', chat.send_email_to_tutor),


      # for students
    path('tutordetails/',chat.TutorDetails,name="TutorDetails"),
     path('studentsent/<str:id>', chat.Student_Sent, name='Student_Sent'),
    path('studentinbox/<str:id>', chat.Student_Inbox, name='Student_Inbox'),

    #Internship
    path('intr/<str:index>',intr.get_list_json),
    path('intr/html/', intr.html_page),
    path('intr/css/', intr.css_compare),
    path('intr/js/', intr.js_test),
    path('intr/python/', intr.python_page),
    path('intr/app_py/', intr.python_page),
    path('intr/json/', intr.json_for_validation),
    path('intr/get/file/',intr.download_files),
    path('intr/score/',intr.get_score),
    path('intr/project/score/',intr.project_score),
    path('intr/db/',intr.database_validation),
    path('test/exercise/', intr.test_questions,name= 'test_questions'),
    
]

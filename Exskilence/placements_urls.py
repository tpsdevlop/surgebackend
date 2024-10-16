
from django.urls import path
from .placements_views import * 


urlpatterns = [
    path('login/', login_view, name='login'),
    path('get/<str:email>/<str:name>/', get_user, name='login-detail'), 
    path('students/', student_list, name='student_list'),
    path('studentslist/', get_all_students, name='get_all_students'),
    path('handle_form_submission/', handle_form_submission, name='handle_form_submission'),
    path ( 'guest/login/', guest_login, name='guest_login'),
]
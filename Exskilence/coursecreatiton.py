from datetime import datetime, timedelta
import json
from django.http import HttpResponse
from rest_framework.decorators import api_view
from .models import CoursePackages
from Exskilence.models import CourseDetails, StudentDetails

@api_view(['POST'])
def createpkgs(request):
    try:
        data = request.body
        data = json.loads(data)
        if request.method == "POST":
            getid = CoursePackages.objects.all().order_by('-CourseId')
            if getid:
                cid = int(getid[0].CourseId[-3:])+1
                if len(str(cid))==1:
                    cid = '00'+str(cid)
                elif len(str(cid))==2:
                    cid = '0'+str(cid)
                elif len(str(cid))==3:
                    cid = str(cid)
                else:
                    cid = str(cid)
            else:
                cid = '001'
            CoursePackages.objects.create(
                CourseId='Course'+str(cid),
                CourseName=data.get('CourseName'),
                CourseDescription=data.get('CourseDescription'),
                Price=data.get('Price'),
                Course_content=data.get('Courses'),
            )
            return HttpResponse('Package created successfully')
        else :
            return HttpResponse('Error! Invalid Request',status=400)
    except Exception as e:
        # print(e)
        return HttpResponse(f"An error occurred: {e}", status=500)
        


@api_view(['GET'])
def coursepackages(request):
    try:
        courses = CoursePackages.objects.all()
        data = []
        for course in courses:
            data.append({
                'CourseId': course.CourseId,
                'CourseName': course.CourseName,
                'CourseDescription': course.CourseDescription,
                'Price': course.Price,
                'Courses': course.Course_content,
            })
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception as e:
        return HttpResponse('Server Error! Please Try Again Later',status=500)

@api_view(['GET'])
def allCourses(request):
    try:
        courses = CourseDetails.objects.all().filter().order_by('SubjectId').values()
        data = []
        for course in courses:
            data.append(course.get('SubjectName'))
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception as e:
        return HttpResponse('Server Error! Please Try Again Later',status=500)

@api_view(['POST'])    
def assigncourse(request):
    try:
        data = request.body
        data = json.loads(data)
        pkg = data.get('CourseId')
        stds = data.get('StudentId')
        user = StudentDetails.objects.filter(StudentId__in=stds)
        pkgs = CoursePackages.objects.get(CourseId=pkg)
        notfoundstd = []
        if pkgs is None:
            return HttpResponse('Error! Package does not exist', status=404)
        for std in stds:
            user1 = user.get(StudentId=std)
            if user1:
                for i in pkgs.Course_content:
                    l = list(user1.Courses)
                    if i not in l:
                        l.append(i)
                        user1.Courses = l
                user1.save()
            else:
                notfoundstd.append(std)
        if len(notfoundstd)>0:
            return HttpResponse (json.dumps({"Students": notfoundstd}),content_type='application/json')
        else:
            return HttpResponse('Success! Course assigned successfully',status=200)
    except Exception as e:
        return HttpResponse(f'an error occurred: {e}',status=500)
        
@api_view(['POST'])
def assigncoursetime(request):
    try:
        data = request.body
        data = json.loads(data)
        pkg = data.get('Courses')
        stds = data.get('StudentId')
        user = StudentDetails.objects.filter(StudentId__in=stds)
        notfoundstd = []
        key=str(pkg.keys())
        key = key.replace('dict_keys(', '')[0:-1]
        for std in stds:
            user1 = user.get(StudentId=std)
            if user1:

                for i in user1.Courses:
                    if i in key:
                        user1.Course_Time.update({i:{
                            "Start":datetime.strptime(pkg.get(i).get('Start'), '%Y-%m-%d'),"End":datetime.strptime(pkg.get(i).get('End'), '%Y-%m-%d').__add__(timedelta(hours=23,minutes=59,seconds=59))}})
                
                    
                user1.save()
            else:
                notfoundstd.append(std)
        if len(notfoundstd)>0:
            return HttpResponse (json.dumps({"Students": notfoundstd}),content_type='application/json')
        else:
            return HttpResponse('Success! Course assigned successfully',status=200)
    except Exception as e:
        return HttpResponse(f'an error occurred: {e}',status=500)

@api_view(['POST'])
def getallstudents(request):
    try:
        data = json.loads(request.body)
        Year = str(data.get('Year'))[-2:] if len(str(data.get('Year'))) != 0 else True
        Center = data.get('Center') if len(str(data.get('Center'))) != 0 else True
        Branch = data.get('Branch') if len(str(data.get('Branch'))) != 0 else True
        CollegeName = data.get('CollegeName') if len(str(data.get('CollegeName'))) != 0 else True
        students = StudentDetails.objects.all().values()
        data = []
        for student in students:
            if (str(student.get('StudentId'))[0:2] == Year or Year == True ) and (student.get('Center') == Center or Center == True) and (student.get('branch') == Branch or Branch == True) and (str(student.get('CollegeName')).lower() == str(CollegeName).lower() or CollegeName == True):
                data.append({
                    'StudentId':student.get('StudentId'),
                    'FirstName':student.get('firstName'),
                    'LastName':student.get('lastName'),
                    'Email':student.get('email'),
                    'College':student.get('college_Id'),
                    'Branch':student.get('branch'),
                    'Center':student.get('Center'),
                    })
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception as e:
        return HttpResponse('Server Error! Please Try Again Later',status=500)

@api_view(['GET'])
def filteringStudents(request):
    try:
        Students = StudentDetails.objects.all().values()
        data = [{
            "College":[ i.get('CollegeName') for i in list(Students.values('CollegeName').distinct())],
            "Branch":[ i.get('branch') for i in list(Students.values('branch').distinct())],
            'Center':[ i.get('Center') for i in list(Students.values('Center').distinct())]
        }]
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception as e:
        return HttpResponse(f'an error occurred: {e}',status=500)
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.core.exceptions import ValidationError
import json
from django.views.decorators.http import require_POST
from  Exskilencebackend160924.Blob_service import *
from rest_framework.decorators import api_view 
@csrf_exempt
def create_student_details(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student = StudentDetails(
                StudentId=data.get('StudentId'),
                firstName=data.get('firstName'),
                lastName=data.get('lastName'),
                college_Id=data.get('college_Id'),
                CollegeName=data.get('CollegeName'),
                Center=data.get('Center'),
                email=data.get('email'),
                whatsApp_No=data.get('whatsApp_No'),
                mob_No=data.get('mob_No'),
                sem=data.get('sem'),
                branch=data.get('branch'),
                status=data.get('status'),
                user_category=data.get('user_category'),
                reg_date=data.get('reg_date'),
                exp_date=data.get('exp_date'),
                score=data.get('score'),
                progress_Id=data.get('progress_Id', {}),
                Assignments_test=data.get('Assignments_test', {}),
                Courses=data.get('Courses', []),
                Course_StartTime=data.get('Course_StartTime', {})
            )
            student.full_clean()
            student.save()
 
            return JsonResponse({"message": "Student details created successfully"}, status=201)
 
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": "An error occurred: " + str(e)}, status=400)
 
    return JsonResponse({"error": "Invalid request method"}, status=405)
 
 
@csrf_exempt
def create_student_details_days_questions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_days_questions = StudentDetails_Days_Questions(
                Student_id=data.get('Student_id'),
                Days_completed=data.get('Days_completed', {}),
                Qns_lists=data.get('Qns_lists', {}),
                Qns_status=data.get('Qns_status', {}),
                Ans_lists=data.get('Ans_lists', {}),
                Score_lists=data.get('Score_lists', {}),
                Start_Course=data.get('Start_Course', {})
            )
            student_days_questions.full_clean()
            student_days_questions.save()
 
            return JsonResponse({"message": "Student days and questions created successfully"}, status=201)
 
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": "An error occurred: " + str(e)}, status=400)
 
    return JsonResponse({"error": "Invalid request method"}, status=405)

from Exskilence.views import rankings
@csrf_exempt
def frontpagedeatialsmethod(request):
    try:
        student_details = list(StudentDetails.objects.all().values(
            'StudentId',
            'firstName',
            'college_Id',
            'branch',
            'CGPA',
            'score'
        ))
        mainuser = list(StudentDetails_Days_Questions.objects.all().values())
        student_ranks = rankings()
        userprogress = []
        for student in mainuser:
            student_ID = student['Student_id']
            student_rank = next((rank['Rank'] for rank in student_ranks if rank['StudentId'] == student_ID), None)
            scores = {
                "id": student_ID,
                "totalScore": scorescumulation(student),
                "overallScore": overallscore(student)["totalscore"],
                "totalNumberOFQuesAns": f"{total_number_of_questions_completed(student)}/{overallscore(student)['totalnumofquestionassigned']}",
                "no_of_hrs": get_total_duration(student_ID),
                "Delay":calculate_course_delay(student_ID),
                "rank": student_rank
            }
            userprogress.append(scores)
        if not student_details:
            return JsonResponse({'message': 'No data found'}, status=404)
        result = [{
            'id': item['StudentId'],
            'name': item['firstName'],
            'College': item['college_Id'],
            'Branch': item['branch'],
            'CGPA': item['CGPA']
        } for item in student_details]
 
        combinedData = combine_data(result, userprogress)
        return JsonResponse(combinedData, safe=False)
 
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
def overallscore(student):
    easy = 0
    medium = 0
    hard = 0
    number_quesitions_assgned = 0
    questionlist = ["HTMLCSS","Java_Script","SQL_Day_1","SQL_Day_2",
                    "SQL_Day_3","SQL_Day_4","SQL_Day_5","SQL_Day_6",
                    "SQL_Day_7","SQL_Day_8","SQL_Day_9","SQL_Day_10"
                    ,"Python_Day_1","Python_Day_2","Python_Day_3",
                    "Python_Day_4","Python_Day_5"
                    ]
    for i in questionlist:
        questionsperlist = student['Qns_lists'].get(i)
        if questionsperlist is not None:
            for i in questionsperlist:
                # # print(number_quesitions_assgned)
                number_quesitions_assgned +=1
                if i[-4] == "E":
                    easy += 1
                elif i[-4] == "M":
                    medium += 1
                else:
                    hard += 1
    totalscore = (5*easy)+(10*medium)+(15*hard)
    return {"totalscore":totalscore,"totalnumofquestionassigned":number_quesitions_assgned}
def combine_data(result, userprogress):
    userprogress_dict = {item['id']: item for item in userprogress}
    combined = []
    for student in result:
        student_id = student['id']
        if student_id in userprogress_dict:
            combined_entry = {**student, **userprogress_dict[student_id]}
        else:
            combined_entry = student
        combined.append(combined_entry)
 
    return combined
def scorescumulation(student):
    score_sum = 0
    score_HTMLCSS = 0
    score_breakdown = {}
    score_lists = student.get('Score_lists', {})
    # print(score_lists)
    for key, value in score_lists.items():
        if isinstance(value, str) and '/' in value:
            try:
                score_value = float(value.split("/")[0])
            except ValueError:
                continue
        elif isinstance(value, (int, float)):
            score_value = value
        else:
            continue
       
        if key == "HTMLScore" or key == "CSSScore":
            score_breakdown[key] = score_value
            score_HTMLCSS += score_value  
        else:
            score_breakdown[key] = score_value
            score_sum += score_value
    total_HTMLCSS = score_HTMLCSS
    total_HTMLCSS_half = round(total_HTMLCSS / 2, 2)
    # print(total_HTMLCSS_half)
    score_sum += total_HTMLCSS_half
    score_breakdown['HTMLCSS_Total'] = total_HTMLCSS_half
    return {
        'Total_Score': score_sum,
        'Score_Breakdown': score_breakdown
    }
 
   
 
def total_number_of_questions_completed(student):
    categories = ["CSS", "Python", "SQL", "Java_Script"]
    per_student_detail = QuestionDetails_Days.objects.filter(
        Student_id=student['Student_id'],
        Subject__in=categories
    ).values('Subject')
    total_questions = per_student_detail.count()
    return total_questions
   
@api_view(['GET'])
def getSTdDaysdetailes(req):
    try:
        mainuser = StudentDetails_Days_Questions.objects.all().values( )
        if mainuser is None:
            HttpResponse('No data found')
        return HttpResponse(json.dumps( list(mainuser) ), content_type='application/json')    
    except Exception as e:
        return HttpResponse('An error occurred'+str(e))
 
@csrf_exempt
@require_POST
def per_student_html_CSS_data(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
 
        if not student_id:
            return JsonResponse({'error': 'student_id is required'}, status=400)
 
        student = StudentDetails_Days_Questions.objects.filter(pk=student_id).values().first()
        if not student:
            return JsonResponse({'error': 'Student not found'}, status=404)
 
        answered_questions = list(QuestionDetails_Days.objects.filter(Student_id=student_id).values())
 
        # Process HTML and CSS questions
        questions_data = {}
        for subject in ['HTML', 'CSS']:
            if subject in student['Qns_status']:
                for qn_id, status in student['Qns_status'][subject].items():
                    if qn_id not in questions_data:
                        questions_data[qn_id] = {
                            'qn_id': qn_id,
                            'html_status': 0,
                            'html_answer_status': 'NA',
                            'html_score': 'NA',
                            'html_testcases_passed':'NA',
                            'css_status': 0,
                            'css_answer_status': 'NA',
                            'css_score': 'NA',
                            'css_testcases_passed': 'NA',
                        }
                   
                    subject_lower = subject.lower()
                    questions_data[qn_id][f'{subject_lower}_status'] = status
                   
                    # Check if the question has been answered
                    answered_question = next((q for q in answered_questions if q['Qn'] == qn_id and q['Subject'] == subject), None)
                    if answered_question:
                        questions_data[qn_id].update({
                            f'{subject_lower}_answer_status': 'Correct' if answered_question['Score'] == answered_question['Score'] else 'Incorrect',
                            f'{subject_lower}_score': answered_question['Score'],
                            # f'{subject_lower}_total_score': answered_question['Total_Score'],
                            f'{subject_lower}_testcases_passed': answered_question['Result']['TestCases']['Testcase']
                        })
 
        # Get student details
        student_details = studentdata(student_id)
 
        response_data = {
            'student_id': student['Student_id'],
            'name': student_details['name'],
            'college': student_details['college'],
            'branch': student_details['branch'],
            'questions': list(questions_data.values())
        }
 
        return JsonResponse(response_data)
 
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 
@csrf_exempt
@require_POST
def per_student_JS_data(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        student = StudentDetails_Days_Questions.objects.filter(pk=student_id).values()
        studenttsdata = studentdata(student_id)
        # print(studenttsdata)
        studentQuesList = []
        if "Java_Script" in student[0]['Qns_lists']:
            studentQuesList.append(student[0]['Qns_lists']['Java_Script'])
        else:
            studentQuesList.append(["no data is found"])
        studentsJava_ScriptStatus = []
        if "Java_Script" in student[0]['Qns_status'].keys():
            for i in student[0]['Qns_status']['Java_Script'].values():
                studentsJava_ScriptStatus.append(i)
        else:
            studentsJava_ScriptStatus.append(["no data is found"])
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not student_id:
        return JsonResponse({'error': 'student_id is required'}, status=400)
    return JsonResponse({
        'student_id': student[0]['Student_id'],
        'Name':studenttsdata['name'],
        'college':studenttsdata['college'],
        'branch':studenttsdata['branch'],
        'studentQuesList': studentQuesList,
        "Javascript":studentsJava_ScriptStatus,
    })
 
 
# this method is to get answers of a particular html css question
@csrf_exempt
@require_POST
def per_student_ques_detials(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        question_id = data.get('question_id')
        if not student_id or not question_id:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        studenttsdata = studentdata(student_id)
        studenthtml_queryset = QuestionDetails_Days.objects.filter(
            Student_id=student_id,
            Qn=question_id,
            Subject="HTML"
        ).values()
        studentCSS_queryset = QuestionDetails_Days.objects.filter(
            Student_id=student_id,
            Qn=question_id,
            Subject="CSS"
        ).values()
        stduentHTMLAns = {}
        studentCSSAns = {}
        if  len(studenthtml_queryset)>0:
            stduentHTMLAns = studenthtml_queryset[0]
            HTMLdict = {
                'question':get_questions(question_id,"HTMLCSS"),
                'Attempts': stduentHTMLAns["Attempts"],
                'Score':stduentHTMLAns["Score"],
                'subject':"HTML",
                'ans':stduentHTMLAns["Ans"]
            }
            stduentHTMLAns = HTMLdict
        # else :
            # print("no data found" + str(stduentHTMLAns))
 
        if len(studentCSS_queryset)>0:
            studentCSSAns = studentCSS_queryset[0]
            CSSdict = {
                'Attempts': studentCSSAns["Attempts"],
                'Score':studentCSSAns["Score"],
                'subject':"CSS",
                'ans':studentCSSAns["Ans"]
            }
            studentCSSAns = CSSdict
        # else :
            # print("no data found" + str(studentCSSAns))
        return JsonResponse({
                'student_id': student_id,
                'Name':studenttsdata['name'],
                'college':studenttsdata['college'],
                'branch':studenttsdata['branch'],
                'question_id': question_id,
                'htmlans': stduentHTMLAns,
                'CSSans':studentCSSAns
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
@csrf_exempt
@require_POST
def per_student_JS_ques_detials(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        question_id = data.get('question_id')
        if not student_id or not question_id:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        studenttsdata = studentdata(student_id)
        studentJS_queryset = QuestionDetails_Days.objects.filter(
            Student_id=student_id,
            Qn=question_id,
            Subject="Java_Script"
        ).values()
        stduentJavaScriptAns = {}
        if  len(studentJS_queryset)>0:
            stduentJavaScriptAns = studentJS_queryset[0]
            JSdict = {
                'question':get_questions(question_id,"Java_Script"),
                'Attempts': stduentJavaScriptAns["Attempts"],
                'Score':stduentJavaScriptAns["Score"],
                'subject':"Java_Script",
                'ans':stduentJavaScriptAns["Ans"]
            }
            stduentJavaScriptAns = JSdict
            # print(stduentJavaScriptAns)
        # else :
            # print("no data found" + str(stduentJavaScriptAns))
        return JsonResponse({
                'student_id': student_id,
                'Name':studenttsdata['name'],
                'college':studenttsdata['college'],
                'branch':studenttsdata['branch'],
                'question_id': question_id,
                'JSAns': stduentJavaScriptAns,
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
 
 
 
def get_questions(questionid,course):
    CONTAINER ="internship"
    qnsdata = download_blob2('Internship_days_schema/'+course+ '/'+questionid+'.json',CONTAINER)
    qnsdata = json.loads(qnsdata)
    return qnsdata["Qn"]
 
def studentdata(studentid):
    try:
        stduent = StudentDetails.objects.filter(pk=studentid).values()
        stduentsendData = {
            'id': stduent[0]['StudentId'],
            'name': stduent[0]['firstName'],
            'college': stduent[0]['college_Id'],
            'branch': stduent[0]['branch'],
        }
 
        return stduentsendData
    except Exception as e:
        return {}
   
def get_total_duration(student_id):
    attendance_records = Attendance.objects.filter(SID=student_id)
    total_duration_in_seconds = 0
    for record in attendance_records:
        total_duration_in_seconds += record.Duration
    total_duration_in_hours = round(total_duration_in_seconds / 3600, 2)
    return total_duration_in_hours
from django.utils import timezone
def calculate_course_delay(student_id):
    try:
        student = StudentDetails.objects.get(StudentId=student_id)
        studentansdetials = StudentDetails_Days_Questions.objects.filter(Student_id=student_id).values().first()
        current_date = timezone.now().date()
        total_delay = 0
        delays = {}
        for course, time_range in student.Course_Time.items():
            end_date = time_range.get("End")
 
            if end_date:
                course_end_date = end_date.date() if isinstance(end_date, datetime) else end_date
                question_data = calculate_questions_completed(studentansdetials, course)
                question_data_course = question_data.get(course,{})
                total_questions = question_data_course.get('total_assigned', 0)
                answered_questions = question_data_course.get('total_answered', 0)
                # if(course=="HTMLCSS"):
                # print("nldmore"+str(student)+str(time_range)+"\t"+"the students questiondata"+str(question_data_course))
                if answered_questions >= total_questions:
                    delays[course] = 0
                else:
                    if current_date > course_end_date:
                        delay_days = (current_date - course_end_date).days
                        delays[course] = delay_days
                        total_delay += delay_days
                    else:
                        delays[course] = 0
        delays["total_delay"] = total_delay
        return delays
    except StudentDetails.DoesNotExist:
        return {"error": "Student with the given ID does not exist."}
 
def calculate_questions_completed(data,subject):
    subjects = ['HTMLCSS', 'JavaScript', 'SQL', 'Python']  # Define your subjects
    results = {}
    assigned_html_css = data.get('Qns_lists', {}).get('HTMLCSS', [])
    answered_html = data.get('Ans_lists', {}).get('HTML', [])
    answered_css = data.get('Ans_lists', {}).get('CSS', [])
    answered_html_css = set(answered_html + answered_css)
    completed_html_css = [q for q in assigned_html_css if q in answered_html_css]
    results['HTMLCSS'] = {
        'total_assigned': len(assigned_html_css),
        'total_answered': len(completed_html_css)
    }
    for subject in ['JavaScript', 'SQL', 'Python']:
        assigned_questions = data.get('Qns_lists', {}).get(subject, [])
        answered_questions = data.get('Ans_lists', {}).get(subject, [])
        completed_questions = [q for q in assigned_questions if q in answered_questions]
       
        results[subject] = {
            'total_assigned': len(assigned_questions),
            'total_answered': len(completed_questions)
        }
       
    return results
 
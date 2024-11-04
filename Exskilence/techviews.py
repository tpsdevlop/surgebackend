from collections import defaultdict
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.core.exceptions import ValidationError
import json
from django.views.decorators.http import require_POST
from  Exskilencebackend160924.Blob_service import *
from rest_framework.decorators import api_view 
from datetime import datetime
from Exskilence.Ranking import getRankings
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
 
 
def get_student_rank(students_data, student_id, ranking_subjects):
    def get_combined_score(student):
        score = 0
        for subject in ranking_subjects:
            subject_score = student['Score_lists'].get(f"{subject}Score", "0/0").split('/')[0]
            score += float(subject_score)
        return score
 
    def is_valid_student(id):
        return not any(keyword in id for keyword in ["ADMI", "TRAI", "TEST"])
 
    scores = [(student['Student_id'], get_combined_score(student))
              for student in students_data
              if is_valid_student(student['Student_id'])]
   
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    ranks = {}
    current_rank = 1
    for i, (id, score) in enumerate(sorted_scores):
        if i > 0 and score < sorted_scores[i-1][1]:
            current_rank = i + 1
        ranks[id] = (current_rank, score)
   
    return ranks.get(student_id, (None, None))
 

def get_student_rank(students_data, student_id, ranking_subjects):
    def get_combined_score(student):
        score = 0
        for subject in ranking_subjects:
            subject_score = student['Score_lists'].get(f"{subject}Score", "0/0").split('/')[0]
            score += float(subject_score)
        return score
 
    def is_valid_student(id):
        return not any(keyword in id for keyword in ["ADMI", "TRAI", "TEST"])
 
    scores = [(student['Student_id'], get_combined_score(student))
              for student in students_data
              if is_valid_student(student['Student_id'])]
   
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    ranks = {}
    current_rank = 1
    for i, (id, score) in enumerate(sorted_scores):
        if i > 0 and score < sorted_scores[i-1][1]:
            current_rank = i + 1
        ranks[id] = (current_rank, score)
   
    return ranks.get(student_id, (None, None))
 
@csrf_exempt
def frontpagedeatialsmethod(request):
    try:
        student_details = list(StudentDetails.objects.all().values(
            'StudentId',
            'firstName',
            'lastName',
            'college_Id',
            'branch',
            'CGPA',
            'score'
        ))
        mainuser = list(StudentDetails_Days_Questions.objects.all().values())
        student_ids = [student['StudentId'] for student in student_details]
        question_details = list(QuestionDetails_Days.objects.filter(
            Student_id__in=student_ids
        ).values('Student_id', 'Subject'))
        attendance_records = list(Attendance.objects.filter(
            SID__in=student_ids
        ).values('SID', 'Login_time', 'Duration', 'Last_update'))
        subject_counts_by_student = get_subject_counts(question_details)
        user_durations = get_total_durations_for_all_students(attendance_records)
        rankings = {rank.StudentId: str(rank.Rank) for rank in Rankings.objects.filter(Course="HTMLCSS", StudentId__in=student_ids)}

        userprogress = []
        for student in mainuser:
            student_ID = student['Student_id'] 
            days = StudentDetails_Days_Questions.objects.filter(Student_id=student_ID).first()
            scores = {
                "id": student_ID,
                "totalScore": scorescumulation(student),
                "overallScore": overallscore(student)["totalscore"],
                "totalNumberOFQuesAns": subject_counts_by_student.get(student_ID, {}),
                "no_of_hrs": user_durations.get(student_ID, {}),
                "Delay":delay(student_ID),
                "rank": rankings.get(student_ID, 'N/A')
            }
            userprogress.append(scores)
        if not student_details:
            return JsonResponse({'message': 'No data found'}, status=404)
        result = [{
            'id': item['StudentId'], 
            'name': item['firstName']+item['lastName'], 
            'College': item['college_Id'], 
            'Branch': item['branch'],
            'CGPA': item['CGPA']
        } for item in student_details]

        combinedData = combine_data(result, userprogress)
        return JsonResponse(combinedData, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_subject_counts(question_details):
    categories = {"HTML": 30, "Python": 200, "SQL": 200, "Java_Script": 30}
    subject_counts_by_student = {}
    for question in question_details:
        student_id = question['Student_id']
        subject = question['Subject']
        if student_id not in subject_counts_by_student:
            subject_counts_by_student[student_id] = {subject: 0 for subject in categories.keys()}
        if subject in categories:
            subject_counts_by_student[student_id][subject] = subject_counts_by_student[student_id].get(subject, 0) + 1
    for student_id, subject_counts in subject_counts_by_student.items():
        for subject, count in subject_counts.items():
            limit = categories[subject]
            subject_counts[subject] = f"{count}/{limit}"
    return subject_counts_by_student

def overallscore(student):
    try:
        easy = medium = hard = 0
        number_questions_assigned = 0
        question_list = {
            "HTMLCSS", "Java_Script", "SQL_Day_1", "SQL_Day_2", "SQL_Day_3",
            "SQL_Day_4", "SQL_Day_5", "SQL_Day_6", "SQL_Day_7", "SQL_Day_8",
            "SQL_Day_9", "SQL_Day_10", "Python_Day_1", "Python_Day_2",
            "Python_Day_3", "Python_Day_4", "Python_Day_5"
        }
        qns_lists = student['Qns_lists']
        for topic in question_list:
            questions_per_list = qns_lists.get(topic)
            if not questions_per_list:
                continue  
            number_questions_assigned += len(questions_per_list)
            for question in questions_per_list:
                if len(question) >= 4:
                    difficulty = question[-4]
                    if difficulty == "E":
                        easy += 1
                    elif difficulty == "M":
                        medium += 1
                    else:
                        hard += 1

        totalscore = (5 * easy) + (10 * medium) + (15 * hard)

        return {
            "totalscore": totalscore,
            "totalnumofquestionassigned": number_questions_assigned
        }
    
    except Exception as e:
        return {"error": str(e)}


def getRankings(COURSE, student_ids):
    try:
        rankings = {rank.StudentId: str(rank.Rank) for rank in Rankings.objects.filter(Course=COURSE, StudentId__in=student_ids)}
        return rankings
    except Exception as e:
        # print(f"Error in getRankings: {str(e)}")
        return {}


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
        if key in {"HTMLScore", "CSSScore"}:
            score_HTMLCSS += score_value
        else:
            score_sum += score_value
        
        score_breakdown[key] = score_value
    total_HTMLCSS_half = score_HTMLCSS / 2
    score_sum += total_HTMLCSS_half

    score_breakdown['HTMLCSS_Total'] = round(total_HTMLCSS_half, 2)
    
    return {
        'Total_Score': score_sum,
        'Score_Breakdown': score_breakdown
    }



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
        else :
            return("no data found + str(stduentHTMLAns)")
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
        else :
            pass
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
        else :
            return ("no data found")
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
    
def get_total_durations_for_all_students(attendance_records):
    # Define date ranges for each subject
    subjects_date_ranges = {
        "HTMLCSS": ("2024-10-03", "2024-10-12"),
        "JavaScript": ("2024-10-14", "2024-11-02"),
        "SQL": ("2024-11-04", "2024-11-13"),
        "Python": ("2024-11-15", "2024-11-24"),
        "Internship": ("2024-11-26", "2024-12-31")
    }

    # Convert date ranges to aware datetime objects
    subjects_date_ranges = {
        subject: (
            timezone.make_aware(datetime.strptime(start, '%Y-%m-%d')), 
            timezone.make_aware(datetime.strptime(end, '%Y-%m-%d'))
        ) for subject, (start, end) in subjects_date_ranges.items()
    }

    student_subject_durations = defaultdict(lambda: defaultdict(float))

    for record in attendance_records:
        student_id = record['SID']
        login_time = record['Login_time']
        duration = record['Duration']

        for subject, (start_date, end_date) in subjects_date_ranges.items():
            if start_date <= login_time <= end_date:
                student_subject_durations[student_id][subject] += duration

    for student_id, durations in student_subject_durations.items():
        student_subject_durations[student_id] = {subject: round(duration / 3600, 2) for subject, duration in durations.items()}

    return student_subject_durations


from datetime import datetime
from django.utils import timezone
from datetime import datetime
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
from Exskilence.filters import filterQuery  
def rankings():
    try:
        ranks = StudentDetails.objects.all()
        if ranks is None:
            HttpResponse('No data found')
        out ={}
        noDAta = []
        for i in ranks:
         if str(i.StudentId)[2:].startswith("ADMI") or str(i.StudentId)[2:].startswith("TRAI") or str(i.StudentId)[2:].startswith("TEST"):
            continue
         user = QuestionDetails_Days.objects.filter(Student_id=i.StudentId)
         if user is None:
            noDAta.append(i.StudentId)
            continue
         HTML = filterQuery(user, 'Subject',  'HTML')
         CSS = filterQuery(user, 'Subject',  'CSS')
         if HTML is None or CSS is None or len(HTML) == 0 or len(CSS) == 0:
            noDAta.append(i.StudentId)
            continue
         HTMLCSSSCORE =0
         HTMLLASTTIME = HTML[0].get('DateAndTime')
         for i1 in HTML:
            # print(i)
            HTMLCSSSCORE += i1.get('Score')
            if i1.get('DateAndTime') > HTMLLASTTIME:
                HTMLLASTTIME = i1.get('DateAndTime')
         for i2 in CSS:
            HTMLCSSSCORE += i2.get('Score')
            if i2.get('DateAndTime') > HTMLLASTTIME:
                HTMLLASTTIME = i2.get('DateAndTime')
        #  print(HTMLCSSSCORE)#,QuestionDetails_Days.objects.filter(    Q(Student_id=i.Student_id) & (Q(Subject='HTML') | Q(Subject='CSS'))).aggregate(total_score=Sum('Score'))['total_score'] or 0 )
         
         out.update({i.StudentId: {
            "HTMLCSS":   HTMLCSSSCORE,
            'HTML_last_Question':   HTMLLASTTIME,
 
        }
    })
        ranks = sorted(    out.items(),     key=lambda x: (-x[1]['HTMLCSS'], x[1]['HTML_last_Question']))  
        # print(ranks)
        res = []
        for i in ranks:
            res.append({'Rank':ranks.index(i)+1,"StudentId":i [0],"Total":i[1]['HTMLCSS'], "LastTime":i[1]['HTML_last_Question']})
            # print({'Rank':ranks.index(i)+1,"StudentId":i [0], "LastTime":i[1]['HTML_last_Question'],"Total":i[1]['HTMLCSS']})
        return res
   
    except Exception as e:
        print(e)
        return HttpResponse('An error occurred'+str(e))
   

     
 

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
from Exskilence.filters import filterQuery  
def rankings():
    try:
        ranks = StudentDetails.objects.all()
        if ranks is None:
            HttpResponse('No data found')
        out ={}
        noDAta = []
        for i in ranks:
         if str(i.StudentId)[2:].startswith("ADMI") or str(i.StudentId)[2:].startswith("TRAI") or str(i.StudentId)[2:].startswith("TEST"):
            continue
         user = QuestionDetails_Days.objects.filter(Student_id=i.StudentId)
         if user is None:
            noDAta.append(i.StudentId)
            continue
         HTML = filterQuery(user, 'Subject',  'HTML')
         CSS = filterQuery(user, 'Subject',  'CSS')
         if HTML is None or CSS is None or len(HTML) == 0 or len(CSS) == 0:
            noDAta.append(i.StudentId)
            continue
         HTMLCSSSCORE =0
         HTMLLASTTIME = HTML[0].get('DateAndTime')
         for i1 in HTML:
            # print(i)
            HTMLCSSSCORE += i1.get('Score')
            if i1.get('DateAndTime') > HTMLLASTTIME:
                HTMLLASTTIME = i1.get('DateAndTime')
         for i2 in CSS:
            HTMLCSSSCORE += i2.get('Score')
            if i2.get('DateAndTime') > HTMLLASTTIME:
                HTMLLASTTIME = i2.get('DateAndTime')
        #  print(HTMLCSSSCORE)#,QuestionDetails_Days.objects.filter(    Q(Student_id=i.Student_id) & (Q(Subject='HTML') | Q(Subject='CSS'))).aggregate(total_score=Sum('Score'))['total_score'] or 0 )
         
         out.update({i.StudentId: {
            "HTMLCSS":   HTMLCSSSCORE,
            'HTML_last_Question':   HTMLLASTTIME,
 
        }
    })
        ranks = sorted(    out.items(),     key=lambda x: (-x[1]['HTMLCSS'], x[1]['HTML_last_Question']))  
        # print(ranks)
        res = []
        for i in ranks:
            res.append({'Rank':ranks.index(i)+1,"StudentId":i [0],"Total":i[1]['HTMLCSS'], "LastTime":i[1]['HTML_last_Question']})
            # print({'Rank':ranks.index(i)+1,"StudentId":i [0], "LastTime":i[1]['HTML_last_Question'],"Total":i[1]['HTMLCSS']})
        return res
   
    except Exception as e:
        print(e)
        return HttpResponse('An error occurred'+str(e))
   

     
 
def delay(student_id):
    try:
        student_data = StudentDetails.objects.filter(StudentId=student_id).first()
        list_of_course=[]
        if student_data:
            course_time = student_data.Course_Time
            ended_courses = {}
            current_time = datetime.now()
            for course, timings in course_time.items():
                start_time = timings['Start']  
                end_time = timings['End']      
                if end_time < current_time:
                    duration = (end_time - start_time).days
                    ended_courses[course] = {
                        'End Time': end_time,
                        'days': duration
                    }
                    list_of_course.append(course)
            response_data = {
                "StudentId": student_data.StudentId,
                "Ended_Courses": ended_courses,
                "list_of_course":list_of_course
            }
        else:
            response_data = {
                "StudentId": student_id,
                "Ended_Courses": {}
            }
       
        data=no_of_q_ans(response_data)
        return data
 
    except ValueError as ve:
        return ve
    except Exception as e:
        pass

 
 
def no_of_q_ans(data):
    student_id=data['StudentId']
    ended_courses=data['Ended_Courses']
    list_of_course=data['list_of_course']
    result={
    }
    days=StudentDetails_Days_Questions.objects.filter(Student_id=student_id).first()
    if days:
        for course in list_of_course:
            total_days = ended_courses.get(course, {}).get('days', 0) +1
            if course=="HTMLCSS":
                if (len(days.Qns_lists[course])==len(days.Ans_lists["HTML"])):
                    ex={
                        "StudentId":student_id,
                        "Course":course,
                        "End_time":ended_courses.get(course, {}).get('End Time', 0)
                    }
                    delay=last_submit(ex)

                    result[course]=delay
                else:
                    delay=compare_w_current(ended_courses[course]['End Time'])
                    result[course]=delay
            if course in days.Qns_lists and course in days.Ans_lists:
                course_len=len(days.Qns_lists[course])
                if (course_len==len(days.Ans_lists[course])):
                    ex={
                        "StudentId":student_id,
                        "Course":course,
                        "End_time":ended_courses.get(course, {}).get('End Time', 0)
                    }
                    delay=last_submit(ex)
                    # result[course]={
                    #     'total_days':total_days,
                    #     'delay':delay,
                    # }
                    result[course]=delay
                else:
                    delay=compare_w_current(ended_courses[course]['End Time'])
                    # result[course]={
                    #     'total_days':total_days,
                    #     'delayexist':delay,
                    # }
                    result[course]=delay
    return result
 
def compare_w_current(time):
    current=datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
    current=datetime.strptime(str(current).split(' ')[0],"%Y-%m-%d")
    existing=datetime.strptime(str(time).split(' ')[0], "%Y-%m-%d")
   
    return ((current-existing).days)
 
def last_submit(ex):
    student_id = ex['StudentId']
    all_submissions = QuestionDetails_Days.objects.filter(Student_id=student_id)
    recent_times = []
    course=ex['Course']
    delay=0
    if all_submissions:
        current_course = "HTML" if course == "HTMLCSS" else course
        for submission in all_submissions:
            if submission.Subject == current_course:
                submission_time = submission.DateAndTime
                recent_times.append(submission_time)
    if recent_times:
        recent_time = max(recent_times)
        current=datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
        current=datetime.strptime(str(current).split(' ')[0],"%Y-%m-%d")
        existing=datetime.strptime(str(recent_time).split(' ')[0], "%Y-%m-%d")
        end=ex['End_time']
        end=datetime.strptime(str(end).split(' ')[0], "%Y-%m-%d")
       
        if (end-existing).days>=0:
            delay="N/A"
        elif (end-existing).days<0:
            delay=(existing-end).days
    return delay


# def total_number_of_questions_completed(student):
#     categories = ["HTML", "Python", "SQL", "Java_Script"]
    
#     questions = QuestionDetails_Days.objects.filter(
#         Student_id=student['Student_id']
#     ).values_list('Subject', flat=True)
    
#     subject_counts = {}
    
#     for subject in categories:
#         completed_questions = questions.filter(Subject=subject).count()
        
#         if(subject=="HTML"or subject=="Java_Script"):
#             subject_counts[subject] = f"{completed_questions}/30"
#         else:
#             subject_counts[subject] = f"{completed_questions}/200"
    
#     return subject_counts
    
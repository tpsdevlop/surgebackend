from django.http import HttpResponse
from Exskilencebackend160924.settings import *
from rest_framework.decorators import api_view
from datetime import date, datetime, time, timedelta
from Exskilence.models import *
from Exskilence.filters import *
from Exskilence.ErrorLog import ErrorLog
from django.db.models import Sum
# from Exskilence.views import rankings
STARTTIMES = {
            'HTMLCSS':{
                'Start':datetime.strptime('2024-10-03 00:00:00', "%Y-%m-%d %H:%M:%S"),
                'End':datetime.strptime('2024-10-12 23:59:59', "%Y-%m-%d %H:%M:%S")
            },
            'Java_Script':{
                'Start':datetime.strptime('2024-10-14 00:00:00', "%Y-%m-%d %H:%M:%S"),
                'End':datetime.strptime('2024-11-02 23:59:59', "%Y-%m-%d %H:%M:%S")
            },
            'SQL':{
                'Start':datetime.strptime('2024-11-04 00:00:00', "%Y-%m-%d %H:%M:%S"),
                'End':datetime.strptime('2024-11-13 23:59:59', "%Y-%m-%d %H:%M:%S")
            },
            'Python':{
                'Start':datetime.strptime('2024-11-15 00:00:00', "%Y-%m-%d %H:%M:%S"),
                'End':datetime.strptime('2024-11-24 23:59:59', "%Y-%m-%d %H:%M:%S")
            }
        }
def updateRanks(COURSE):
    try:
        # std_all = StudentDetails.objects.all()
        std_days_all = StudentDetails_Days_Questions.objects.all()
        new_ranks = []
        if COURSE == "HTMLCSS" or COURSE == "HTML" or COURSE == "CSS":
            COURSE = "HTMLCSS"
        print('COURSE',COURSE)
        
        maxscore = filterQueryMaxValueScore(std_days_all,COURSE)
        maxdelay1 = filterQueryMaxdelay(std_days_all,COURSE)
        if COURSE == 'HTMLCSS' or COURSE == 'HTML' or COURSE == 'CSS' :
            COURSE = 'HTMLCSS'
            maxdelay = (datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")-STARTTIMES.get(COURSE).get('Start')).total_seconds()/60*60
        elif COURSE == 'Java_Script' :
            maxdelay = (datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")-STARTTIMES.get(COURSE).get('Start')).total_seconds()/60*60
        else:
            maxdelay = (datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")-STARTTIMES.get(COURSE).get('Start')).total_seconds()/60*60

        for user in std_days_all:
            if str(user.Student_id)[2:].startswith("ADMI") or str(user.Student_id)[2:].startswith("TRAI") or str(user.Student_id)[2:].startswith("TEST"):
                continue
            if COURSE == 'HTMLCSS' or COURSE == 'Java_Script':
                if user.Qns_lists.get(COURSE) is None:
                    user.Qns_lists.update({COURSE:[]})
                    user.Ans_lists.update({COURSE:[]})
                    user.Score_lists.update({COURSE:0})
                if len(user.Qns_lists.get(COURSE,[]) ) == len(user.Ans_lists.get(COURSE if COURSE != 'HTMLCSS' else 'HTML',[]) ) and len(user.Qns_lists.get(COURSE,[]) )  > 0:
                    if COURSE == 'HTMLCSS' or COURSE == 'HTML' or COURSE == 'CSS':
                        userScore = (float(str(user.Score_lists.get("HTMLScore",0)).split('/')[0])+float(str(user.Score_lists.get("CSSScore",0)).split('/')[0]))
                    else:
                        userScore = float(str(user.Score_lists.get(str(COURSE)+'Score',0)).split('/')[0])
                    userDelay = user.End_Course.get(COURSE) if user.End_Course.get(COURSE) is not None else user.Start_Course.get(COURSE,STARTTIMES.get(COURSE).get('Start') if COURSE != 'HTMLCSS' and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('End'))
                else:
                    # print('Qns_lists',len(user.Qns_lists.get(COURSE,[]) ),'Ans_lists',len(user.Ans_lists.get(COURSE if COURSE != 'HTMLCSS' else 'HTML',[]) ),'SID',user.Student_id,"*******************************")
                    continue
            else:
                    userScore = float(str(user.Score_lists.get(str(COURSE)+'Score',0)).split('/')[0])
                    userDelay = user.End_Course.get(COURSE) if user.End_Course.get(COURSE) is not None else user.Start_Course.get(COURSE,STARTTIMES.get(COURSE).get('Start') if COURSE != 'HTMLCSS' and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('End'))


            startdate = STARTTIMES.get(COURSE).get('Start') #if COURSE != 'HTMLCSS' and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('Start')
            delay =(datetime.strptime(str(userDelay).split('.')[0], "%Y-%m-%d %H:%M:%S")-startdate).total_seconds()/60*60
            # print('delay',delay,'maxdelay',maxdelay,'userScore',userScore,'maxscore',maxscore,'COURSE',COURSE,'startdate',startdate,'userDelay',userDelay,'delay',)
            # if delay < 0:
            #     delay = 0
            # if  maxdelay == 0:  
            #     Scorevalue = (0.8 * (userScore/maxscore))-0
            # else:
            #     Scorevalue = (0.8 * (userScore/maxscore))-( (0.2) * (delay/maxdelay))
 
            Scorevalue = (0.8 * (userScore/maxscore))-( (0.2) * (delay/maxdelay))
            new_ranks.append({
                'StudentId':user.Student_id,
                'Score':Scorevalue,
                'Course':COURSE,
                'DateTime':userDelay,
                'userScore':userScore,
                'delay':(datetime.strptime(str(userDelay).split('.')[0], "%Y-%m-%d %H:%M:%S")-startdate).days
            })
        new_ranks = [i for i in new_ranks if i.get('Score') != 0 ]
        new_ranks = sorted(new_ranks, key=lambda x: x['Score'], reverse=True)
        for i in new_ranks:
            i['Rank'] = new_ranks.index(i)+1
            print(i.get('Rank'),'\t',i.get('StudentId'),'\t',i.get('Score'),'\t',i.get('Course'),'\t',i.get('DateTime'),'\t',i.get('userScore'),'\t',i.get('delay'))
         
        oldranks = Rankings.objects.filter(Course = COURSE).order_by('-Rank')
        new_rankings = []
        if  len(oldranks) > 0:
            for i in oldranks:
                i.delete()
        for i in new_ranks:
            r = Rankings.objects.create(
                StudentId = i.get('StudentId'),
                Rank = i.get('Rank'),
                Course = i.get('Course'),
                Score = i.get('Score'),
                DateTime = i.get('DateTime'),
                Delay = (i.get('delay')),
            ) 
            if r is not None:
                new_rankings.append(  r)
        return new_rankings
        
    except Exception as e:
        print(e) 
        return  'An error occurred  :'+str(e) 
def updateRanks2(COURSE):
    try:
        std_days_all = StudentDetails_Days_Questions.objects.all()
        std_all = StudentDetails.objects.all()
        ranks = rankings(filterQueryTodict(std_all),COURSE)
        new_ranks = []
        if COURSE == "HTMLCSS" or COURSE == "HTML" or COURSE == "CSS":
            COURSE = "HTMLCSS"
        print('COURSE',COURSE)
        
        for i in std_days_all:
            for j in ranks:
                if i.Student_id == j['StudentId']:
                    if i.__dict__.get('End_Course') is None:
                        i.End_Course ={
                            # COURSE:j['LastTime']
                           COURSE: datetime.strptime(str(j['LastTime']).split('.')[0], "%Y-%m-%d %H:%M:%S") 
                        }
                    else:
                        i.End_Course.update({ COURSE: datetime.strptime(str(j['LastTime']).split('.')[0], "%Y-%m-%d %H:%M:%S") })
                    i.save()
                # else:
                #     if i.__dict__.get('End_Course') is None:
                #         i.End_Course ={
                #             COURSE:STARTTIMES.get(COURSE).get('Start') if COURSE != 'HTMLCSS' and COURSE != 'HTML' and COURSE != 'CSS' and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('End')
                #         }
                #     else:
                #         i.End_Course.update({
                #         COURSE:datetime.strptime(str(i.Start_Course.get(COURSE,None)).split('.')[0], "%Y-%m-%d %H:%M:%S") if i.Start_Course.get(COURSE,None) is not None else STARTTIMES.get(COURSE).get('Start') if COURSE != 'HTMLCSS'  and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('End')
                #             })
                #     i.save()
                # else:
                #         print('Not found',i.Student_id,j['StudentId'])
        
        
        maxscore = filterQueryMaxValueScore(std_days_all,COURSE)
        maxdelay1 = filterQueryMaxdelay(std_days_all,COURSE)
        # print(COURSE)
        if COURSE == 'HTMLCSS' or COURSE == 'HTML' or COURSE == 'CSS' :
            COURSE = 'HTMLCSS'
            # maxdelay = (STARTTIMES.get(COURSE).get('End')-datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")).total_seconds()/60*60
            maxdelay = (datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")-STARTTIMES.get(COURSE).get('End')).total_seconds()/60*60
        elif COURSE == 'Java_Script' :
            # maxdelay = (STARTTIMES.get(COURSE).get('End')-datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")).total_seconds()/60*60
            maxdelay = (datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")-STARTTIMES.get(COURSE).get('End')).total_seconds()/60*60
        else:
            # maxdelay =  (STARTTIMES.get(COURSE).get('Start')-datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")).total_seconds()/60*60
            maxdelay = (datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")-STARTTIMES.get(COURSE).get('Start')).total_seconds()/60*60

        for user in std_days_all:
            if str(user.Student_id)[2:].startswith("ADMI") or str(user.Student_id)[2:].startswith("TRAI") or str(user.Student_id)[2:].startswith("TEST"):
                continue
            if COURSE == 'HTMLCSS' or COURSE == 'Java_Script':
                if user.Qns_lists.get(COURSE) is None:
                    user.Qns_lists.update({COURSE:[]})
                    user.Ans_lists.update({COURSE:[]})
                    user.Score_lists.update({COURSE:0})
                if len(user.Qns_lists.get(COURSE,[]) ) == len(user.Ans_lists.get(COURSE if COURSE != 'HTMLCSS' else 'HTML',[]) ) and len(user.Qns_lists.get(COURSE,[]) )  > 0:
                    if COURSE == 'HTMLCSS' or COURSE == 'HTML' or COURSE == 'CSS':
                        userScore = (float(str(user.Score_lists.get("HTMLScore",0)).split('/')[0])+float(str(user.Score_lists.get("CSSScore",0)).split('/')[0]))
                    else:
                        userScore = float(str(user.Score_lists.get(str(COURSE)+'Score',0)).split('/')[0])
                    userDelay = user.End_Course.get(COURSE) if user.End_Course.get(COURSE) is not None else user.Start_Course.get(COURSE,STARTTIMES.get(COURSE).get('Start') if COURSE != 'HTMLCSS' and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('End'))
            else:
                    userScore = float(str(user.Score_lists.get(str(COURSE)+'Score',0)).split('/')[0])
                    userDelay = user.End_Course.get(COURSE) if user.End_Course.get(COURSE) is not None else user.Start_Course.get(COURSE,STARTTIMES.get(COURSE).get('Start') if COURSE != 'HTMLCSS' and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('End'))


            startdate = STARTTIMES.get(COURSE).get('Start') if COURSE != 'HTMLCSS' and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('End')
            delay =(datetime.strptime(str(userDelay).split('.')[0], "%Y-%m-%d %H:%M:%S")-startdate).total_seconds()/60*60
            # print('delay',delay,'maxdelay',maxdelay,'userScore',userScore,'maxscore',maxscore,'COURSE',COURSE,'startdate',startdate,'userDelay',userDelay,'delay',)
            if delay < 0:
                delay = 0
            if  maxdelay == 0:  
                Scorevalue = (0.8 * (userScore/maxscore))-0
            else:
                Scorevalue = (0.8 * (userScore/maxscore))-( (0.2) * (delay/maxdelay))
            new_ranks.append({
                'StudentId':user.Student_id,
                'Score':Scorevalue,
                'Course':COURSE,
                'DateTime':userDelay,
                'userScore':userScore,
                'delay':(datetime.strptime(str(userDelay).split('.')[0], "%Y-%m-%d %H:%M:%S")-startdate).days
            })
        new_ranks = sorted(new_ranks, key=lambda x: x['Score'], reverse=True)
        for i in new_ranks:
            i['Rank'] = new_ranks.index(i)+1
            print(i.get('Rank'),'\t',i.get('StudentId'),'\t',i.get('Score'),'\t',i.get('Course'),'\t',i.get('DateTime'),'\t',i.get('userScore'),'\t',i.get('delay'))
         
        oldranks = Rankings.objects.filter(Course = COURSE).order_by('-Rank')
        new_rankings = []
        if  len(oldranks) > 0:
            for i in oldranks:
                i.delete()
        for i in new_ranks:
            r = Rankings.objects.create(
                StudentId = i.get('StudentId'),
                Rank = i.get('Rank'),
                Course = i.get('Course'),
                Score = i.get('Score'),
                DateTime = i.get('DateTime'),
                Delay = (i.get('delay')),
            ) 
            if r is not None:
                new_rankings.append(  r)
        return new_rankings
    except Exception as e:
        print(e) 
        return  'An error occurred  :'+str(e) 

def getRankings(COURSE,SID):
    try:
        userRank = Rankings.objects.filter(Course = COURSE,StudentId = SID).first()
        if userRank is not None:
            return userRank.Rank
        else:
            return 'N/A'
    except Exception as e:
        print(e)

def rankings(allusers,COURSE):
    try:
        allmainQns = QuestionDetails_Days.objects.all()
        ranks = allusers
        if ranks is None:
            HttpResponse('No data found')
        out ={}
        noDAta = []
        for i in ranks:
         if str(i.get('StudentId'))[2:].startswith("ADMI") or str(i.get('StudentId'))[2:].startswith("TRAI") or str(i.get('StudentId'))[2:].startswith("TEST"):
            continue
         user = filterQuery(allmainQns, 'Student_id',  i.get('StudentId'))
         if user is None:
            noDAta.append(i.get('StudentId'))
            continue
         if COURSE == 'HTMLCSS' or COURSE == 'HTML' or COURSE == 'CSS'  :
                HTML = filterQueryfromdict(user, 'Subject',  'HTML')
                CSS = filterQueryfromdict(user, 'Subject',  'CSS')
                if HTML is None  or len(HTML) == 0  :
                    noDAta.append(i.get('StudentId'))
                    # print(i.get('StudentId'))
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
                
                out.update({i.get('StudentId'): {
                    "HTMLCSS":   HTMLCSSSCORE,
                    'HTML_last_Question':   HTMLLASTTIME,
                }})
         elif COURSE == 'Java_Script' or COURSE == 'JavaScript' :
                JS = filterQueryfromdict(user, 'Subject',  'Java_Script')
                if JS is None  or len(JS) == 0  :
                    noDAta.append(i.get('StudentId'))
                    # print(i.get('StudentId'))
                    continue
                JSSCORE =0
                JSLASTTIME = JS[0].get('DateAndTime')
                for i1 in JS:
                    # print(i)
                    JSSCORE += i1.get('Score')
                    if i1.get('DateAndTime') > JSLASTTIME:
                        JSLASTTIME = i1.get('DateAndTime')
                out.update({i.get('StudentId'): {
                    "HTMLCSS":   JSSCORE,
                    'HTML_last_Question':   JSLASTTIME,
                }})
         else:
                coursedata = filterQueryfromdict(user, 'Subject',  COURSE)
                if coursedata is None  or len(coursedata) == 0  :
                    noDAta.append(i.get('StudentId'))
                    # print(i.get('StudentId'))
                    continue
                SCORE =0
                LASTTIME = coursedata[0].get('DateAndTime')
                for i1 in coursedata:
                    # print(i)
                    SCORE += i1.get('Score')
                    if i1.get('DateAndTime') > LASTTIME:
                        LASTTIME = i1.get('DateAndTime') 
                out.update({i.get('StudentId'): {
                    "HTMLCSS":   SCORE,
                    'HTML_last_Question':   LASTTIME,
                }})
        ranks = sorted(    out.items(),     key=lambda x: (-x[1]['HTMLCSS'], x[1]['HTML_last_Question']))  
        res = []
        for i in ranks:
                res.append({'Rank':ranks.index(i)+1,"StudentId":i [0],"Total":i[1]['HTMLCSS'], "LastTime":i[1]['HTML_last_Question']})
                # print({'Rank':ranks.index(i)+1,"StudentId":i [0], "LastTime":i[1]['HTML_last_Question'],"Total":i[1]['HTMLCSS']})
        return res
    except Exception as e:
        print(e)
        return  'An error occurred'+str(e)
    
def  OverallRankings(COURSEs,SID):#COURSEs = ["HTMLCSS", "Java_Script"] , SID = "24ADMI0001"
    try:
        aggregate_scores = Rankings.objects.filter(Course__in=COURSEs).values('StudentId').annotate(total_score=Sum('Score')).order_by('-total_score')
        rank = 1
        for student_score in aggregate_scores:
            if student_score['StudentId'] == SID:
                # print('Rank',rank,f"Student: {student_score['StudentId']}, Total Score: {student_score['total_score']}")
                return  rank
            # else:
            #       print('Rank',rank,f"Student: {student_score['StudentId']}, Total Score: {student_score['total_score']}")
            rank += 1
        return  'N/A'
    except Exception as e:
        print(e)
        return  'An error occurred'+str(e)
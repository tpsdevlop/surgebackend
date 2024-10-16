from django.http import JsonResponse
from collections import defaultdict
from datetime import timedelta, datetime
from django.utils.timezone import now
 
from .models import Attendance, BugDetails
 
def get_bugs_reported_by_period(request, period):
    start_date = None
    current_date = now().date()  # Get today's date for filtering
 
    if period == 'week':
        start_date = current_date - timedelta(weeks=1)
    elif period == 'month':
        start_date = current_date - timedelta(weeks=4)
    elif period == 'months':
        start_date = current_date - timedelta(days=365)
 
    # Fetch bugs reported after the start date and up to the current date
    bugs_reported = BugDetails.objects.filter(Reported__gte=start_date, Reported__lte=current_date)
 
    if period in ['week', 'month']:
        weekly_data = defaultdict(int)
        for bug in bugs_reported:
            # Get the start of the week (Monday)
            week_start = bug.Reported - timedelta(days=bug.Reported.weekday())
            if week_start.date() <= current_date:  # Ensure week_start is not in the future
                weekly_data[week_start.date()] += 1
 
        return JsonResponse([{'week_start': str(week), 'total': total} for week, total in weekly_data.items()], safe=False)
 
    elif period == 'months':
        monthly_data = defaultdict(int)
        for bug in bugs_reported:
            # Get the start of the month
            month_start = datetime(bug.Reported.year, bug.Reported.month, 1)
            if month_start.date() <= current_date:  # Ensure month_start is not in the future
                monthly_data[month_start] += 1
 
        return JsonResponse([{'month_start': str(month), 'total': total} for month, total in monthly_data.items()], safe=False)
 
def get_bug_count(request):
    if request.method == 'GET':
        total_bugs = BugDetails.objects.count()
        return JsonResponse({"total_bugs": total_bugs}, status=200)
 
 
def get_bugs_resolved_by_period(request, period):
    start_date = None
    current_date = now().date()  # Get today's date for filtering
 
    if period == 'week':
        start_date = current_date - timedelta(weeks=1)
    elif period == 'month':
        start_date = current_date - timedelta(weeks=4)
    elif period == 'months':
        start_date = current_date - timedelta(days=365)
 
    # Fetch bugs resolved after the start date and up to the current date
    bugs_resolved = BugDetails.objects.filter(Resolved__gte=start_date, Resolved__lte=current_date)
 
    if period in ['week', 'month']:
        weekly_data = defaultdict(int)
        for bug in bugs_resolved:
            # Ensure bug.Resolved is a datetime object
            resolved_date = bug.Resolved
 
            # Check if resolved_date is a datetime
            if isinstance(resolved_date, int):  # Check if it's an integer (timestamp)
                resolved_date = datetime.fromtimestamp(resolved_date)  # Convert to datetime
            elif not isinstance(resolved_date, datetime):  # Ensure it's a datetime object
                continue  # Skip if it's neither
 
            # Get the start of the week (Monday)
            week_start = resolved_date - timedelta(days=resolved_date.weekday())
            if week_start.date() <= current_date:  # Ensure week_start is not in the future
                weekly_data[week_start.date()] += 1
 
        return JsonResponse([{'week_start': str(week), 'total': total} for week, total in weekly_data.items()], safe=False)
 
    elif period == 'months':
        monthly_data = defaultdict(int)
        for bug in bugs_resolved:
            # Ensure bug.Resolved is a datetime object
            resolved_date = bug.Resolved
 
            # Check if resolved_date is a datetime
            if isinstance(resolved_date, int):  # Check if it's an integer (timestamp)
                resolved_date = datetime.fromtimestamp(resolved_date)  # Convert to datetime
            elif not isinstance(resolved_date, datetime):  # Ensure it's a datetime object
                continue  # Skip if it's neither
 
            # Get the start of the month
            month_start = datetime(resolved_date.year, resolved_date.month, 1)
            if month_start.date() <= current_date:  # Ensure month_start is not in the future
                monthly_data[month_start] += 1
 
        return JsonResponse([{'month_start': str(month), 'total': total} for month, total in monthly_data.items()], safe=False)
   
def get_active_users(request):
    # Get the 'period' parameter from the query string (default to '1')
    period = request.GET.get('period', '1')  # Default to last week if not provided
 
    # Calculate the date range based on the period
    datenow = now().date()
 
    if period == '1':  # Last week
        start_date = datenow - timedelta(weeks=1)  # Last 7 days
    elif period == '2':  # Last month
        start_date = datenow - timedelta(days=30)
    elif period == '3':
        start_date = datenow - timedelta(days=60)  # Last 30 days
    else:
        return JsonResponse({'error': 'Invalid period. Use "1" for week or "2" for month.'}, status=400)
 
    # Fetch the attendance data from the Attendance collection
    attendance_records = Attendance.objects.filter(
        Login_time__lte=datenow,
        Last_update__gte=start_date
    )
 
    # Count active users by date
    active_user_count = defaultdict(set)  # Using a set to avoid duplicates
 
    for record in attendance_records:
        last_update_date = record.Last_update.date()  # Get the date part
        active_user_count[last_update_date].add(record.SID)  # Add the student ID to the set
 
    # Prepare the result for JSON response
    result = [{'day': str(day), 'active_users': len(users)} for day, users in active_user_count.items()]
    result.sort(key=lambda x: x['day'])  # Sort by day
 
    return JsonResponse(result, safe=False)
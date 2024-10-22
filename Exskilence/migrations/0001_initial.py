# Generated by Django 4.1.13 on 2024-10-21 11:39

from django.db import migrations, models
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('Login_id', models.AutoField(primary_key=True, serialize=False)),
                ('SID', models.CharField(max_length=15)),
                ('Login_time', models.DateTimeField()),
                ('Last_update', models.DateTimeField()),
                ('Status', models.TextField(default='in')),
                ('Duration', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='BugDetails',
            fields=[
                ('sl_id', models.AutoField(primary_key=True, serialize=False)),
                ('Student_id', models.CharField(max_length=25)),
                ('Img_path', models.TextField()),
                ('BugDescription', models.TextField()),
                ('BugStatus', models.CharField(default='Pending', max_length=50)),
                ('Issue_type', models.CharField(max_length=50)),
                ('Reported', models.DateTimeField()),
                ('Resolved', models.DateTimeField(null=True)),
                ('Comments', djongo.models.fields.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Chatbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Message_Id', models.CharField(max_length=5)),
                ('From_User', models.CharField(max_length=100)),
                ('To_User', models.CharField(max_length=100)),
                ('Timestamp', models.DateTimeField()),
                ('Subject', models.CharField(max_length=100)),
                ('Content', models.TextField()),
                ('Seen', models.BooleanField(default=False)),
                ('Attachments', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('hiringManager', 'Hiring Manager'), ('volunteer', 'Volunteer')], max_length=50)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('designation', models.CharField(blank=True, max_length=255)),
                ('contactNumber', models.CharField(blank=True, max_length=20)),
                ('company', models.CharField(blank=True, max_length=255)),
                ('loc', models.CharField(blank=True, max_length=255)),
                ('openings', models.CharField(blank=True, max_length=255)),
                ('employmentType', models.CharField(blank=True, max_length=50)),
                ('duration', models.CharField(blank=True, max_length=50)),
                ('hasBond', models.CharField(blank=True, max_length=10)),
                ('bondDuration', models.CharField(blank=True, max_length=50)),
                ('packageInLPA', models.CharField(blank=True, max_length=50)),
                ('comments', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CourseDetails',
            fields=[
                ('SubjectId', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('SubjectName', models.CharField(max_length=20)),
                ('path', models.CharField(max_length=500)),
                ('Discription', models.CharField(default='', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='CoursePackages',
            fields=[
                ('CourseId', models.CharField(max_length=9, primary_key=True, serialize=False)),
                ('CourseName', models.CharField(max_length=20)),
                ('CourseDescription', models.CharField(max_length=500)),
                ('Price', models.IntegerField()),
                ('Course_content', djongo.models.fields.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='ErrorLogs',
            fields=[
                ('Error_id', models.AutoField(primary_key=True, serialize=False)),
                ('StudentId', models.CharField(max_length=15)),
                ('Email', models.EmailField(max_length=254)),
                ('Name', models.CharField(max_length=25)),
                ('Occrued_time', models.DateTimeField()),
                ('Error_msg', models.TextField()),
                ('Stack_trace', models.TextField()),
                ('User_agent', models.TextField()),
                ('Operating_sys', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='InternshipDetails',
            fields=[
                ('sl_id', models.AutoField(primary_key=True, serialize=False)),
                ('Student_id', models.CharField(max_length=25)),
                ('Name', models.CharField(max_length=55)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('Project_name', models.CharField(max_length=50)),
                ('HTML_Code', djongo.models.fields.JSONField(default=dict)),
                ('HTML_Score', djongo.models.fields.JSONField(default=dict)),
                ('CSS_Code', djongo.models.fields.JSONField(default=dict)),
                ('CSS_Score', djongo.models.fields.JSONField(default=dict)),
                ('JS_Code', djongo.models.fields.JSONField(default=dict)),
                ('JS_Score', djongo.models.fields.JSONField(default=dict)),
                ('Python_Code', djongo.models.fields.JSONField(default=dict)),
                ('Python_Score', djongo.models.fields.JSONField(default=dict)),
                ('AppPy_Code', djongo.models.fields.JSONField(default=dict)),
                ('AppPy_Score', djongo.models.fields.JSONField(default=dict)),
                ('Database_Code', djongo.models.fields.JSONField(default=dict)),
                ('Database_Score', djongo.models.fields.JSONField(default=dict)),
                ('Score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Login',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=5)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('timestamp', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='login_data',
            fields=[
                ('User_ID', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('User_name', models.CharField(max_length=25)),
                ('User_emailID', models.EmailField(max_length=254, unique=True)),
                ('User_catagory', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionDetails_Days',
            fields=[
                ('sl_no', models.AutoField(primary_key=True, serialize=False)),
                ('Student_id', models.CharField(max_length=25)),
                ('Subject', models.CharField(max_length=25)),
                ('Attempts', models.IntegerField()),
                ('DateAndTime', models.DateTimeField()),
                ('Score', models.FloatField()),
                ('Qn', models.TextField(max_length=25)),
                ('Ans', models.TextField()),
                ('Result', djongo.models.fields.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Rankings',
            fields=[
                ('Rank_id', models.AutoField(primary_key=True, serialize=False)),
                ('StudentId', models.CharField(max_length=15)),
                ('Rank', models.IntegerField()),
                ('Course', models.CharField(max_length=100)),
                ('Score', models.FloatField()),
                ('DateTime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='StudentDetails',
            fields=[
                ('StudentId', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('firstName', models.CharField(max_length=20)),
                ('lastName', models.CharField(max_length=20)),
                ('college_Id', models.CharField(max_length=20)),
                ('CollegeName', models.CharField(max_length=20)),
                ('Center', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('whatsApp_No', models.IntegerField()),
                ('mob_No', models.IntegerField()),
                ('sem', models.CharField(max_length=3)),
                ('branch', models.CharField(max_length=10)),
                ('status', models.CharField(max_length=3)),
                ('user_category', models.CharField(max_length=3)),
                ('reg_date', models.DateField()),
                ('exp_date', models.DateField()),
                ('score', models.FloatField()),
                ('progress_Id', djongo.models.fields.JSONField(default=dict)),
                ('Assignments_test', djongo.models.fields.JSONField(default=dict)),
                ('Courses', djongo.models.fields.JSONField(default=list)),
                ('Course_Time', djongo.models.fields.JSONField(default=dict)),
                ('CGPA', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='StudentDetails_Days_Questions',
            fields=[
                ('Student_id', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('Days_completed', djongo.models.fields.JSONField(default=dict)),
                ('Qns_lists', djongo.models.fields.JSONField(default=dict)),
                ('Qns_status', djongo.models.fields.JSONField(default=dict)),
                ('Ans_lists', djongo.models.fields.JSONField(default=dict)),
                ('Score_lists', djongo.models.fields.JSONField(default=dict)),
                ('Start_Course', djongo.models.fields.JSONField(default=dict)),
                ('End_Course', djongo.models.fields.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('profileimage', models.TextField()),
                ('name', models.CharField(max_length=100)),
                ('college', models.TextField()),
                ('branch', models.CharField(max_length=100)),
                ('contact', models.CharField(max_length=10)),
                ('emailid', models.EmailField(max_length=100)),
                ('cgpa', models.FloatField(blank=True, null=True)),
                ('skills', models.TextField()),
                ('otherskills', models.TextField()),
                ('entranceTest', models.CharField(max_length=10)),
                ('python', models.CharField(max_length=10)),
                ('sql', models.CharField(max_length=10)),
                ('dsa', models.CharField(max_length=10)),
                ('aptitude', models.CharField(max_length=10)),
                ('rank', models.IntegerField()),
                ('resumeLink', models.TextField()),
                ('communicationVideo', models.TextField()),
                ('hackerrankLink', models.TextField()),
                ('leetcodeLink', models.TextField()),
                ('githubLink', models.TextField()),
                ('isSelected', models.BooleanField(default=False)),
                ('financialaid', models.TextField()),
                ('placed', models.TextField(default='No')),
            ],
        ),
        migrations.CreateModel(
            name='Switches',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Key', models.CharField(max_length=100)),
                ('Value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='userdetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userID', models.CharField(max_length=100, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('category', models.CharField(default='', max_length=100)),
                ('expiry_date', models.DateField()),
                ('status', models.CharField(max_length=50)),
                ('register_date', models.DateField(auto_now_add=True)),
                ('firstName', models.CharField(max_length=20)),
                ('lastName', models.CharField(max_length=20)),
            ],
        ),
    ]

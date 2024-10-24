import base64
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from .models import *
from rest_framework import viewsets
from rest_framework.response import Response
import json
from rest_framework.decorators import api_view
from .filters import *

from Exskilencebackend160924.Blob_service import *
from Exskilencebackend160924.settings import *
  
@api_view(['POST'])
def chatbox(request):
    try:
        data = json.loads(request.body)
        from_user = data.get('From')
        to_users = data.get('To')  # 'To' is an array of student IDs
        Subject = data.get('Subject')
        Content = data.get('Content')
        # Attachments = data.get('Attachments')
        
        created_messages = []
        all_data = Chatbox.objects.all()

        # Find the current maximum Message_Id
        max_message_data = filterQueryOrderby(all_data, 'Message_Id', True)
        if len(max_message_data) != 0:
            maxId = int(max_message_data[0]['Message_Id'])
        else:
            maxId = 0  # Start with 0 if no messages exist
        
        for to_user in to_users:
            # Check if there's already a conversation between from_user and to_user
            filtered_data = filterQueryandv1v2(all_data, 'From_User', from_user, 'To_User', to_user)
            
            # Create a new message with incremented Message_Id if no prior conversation exists
            if len(filtered_data) == 0:
                new_message_id = str(maxId + 1)  # Increment the Message_Id for each new message
                
                # Handle file upload for each message
                res = file_upload(request, new_message_id)
                if res.get('message') == 'File uploaded successfully':
                    new_message = Chatbox.objects.create(
                        Message_Id=new_message_id,
                        From_User=from_user,
                        To_User=to_user,  # Create a separate message for each 'To_User'
                        Subject=Subject,
                        Content=Content,
                        Timestamp=datetime.utcnow().__add__(timedelta(hours=5, minutes=30)),
                        # Attachments=Attachments
                    )
                    created_messages.append(new_message)
                    maxId += 1  # Increment maxId for the next message
                else:
                    return HttpResponse(json.dumps({"data": res}), content_type='application/json')
            else:
                # Use the existing Message_Id if a conversation exists
                existing_message_id = filtered_data[0]['Message_Id']
                existing_message = Chatbox.objects.create(
                    Message_Id=existing_message_id,
                    From_User=from_user,
                    To_User=to_user,
                    Subject=Subject,
                    Content=Content,
                    Timestamp=datetime.utcnow().__add__(timedelta(hours=5, minutes=30)),
                    # Attachments=Attachments
                )
                created_messages.append(existing_message)
        
        # Prepare the response with all created messages
        response_data = [{
            'id': message.id,
            'Message_Id': message.Message_Id,
            'From_User': message.From_User,
            'To_User': message.To_User,
            'Subject': message.Subject,
            'Content': message.Content,
            'Timestamp': str(message.Timestamp),
            # 'Attachments': message.Attachments
        } for message in created_messages]

        return HttpResponse(json.dumps({"data": response_data}), content_type='application/json')

    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({"error": str(e)}), content='application/json', status=500)
 




    
@api_view(['POST'])
def file_upload(request):
    try:
        if 'file' not in request.FILES:
            print('no file', request.FILES.get('file') )
            return HttpResponse(json.dumps({"message": "No file provided"}), content_type='application/json', status=400)
        if 'From' not in request.POST:
            return HttpResponse(json.dumps({"message": "No From provided"}), content_type='application/json', status=400)
        if 'To' not in request.POST:
            return HttpResponse(json.dumps({"message": "No To provided"}), content_type='application/json', status=400)
        from_user = request.POST['From']
        to_user = request.POST['To']
        all_data = Chatbox.objects.all()
        if all_data:
            filtered_data = filterQueryandv1v2 (all_data, 'From_User', from_user , 'To_User', to_user)
            if len(filtered_data) == 0:
                maxId = filterQueryOrderby(all_data, 'Message_Id', True)
                if len(maxId) != 0:
                    maxId = maxId[0]['Message_Id']
                else:
                    maxId = 0
            else:
                maxId = filtered_data[0]['Message_Id']
        else:
            maxId = 0
        Message_Id = str(int(maxId) + 1)      
        file = request.FILES['file']
        print(('file', file))
        file_type = file.content_type.split('/')[0]
        blob_path = f'Chatbox/{Message_Id}/{file_type}/[{str(datetime.utcnow().__add__(timedelta(hours=5, minutes=30))).replace(" ", "_")}]{file.name}'
        blob_client = get_blob_service_client().get_blob_client(container=AZURE_CONTAINER, blob=blob_path)
        blob_client.upload_blob(file, overwrite=True)
        image_base64 = None
        if file_type == 'image':
            blob_data = blob_client.download_blob().readall()
            image_base64 = base64.b64encode(blob_data).decode('utf-8')
        response_data = {
            "message": "File uploaded successfully",
            "file_url": blob_client.url,
            'Message_Id': Message_Id
        }
 
 
        return  HttpResponse(json.dumps(response_data), content_type='application/json')
   
    except Exception as e:
        print(e)
        return HttpResponse({"error": str(e)}, status= 500)
   

@api_view(['POST'])
def send_email(request):
    if request.method == 'POST':
        try:
            print("Received POST request.")
            data = json.loads(request.POST['data'])
            from_user = data.get('From')
            to_users = data.get('To')
            Subject = data.get('Subject')
            Content = data.get('Content')
            all_data = Chatbox.objects.all()
            file = request.FILES.get('file')  # Ensure you have the file object
            responses = []

            # Retrieve the current max Message_Id from all messages at the start
            maxId = filterQueryOrderby(all_data, 'Message_Id', True)
            current_max_id = int(maxId[0]['Message_Id']) if maxId else 0

            for to in to_users:
                print(f"Processing user: {to}")
                timestamp = datetime.utcnow() + timedelta(hours=5, minutes=30)
                timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

                # Log request method
                print(f"Request method for user {to}: {request.method}")

                # Check for existing messages
                filtered_data = filterQueryandv1v2(all_data, 'From_User', from_user, 'To_User', to)

                if len(filtered_data) > 0:
                    # Existing message found, reuse the Message_Id
                    mid = filtered_data[0]['Message_Id']
                    message_id = mid
                    print('Reusing existing Message_Id:', mid)
                else:
                    # New message, generate a unique Message_Id
                    message_id = str(current_max_id + 1)
                    current_max_id += 1  # Increment for the next message ID
                    print('New Message_Id generated:', message_id)

                # Handle attachments for each user
                Attachments = ''
                if file:
                    res = uploasAttachment(request, message_id)  # Attempt to upload for each user
                    if res.get('error'):
                        print(f"Attachment error for user {to}: {res.get('error')}")
                        return HttpResponse(json.dumps({"data": res}), content_type='application/json', status=400)
                    Attachments = res.get('url')
                    print('Attachment uploaded:', Attachments)

                # Create the message
                newdata = Chatbox.objects.create(
                    Message_Id=message_id,
                    From_User=from_user,
                    To_User=to,
                    Subject=Subject,
                    Content=Content,
                    Timestamp=timestamp,
                    Attachments=Attachments
                )

                # Log message creation
                print(f"Message created for user {to}: {newdata.id}")

                # Get recipient's name
                to_user_name = StudentDetails.objects.filter(StudentId=to).values_list('firstName', 'lastName').first()
                to_user_full_name = f"{to_user_name[0]} {to_user_name[1]}" if to_user_name else "Unknown User"
                out = {
                    'id': newdata.id,
                    'Message_Id': newdata.Message_Id,
                    'From_User': newdata.From_User,
                    'To_User': newdata.To_User,
                    'Subject': newdata.Subject,
                    'Content': newdata.Content,
                    'Timestamp': timestamp_str,
                    'Attachments': newdata.Attachments,
                    'name': to_user_full_name
                }
                responses.append(out)

            print("All messages processed successfully.")
            return HttpResponse(json.dumps({"data": responses}), content_type='application/json')

        except Exception as e:
            print('Error:', e)
            return HttpResponse(json.dumps({"error": str(e)}), content_type='application/json', status=500)
    else:
        print("Method Not Allowed")
        return HttpResponse(status=405)  # Method Not Allowed


@api_view(['POST'])
def send_email_to_tutor(request):
    if request.method == 'POST':
        try:
            print("Received POST request.")
            data = json.loads(request.POST['data'])
            from_user = data.get('From')
            to_users = data.get('To')
            Subject = data.get('Subject')
            Content = data.get('Content')
            all_data = Chatbox.objects.all()
            file = request.FILES.get('file')  # Ensure you have the file object
            responses = []

            # Retrieve the current max Message_Id from all messages at the start
            maxId = filterQueryOrderby(all_data, 'Message_Id', True)
            current_max_id = int(maxId[0]['Message_Id']) if maxId else 0

            for to in to_users:
                print(f"Processing user: {to}")
                timestamp = datetime.utcnow() + timedelta(hours=5, minutes=30)
                timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

                # Log request method
                print(f"Request method for user {to}: {request.method}")

                # Check for existing messages
                filtered_data = filterQueryandv1v2(all_data, 'From_User', from_user, 'To_User', to)

                if len(filtered_data) > 0:
                    # Existing message found, reuse the Message_Id
                    mid = filtered_data[0]['Message_Id']
                    message_id = mid
                    print('Reusing existing Message_Id:', mid)
                else:
                    # New message, generate a unique Message_Id
                    message_id = str(current_max_id + 1)
                    current_max_id += 1  # Increment for the next message ID
                    print('New Message_Id generated:', message_id)

                # Handle attachments for each user
                Attachments = ''
                if file:
                    res = uploasAttachment(request, message_id)  # Attempt to upload for each user
                    if res.get('error'):
                        print(f"Attachment error for user {to}: {res.get('error')}")
                        return HttpResponse(json.dumps({"data": res}), content_type='application/json', status=400)
                    Attachments = res.get('url')
                    print('Attachment uploaded:', Attachments)

                # Create the message
                newdata = Chatbox.objects.create(
                    Message_Id=message_id,
                    From_User=from_user,
                    To_User=to,
                    Subject=Subject,
                    Content=Content,
                    Timestamp=timestamp,
                    Attachments=Attachments
                )

                # Log message creation
                print(f"Message created for user {to}: {newdata.id}")

                # Get recipient's name
                to_user_name = userdetails.objects.filter(userID=to).values_list('firstName', 'lastName').first()
                to_user_full_name = f"{to_user_name[0]} {to_user_name[1]}" if to_user_name else "Unknown User"
                out = {
                    'id': newdata.id,
                    'Message_Id': newdata.Message_Id,
                    'From_User': newdata.From_User,
                    'To_User': newdata.To_User,
                    'Subject': newdata.Subject,
                    'Content': newdata.Content,
                    'Timestamp': timestamp_str,
                    'Attachments': newdata.Attachments,
                    'name': to_user_full_name
                }
                responses.append(out)

            print("All messages processed successfully.")
            return HttpResponse(json.dumps({"data": responses}), content_type='application/json')

        except Exception as e:
            print('Error:', e)
            return HttpResponse(json.dumps({"error": str(e)}), content_type='application/json', status=500)
    else:
        print("Method Not Allowed")
        return HttpResponse(status=405)  # Method Not Allowed


# def send_email_to_tutor(request):
#     try:
#         print("got the data")
#         print(request.POST)
#         data = json.loads(request.POST['data'])
#         from_user = data.get('From')
#         to_user = data.get('To')
#         Subject = data.get('Subject')
#         Content = data.get('Content')
#         all_data = Chatbox.objects.all()
#         file = request.FILES.get('file')
#         if all_data:
#             timestamp = datetime.utcnow() + timedelta(hours=5, minutes=30)
#             timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"  # Format to ISO 8601

#             filtered_data = filterQueryandv1v2 (all_data, 'From_User', from_user , 'To_User', to_user)
#             if len(filtered_data) == 0:
#                 maxId = filterQueryOrderby(all_data, 'Message_Id', True)
#                 if len(maxId) != 0:
#                     maxId = maxId[0]['Message_Id']
#                 else:
#                     maxId = 0
#                 if file:
#                     res =uploasAttachment(request, str(int(maxId) + 1))
#                     if res.get('error'):
#                         return HttpResponse(json.dumps({"data": res}), content_type='application/json')
#                     Attachments = res.get('url')
#                 else:
#                     Attachments = ''
               
#                 newdata = Chatbox.objects.create(Message_Id=str(int(maxId) + 1),
#                                                       From_User=from_user,
#                                                       To_User=to_user,
#                                                       Subject=Subject,
#                                                       Content=Content,
#                                                       Timestamp=timestamp,
#                                                       Attachments=Attachments
#                                                       )
#                 to_user_name = userdetails.objects.filter(userID=to_user).values_list('firstName', 'lastName').first()
#                 to_user_full_name = f"{to_user_name[0]} {to_user_name[1]}" if to_user_name else "Unknown User"
#                 out  ={
#                         'id': newdata.id,
#                         'Message_Id': newdata.Message_Id,
#                         'From_User': newdata.From_User,
#                         'To_User': newdata.To_User,
#                         'Subject': newdata.Subject,
#                         'Content': newdata.Content,
#                         'Timestamp': timestamp_str,
#                         'Attachments': newdata.Attachments,
#                         'name': to_user_full_name
#                     }
#                 return HttpResponse(json.dumps({"data": out}), content_type='application/json')            
#             else:
#                 mid = filtered_data[0]['Message_Id']
#                 if file:
#                     res =uploasAttachment(request, str(int(mid) ))
#                     if res.get('error'):
#                         return HttpResponse(json.dumps({"data": res}), content_type='application/json')
#                     Attachments = res.get('url')
#                 else:
#                     Attachments = ''
#                 olddata = Chatbox.objects.create(
#                     Message_Id=mid,
#                     From_User=from_user,
#                     To_User=to_user,
#                     Subject=Subject,
#                     Content=Content ,
#                     Timestamp=timestamp,
#                     Attachments=Attachments
#                     )
#                 to_user_name = userdetails.objects.filter(userID=to_user).values_list('firstName', 'lastName').first()
#                 to_user_full_name = f"{to_user_name[0]} {to_user_name[1]}" if to_user_name else "Unknown User"
#                 out  ={
#                     'id': olddata.id,
#                     'Message_Id': olddata.Message_Id,
#                     'From_User': olddata.From_User,
#                     'To_User': olddata.To_User,
#                     'Subject': olddata.Subject,
#                     'Content': olddata.Content,
#                     'Timestamp': timestamp_str,
#                     'Attachments': olddata.Attachments,
#                     'name': to_user_full_name
#                 }
#                 return HttpResponse(json.dumps({"data": out}), content_type='application/json')
#         if file:
#             res =uploasAttachment(request,  1)
#             if res.get('error'):
#                 return HttpResponse(json.dumps({"data": res}), content_type='application/json')
#             Attachments = res.get('url')
#         else:
#             Attachments = ''
#         newdata = Chatbox.objects.create(
#             Message_Id=1,
#             From_User=from_user,
#             To_User=to_user,
#             Subject=Subject,
#             Content=Content ,
#             Timestamp=datetime.utcnow().__add__(timedelta(hours=5, minutes=30) ),
#             Attachments=Attachments)
#         to_user_name = userdetails.objects.filter(userID=to_user).values_list('firstName', 'lastName').first()
#         to_user_full_name = f"{to_user_name[0]} {to_user_name[1]}" if to_user_name else "Unknown User"
                
#         out  ={
#             'id': newdata.id,
#             'Message_Id': newdata.Message_Id,
#             'From_User': newdata.From_User,
#             'To_User': newdata.To_User,
#             'Subject': newdata.Subject,
#             'Content': newdata.Content,
#             'Timestamp': datetime.utcnow().__add__(timedelta(hours=5, minutes=30) ),
#             'Attachments': newdata.Attachments,
#             'name':to_user_full_name
#         }
#         return HttpResponse(json.dumps({"data": out}), content='application/json')
#     except Exception as e:
#         print(e)
#         return HttpResponse(json.dumps({"error": str(e)}),content='application/json', status= 500)


def uploasAttachment(req, message_id):
    try:
        file = req.FILES.get('file')
        if not file:
            raise ValueError("No file found in request.")
        
        file_type = file.content_type.split('/')[0]
        timestamp_str = datetime.utcnow().__add__(timedelta(hours=5, minutes=30)).strftime("%Y%m%d_%H%M%S")
        blob_path = f'Chatbox/{message_id}/{file_type}/{timestamp_str}_{file.name}'.replace(" ", "_")

        blob_client = get_blob_service_client().get_blob_client(container=AZURE_CONTAINER, blob=blob_path)
        file.seek(0)  # Reset file pointer
        blob_client.upload_blob(file)
        return {'url': blob_client.url}
    except Exception as e:
        print(f"Error uploading attachment: {e}")
        return {'error': str(e)} 
    
# views+++++++++++++++++++++++++++++++++++++++++++++++++++++++


@api_view(['GET'])
def Sent(request, id):
    try:
        sent_messages = Chatbox.objects.filter(From_User=id)
        messages_list = [
            {
                "id": message.id,
                "Message_Id": message.Message_Id,
                # "From_User": message.From_User,
                "To_User": message.To_User,
                "Timestamp": message.Timestamp,
                "Subject": message.Subject,
                "Content": message.Content,
                "Seen": message.Seen,
                "Attachments": message.Attachments,
                "name": f"{StudentDetails.objects.filter(StudentId=message.To_User).values_list('firstName', flat=True).first()} {StudentDetails.objects.filter(StudentId=message.To_User).values_list('lastName', flat=True).first()}"
            }
            for message in sent_messages
        ]
        return JsonResponse({'data': messages_list})  # Use JsonResponse for proper JSON formatting
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error as JSON with a status code

@api_view(['GET'])

def Inbox(request, id):
    try:
        sent_messages = Chatbox.objects.filter(To_User=id)
        messages_list = [
            {
                "id": message.id,
                "Message_Id": message.Message_Id,
                "From_User": message.From_User,
                # "To_User": message.To_User,
                "Timestamp": message.Timestamp,
                "Subject": message.Subject,
                "Content": message.Content,
                "Seen": message.Seen,
                "Attachments": message.Attachments,
                "name": f"{StudentDetails.objects.filter(StudentId=message.From_User).values_list('firstName', flat=True).first()} {StudentDetails.objects.filter(StudentId=message.From_User).values_list('lastName', flat=True).first()}"
            }
            for message in sent_messages
        ]
        return JsonResponse({'data': messages_list})  # Use JsonResponse for proper JSON formatting
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error as JSON with a status code


@api_view(['GET'])
def Student_Sent(request, id):
    try:
        sent_messages = Chatbox.objects.filter(From_User=id)
        messages_list = [
            {
                "id": message.id,
                "Message_Id": message.Message_Id,
                # "From_User": message.From_User,
                "To_User": message.To_User,
                "Timestamp": message.Timestamp,
                "Subject": message.Subject,
                "Content": message.Content,
                "Seen": message.Seen,
                "Attachments": message.Attachments,
                "name": f"{userdetails.objects.filter(userID=message.To_User).values_list('firstName', flat=True).first()} {userdetails.objects.filter(userID=message.To_User).values_list('lastName', flat=True).first()}"
            }
            for message in sent_messages
        ]
        return JsonResponse({'data': messages_list})  # Use JsonResponse for proper JSON formatting
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error as JSON with a status code

@api_view(['GET'])
def Student_Inbox(request, id):
    try:
        sent_messages = Chatbox.objects.filter(To_User=id)
        messages_list = [
            {
                "id": message.id,   
                "Message_Id": message.Message_Id,
                "From_User": message.From_User,
                # "To_User": message.To_User,
                "Timestamp": message.Timestamp,
                "Subject": message.Subject,
                "Content": message.Content,
                "Seen": message.Seen,
                "Attachments": message.Attachments,
                "name": f"{userdetails.objects.filter(userID=message.From_User).values_list('firstName', flat=True).first()} {userdetails.objects.filter(userID=message.From_User).values_list('lastName', flat=True).first()}"
            }
            for message in sent_messages
        ]
        return JsonResponse({'data': messages_list})  # Use JsonResponse for proper JSON formatting
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error as JSON with a status code

@api_view(['GET'])
def TutorDetails(request):
    try:
        tutor_details = userdetails.objects.all()
        userlist=[]
        for tutor in tutor_details:
            userlist.append({
                "userID": tutor.userID,
                # "email": tutor.email,
                # "category": tutor.category,
                # "expiry_date": tutor.expiry_date,
                # "status": tutor.status,
                # "register_date": tutor.register_date,
                "firstName": tutor.firstName,
                "lastName": tutor.lastName,
            })
        return JsonResponse({'data': userlist}, safe=False)
    except Exception as e:
      print(e)
      return JsonResponse({"error": str(e)}, status=500)

@api_view(['POST'])
def mark_as_read(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  
            message_data = json.loads(data['data'])  
            Message_Id = message_data.get('Message_Id')
            Content = message_data.get('Content')
            Subject = message_data.get('Subject')
            message = Chatbox.objects.filter(
                Message_Id=Message_Id,
                Content=Content,
                Subject=Subject
            ).first()
            if message:
               
                message.Seen = True
                message.save()  
 
            print(f'Marked message as read: {Message_Id}, Subject: {Subject}')
            return HttpResponse(json.dumps({"success": True}), content_type='application/json')
        except Exception as e:
            print(f'Error: {e}')
            return HttpResponse(json.dumps({"error": "Invalid request"}), content_type='application/json')
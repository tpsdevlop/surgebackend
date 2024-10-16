
import json
from Exskilencebackend160924.Blob_service import get_blob_service_client
from rest_framework.decorators import api_view

def download_list_blob2(blob_name, startwith, container_client):
    container_client = get_blob_service_client().get_container_client(container_client)
    files = []
    for blob in container_client.list_blobs(name_starts_with=blob_name):
        if blob.name.split('/')[-1].lower().startswith(str(startwith).lower()):
            blob_data = container_client.get_blob_client(blob).download_blob().readall()
            json_content_str = blob_data.decode('utf-8')
            json_data = json.loads(json_content_str)
            files.append({"Qn": json_data.get("Qn"),"Qn_name" : str(blob.name.split('/')[-1]).replace('.json','')})
    return files


from django.http import JsonResponse
from django.conf import settings
CONTAINER ="internship"
@api_view(['GET'])
def Questions(request, course):
    blob_name = 'Internship_days_schema/' + course + '/'
    startwith = ''

    questions = download_list_blob2(blob_name, startwith, CONTAINER )
    return JsonResponse(questions, safe=False)
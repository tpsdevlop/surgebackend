from datetime import datetime
import json
from azure.storage.blob import BlobServiceClient
from .settings import *
from django.views.decorators.cache import cache_page
from django.core.cache import cache

def get_blob_service_client():
    account_name = AZURE_ACCOUNT_NAME
    account_key = AZURE_ACCOUNT_KEY
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    return BlobServiceClient.from_connection_string(connection_string)
def get_blob_container_client():
    account_name = AZURE_ACCOUNT_NAME
    account_key = AZURE_ACCOUNT_KEY
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    return BlobServiceClient.from_connection_string(connection_string).get_container_client(AZURE_CONTAINER)

def download_blob(blob_name):
    # cacheresponse = cache.get(blob_name)
    # if cacheresponse:
    #     # print('cache hit')
    #     cache.set(blob_name,cacheresponse,60*60)
    #     return cacheresponse
    print('cache miss')
    container_client =  get_blob_container_client()
    blob_client = container_client.get_blob_client(blob_name)
    blob_data = blob_client.download_blob().readall()
    # cache.set(blob_name,blob_data,60*60)
    return blob_data

def download_blob2(blob_name,container_client):

    # cacheresponse = cache.get(blob_name)
    # if cacheresponse:
    #     # print('cache hit')
    #     cache.set(blob_name,cacheresponse,60*60)
    #     return cacheresponse
    # print('cache miss')
    container_client =  get_blob_service_client().get_container_client(container_client)
    blob_client = container_client.get_blob_client(blob_name)
    # ctime = datetime.now()
    blob_data = blob_client.download_blob()#.readall()
    # print((datetime.now()-ctime).total_seconds(),'download')
    # ctime = datetime.now()
    blob_data = blob_data.readall()
    # print((datetime.now()-ctime).total_seconds(),'readall')
    # cache.set(blob_name,blob_data,60*60)
    return blob_data

def download_list_blob(blob_name,startwith):
    # cacheresponse = cache.get(blob_name)
    # if cacheresponse:
    #     # print('cache hit')
    #     cache.set(blob_name,cacheresponse,60*60)
    #     return cacheresponse
    # print('cache miss')
    container_client =  get_blob_container_client()
    files = []
    for blob in container_client.list_blobs(name_starts_with=blob_name):
        if blob.name.split('/')[-1].lower().startswith(str(startwith).lower()):
            blob_data = container_client.get_blob_client(blob).download_blob().readall()
            json_content_str = blob_data.decode('utf-8') 
            json_data = json.loads(json_content_str)
            json_data.update({ "Qn_name": blob.name.split('/')[-1].split('.')[0]})
            files.append(json_data)
    # cache.set(blob_name,files,60*60)
    return  files
def download_list_blob2(blob_name,startwith,container_client):
    container_client =  get_blob_service_client().get_container_client(container_client)
    files = []
    for blob in container_client.list_blobs(name_starts_with=blob_name):
        if blob.name.split('/')[-1].lower().startswith(str(startwith).lower()):
            blob_data = container_client.get_blob_client(blob).download_blob().readall()
            json_content_str = blob_data.decode('utf-8') 
            json_data = json.loads(json_content_str)
            json_data.update({ "Qn_name": blob.name.split('/')[-1].split('.')[0]})
            files.append(json_data)
    return  files
import os
import openai
import datetime
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, BlobSasPermissions, generate_blob_sas
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 327680000

# Please set those variables
STORAGE_ACCOUNT_CONNECTION_STRING = "XXXXXXXXXXXXXXXXXXXXX"
container_name_documents = 'XXXXXXXXXXXXXXXX' #raw pdf files
OPENAI_API_KEY = "XXXXXXXXXXXXXXXXXXXXXX" # SET YOUR OWN API KEY HERE
AZURE_OPENAI_RESOURCE_ENDPOINT = "https://XXXXXXXXXX.openai.azure.com/" # SET A LINK TO YOUR RESOURCE ENDPOINT
FORM_RECOGNIZER_ENDPOINT = "https://XXXXXXXXXXX.cognitiveservices.azure.com/"
FORM_RECOGNIZER_KEY = "XXXXXXXXXXXXXXXXXXXXXX"
PROMPT= [XXXXXXXXXXXXX]

openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_RESOURCE_ENDPOINT
openai.api_version = "2023-07-01-preview"
openai.api_key = OPENAI_API_KEY



def get_authenticated_url(container_name,filename):
    """Returns a list of tuple of (document name, authenticated URLs) for
    documents in the given container."""
    # Connect to the storage account
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(container_name)
        
    # Upload the file    
    blob_client = container_client.get_blob_client(filename)

    # [START upload_a_blob]
    # Upload content to block blob
    with open("./"+filename, "rb") as data:
        blob_client.upload_blob(data, blob_type="BlockBlob",overwrite=True)
    # [END upload_a_blob]

    blob_url = blob_client.url
 
    print(f"Generating authenticated URL for: {filename}")
 
    blob_sas = generate_blob_sas(
        account_name=container_client.account_name,
        account_key=container_client.credential.account_key,
        container_name=container_name,
        blob_name=filename,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1))
 
    authenticated_url = f"{blob_url}?{blob_sas}"

    return authenticated_url 
 
def get_content(document_url):
    """Returns the text content of the file at the given URL."""
    print("Analyzing", document_url)
 
    document_analysis_client = DocumentAnalysisClient(
        endpoint=FORM_RECOGNIZER_ENDPOINT,
        credential=AzureKeyCredential(FORM_RECOGNIZER_KEY),
    )
    
    poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-read", document_url)
    result = poller.result()
 
    return result.content 


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename)
        print(filename)
        # Here you should save the file
        file.save(filename)

        auth_url = get_authenticated_url(container_name_documents,filename)

        text = get_content(auth_url)
        #print(text)
        print("Doc name : " + filename + " | " + "URL : "+auth_url)
 
        prompt = PROMPT 
        prompt.append({"role":"user", "content": text})
        #print(prompt)

 
        response = openai.ChatCompletion.create(  engine="gpt-35-turbo",messages = prompt,temperature=0.7,max_tokens=800,top_p=0.95,frequency_penalty=0,presence_penalty=0,stop=None)
 
        print(response.choices[0].message.content)

        return response.choices[0].message.content
       
    return 'No file uploaded'


if __name__ == '__main__':
   app.run()

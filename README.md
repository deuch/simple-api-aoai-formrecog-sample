# simple-api-aoai-formrecog-sample

## Prepare AML Compute instance

- Clone the repo in your home directory on AML compute instance
- Run : `!pip install -r requirements.txt`
- Run : `az upgrade`
- Run : `az login`

## Modify values in app.py

`STORAGE_ACCOUNT_CONNECTION_STRING = "XXXXXXXXXXXXXXXXXXXXX"`  
`container_name_documents = 'XXXXXXXXXXXXXXXX' #raw pdf files`  
`OPENAI_API_KEY = "XXXXXXXXXXXXXXXXXXXXXX" # SET YOUR OWN API KEY HERE`  
`AZURE_OPENAI_RESOURCE_ENDPOINT = "https://XXXXXXXXXX.openai.azure.com/" # SET A LINK TO YOUR RESOURCE ENDPOINT`  
`FORM_RECOGNIZER_ENDPOINT = "https://XXXXXXXXXXX.cognitiveservices.azure.com/"`  
`FORM_RECOGNIZER_KEY = "XXXXXXXXXXXXXXXXXXXXXX"`  
`PROMPT= [XXXXXXXXXXXXX]`

## Deploy Azure App Services

- In the directory where **app.py** and **requirements.txt** reside, run :
  - Replace *myappname*, *mylocation* and *mysub* bu the desired values
  
  `az webapp up --runtime PYTHON:3.9 --sku B1 --name myappname --location mylocation --subscription mysub`

It will create and deploy an App Services Instance with the python code and the associated requirements. You can use the same command to update the app service in you make some modifications in your code

## Testing

You can test with POSTMAN or curl command. You need to use a "file" field to upload the document.  
Replace *myfile.pdf* and *myapp* with the desired values.

For curl with the App Service Deployment :  
`curl -k -X POST -F file=@myfile.pdf https://myapp.azurewebsites.net/upload`

Or to test locally in the AML Compute Instance :  
`curl -k -X POST -F file=@myfile.pdf http://localhost:5000/upload`

Overwrite is enabled for the blob, so you can upload a file with the same name and it will be overwritten.

If you have some HTTP 413 errors (Entity too large), you can increase this variable : `app.config['MAX_CONTENT_LENGTH'] = 327680000`

## Best practices

- **It's better and safer to use Managed Identities instead of key or access keys**

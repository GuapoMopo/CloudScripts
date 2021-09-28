import json
import os 
import boto3
from datetime import datetime


s3 = boto3.resource("s3")
s3client = boto3.client("s3")

def lambda_handler(event, context):
    
    destBuck = 'copytwopaulwasilewicz'
    sourceBuck = event['Records'][0]['s3']['bucket']['name']
    fileName = event['Records'][0]['s3']['object']['key']
    
    bucket = s3.Bucket(sourceBuck)

    s3client.copy_object(Bucket=destBuck, CopySource=sourceBuck+'/'+fileName, Key=fileName)
    
    today = datetime.today()
    string = "Uploaded file "+ fileName+": "+ str(today) + "\n Copied file "+fileName+" to bucket "+destBuck
    encoded_string = string.encode("utf-8")
    
    logName = 'LOG-'+fileName[:-4]+'.txt'
    s3_path = "logs/" + logName

    
    s3.Bucket(destBuck).put_object(Key=s3_path, Body=encoded_string)
    
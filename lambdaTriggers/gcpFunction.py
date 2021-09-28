from google.cloud import storage

def hello_gcs(event, context):

     #sourceBuck = 'a3cloudbucket'
     sourceBuck = event['bucket']
     destBuck = 'copytwopaulwasilewicz'
     dest_blob_name = event['name']


     storage_client = storage.Client()
     source_bucket = storage_client.bucket(sourceBuck)
     source_blob = source_bucket.blob(event['name'])
     dest_bucket = storage_client.bucket(destBuck)

     blob_copy = source_bucket.copy_blob(source_blob, dest_bucket, dest_blob_name)


     #logging
     logFilename = 'Log-'+dest_blob_name[:-3]+'.txt'

     logBuck = storage_client.get_bucket('copytwopaulwasilewicz')
     logBlob = logBuck.blob(logFilename)
     logBlob.upload_from_string('Uploaded file: '+event['name']+'\nCopied file '+event['name']+' to bucket '+destBuck)
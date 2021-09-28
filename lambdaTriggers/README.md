

Paul Wasilewicz
1007938

Cloud System 1: AWS

AWS LambdaTrigger to create a log when a new bucket is created with name and datetime

Trigger bucket: a3lambdatrigger
    Gets triggered on adding a file to the bucket at the root
The copy to bucket: copytwopaulwasilewicz
    Copy's the file to the root directory
    Places the log file in the folder 'logs/' and then the format are the log file name is, LOG-filename.txt
    If you upload a folder into the a3lambdatrigger then the logs will be in that same folder with logs appended to the front of it

AWS file is 
    awsLambdaFunction.py
Done in python

Setup:
    I set the trigger up on the management console, and then create the function on aws, using the event call to get the source bucket name and file and then uses the boto3 copy command to copy the file over to my destination bucket. The source bucket is dynamic and same with the file but the destination bucket is static, 'copytwopaulwasilewicz' is hardcoded.

Cloud System 2: Google Cloud Platform

GCP trigger to create a log when a new bucket is created with name and datetime

Trigger Bucket: a3cloudbucket
    Gets triggered on adding a file
Copy to bucket: copytwopaulwasilewicz
    Copy's file to the root directory
    Places the log file in the root directory of the bucket and then the format are the log file name is, LOG-filename.txt

GCP file: 
    gcpFunction.py
Done in python

Setup:
    I set the trigger on the gcp platform function, and then created the function in python on gcp, and again using the event arg, I get the source bucket name and the filename and then copy it to my 'copytwopaulwasilewicz' which is hardcoded, but the source bucket and filename are found dynamically. 


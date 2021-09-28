#######################################################
# Paul Wasilewicz                                     #
# 1007938                                             #
# CIS*4010 A1                                         #
#######################################################

import boto3
import botocore
#import time
import configparser




config = configparser.ConfigParser() #try catch this and print config is not found
config.read('config.ini')

ACCESS_KEY = ''
SECRET_KEY = ''
REGION = ''
#ACCESS_KEY=config['DEFAULT']['AccessKey']
#SECRET_KEY=config['DEFAULT']['SecretKey']
#REGION=config['DEFAULT']['Region']
commands = ["mkbucket", "ls", "pwd", "cd", "mkdir", "rmdir"]
wd = 's3:/'
flag = 1
rootFlag = 1

s3_resource = boto3.resource('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )




def rmDir(dirList): #remove a folder : GOOD 

    if(rootFlag == 1):
        print('error: cannot remove directories at the root level')
        return

    currentBucket = wd.split('/')[1]
    s3 = boto3.resource('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
    bucket = s3.Bucket(currentBucket)


    if(len(dirList)>2): # this is for -p option
        if(str(dirList[1]) == '-p'):
            dirName = str(dirList[2]) + '/'
            bucket.objects.filter(Prefix=dirName).delete()
            return
        else:
            print('error: Invalid arguments')
            return
    
    #print(dirList)
    dirName = str(dirList[1]) + '/'
    dirName = wd.replace('s3:/'+currentBucket,'') + '/' + dirName
    dirName = dirName[1:]
    
    #print(dirName)
    
    objs = list(bucket.objects.filter(Prefix=dirName))
    #print(objs)
    if(len(objs)>1): #tell user that they need -p flag
        print('failed to remove directory: ','\'',dirName[:-1],'\'',': Directory not empty')
        print('-p: to remove DIRECTORY and its ancestors')
    else:
        bucket.objects.filter(Prefix=dirName).delete()


    return


def makeBucket(buckName):

    s3 = boto3.resource('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
    #have to check if the bucket already exists
    if(s3.Bucket(buckName).creation_date is None):
        try:
            s3.create_bucket(Bucket=buckName, CreateBucketConfiguration={'LocationConstraint':REGION})
        except:
            print('Bucket already exists or invalid bucket name')
        return
    else:
        print('Bucket already exists')

    

    return

def makeDir(dirName): #: should be good
    global wd
    s3 = boto3.resource('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    if rootFlag == 1: #cant make directory at root level
        print('error: cannot make directory at root level')
        return

    dirList = dirName.split('/')
    if(len(dirList)>1): #cant have / in directory name
        print('mkdir: cannot create directory',dirName,': no such file or directory')
        return

    currentBucket = wd.split('/')[1]
    path = wd.replace('s3:/'+currentBucket, '')
    if path != '':
        path = path[1:]
        path = path+'/'+dirName
    else:
        path = dirName
    #print('Path',path)
    try:
        s3.Object(currentBucket, path+'/').put(Body=dirName)  #this works and makes a folder on the aws website
    except:
        print('error: bad request')


    return

def pwd(): #print my global path
    print(wd)
    return

def cd(path):
    global wd, rootFlag
    s3 = boto3.resource('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
    if len(path) == 1 and path != '~':
        return
    if(path == '..'): #move back 1 directory
        tmpList = wd.split('/')
        #print(tmpList)
        if(len(tmpList) == 2):
            tmpList.pop()
            wd = 's3:/'
            rootFlag = 1
        elif(len(tmpList)<2):
            return
        else:
            tmpList.pop()
            wd = '/'.join(tmpList)
        #print(wd)
        return

    if(path[0]=='.' and path[1]=='.' and path[2]=='/'): #loop through ../.. for however many directories
        tmpList = path.split('/')
        num = len(tmpList)
        wdList = wd.split('/')
        for _ in range(num):
            if(len(wdList)>2):
                wdList.pop()
            else:
                wd = 's3:/'
                rootFlag = 1
                return
        wd = '/'.join(wdList)
        
        
        return

    
    if(path == '~'): #root directory
        wd = 's3:/'
        rootFlag = 1
        return

    path = path+'/'

    if rootFlag == 1: #were in root directory, looking to enter buckets
        dirList = path.split('/')
        dirList.pop()
        #print(dirList)
        for bucket in s3.buckets.all(): #check if bucket exists, if yes then add its to the working directory
            #print('whatttt',dirList[0], bucket.name)
            if bucket.name == dirList[0]:
                #print('are we in here')
                wd = wd + bucket.name
                currentBucket = bucket.name
                rootFlag = 0
                break
        else: #bucket doesn't exist
                print('error:invalid bucket')
                return
        if len(dirList) > 1: #this is for multiply directory traversal
            curPath = path.replace(currentBucket+'/','') #enter the bucket and check if the object exists there
            #print(curPath)
            bucket = s3.Bucket(currentBucket)
            objs = list(bucket.objects.filter(Prefix=curPath))
            if(len(objs)>0 and objs[0].key==curPath): #if it does then go in and if not go back to root directory
                path = path[:-1]
                wd = 's3:/'+path
            else:
                wd = 's3:/'
                rootFlag = 1
                print('no such file or directory')
    elif rootFlag == 0: #were in a bucket or in an object
        currentBucket = wd.split('/')[1]
        prefixPath = (wd.replace('s3:/'+currentBucket,''))
        #print('yes', prefixPath)
        if prefixPath != '':
            prefixPath = prefixPath[1:]
            prefixPath = prefixPath+'/'+path
        else:
            prefixPath = path
            #print('here',prefixPath)
        bucket = s3.Bucket(currentBucket)
        objs = list(bucket.objects.filter(Prefix=prefixPath))
        #print(objs)
        if(len(objs)>0 and objs[0].key==prefixPath): #for the aa thing, the key is made as aa/new.txt so thats how you would have to specify to enter
            path = path[:-1]
            wd = wd+'/'+path

    return

def listBucks(flag): #its good but it breaks if theres an invalid directory

    if(flag != None and flag != '-l'):
        print('error: invalid argument')
        return

    s3 = boto3.resource('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    if rootFlag == 1:     #if were in root only display bucket names
        for bucket in s3.buckets.all():
            print('-dir-\t',bucket.name)
    if rootFlag == 0:   #if were in a bucket then list contents of were we are
        tempList = wd.split('/')
        currentBucket =  str(tempList[1])
        if(len(tempList)>2):
            prefixPath = (wd.replace('s3:/'+currentBucket+'/',''))+'/'
        else:
            prefixPath = ''

        my_bucket = s3.Bucket(currentBucket)

        client = boto3.client('s3',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY
        )
        paginator = client.get_paginator('list_objects')
        result = paginator.paginate(Bucket=currentBucket, Delimiter='/',Prefix=prefixPath) 

        for prefix in result.search('CommonPrefixes'): #this prints all -l flag for directories
            if(prefix != None):
                tempString = prefix.get('Prefix')
                if(flag == '-l'):
                    tmpObj = s3.Object(currentBucket,tempString)
                    tempString = tempString.replace(prefixPath,'') 
                    print('{:<25} {:<12} {:<30} {:<25}'.format(tmpObj.content_type, '0', str(tmpObj.last_modified), tempString))
                else:
                    #print(tempString, prefixPath)
                    tempString = tempString.replace(prefixPath,'',1)
                    print('-dir-\t', tempString)
            

        for my_bucket_object in my_bucket.objects.filter(Delimiter='/',Prefix=prefixPath): #this prints files and -l info for files
            tempString = my_bucket_object.key
            tmpObj = s3.Object(currentBucket,tempString)
            tempString = tempString.replace(prefixPath,'')
            if(tempString != ''):
                if(flag == '-l'):
                    tempString = tempString.replace(prefixPath,'')
                    #print(tmpObj.content_type,'\t',str(tmpObj.content_length),'\t',tmpObj.last_modified,'\t',tempString)
                    print('{:<25} {:<12} {:<30} {:<25}'.format(tmpObj.content_type, tmpObj.content_length, str(tmpObj.last_modified), tempString))
                else:
                    print('    \t',tempString)

    return

def upload(localFile, objName): #pretty sure this is good
    s3 = boto3.resource('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    fix = objName.split('/')
    oldPath = 0
    if fix[0] == 's3:':
        fix.pop(0)
        objName = '/'.join(fix)
        oldPath = 1

    if(rootFlag == 1):
        myList = objName.split('/')
        currentBucket = str(myList[0])
        myList.pop(0)
        objName = objName.replace(currentBucket+'/','')
       # print('first',objName)
        #have to check if the path exists
        if(s3.Bucket(currentBucket).creation_date is None):
            print('error: no such file or directory : bad bucket')
            return
        if len(myList) == 1 and oldPath == 1:
            #print('yessir')
            try:
                s3.meta.client.upload_file(localFile, currentBucket, objName)
            except:
                print('error: system cannot find the file specified')
                return
            return

        key = '/'.join(myList[:-1]) + '/'
        #print('key',key)
        bucket = s3.Bucket(currentBucket)
        objs = list(bucket.objects.filter(Prefix=key))

         
        if len(objs) > 0 and objs[0].key == key:
            try:
                s3.meta.client.upload_file(localFile, currentBucket, objName)
            except:
                print('error: system cannot find the file specified')
                return
        else:
            print('error: no such file or directory : bad folder')
            return
        
    elif(rootFlag == 0):
        currentBucket = wd.split('/')[1]
        myList = objName.split('/')
        #print(myList)
        if len(myList) > 2:
            #print('1')
            prefixPath = '/'.join(myList[1:-1])
        else:
            #print('2')
            prefixPath = (wd.replace('s3:/'+currentBucket,''))
            if prefixPath != '':
                prefixPath = prefixPath[1:] + '/' #this should work test it
        
        myList = objName.split('/')
        newBuck = myList[0]
        myList.pop(0)
        if(len(myList) == 1) and oldPath == 1:
            if(s3.Bucket(newBuck).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            try:
                s3.meta.client.upload_file(localFile, newBuck, myList[-1])
            except:
                print('error: system cannot find the file specified')
                return
        elif(len(myList)>1) and oldPath == 1:
            if(prefixPath != ''):
                prefixPath = prefixPath+'/'
            if(s3.Bucket(newBuck).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            bucket = s3.Bucket(newBuck)
            objs = list(bucket.objects.filter(Prefix=prefixPath))
            if len(objs) > 0 and objs[0].key == prefixPath and oldPath == 1:
                #print(localFile, currentBucket, prefixPath, objName)
                try:
                    s3.meta.client.upload_file(localFile, newBuck, prefixPath+myList[-1])
                except:
                    print('error: system cannot find the file specified')
                    return
            else:
                print('error: no such file or directory')
                return    
        else:  #were adding it to the working directory
            #print(localFile, currentBucket, prefixPath, objName, myList)
            try:
                s3.meta.client.upload_file(localFile, currentBucket, prefixPath+objName)
            except:
                print('error: system cannot find the file specified')
                return


    return

def download(objName, localFile): #pretty sure this is good
    s3 = boto3.resource('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    fix = objName.split('/')
    oldPath = 0
    if fix[0] == 's3:':
        fix.pop(0)
        objName = '/'.join(fix)
        oldPath = 1

    if(rootFlag == 1):
        myList = objName.split('/')
        currentBucket = str(myList[0])
        myList.pop(0)
        objName = objName.replace(currentBucket+'/','')
        #print('first',objName)
        #have to check if the path exists
        if(s3.Bucket(currentBucket).creation_date is None):
            print('error: no such file or directory : bad bucket')
            return
        if len(myList) == 1:
            #print('yessir')
            try:
                s3.Bucket(currentBucket).download_file(objName, localFile)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print('error: the file does not exist')
                else:
                    raise
            return

        key = '/'.join(myList[:-1]) + '/'
        #print('key',key)
        bucket = s3.Bucket(currentBucket)
        objs = list(bucket.objects.filter(Prefix=key))
         
        if len(objs) > 0 and objs[0].key == key and oldPath == 1:
            try:
                s3.Bucket(currentBucket).download_file(objName, localFile)
                #s3.meta.client.upload_file(currentBucket, objName, localFile)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print('error: the file does not exist')
                else:
                    raise
        else:
            print('error: no such file or directory : bad folder')
            return
        
    elif(rootFlag == 0): #make sure this works with s3
        currentBucket = wd.split('/')[1]
        if len(wd.split('/')) > 2:
            #print('1')
            prefixPath = (wd.replace('s3:/'+currentBucket+'/',''))+'/'
        else:
            #print('2',)
            prefixPath = (wd.replace('s3:/'+currentBucket,''))
        #print(prefixPath, currentBucket)
        
        myList = objName.split('/')
        newBuck = myList[0]
        if(len(myList)>1 and oldPath == 1):
            #print(myList)
            key = prefixPath+'/'.join(myList[1:-1])+'/'
            bucket = s3.Bucket(newBuck)
            objs = list(bucket.objects.filter(Prefix=key))
            #print(objs)
            if len(myList) == 2:
                try:
                    s3.Bucket(newBuck).download_file(myList[-1], localFile)
                except:
                    print('error: the file does not exist')
            elif len(objs) > 0 and objs[0].key == key:
                #print('here sir')
                try:
                    #print(objName)
                    s3.Bucket(newBuck).download_file(key+myList[-1], localFile)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        print('error: the file does not exist')
                    else:
                        raise
            else:
                print('error: no such file or directory')
                return
        else:  #were downloading from the working directory
            #print('are we here')
            try:
                s3.Bucket(currentBucket).download_file(prefixPath+objName, localFile)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print('error: the file does not exist')
                else:
                    raise

    return

def cp(oldObj, newObj):

    s3 = boto3.resource('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
    fix = oldObj.split('/')
    fix2 = newObj.split('/')
    oldPath = 0
    newPath = 0
    if fix[0] == 's3:':
        fix.pop(0)
        oldObj = '/'.join(fix)
        oldPath = 1
    if fix2[0] == 's3:':
        fix2.pop(0)
        newObj = '/'.join(fix2)
        newPath = 1


    if (oldObj.split('/')[-1] == newObj.split('/')[-1]):
        print('error: these are the same files')
        return

    if(rootFlag == 1): #have to fix copying from bucket 
        oldList = oldObj.split('/')
        newList = newObj.split('/')
        oldBucket = str(oldList[0])
        newBucket = str(newList[0])
        oldList.pop(0)
        newList.pop(0)
        oldObj = oldObj.replace(oldBucket+'/','')
        newObj = newObj.replace(newBucket+'/','')
        #print('first',oldObj)
        #have to check if the path exists
        #print(s3.Bucket(oldBucket).creation_date)
        #print('im over here',len(oldList),len(newList))
        if(s3.Bucket(oldBucket).creation_date is None or s3.Bucket(newBucket).creation_date is None):
            print('error: no such file or directory : bad bucket')
            return
        if len(oldList) == 1 and len(newList) == 1 and (oldPath == 1 and newPath == 1): #copy from bucket to bucket : GOOD
            #print('yessir how do we even',newList)

            source = oldBucket+'/'+oldObj
            dest = newObj
           # print('source:',source,'bucket',newBucket,'dest:',dest)
            try:
                s3.meta.client.copy_object(CopySource=source, Bucket=newBucket, Key=dest)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "NoSuchKey":
                    print('error: object does not exist')
                else:
                    raise

        elif len(oldList) > 1 and len(newList) > 1 and (oldPath == 1 and newPath == 1): #copying from path to path : GOOD
            #print('yessir2',newList)
            key = '/'.join(newList[:-1])+'/'
            key2 = '/'.join(oldList[:-1])+'/'
            #print('key',key,'      key2:',key2)
            bucket = s3.Bucket(newBucket)
            objs = list(bucket.objects.filter(Prefix=key))
            bucket2 = s3.Bucket(oldBucket)
            objs2 = list(bucket2.objects.filter(Prefix=key2))

            if (len(objs) > 0 and objs[0].key == key) and (len(objs2)> 0 and objs2[0].key == key2):
                #print('gucci')

                try:
                    source = oldBucket+'/'+oldObj
                    dest = newObj
                    #print('source:',source,'bucket',newBucket,'dest:',dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=newBucket, Key=dest)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
            else:
                print('error: no such file or directory : bad folder')
                return
        elif len(oldList) > 1 and len(newList) == 1 and (oldPath == 1 and newPath == 1): #path to bucket : GOOD
            #('whats going on')
            key = '/'.join(oldList[:-1])+'/'
            bucket = s3.Bucket(oldBucket)
            objs = list(bucket.objects.filter(Prefix=key))
            if (len(objs) > 0 and objs[0].key == key):
                try:
                    source = oldBucket+'/'+oldObj
                    dest = newObj
                    #print('source:',source,'bucket',newBucket,'dest:',dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=newBucket, Key=dest)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
            else:
                print('error: no such file or directory : bad folder')
                return

        elif len(oldList) == 1 and len(newList) > 1 and (oldPath == 1 and newPath == 1): #bucket to path : GOOD
            #print('whats going on2')
            key = '/'.join(newList[:-1])+'/'
            bucket = s3.Bucket(newBucket)
            objs = list(bucket.objects.filter(Prefix=key))
            if (len(objs) > 0 and objs[0].key == key):
                try:
                    source = oldBucket+'/'+oldObj
                    dest = newObj
                    #print('source:',source,'bucket',newBucket,'dest:',dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=newBucket, Key=dest)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
            else:
                print('error: no such file or directory : bad folder')
                return
        
    elif(rootFlag == 0):
        currentBucket = wd.split('/')[1]
        newList = newObj.split('/')
        oldList = oldObj.split('/')
        key = '/'.join(oldList[1:-1])+'/'
        
        if(len(newList) == 1 and len(oldList) == 1): #cp from the directory were in to the directory we are in : GOOD
            if(s3.Bucket(currentBucket).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            else:
                try:
                    curDir = wd.replace('s3:/'+currentBucket,'')
                    #print(curDir)

                    if curDir != '':
                        if curDir[0] == '/':
                            curDir = curDir[1:]
                        source = currentBucket+'/'+curDir+'/'+oldObj
                        dest = curDir+'/'+newObj
                    else:
                        source = currentBucket+'/'+oldObj
                        dest = newObj
                    #print(source,currentBucket, dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=currentBucket, Key=dest)
                    return
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
        if (len(oldList) == 1 and len(newList) > 1) and (newPath == 1): #cp from current directory to path : GOOD
            #print('yeha', newPath)
            bucket = s3.Bucket(currentBucket)
            if(s3.Bucket(newList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            if len(newList) > 2:
                key = '/'.join(newList[1:-1])+'/'
                #print(key)
                bucket2 = s3.Bucket(newList[0])
                objs = list(bucket2.objects.filter(Prefix=key))
                #print(objs)
                if (len(objs) > 0 and objs[0].key == key):
                    try:
                        curDir = wd.replace('s3:/'+currentBucket,'')
                        destBucket = newList[0]
                        newList.pop(0)
                        if len(newList) > 1:
                            #newDir = '/'.join(newList)
                            #dest = newDir+newList[-1]
                            dest = '/'.join(newList)
                        else:
                            dest = newList[-1]

                        if curDir != '':
                            curDir = curDir[1:] + '/'
                        source = currentBucket+'/'+curDir+oldObj
                        #print(currentBucket,source,destBucket,dest)
                        s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                        return
                    except botocore.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == "NoSuchKey":
                            print('error: object does not exist')
                        else:
                            raise
                    return
                else:
                    print('error: no such file or directory : bad folder here')
                    return
            elif (len(newList) == 2 and len(oldList) == 1) and (newPath == 1): #copying from current directory into a bucket : GOOD
                bucket2 = s3.Bucket(newList[0])
                #print('this time')
                try:
                    curDir = wd.replace('s3:/'+currentBucket,'')
                    destBucket = newList[0]
                    newList.pop(0)
                    if len(newList) > 1:
                        dest = '/'.join(newList)
                    else:
                        dest = newList[-1]
                    if curDir != '':
                        curDir = curDir[1:] + '/'
                    source = currentBucket+'/'+curDir+oldObj
                    #print(currentBucket,source,destBucket,dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                    return
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
                return



        if (len(newList) == 1 and len(oldList) > 2) and (oldPath == 1): #cp from path to current directory : GOOD
            pathBucket = s3.Bucket(oldList[0])
            if(s3.Bucket(oldList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            key = '/'.join(oldList[1:-1])+'/'
            #print('yeshuh',key)
            objs = list(pathBucket.objects.filter(Prefix=key))
            #print('key:',key, objs)
            if (len(objs) > 0 and objs[0].key == key):
                try:
                    curDir = wd.replace('s3:/'+currentBucket,'')
                    destBucket = currentBucket
                    if len(oldList) > 1:
                        source = '/'.join(oldList)
                    else:
                        source = oldList[-1]
                    if curDir != '':
                        curDir = curDir[1:] + '/'
                    dest = curDir+newObj
                   # print(currentBucket,source,destBucket,dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                    return
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
                return
        elif (len(newList) == 2 and len(oldList) > 2) and (oldPath == 1 and newPath == 1): #copying from path into a bucket : GOOD
           # print('this time2')
            if(s3.Bucket(oldList[0]).creation_date is None or s3.Bucket(newList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return

            key = '/'.join(oldList[1:-1])+'/'
            #print('yes4',key)
            pathBucket = s3.Bucket(oldList[0])
            objs = list(pathBucket.objects.filter(Prefix=key))
            #print('key:',key, objs)
            if (len(objs) > 0 and objs[0].key == key):
                try:
                    destBucket = newList[0]
                    dest = newList[-1]
                    source = oldObj
                    #print(currentBucket,source,destBucket,dest, 'this one')
                    s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                    return
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
                return
            else:
               # print('hererererere')
                print('error: no such file or directory : bad folder')
                return
 ############################
        elif (len(oldList) == 2 and len(newList) > 2) and (oldPath == 1 and newPath == 1): #bucket to path : GOOD
           # print('whats going on3')
            newBucket = newList[0]
            oldBucket = oldList[0]

            if(s3.Bucket(oldBucket).creation_date is None or s3.Bucket(newBucket).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return

            oldList.pop(0)
            key = '/'.join(newList[1:-1])+'/'
           # print('key', key)
            bucket = s3.Bucket(newBucket)
            objs = list(bucket.objects.filter(Prefix=key))
            if (len(objs) > 0 and objs[0].key == key):
                try:
                    source = oldObj
                    tmpList = newObj.split('/')
                    dest = '/'.join(tmpList[1:])
                    #dest = newObj
                    #print('source:',source,'bucket',newBucket,'dest:',dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=newBucket, Key=dest)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
            else:
                print('error: no such file or directory : bad folder')
                return  
        ############################
        elif (len(oldList) > 2 and len(newList) > 2) and (oldPath == 1 and newPath == 1): #oldlist and newlist are both greater than 1, copy from path to path : GOOD
            #print('final')
            if(s3.Bucket(oldList[0]).creation_date is None or s3.Bucket(newList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            key = '/'.join(oldList[1:-1])+'/'
            key2 = '/'.join(newList[1:-1])+'/'
            pathBucket = s3.Bucket(oldList[0])
            pathBucket2 = s3.Bucket(newList[0])
            objs = list(pathBucket.objects.filter(Prefix=key))
            objs2 = list(pathBucket2.objects.filter(Prefix=key2))

            if ((len(objs) > 0 and objs[0].key == key) and (len(objs2) > 0 and objs2[0].key == key2)):
                try:
                    destBucket = newList[0]
                    dest = '/'.join(newList[1:])
                    source = oldObj
                    #print(currentBucket,source,destBucket,dest, 'this one 4')
                    #return
                    s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                    return
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
                return
            else:
                #print('at the end')
                print('error: no such file or directory : bad folder')
                return

        if (len(oldList) == 2 and len(newList) == 2) and (oldPath == 1 and newPath == 1): #bucket to bucket : GOOD
            if(s3.Bucket(oldList[0]).creation_date is None or s3.Bucket(newList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            try:
                destBucket = newList[0]
                dest = newObj.replace(newList[0]+'/','')
                source = oldObj
                #print(currentBucket,source,destBucket,dest, 'this one 5')
                s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                return
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "NoSuchKey":
                    print('error: object does not exist')
                else:
                    raise
            return

        if (len(oldList) == 2 and len(newList) == 1) and (oldPath == 1): #bucket to current directory : GOOD
            bucket2 = s3.Bucket(oldList[0])
            #print('this timeeee')
            if(s3.Bucket(oldList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            try:
                curDir = wd.replace('s3:/'+currentBucket,'')
                destBucket = currentBucket
                if curDir != '':
                    curDir = curDir[1:] + '/'
                dest = curDir+newObj
                source = oldObj
                #print(currentBucket,source,destBucket,dest)
                s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                return
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "NoSuchKey":
                    print('error: object does not exist')
                else:
                    raise
            return
    return

def mv(oldObj, newObj):
    
    s3 = boto3.resource('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    fix = oldObj.split('/')
    fix2 = newObj.split('/')
    oldPath = 0
    newPath = 0
    if fix[0] == 's3:':
        fix.pop(0)
        oldObj = '/'.join(fix)
        oldPath = 1
    if fix2[0] == 's3:':
        fix2.pop(0)
        newObj = '/'.join(fix2)
        newPath = 1

    bucketToDeleteFrom = oldObj.split('/')[0]

    if(rootFlag == 1): 
        oldList = oldObj.split('/')
        newList = newObj.split('/')
        oldBucket = str(oldList[0])
        newBucket = str(newList[0])
        oldList.pop(0)
        newList.pop(0)
        oldObj = oldObj.replace(oldBucket+'/','')
        newObj = newObj.replace(newBucket+'/','')
        #print('first',oldObj)
        #have to check if the path exists
        if(s3.Bucket(oldBucket).creation_date is None or s3.Bucket(newBucket).creation_date is None):
            print('error: no such file or directory : bad bucket')
            return
        if (len(oldList) == 1 and len(newList) == 1) and (oldPath == 1 and newPath == 1): #copy from bucket to bucket : GOOD
           # print('yessir how do we even get in here',newList)

            source = oldBucket+'/'+oldObj
            dest = newObj
           # print('source:',source,'bucket',newBucket,'dest:',dest)
            try:
                s3.meta.client.copy_object(CopySource=source, Bucket=newBucket, Key=dest)
                tmpList = source.split('/')
                if len(tmpList) == 1:
                    keyToDel = source
                else:
                    keyToDel = '/'.join(tmpList[1:])
                s3.meta.client.delete_object(Bucket=oldBucket, Key=keyToDel)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "NoSuchKey":
                    print('error: object does not exist')
                else:
                    raise

        elif (len(oldList) > 1 and len(newList) > 1) and (oldPath == 1 and newPath == 1): #copying from path to path : GOOD
           # print('yessir2',newList)
            key = '/'.join(newList[:-1])+'/'
            key2 = '/'.join(oldList[:-1])+'/'
           # print('key',key,'      key2:',key2)
            bucket = s3.Bucket(newBucket)
            objs = list(bucket.objects.filter(Prefix=key))
            bucket2 = s3.Bucket(oldBucket)
            objs2 = list(bucket2.objects.filter(Prefix=key2))

            if (len(objs) > 0 and objs[0].key == key) and (len(objs2)> 0 and objs2[0].key == key2):
             #   print('gucci')

                try:
                    source = oldBucket+'/'+oldObj
                    dest = newObj
                   # print('source:',source,'bucket',newBucket,'dest:',dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=newBucket, Key=dest)
                    tmpList = source.split('/')
                    if len(tmpList) == 1:
                        keyToDel = source
                    else:
                        keyToDel = '/'.join(tmpList[1:])
                    s3.meta.client.delete_object(Bucket=oldBucket, Key=keyToDel)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
            else:
                print('error: no such file or directory : bad folder')
                return
        elif len(oldList) > 1 and len(newList) == 1: #path to bucket : GOOD
           # print('whats going on')
            key = '/'.join(oldList[:-1])+'/'
            bucket = s3.Bucket(oldBucket)
            objs = list(bucket.objects.filter(Prefix=key))
            if (len(objs) > 0 and objs[0].key == key):
                try:
                    source = oldBucket+'/'+oldObj
                    dest = newObj
                    #print('source:',source,'bucket',newBucket,'dest:',dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=newBucket, Key=dest)
                    tmpList = source.split('/')
                    if len(tmpList) == 1:
                        keyToDel = source
                    else:
                        keyToDel = '/'.join(tmpList[1:])
                    s3.meta.client.delete_object(Bucket=oldBucket, Key=keyToDel)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
            else:
                print('error: no such file or directory : bad folder')
                return

        elif (len(oldList) == 1 and len(newList) > 1) and (oldPath == 1 and newPath == 1): #bucket to path : GOOD
           # print('whats going on2')
            key = '/'.join(newList[:-1])+'/'
            bucket = s3.Bucket(newBucket)
            objs = list(bucket.objects.filter(Prefix=key))
            if (len(objs) > 0 and objs[0].key == key):
                try:
                    source = oldBucket+'/'+oldObj
                    dest = newObj
                    #print('source:',source,'bucket',newBucket,'dest:',dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=newBucket, Key=dest)
                    tmpList = source.split('/')
                    if len(tmpList) == 1:
                        keyToDel = source
                    else:
                        keyToDel = '/'.join(tmpList[1:])
                    s3.meta.client.delete_object(Bucket=bucketToDeleteFrom, Key=keyToDel)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
            else:
                print('error: no such file or directory : bad folder')
                return        
        
    elif(rootFlag == 0):
        currentBucket = wd.split('/')[1]
        newList = newObj.split('/')
        oldList = oldObj.split('/')
        key = '/'.join(oldList[1:-1])+'/'
        
        if(len(newList) == 1 and len(oldList) == 1) : #cp from the directory were in to the directory we are in : GOOD
            if(s3.Bucket(currentBucket).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            else:
                try:
                    curDir = wd.replace('s3:/'+currentBucket,'')
                   # print(curDir)

                    if curDir != '':
                        if curDir[0] == '/':
                            curDir = curDir[1:]
                        source = currentBucket+'/'+curDir+'/'+oldObj
                        dest = curDir+'/'+newObj
                    else:
                        source = currentBucket+'/'+oldObj
                        dest = newObj
                    #print(source,currentBucket, dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=currentBucket, Key=dest)
                    tmpList = source.split('/')
                    if len(tmpList) == 1:
                        keyToDel = source
                    else:
                        keyToDel = '/'.join(tmpList[1:])
                    s3.meta.client.delete_object(Bucket=currentBucket, Key=keyToDel)
                    return
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
        if (len(oldList) == 1 and len(newList) > 1) and (newPath == 1): #cp from current directory to path : GOOD
           # print('yeha')
            bucket = s3.Bucket(currentBucket)
            if(s3.Bucket(newList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            if len(newList) > 2:
                key = '/'.join(newList[1:-1])+'/'
                #print(key)
                bucket2 = s3.Bucket(newList[0])
                objs = list(bucket2.objects.filter(Prefix=key))
                #print(objs)
                if (len(objs) > 0 and objs[0].key == key):
                    try:
                        curDir = wd.replace('s3:/'+currentBucket,'')
                        destBucket = newList[0]
                        newList.pop(0)
                        if len(newList) > 1:
                            #newDir = '/'.join(newList)
                            #dest = newDir+newList[-1]
                            dest = '/'.join(newList)
                        else:
                            dest = newList[-1]

                        if curDir != '':
                            curDir = curDir[1:] + '/'
                        source = currentBucket+'/'+curDir+oldObj
                        #print(currentBucket,source,destBucket,dest)
                        s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                        tmpList = source.split('/')
                        if len(tmpList) == 1:
                            keyToDel = source
                        else:
                            keyToDel = '/'.join(tmpList[1:])
                            print(tmpList)
                        s3.meta.client.delete_object(Bucket=currentBucket, Key=keyToDel)
                        return
                    except botocore.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == "NoSuchKey":
                            print('error: object does not exist')
                        else:
                            print('error deleting')
                            return
                    return
                else:
                    print('error: no such file or directory : bad folder')
                    return
            elif (len(newList) == 2 and len(oldList) == 1) and (newPath == 1): #copying from current directory into a bucket : GOOD
                #print(wd)
                bucket2 = s3.Bucket(newList[0])
               # print('this time')
                try:
                    curDir = wd.replace('s3:/'+currentBucket,'')
                    destBucket = newList[0]
                    newList.pop(0)
                    if len(newList) > 1:
                        dest = '/'.join(newList)
                    else:
                        dest = newList[-1]
                    if curDir != '':
                        curDir = curDir[1:] + '/'
                    source = currentBucket+'/'+curDir+oldObj
                   # print(currentBucket,source,destBucket,dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                    tmpList = source.split('/')
                    if len(tmpList) == 1:
                        keyToDel = source
                    else:
                        keyToDel = '/'.join(tmpList[1:])
                    s3.meta.client.delete_object(Bucket=currentBucket, Key=keyToDel)
                    return
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
                return



        if (len(newList) == 1 and len(oldList) > 2) and (oldPath == 1): #cp from path to current directory : GOOD
            pathBucket = s3.Bucket(oldList[0])
            if(s3.Bucket(oldList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            key = '/'.join(oldList[1:-1])+'/'
            #print('yeshuh',key)
            objs = list(pathBucket.objects.filter(Prefix=key))
            #print('key:',key, objs)
            if (len(objs) > 0 and objs[0].key == key):
                try:
                    curDir = wd.replace('s3:/'+currentBucket,'')
                    destBucket = currentBucket
                    if len(oldList) > 1:
                        source = '/'.join(oldList)
                    else:
                        source = oldList[-1]
                    if curDir != '':
                        curDir = curDir[1:] + '/'
                    dest = curDir+newObj
                   # print(currentBucket,source,destBucket,dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                    tmpList = source.split('/')
                    if len(tmpList) == 1:
                        keyToDel = source
                    else:
                        keyToDel = '/'.join(tmpList[1:])

                    s3.meta.client.delete_object(Bucket=oldList[0], Key=keyToDel)
                    return
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
                return
        elif (len(newList) == 2 and len(oldList) > 2) and (oldPath == 1 and newPath == 1): #copying from path into a bucket : GOOD
            #print('this time2')
            if(s3.Bucket(oldList[0]).creation_date is None or s3.Bucket(newList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return

            key = '/'.join(oldList[1:-1])+'/'
           # print('yes4',key)
            pathBucket = s3.Bucket(oldList[0])
            objs = list(pathBucket.objects.filter(Prefix=key))
            #print('key:',key, objs)
            if (len(objs) > 0 and objs[0].key == key):
                try:
                    destBucket = newList[0]
                    dest = newList[-1]
                    source = oldObj
                    #print(currentBucket,source,destBucket,dest, 'this one')
                    s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                    tmpList = source.split('/')
                    if len(tmpList) == 1:
                        keyToDel = source
                    else:
                        keyToDel = '/'.join(tmpList[1:])
                    s3.meta.client.delete_object(Bucket=oldList[0], Key=keyToDel)
                    return
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
                return
            else:
              #  print('hererererere')
                print('error: no such file or directory : bad folder')
                return
        ############################
        elif (len(oldList) == 2 and len(newList) > 2) and (oldPath == 1 and newPath == 1): #bucket to path : GOOD
            #print('whats going on22')
            newBucket = newList[0]
            oldBucket = oldList[0]

            if(s3.Bucket(oldBucket).creation_date is None or s3.Bucket(newBucket).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return

            oldList.pop(0)
            key = '/'.join(newList[1:-1])+'/'
           # print('key', key)
            bucket = s3.Bucket(newBucket)
            objs = list(bucket.objects.filter(Prefix=key))
            if (len(objs) > 0 and objs[0].key == key):
                try:
                    source = oldObj
                    tmpList = newObj.split('/')
                    dest = '/'.join(tmpList[1:])
                    #dest = newObj
                    #print('source:',source,'bucket',newBucket,'dest:',dest)
                    s3.meta.client.copy_object(CopySource=source, Bucket=newBucket, Key=dest)
                    tmpList = source.split('/')
                    if len(tmpList) == 1:
                        keyToDel = source
                    else:
                        keyToDel = '/'.join(tmpList[1:])
                    s3.meta.client.delete_object(Bucket=bucketToDeleteFrom, Key=keyToDel)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
            else:
                print('error: no such file or directory : bad folder')
                return  
        ############################
        elif (len(oldList) > 2 and len(newList) > 2) and (oldPath == 1 and newPath == 1): #oldlist and newlist are both greater than 1, copy from path to path : GOOD
            print('final')
            if(s3.Bucket(oldList[0]).creation_date is None or s3.Bucket(newList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            key = '/'.join(oldList[1:-1])+'/'
            key2 = '/'.join(newList[1:-1])+'/'
            pathBucket = s3.Bucket(oldList[0])
            pathBucket2 = s3.Bucket(newList[0])
            objs = list(pathBucket.objects.filter(Prefix=key))
            objs2 = list(pathBucket2.objects.filter(Prefix=key2))

            if ((len(objs) > 0 and objs[0].key == key) and (len(objs2) > 0 and objs2[0].key == key2)):
                try:
                    destBucket = newList[0]
                    dest = '/'.join(newList[1:])
                    source = oldObj
                   # print(currentBucket,source,destBucket,dest, 'this one 4')
                    #return
                    s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                    tmpList = source.split('/')
                    if len(tmpList) == 1:
                        keyToDel = source
                    else:
                        keyToDel = '/'.join(tmpList[1:])
                    s3.meta.client.delete_object(Bucket=oldList[0], Key=keyToDel)
                    return
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchKey":
                        print('error: object does not exist')
                    else:
                        raise
                return
            else:
              #  print('at the end')
                print('error: no such file or directory : bad folder')
                return

        if (len(oldList) == 2 and len(newList) == 2) and (oldPath == 1 and newPath == 1): #bucket to bucket : GOOD
            if(s3.Bucket(oldList[0]).creation_date is None or s3.Bucket(newList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            try:
                destBucket = newList[0]
                dest = newObj.replace(newList[0]+'/','')
                source = oldObj
               # print(currentBucket,source,destBucket,dest, 'this one 5')
                s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                tmpList = source.split('/')
                if len(tmpList) == 1:
                    keyToDel = source
                else:
                    keyToDel = '/'.join(tmpList[1:])
                s3.meta.client.delete_object(Bucket=oldList[0], Key=keyToDel)
                return
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "NoSuchKey":
                    print('error: object does not exist')
                else:
                    raise
            return

        if (len(oldList) == 2 and len(newList) == 1) and (oldPath == 1): #bucket to current directory : GOOD
            bucket2 = s3.Bucket(oldList[0])
            #print('this timeeee')
            if(s3.Bucket(oldList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            try:
                curDir = wd.replace('s3:/'+currentBucket,'')
                destBucket = currentBucket
                if curDir != '':
                    curDir = curDir[1:] + '/'
                dest = curDir+newObj
                source = oldObj
              #  print(currentBucket,source,destBucket,dest)
                s3.meta.client.copy_object(CopySource=source, Bucket=destBucket, Key=dest)
                tmpList = source.split('/')
                if len(tmpList) == 1:
                    keyToDel = source
                else:
                    keyToDel = '/'.join(tmpList[1:])
                s3.meta.client.delete_object(Bucket=oldList[0], Key=keyToDel)
                return
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "NoSuchKey":
                    print('error: object does not exist')
                else:
                    raise
            return
    return


def rm(objName): #pretty sure this is good

    s3 = boto3.resource('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
    fix = objName.split('/')
    oldPath = 0
    if fix[0] == 's3:':
        fix.pop(0)
        objName = '/'.join(fix)
        oldPath = 1

    if rootFlag == 1:
        objList = objName.split('/')
        if len(objList) == 2 and oldPath == 1: #rm from a bucket
            if(s3.Bucket(objList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            try:
                s3.meta.client.delete_object(Bucket=objList[0], Key=objList[1])
            except:
                print('error: Bad request')
                return
            return
        elif len(objList) > 2 and oldPath == 1: #rm from path
            if(s3.Bucket(objList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            keyToFind = '/'.join(objList[1:-1])+'/'
            pathBucket = s3.Bucket(objList[0])
            objs = list(pathBucket.objects.filter(Prefix=keyToFind))
            #print(keyToFind)
           # print(objs)
            if len(objs) > 0 and objs[0].key == keyToFind:
                keyToDel = '/'.join(objList[1:]) 
                try:
                    s3.meta.client.delete_object(Bucket=objList[0], Key=keyToDel)
                except:
                    print('error: Bad request')
                    return
                return  
            else:
                print('error: no such file or directory: bad folder')
    elif rootFlag == 0:
        objList = objName.split('/')
        currentBucket = wd.split('/')[1]
        #print(objList)
        if len(objList) == 1: #remove from current directory
            #print(currentBucket, 'here')
            curDir = wd.replace('s3:/'+currentBucket,'') 
            if(s3.Bucket(currentBucket).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            if curDir == '':
                try:
                    s3.meta.client.delete_object(Bucket=currentBucket, Key=objList[0])
                except:
                    print('error: Bad request')
                    return
            else:
                try:
                    s3.meta.client.delete_object(Bucket=currentBucket, Key=curDir[1:]+'/'+objList[0])
                except:
                    print('error: Bad request')
                    return
            return
        elif len(objList) == 2 and oldPath == 1: #remove from bucket
            if(s3.Bucket(objList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            try:
                s3.meta.client.delete_object(Bucket=objList[0], Key=objList[1])
            except:
                print('error: Bad request')
                return
            return
        elif len(objList) > 2 and oldPath == 1: #remove from path
            if(s3.Bucket(objList[0]).creation_date is None):
                print('error: no such file or directory : bad bucket')
                return
            keyToFind = '/'.join(objList[1:-1])+'/'
            pathBucket = s3.Bucket(objList[0])
            objs = list(pathBucket.objects.filter(Prefix=keyToFind))
            if len(objs) > 0 and objs[0].key == keyToFind:
                keyToDel = '/'.join(objList[1:]) 
                try:
                    s3.meta.client.delete_object(Bucket=objList[0], Key=keyToDel)
                except:
                    print('error: Bad request')
                    return
                return
            else:
                print('error: no such file or directory: bad folder')

    return

def loginCmd(creds): #pretty sure this is good
    global ACCESS_KEY
    global SECRET_KEY
    global REGION

    if(len(creds) == 1):
        try:
            ACCESS_KEY= config['DEFAULT']['AccessKey']
            SECRET_KEY= config['DEFAULT']['SecretKey']
            REGION= config['DEFAULT']['Region']
        except:
            print('User does not exist')
    elif(len(creds) == 2):
        try:
            ACCESS_KEY= config[str(creds[1])]['AccessKey']
            SECRET_KEY= config[str(creds[1])]['SecretKey']
            REGION= config[str(creds[1])]['Region']
        except:
            print('User does not exist')




def startProg(): #pretty sure this is good
    print(wd+'> ', end='')
    inputStr = input().split()
    if not inputStr:
        startProg()
    while(str(inputStr[0]) != 'logout' and str(inputStr[0]) !='quit' and str(inputStr[0]) !='exit'):

        if(str(inputStr[0]) == 'mkbucket'):
            if len(inputStr) < 2 or len(inputStr) > 2:
                print('Invalid agruments')
            else:
                makeBucket(str(inputStr[1]))
        if(str(inputStr[0]) == 'ls'):
            if(len(inputStr)<2):
                listBucks(None)
            else:
                listBucks(str(inputStr[1]))
        if(str(inputStr[0]) == 'mkdir'):
            if len(inputStr) < 2 or len(inputStr) > 2:
                print('error: invalid arguments')
            else:
                if(str(inputStr[1]) != '/'):
                    makeDir(str(inputStr[1]))
                else:
                    print("error: invalid name")
        if(str(inputStr[0]) == 'pwd'):
            pwd()
        if(str(inputStr[0]) == 'cd'):
            if len(inputStr) < 2 or len(inputStr) > 2:
                pass
            else:
               cd(str(inputStr[1]))
        if(str(inputStr[0]) == 'rmdir'):
            if len(inputStr) < 2 or len(inputStr) > 3:
                print('error: invalid arguments')
            else:
               rmDir(inputStr)
        if(str(inputStr[0]) == 'upload'):
            if len(inputStr) < 3 or len(inputStr) > 4:
                print('error: invalid arguments')
            else:
                upload(str(inputStr[1]),str(inputStr[2]))
        if(str(inputStr[0]) == 'download'):
            if len(inputStr) < 3 or len(inputStr) > 4:
                print('error: invalid arguments')
            else:
                download(str(inputStr[1]),str(inputStr[2]))
        if(str(inputStr[0]) == 'cp'):
            if len(inputStr) < 3 or len(inputStr) > 4:
                print('error: invalid arguments')
            else:
                cp(str(inputStr[1]),str(inputStr[2]))
        if(str(inputStr[0]) == 'mv'):
            if len(inputStr) < 3 or len(inputStr) > 4:
                print('error: invalid arguments')
            else:
                mv(str(inputStr[1]),str(inputStr[2]))
        if(str(inputStr[0]) == 'rm'):
            if len(inputStr) < 2 or len(inputStr) > 3:
                print('error: invalid arguments')
            else:
                rm(str(inputStr[1]))
        if(str(inputStr[0]) == 'login'):
            loginCmd(inputStr)


        
        print(wd+'> ', end='')
        inputStr = input().split()



def main(): #pretty sure this is good
    global flag

    while (flag == 1):
        print('> ', end='')
        inputStr = input().split()
        if not inputStr:
            continue
        elif str(inputStr[0]) == 'logout' or str(inputStr[0]) =='quit' or str(inputStr[0]) =='exit':
            exit()
        elif inputStr[0] != 'login':
            print("Invalid command")
        elif len(inputStr) > 2:
            print("Invalid, Too many agruments")
        else:
            flag = 0

    #this will call the function, checks for login
    global ACCESS_KEY
    global SECRET_KEY
    global REGION
    
    if inputStr[0] == 'login' and len(inputStr) == 1 :
        #print("use default values from config.ini")
        try:
            ACCESS_KEY= config['DEFAULT']['AccessKey']
            SECRET_KEY= config['DEFAULT']['SecretKey']
            REGION= config['DEFAULT']['Region']
        except:
            print('User does not exist')
            flag = 1
            main()
        startProg()

    elif inputStr[0] == 'login' and len(inputStr) == 2:
        print("use username: " + inputStr[1])
        try:
            ACCESS_KEY= config[str(inputStr[1])]['AccessKey']
            SECRET_KEY= config[str(inputStr[1])]['SecretKey']
            REGION= config[str(inputStr[1])]['Region']
        except:
            print('User does not exist')
            flag = 1
            main()
        startProg()
    
    

#start
if __name__ == "__main__":
    main()


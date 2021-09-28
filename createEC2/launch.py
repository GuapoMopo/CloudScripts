#######################################################
# Paul Wasilewicz                                     #
# 1007938                                             #
# CIS*4010 A2                                         #
#######################################################



import boto3
import csv
from collections import defaultdict



ec2 = boto3.resource('ec2','us-east-1')

def makeInstances(tempLine, instaLine, conList, location): #create instances from template 

    keyName = instaLine[2][:-4]
    print('Creating: '+keyName)
    try: #Creates the key pairs, if they exist then it just carries on
        keyPair = ec2.create_key_pair(KeyName = keyName)
        KeyPairOut = str(keyPair.key_material)
        with open(instaLine[2],'w') as outfile: #writes the key pair to a file in the current directory
            outfile.write(KeyPairOut)
    except:
        print(keyName+' exists')

    check = location.replace('Docker hub','') #this is a special case for a user on docker hub
    if len(check) != 0:
        check = check[1:]
        check = check+'/'

    #Scripts to install Docker on each operating system

    installDockerAL2 = '''#!/bin/bash
    yum update -y ; amazon-linux-extras install docker ; service docker start ; usermod -a -G docker ec2-user'''
    
    installDockerUbun = '''#! /bin/bash
    apt-get update -y ; apt-get install -y docker.io ; usermod -a -G docker ubuntu'''

    installDockerSu = '''#! /bin/bash
    zypper install docker ; systemctl enable docker ; usermod -a -G docker ec2-user ; systemctl restart docker'''

    #Create the html page and set up the nginx stuff and run the server
    nginxWebpageUbun = '''
    cd /home/ubuntu/
    mkdir /home/ubuntu/webcontent ; echo '<html><body>It works!</body></html>' > /home/ubuntu/webcontent/index.html ; chmod 666 /home/ubuntu/webcontent/index.html ; echo $'FROM nginx\\nCOPY webcontent /usr/share/nginx/html' > /home/ubuntu/Dockerfile ; docker build -t some-content-nginx . ; docker run --name some-nginx -d -p 8080:80 some-content-nginx'''
    nginxWebpageAL2 = '''
    cd /home/ec2-user/
    mkdir /home/ec2-user/webcontent ; echo '<html><body>It works!</body></html>' > /home/ec2-user/webcontent/index.html ; chmod 666 /home/ec2-user/webcontent/index.html ; echo $'FROM nginx\\nCOPY webcontent /usr/share/nginx/html' > /home/ec2-user/Dockerfile ; docker build -t some-content-nginx . ; docker run --name some-nginx -d -p 8080:80 some-content-nginx'''
    
    #Looks in the necessary container and adds it the script to pull
    containerScript = ''
    for con in conList:
        if len(check) != 0 and con == 'hellocloud': #okay so this doesnt work cause it'll attach check to the first one and not the correct one
            containerScript = containerScript + ' ; docker pull '+check+con
            check = ''
        else:
            containerScript = containerScript + ' ; docker pull '+con
    
    

    scriptToSendAL = installDockerAL2 + containerScript + nginxWebpageAL2
    scriptToSendUbun = installDockerUbun + containerScript + nginxWebpageUbun
    scriptToSendSu = installDockerSu + containerScript

    #Amazon linux 2
    if tempLine[1] == 'ami-0947d2ba12ee1ff75': 
        print('Creating: ',instaLine[1]+'...')
        try:
            instances = ec2.create_instances(
                BlockDeviceMappings=[
                {
                    'DeviceName':'/dev/xvda',
                    'Ebs': {'VolumeSize' : int(tempLine[3])}
                }
                ],  
                ImageId=tempLine[1],
                MinCount=1,
                MaxCount=1,
                InstanceType=tempLine[2],
                KeyName=instaLine[2][:-4],
                SecurityGroups=[
                    str(tempLine[4])
                ],
                UserData=scriptToSendAL
            )
            instances[0].wait_until_running()
            print('Done.')
        except:
            print('Unable to create instance ', instaLine[1])
            return
    #Ubuntu
    elif tempLine[1] == 'ami-0dba2cb6798deb6d8':
        print('Creating: ',instaLine[1]+'...')
        try:
            instances = ec2.create_instances(
                BlockDeviceMappings=[
                {
                'DeviceName':'/dev/sda1',
                    'Ebs': {'VolumeSize' : int(tempLine[3])}
                }
                ],  
                ImageId=tempLine[1],
                MinCount=1,
                MaxCount=1,
                InstanceType=tempLine[2],
                KeyName=instaLine[2][:-4],
                SecurityGroups=[
                    str(tempLine[4])
                ],
                UserData=scriptToSendUbun
            )
            instances[0].wait_until_running()
            print('Done.')
        except:
            print('Unable to create instance ', instaLine[1])
            return
    else: 
        print('Creating: ',instaLine[1]+'...')
        #Suse
        try:
            instances = ec2.create_instances( 
                ImageId=tempLine[1],
                MinCount=1,
                MaxCount=1,
                InstanceType=tempLine[2],
                KeyName=instaLine[2][:-4],
                SecurityGroups=[
                    str(tempLine[4])
                ],
                UserData=scriptToSendSu
            )
            instances[0].wait_until_running() 
            print('Done.')
        except:
            print('Unable to create instance ', instaLine[1])
            return
    for instance in instances: #create tage for each instance from instances.csv
        print('Creating tags for ', instaLine[1])
        ec2.create_tags(Resources=[instance.id], Tags=[{'Key':'Name', 'Value': str(instaLine[1])}])

    return

def parser():
    instanceNum = []
    tempData = []
    instaData = []
    conData = []
    i = 0

    with open("template.csv") as csv_file: #puts template file in a 2d array
        csvReader = csv.reader(csv_file, delimiter=',')
        for tempRow in csvReader:
            instanceNum.append(0)
            tempData.append(tempRow)
            with open("instances.csv") as csv_file: #instances file in a 2d array and counts how many occurences of each vm to make
                csvReader = csv.reader(csv_file, delimiter=',')
                for instanRow in csvReader:
                    if i == 0:
                        instaData.append(instanRow)
                    if tempRow[0] == instanRow[0]:
                        instanceNum[i] += 1

            i += 1

    conData = list(csv.reader(open("container.csv"))) #container.csv into 2d array
    containerDict = defaultdict(list)
    for i in range(0,len(conData)): #makes a dictionary for the docker images
        tmpList = [conData[i][1],conData[i][2]]
        containerDict[conData[i][0]].append(conData[i][1])


    i = 0
    total = sum(instanceNum)
    j=0
    breakVar = instanceNum[0]

    for i in range(0, len(tempData)): #send information for each instance to create
        while(j <= total):
            for temp in conData:
                if temp[0] == instaData[j][3]:
                    locationToSend = temp[2]
                    continue
            makeInstances(tempData[i], instaData[j], containerDict[instaData[j][3]], locationToSend)
            j+=1
            if j == breakVar:
                try:
                    breakVar += instanceNum[i+1]
                except:
                    pass
                break

    return

def main():
    parser()


if __name__ == "__main__":
    main()
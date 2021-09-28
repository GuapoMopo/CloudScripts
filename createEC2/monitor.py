#######################################################
# Paul Wasilewicz                                     #
# 1007938                                             #
# CIS*4010 A2                                         #
#######################################################




import boto3
import os
import subprocess

ec2 = boto3.resource('ec2','us-east-1')
ec2Cli = boto3.client('ec2','us-east-1')



def monitor():


    print('\n')
    print('{:^15}{:^23}{:^15}{:^25}{:^15}{:^23}{:^20}{:^18}{:^13}'.format('STATE','INSTANCE ID','INSTANCE NAME', 'IMAGE ID', 'INSTANCE TYPE','SECURITY GROUP NAME','SECURITY GROUPID','IP ADDRESS', 'KEY NAME'))
    for instance in ec2.instances.all():
        #Start of ssh commands
        ALcommand = 'ssh -o StrictHostKeyChecking=no -i'
        Ubuncommand = 'ssh -o StrictHostKeyChecking=no -i'
        Susecommand = 'ssh -o StrictHostKeyChecking=no -i'

        if not instance.security_groups: #some error checking
            security = 'offline'
            securityID = 'offline'
        else:
            security = str(instance.security_groups[0]['GroupName'])
            securityID = str(instance.security_groups[0]['GroupId'])
        if instance.public_ip_address == None: #more error checking
            ipAdd = 'offline'
        else:
            ipAdd = str(instance.public_ip_address)
        if instance.tags is None: #error checking
            tag = ''
        else:
            tag = str(instance.tags[0]['Value'])

        #Get info to run the ssh command
        if instance.state['Name'] == 'running':
            if instance.image_id == 'ami-0947d2ba12ee1ff75': #Amazon linux ssh command
                inKey = instance.key_name
                inUser = 'ec2-user'
                inPubDNS = instance.public_dns_name
                ALcommand = ALcommand + ' "'+inKey+'.pem'+'" '+inUser+'@'+inPubDNS+' sudo docker image ls'
                response = subprocess.check_output(ALcommand, shell=False)
                response = response.split()
            elif instance.image_id == 'ami-0dba2cb6798deb6d8': #Ubuntu ssh command
                inKey = instance.key_name
                inUser = 'ubuntu'
                inPubDNS = instance.public_dns_name
                Ubuncommand = Ubuncommand + ' "'+inKey+'.pem'+'" '+inUser+'@'+inPubDNS+' sudo docker image ls'
                response = subprocess.check_output(Ubuncommand, shell=False)
                response = response.split()
            elif instance.image_id == 'ami-0a782e324655d1cc0': #Suse ssh command
                inKey = instance.key_name
                inUser = 'ec2-user'
                inPubDNS = instance.public_dns_name
                Susecommand = Susecommand + ' "'+inKey+'.pem'+'" '+inUser+'@'+inPubDNS+' sudo docker image ls'
                response = subprocess.check_output(Susecommand, shell=False)
                response = response.split()
        
        #table formatting
        print(' _______________________________________________________________________________________________________________________________________________________________________')
        print('{:<1}{:^15}{:^23}{:^15}{:^25}{:^15}{:^23}{:^20}{:^18}{:^13}{:<1}'.format('|',str(instance.state['Name']),instance.id, tag,instance.image_id, instance.instance_type, security,securityID,ipAdd, instance.key_name,'|'))
        print('|_______________________________________________________________________________________________________________________________________________________________________|')
        if instance.state['Name'] == 'running': #only search for containers in running instances cause terminated ones don't have a live ip
            print('|    {:^43}{:^50}{:<30}{:>45}'.format('CONTAINER(S)', 'IMAGE ID','SIZE','|'))
            for i in range(6,len(response),7):
                try: #Get fields from docker image ls
                    conPrint = str(response[i])[2:-1]
                    imagePrint = str(response[i+2])[2:-1]
                    sizePrint = str(response[i+6])[2:-1]
                except:
                    print('An error occured printing')
                    break
                print('|                   {:<49}{:<29}{:<30}{:>45}'.format(conPrint,imagePrint,sizePrint,'|'))
        print('|_______________________________________________________________________________________________________________________________________________________________________|')


    
    return


def main():
    monitor()

    return


if __name__ == "__main__":
    main()
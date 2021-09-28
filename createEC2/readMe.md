#######################################################
# Paul Wasilewicz                                     #
# 1007938                                             #
# CIS*4010 A2                                         #
#######################################################

Part 1: 
    
    launch.py

        Python modules:
            import boto3
            import csv
            from collections import defaultdict
        
        To run:
            python3 launch.py

            My program will first parse each .csv file and grab the info I need and put it in list and dictionaries, it'll then create the keys, and write them to a file in the current directory, if the key exists then it prints exists and carries on. It'll start instantiating each container and install the required container using the userdata field. I also tried my best to print what the program is doing at each step, but since I didn't use an ssh library to install Docker and did everything through UserData field by creating the scripts dynamically, I couldn't stream the output like others said they were doing. I just wanted to keep libraries to a minimum, hope that's alright. Everything should work properly. Oh it takes some time, the Amazon linux and Ubuntu vm's take 3-5 minutes but I also did a Suse os for extra marks a that one takes like 5-7 minutes.

    monitor.py
    
        Python modules:
            import boto3
            import os
            import subprocess

        To run: 
            python3 monitor.py

            This does everything specified, on run it'll print a table with each VM and some of there fields('STATE','INSTANCE ID','INSTANCE NAME', 'IMAGE ID', 'INSTANCE TYPE','SECURITY GROUP NAME','SECURITY GROUPID','IP ADDRESS', 'KEY NAME') and then the VM's underneath, then I did a nested table for each VM for there containers, this lists ('CONTAINER(S)', 'IMAGE ID','SIZE') and then the program exits. 

            ex.
            STATE       INSTANCE ID     INSTANCE NAME       IMAGE ID     INSTANCE TYPE       SECURITY GROUP NAME    SECURITY GROUPID      IP ADDRESS     KEY NAME
                    
                        CONTAINER(S)        IMAGE ID        SIZE

Part 2: 
    Part2.pdf
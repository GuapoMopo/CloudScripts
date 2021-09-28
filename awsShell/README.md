Paul Wasilewicz 1007938


General:

Part 1: awsS3Shell.py

    Python Modules:
        import boto3
        import botocore
        import configparser

    ***for all command that would use total path name. My total pathname uses s3:/(ex. s3:/bucket/folder/file) and will not work without the s3:/
        I had relative paths before but then I asked and was told total pathname includes s3:/ and I changed it and then you guys said we could use relative but I didn't want to change it back.

    login:
        Login will use default user if none specified and can be swapped to another user if you try to login again. It'll through an error message if the user doesn't exist
    logout/exit/quit:
        These will all terminate the program from wherever you are
    mkbucket:
        It'll make an S3 bucket at the root, you can call it from any directory and it'll make it at the root. 
        It'll through an error if the bucket exists or invalid name
    ls <-l>:
        It'll list directories and then files in your current directory, -l will list size, file type, date of creation.
    pwd:
        Prints working directory, no biggie.
    cd:
        cd does it all. 
            ~ 
                goes to root
            .. 
                will go back one directory
            ../../.. 
                will go back as many directories as specified
            cd dir 
                will go to that directory
            cd dir/subdir  
                works and will go as far as you specify, this can be done from the root level
    mkdir: 
        Makes a new directory where you currently are and cannot be created at the root, it'll through an error message
    rmdir: 
        this will remove folders, if the folder is not empty then a message will pop up telling you it's not empty and to use the -p flag
        -p: will remove folder and everything inside
    upload:
        this does as specified and should work properly
    download:
        this does as specified and should work properly
    cp:
        now I'm not proud of this function and it definitely could've be done better but it works
    mv: 
        not proud of this one either cause it's basically the same as cp and these two function are like half my code but it works as well
    rm:
        this function works and will remove from current directory or specified total path

Part 2: DynamoDB

    loadTable.py 
        Python Modules:
            import boto3
            import csv
            import sys
            from decimal import Decimal


            run: python3 loadTables.py should work
                It'll prompt for a filename and table name
                It works with either STDIN or on the commandline so you choose!
                Oh it also takes a minute so
            -Primary Key: commodity (I realized I used the wrong primary key but its kind of too late)
            -Field/Attribute Names:
            -encodings loaded by loadTable.py: no
                I didn't use a program to load encoding.csv cause I had questions about it and didn't really want to wait, so I just copy and pasted them into a python dictionary and then check to see if the entered shortform (ex. WT) exists and if it didn't then I reverse the dictionary and check to see if the entered longform (ex. Wheat) and if that doesn't either then I reloop and ask for input.
            Error conditions:
                Does all the basic error checking 
                If table exists it throws an error

    queryOECD.py

        Python Modules:
            import boto3
            from boto3.dynamodb.conditions import Key, Attr
            import os
            from decimal import Decimal
            import sys

            run: python3 queryOECD.py should work
                It'll prompt for a commodity
                It works with either STDIN or on the commandline so you choose again!

            Error conditions:
                If invalid commodity then it just reloops


Comments/Instructions
I'm pretty sure you'll know how to use it, there's nothing crazy in here
I hope you enjoy! Thanks
import boto3
import csv
import sys
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

def createtable(tabName):

    tableN = tabName
    createdTables = dynamodb.meta.client.list_tables()['TableNames']

    if tableN not in createdTables:
        table = dynamodb.create_table(
            TableName = tableN,
            KeySchema=[
                {
                    'AttributeName' : 'commodity',
                    'KeyType' : 'HASH'
                },
                {
                    'AttributeName' : 'value',
                    'KeyType' : 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName' : 'commodity',
                    'AttributeType' : 'S'
                },
                {
                    'AttributeName' : 'value',
                    'AttributeType' : 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits' : 5,
                'WriteCapacityUnits' : 5
            }
        )
        print('Creating table...')
        table.meta.client.get_waiter('table_exists').wait(TableName=tableN)
    else:
        print('Table already exists')
        table = dynamodb.Table(tabName)
        #print(table.item_count)
    
    return

def addToTable(filename, tabName):

    try:
        with open(filename) as csvfile:
            print('Populating',tabName,'table...')
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                table = dynamodb.Table(tabName)
                table.put_item(
                    Item={
                        'commodity' : row[0],
                        'variable' : row[1],
                        'year' : row[2],
                        'units' : row[3],
                        'mfactor' : row[4],
                        'value' : Decimal(row[5])
                    }
                )
    except:
        print('Invalid File')
        return

    return

def main(filename, tabname):
    if filename == None or tabname == None: 
        while(1):
            print('Enter a Filename and a Table name(exit to exit): ', end='')
            myList = input().split(' ')
            if len(myList) == 1:
                if myList[0] == 'exit':
                    return
            if(len(myList) != 2):
                print('error: Invalid arguments')
            else:
                createtable(myList[1])
                addToTable(myList[0], myList[1])
    else:
        createtable(tabname)
        addToTable(filename, tabname)

    return

if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    else:
        main(None, None)

    sys.exit(0)
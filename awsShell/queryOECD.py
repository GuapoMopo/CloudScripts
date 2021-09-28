import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
from decimal import Decimal
import sys

#the formatting could be fixed to look a little nicer

dynamodb = boto3.resource('dynamodb')

codes = {
    'BD' : 'Biodiesel',
    'BT' : 'Butter',
    'BV' : 'Beef and veal',
    'CA' : 'Casein',
    'CH' : 'Cheese',
    'CT' : 'COTTON',
    'DDG' : 'Distiller\'s dry grains',
    'ET' : 'Ethanol',
    'FDP' : 'Fresh dairy products',
    'FH' : 'Fish',
    'FHA' : 'Fish from aquaculture',
    'FHC' : 'Fish from capture',
    'FL' : 'Fish oil',
    'FM' : 'Fish meal',
    'FT' : 'Fertilizer',
    'HFCS' : 'High fructose corn syrup',
    'MA' : 'Maize',
    'MK' : 'Milk',
    'MOL' : 'Molasses',
    'OCG' : 'Other coarse grains',
    'OIL' : 'Oil',
    'OOS' : 'Other oilseeds',
    'PK' : 'Pigmeat',
    'PM' : 'Protein meals',
    'PS' : 'PULSES',
    'PT' : 'Poultry meat',
    'RI' : 'Rice',
    'RT' : 'ROOTS AND TUBERS',
    'SB' : 'Soybean',
    'SBE' : 'Sugar beet',
    'SCA' : 'Sugar cane',
    'SH' : 'Sheepmeat',
    'SMP' : 'Skim milk powder',
    'SU' : 'Sugar',
    'SUR' : 'Raw sugar',
    'SUW' : 'White sugar',
    'VL' : 'Vegetable oils',
    'WMP' : 'Whole milk powder',
    'WT' : 'Wheat',
    'WYP' : 'Whey powder'
}
varCodes = {
    'AH' : 'Area harvested',
    'BF' : 'Biofuel use',
    'CI' : 'Cow inventory',
    'CR' : 'Crush',
    'EX' : 'Exports',
    'FE' : 'Feed',
    'FO' : 'Food',
    'IM' : 'Imports',
    'NT' : 'Trade balance',
    'OU' : 'Other use',
    'PC' : 'Human consumption per capita',
    'PP' : 'Producer price',
    'QC' : 'Consumption',
    'QP' : 'Production',
    'QP__MA' : 'Ethanol production from maize',
    'QP__SCA' : 'Ethanol production from sugar cane',
    'QP__VL' : 'Biodiesel production from vegetable oil',
    'ST' : 'Ending stocks',
    'XP' : 'World Price',
    'YLD' : 'Yield'
}

def search(comm):

    varList = []
    yearList = []
    canTable = dynamodb.Table('canada')
    usaTable = dynamodb.Table('usa')
    mexicoTable = dynamodb.Table('mexico')
    naTable = dynamodb.Table('northamerica')
    canFinal = 0
    mexFinal = 0
    usaFinal = 0
    naFinal = 0

    longForm = codes.get(comm)
    shortForm = comm
    if longForm == None: 
        longForm = comm
        revCode = {value : key for (key,value) in codes.items()}
        shortForm = revCode.get(comm)
        if shortForm == None:
            return

    naResponse = naTable.scan(
        FilterExpression=Attr('commodity').eq(shortForm)
    )

    for x in naResponse['Items']: #gets all the variables and years in north america
        varList.append(x['variable'])
        yearList.append(x['year'])

    yearList = list(set(yearList))
    yearList.sort()
    varList = list(set(varList))
    varList.sort()
    cc1 = 0
    cc2 = 0
    cc3 = 0
    print('Commodity:', longForm)
    for i in varList:
        c1 = 0
        c2 = 0
        c3 = 0
        print('Variable: ',varCodes[i])
        print('{:<10}{:<17}{:<17}{:<17}{:<17}{:<17}{:<17}{:<17}'.format('Year','North America','Canada','USA','Mexico','CAN+USA','CAN+USA+MEX','NADefn'))
        #print('Year\tNorth America\t Canada\t USA\t\t Mexico\t\t CAN+USA\t\tCAN+USA+MEX\tNADefn')
        for j in yearList:
            canResponse = canTable.query(
                KeyConditionExpression=Key('commodity').eq(shortForm), FilterExpression=Attr('variable').eq(i) & Attr('year').eq(j)
            )
            usaResponse = usaTable.query(
                KeyConditionExpression=Key('commodity').eq(shortForm), FilterExpression=Attr('variable').eq(i) & Attr('year').eq(j)
            )
            mexResponse = mexicoTable.query(
                KeyConditionExpression=Key('commodity').eq(shortForm), FilterExpression=Attr('variable').eq(i) & Attr('year').eq(j)
            )
            naResponse = naTable.query(
                KeyConditionExpression=Key('commodity').eq(shortForm), FilterExpression=Attr('variable').eq(i) & Attr('year').eq(j)
            )
            if canResponse['Items']:
                canValue = Decimal(canResponse['Items'][0]['value'])
                mult = Decimal(canResponse['Items'][0]['mfactor'])
                canFinal = Decimal(canValue).shift(mult)
            if usaResponse['Items']:
                usaValue = Decimal(usaResponse['Items'][0]['value'])
                mult = Decimal(usaResponse['Items'][0]['mfactor'])
                usaFinal = Decimal(usaValue).shift(mult)
            if mexResponse['Items']:
                mexValue = Decimal(mexResponse['Items'][0]['value'])
                mult = Decimal(mexResponse['Items'][0]['mfactor'])
                mexFinal = Decimal(mexValue).shift(mult)
            if naResponse['Items']:
                naValue = Decimal(naResponse['Items'][0]['value'])
                mult = Decimal(naResponse['Items'][0]['mfactor'])
                naFinal = Decimal(naValue).shift(mult)
            
            #print('{:<4s}{:>18}{:>9}{:>13}{:>19}{:>17}{:>20}{:>10}'.format(j,naFinal,canFinal,usaFinal,mexFinal,canFinal+usaFinal,canFinal+usaFinal+mexFinal,'tbd'))

            if canFinal+usaFinal == naFinal:
                naDef = 'CAN+USA'
                c1 += 1
            elif canFinal+usaFinal+mexFinal == naFinal:
                naDef = 'CAN+USA+MEX'
                c2 += 1
            else:
                naDef = 'Neither'
                c3 += 1
            print('{:<10}{:<17}{:<17}{:<17}{:<17}{:<17}{:<17}{:<17}'.format(j,round(naFinal,3),round(canFinal,3),round(usaFinal,3),round(mexFinal,3),round(canFinal+usaFinal,3),round(canFinal+usaFinal+mexFinal,3),naDef))
            #print(j,'\t',round(naFinal,3),'\t',round(canFinal,3),'\t',round(usaFinal,3),'\t',round(mexFinal,3),'\t',round(canFinal+usaFinal,3),'\t',round(canFinal+usaFinal+mexFinal,3),'\t',naDef)

        print('North America Definition Results:', c1, 'CAN+USA,', c2, 'CAN+USA+MEX,', c3,'Neither')
        if (c1 >= c2) and (c1 >= c3):
            print('Therefore we conclude North America = CAN+USA')
        elif (c2 >= c1) and (c2 >= c3):
            print('Therefore we conclude North America = CAN+USA+MEX')
        else:
            print('Therefore we conclude North America = Neither')
        cc1 = cc1 + c1
        cc2 = cc2 + c2
        cc3 = cc3 + c3
    print('Overall North America Definition Results:', cc1, 'CAN+USA,', cc2, 'CAN+USA+MEX,', cc3,'Neither')
    if (cc1 >= cc2) and (cc1 >= cc3):
        print('Conclusion for all '+longForm+' variable, North America = CAN+USA')
    elif (cc2 >= cc1) and (cc2 >= cc3):
        print('Conclusion for all '+longForm+' variable, North America = CAN+USA+MEX')
    else:
        print('Conclusion for all '+longForm+' variable, North America = Neither')

    return

def main(arg1):

    if arg1 == None:
        while(1):
            print('Enter the code for commodity(exit to exit): ',end='')
            comm = input()
            if(comm == 'exit'):
                return
            elif comm != '':
                search(comm)
    else:
        search(arg1)
        while(1):
            print('Enter the code for commodity(exit to exit): ',end='')
            comm = input()
            if(comm == 'exit'):
                return
            elif comm != '':
                search(comm)

    return

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main(None)


    sys.exit(0)
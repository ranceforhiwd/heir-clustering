import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import FeatureAgglomeration
from sklearn.metrics import pairwise_distances
from sklearn.cluster import KMeans
import re
from tabulate import tabulate
import us
from boto3.dynamodb.conditions import Key, Attr
newXcoord=[]
newYcoord=[]
newWcoord=[]
#vocabulary list
vocabulary = ['Street', 'state', 'zipcode', 'Road','Ave.,', 'Boulevard', 'route', 'PO', 'Box', 'APT', 'Lane']


def createPlot(c):
    finalx1 = []
    finaly1 = []

    for value in c:
                finalx1.append(int(value[0]))
                finaly1.append(int(value[1]))
    
    return [finalx1, finaly1]

def makeClusters(d, c):
    mycluster1 = []
    mycluster2 = []
    hc = AgglomerativeClustering(n_clusters=c, metric='euclidean', linkage='ward')
    l = hc.fit_predict(d)
    section1 = np.where(l == 0)
    section2 = np.where(l == 1)
    for pt in section1:
        for item in pt:
            mycluster1.append(d[item])

    for pt in section2:
        for item in pt:
            mycluster2.append(d[item])

    return [section1, mycluster1, section2, mycluster2]

#function to check states
def checkStates(state):
    us_states = []
    statesList = us.states.mapping('abbr', 'name')
    stateListObject = json.dumps(statesList)
    usStates = json.loads(stateListObject)

    for states in usStates:
        us_states.append(states)
        #loop through the states and find matches
        for i in range(len(us_states)):
            if state == us_states[i]:
                return True

#function to check zip code
#example format:
#1: 12345
#2: 12345-6789
def checkZipCode(code):
    isZipcode = re.compile('^\d{5}(?:[-]\d{4})?$')
    #validate code if it's numeric
    if isZipcode.search(code): 
        return True

#function to check street name
def checkStreetName(street):
    street_add = re.compile('^.*?\s[N]{0,1}([-a-zA-Z0-9]+)\s*\w*$')
    #validate street name
    if street_add.search(street):
        return True

#function to chunk list data
def chunk_address(arr):
    chunkAdd = []
    start = 0
    end = len(arr) 
    step = 7

    #loop thru
    for i in range(start, end, step): 
        x = i 
        #push the item to chunkAdd list
        chunkAdd.append(arr[x:x+step])
    return chunkAdd

#function to format address to json object
def format_add(add):
    #create an empty json object
    json_address = json.loads('{}')

    #make an arry list using numpy
    arr = np.array(add)
    
    #validate size of list
    if len(add) > 0:
        #loop thru the address object
        for a in range(len(add)):
            #key importants:
            #1. The a variable stands for the key/index of address example: 0,1,2 and so on... and str is the data type of python to convert int to string
            #2. The re(stands for the regex operation) the sub(stands for substitute/replace). This is same idea with PHP and JS.
            #3. The arr(stands for array from numpy).I used this inorder to easily get the values from 2-dimensional array

            #overall explaination,we create a json object with the values of address(with dynamic key) and assign the values to the address
            #being generated from the ML and I remove special characters from string.
            json_address['address_' + str(a)] = re.sub('[^A-Za-z0-9]+', '', arr[a,0]) +  ' ' + re.sub('[^A-Za-z0-9]+', '', arr[a,1]) + ' ' + re.sub('[^A-Za-z0-9]+', '', arr[a,2]) + ' ' + re.sub('[^A-Za-z0-9]+', '', arr[a,3]) + ' ' + re.sub('[^A-Za-z0-9]+', '', arr[a,4]) + ' ' + re.sub('[^A-Za-z0-9]+', '', arr[a,5]) + ' ' + re.sub('[^A-Za-z0-9]+', '', arr[a,6])
    
    #return the json address object
    return json_address

#function save appraisal address to db
def saveToDB(d):
    #validate size of list
    if len(d) > 0:
        #save item to db
        appraisalTbl.put_item(
            Item={
                    'appraisal_pk': 'appraisal',
                    'address': d
                }
            )
        print('Data save to DB!')
    else: 
        print('Error: DB Insertion Failed!')

#function check clusters
#params c1 - stands for cluster 1
#params c2 - stands for cluster 2
def check_clusters(c1,c2,wcoord,vocabulary,ycoord):
    #cluster data list
    clusterData1 = []
    clusterData2 = []

    #reverse the wcoord to check for cluster2 because its text is coming from bottom to top
    reverse_wcoord = wcoord[::-1] 

    #validate clusters1 data
    for i in range(len(c1[0])):
        #validate if the keyword exists in vocabulary,states and if the format match the zipcode
        if  wcoord[i] and wcoord[i] in vocabulary or checkStates(str(wcoord[i])) == True or checkZipCode(str(wcoord[i])) == True:
            #append the coordinates 
            clusterData1.append(ycoord[i])
    
    #validate for clusters2 data
    for i in range(len(c2[0])):
        #key importants:
        #1. For c2 we need to reverse the array to get the correct word

        #validate if the keyword exists in vocabulary,states and if the format match the zipcode
        if  reverse_wcoord[i] and reverse_wcoord[i] in vocabulary or checkStates(str(reverse_wcoord[i])) == True or checkZipCode(str(reverse_wcoord[i])) == True:
            #append the coordinates 
            clusterData2.append(ycoord[i])
    
    #validate length of each cluster
    if len(clusterData1) > 0:
        #return found coordinates and cluster 1 data
        return [clusterData1,c1[0]]
    else:
        #return found coordinates and cluster 2 data
        return [clusterData2,c2[0]]

#functions get the y coordinates
#params 
#cluster -selected cluster
#word - scanned word
#ycoord - ycoordinates
def get_y_coordinates(cluster,word, ycoord,vocabulary, font_size_height,xcoord,height,width):
    yValues = []
    print(ycoord)
    #loop through the clusters
    for i in range(len(word)):
        yValues1 = []
        if word[i] in vocabulary  or checkZipCode(str(word[i])) == True:
        #if word[i] in vocabulary:
            upper = ycoord[i] + font_size_height[i]
            lower = ycoord[i] - font_size_height[i]
            print(upper)
            exit()
            thetype = type(word[i])
            isnumberic = word[i].isnumeric()
            yValues1.append(word[i])
            yValues1.append(xcoord[i])
            yValues1.append(ycoord[i])
            yValues1.append(width[i])
            yValues1.append(height[i])
            yValues.append(yValues1)
    return yValues

#function get addresses
#param
#cluster - selected cluster
#yArr - arry of y coordinates
#ycoord - origin y coordinates coming from db
#wcoord - scan text from db
def get_addresses(cluster,yArr,ycoord,wcoord):
    addresses = []
    for j in range(len(yArr)):
        for i in range(len(wcoord)):
            # if (len(yValues) > 0 and ycoord[i] == yValues[0]) or (len(spaceList) > 0 and ycoord[i] == spaceList[0]) or (len(spaceList) > 0 and ycoord[i] == spaceList[1]):
            if (len(yArr) > 0 and ycoord[i] == yArr[j]):
                # thetype = type(wcoord[i])
                # isnumberic = wcoord[i].isnumeric()
                # print(wcoord[i]+ ': ' + str(thetype) + str(isnumberic) + ': ' + str(ycoord[i])) 
                # plt.annotate(wcoord[i], (var2[0][i] + 0.3, var2[1][i] + 0.9))
                addresses.append(wcoord[i])
    return addresses

#function to create login Session
def createSession(boto3):
    #create session with credentials
    sessionParam = boto3.Session(
    region_name = 'us-east-1',
    aws_access_key_id='AKIAZC6U4MOHHXX3YROM',
    aws_secret_access_key='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',
    )
    return sessionParam

#function to get record from db
def getRecordFromTable(session, dbName, tblName, fileName ):
    # Get the service resource.
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(dbName)

    #set the appraisal table
    appraisalTbl = dynamodb.Table(tblName)

    #test documents:
    #./stanford.pdf~23.png - standford
    #./inseptioncopy7771.pdf~01.png - inspection
    #./doc73.pdf~02.png - appraisal

    response = table.query(
        IndexName='pk-sk-index',
            KeyConditionExpression=Key('pk').eq('churchillrealestate'),
            FilterExpression=Attr('pngfilename').eq(fileName)
        )
    
    #t = response['Items'][0]['text']
    #return json.loads(t);
    return response['Items']

#function prepare data array
def preparteArrayWithCoordinatesBasedonWord(cluster,yArr,ycoord,wcoord,xcoord,height, width):
    addressDetails = []
    for j in range(len(yArr)):
        for i in range(len(wcoord)):
            # if (len(yValues) > 0 and ycoord[i] == yValues[0]) or (len(spaceList) > 0 and ycoord[i] == spaceList[0]) or (len(spaceList) > 0 and ycoord[i] == spaceList[1]):
            if (len(yArr) > 0 and ycoord[i] == yArr[j]):
                addresWithCoordinate = []
                addresWithCoordinate.append(xcoord[i]) 
                addresWithCoordinate.append(ycoord[i])
                addresWithCoordinate.append(height[i])
                addresWithCoordinate.append(width[i])
                addresWithCoordinate.append(wcoord[i])
                addressDetails.append(addresWithCoordinate)

    return addressDetails

#function save address results to markup table
def saveResultsInMarkupTable(session,data,fileName,dbName, tblName,pngFile):
    jsonData = format_add(data)
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(dbName)

    #set the appraisal table
    appraisalTbl = dynamodb.Table(tblName)
    if len(jsonData) > 0:
        #save item to db
        appraisalTbl.put_item(
            Item={
                    'pngname_pk': 'pngname_pk',
                    'pngname_sk': 'pngname_pk-'+pngFile,
                    'png_file_name': pngFile,
                    'pdf_file_name': fileName,
                    'json_data': jsonData
                }
            )
        print('Data save to DB!')
    else: 
        print('Error: DB Insertion Failed!')

#create Json Object
def format_add(add):
    #create an empty json object
    json_address = json.loads('{}')

    #make an arry list using numpy
    arr = np.array(add)
    
    #validate size of list
    if len(add) > 0:
        #loop thru the address object
        for a in range(len(add)):
            json_address['address_' + str(a)] = re.sub('[^A-Za-z0-9]+', '', arr[a,0]) +  ' ' + re.sub('[^A-Za-z0-9]+', '', arr[a,1]) + ' ' + re.sub('[^A-Za-z0-9]+', '', arr[a,2]) + ' ' + re.sub('[^A-Za-z0-9]+', '', arr[a,3]) + ' '+ re.sub('[^A-Za-z0-9]+', '', arr[a,4]) + ' '
            
    return json_address

#Validate final address
def validateAddress(data):
    for i in range(len(data)):    
        if data[i][4].startswith('(') or data[i][4].startswith('"') or data[i][4].startswith('[') or data[i][4].startswith('$') or data[i][4].startswith('%'):
            #print(data[i][4])
            data.pop(i)

    return data     

#Validate final address second time
def validateAddress2(data):
    
    for i in range(len(data)):
        if i + 1 < len(data):
            if checkZipCode(data[i][4]) == True:
                
                #print(data[i][4])
                if data[i - 1][4] in vocabulary or data[i + 1][4] in vocabulary or checkStates(str(data[i - 1][4])) == True or checkStates(str(data[i + 1][4])) == True:
                    print('')
                else:
                    data.pop(i)
 
    return data  

def checkXcoordinates(data,wcoord,xcoord):
    foundedXcoordinates = []
    for i in range(len(data)):
        word = data[i][0]
        xcord = data[i][1]
        ycord = data[i][2]
        for c in range(len(xcoord)):
            if(xcord == xcoord[c]):
                foundedXcoordinates.append(c)

    return foundedXcoordinates

def get_all_coordinates(cluster,word, ycoord,vocabulary, font_size_height,xcoord,height,width):
    yValues = []
    
    #loop through the clusters
    for i in range(len(word)):
        yValues1 = []
        if word[i]:
            thetype = type(word[i])
            isnumberic = word[i].isnumeric()
            yValues1.append(word[i])
            yValues1.append(xcoord[i])
            yValues1.append(ycoord[i])
            yValues1.append(width[i])
            yValues1.append(height[i])
            yValues.append(yValues1)
    return yValues

def get_y_coordinates2(cluster,word, ycoord,vocabulary, font_size_height,xcoord,height,width):
    yValues = []
    
    #loop through the clusters
    for i in range(len(word)):
        yValues1 = []
        if word[i] in vocabulary  or checkZipCode(str(word[i])) == True:
        #if word[i] in vocabulary:
            upper = ycoord[i] - font_size_height[i]
            lower = ycoord[i] + font_size_height[i]
            
            thetype = type(word[i])
            isnumberic = word[i].isnumeric()
            yValues1.append(word[i])
            yValues1.append(xcoord[i])
            yValues1.append(ycoord[i])
            yValues1.append(width[i])
            yValues1.append(height[i])
            yValues1.append(upper)
            yValues1.append(lower)
            yValues.append(yValues1)
    return yValues

def getAllupperwords(allCoordinates,yValues):
    upperwordList = []
    for i in range(len(yValues)):
        uppder = yValues[i][5]
        lower = yValues[i][6]
        ycoord = yValues[i][2]
        

        for j in range(len(allCoordinates)):
            ycoordAllwords = allCoordinates[j][2]
            if allCoordinates[j][2] >= uppder and allCoordinates[j][2] <= ycoord:
                upperwordList.append(allCoordinates[j][0])
    return upperwordList

def getAlllowerwords(allCoordinates,yValues):
    lowerwordList = []
    for i in range(len(yValues)):
        uppder = yValues[i][5]
        lower = yValues[i][6]
        ycoord = yValues[i][2]
        for j in range(len(allCoordinates)):
            ycoordAllwords = allCoordinates[j][2]
            if allCoordinates[j][2] <= lower and allCoordinates[j][2] >= ycoord:
                lowerwordList.append(allCoordinates[j][0])

    return lowerwordList
            
            

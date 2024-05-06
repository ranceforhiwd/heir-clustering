#!/usr/bin/env python3
from ml_functions import *
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import os
#get the env variable
pdfFullPath = os.environ["PNGFILENAME"]
print(pdfFullPath)
fileName = pdfFullPath.replace('"', '')

# Below is for local test
# fileName = './marinecopy321.pdf~06.png'
print(fileName)
session = createSession(boto3)

dbName = 'scan_pdf_content2'
tableName = 'appraisal'

#t = getRecordFromTable(session, dbName, tableName, fileName )
 
query_results_all = getRecordFromTable(session, dbName, tableName, fileName )
# print(query_results_all)
 
for query_results in query_results_all:
    pngFile = query_results['pngfilename']
    pngRecord = json.loads(query_results['text'])
    xcoord = []
    ycoord = []
    wcoord = []
    height = []
    width = []
    font_size = []
    font_size_height = []
    yValues = []
    upper = ''
    lower = ''
    original = ''
    spaceList = []
    addresses = []
    for x in pngRecord:
        if pngRecord[x].get('text'):
            xcoord.append(int(pngRecord[x].get('x')))
            ycoord.append(int(pngRecord[x].get('y')))
            height.append(int(pngRecord[x].get('height')))
            width.append(int(pngRecord[x].get('width')))
            font_size.append(pngRecord[x].get('font_size_px'))
            font_size_height.append(pngRecord[x].get('font_size_height_px'))
            wcoord.append(pngRecord[x].get('text'))
 
    #vocabulary list
    vocabulary = ['Street', 'state', 'zipcode', 'Road','Ave.,', 'Boulevard', 'route', 'PO', 'Box', 'APT', 'Lane', 'Round', 'Circle']
 
    data = list(zip(xcoord, ycoord))
    clusters = makeClusters(data, 2)
 
    # var1 = createPlot(clusters[1])
    var2 = createPlot(clusters[3])
 
    # Loop for annotation of all points
    yValues = get_y_coordinates(var2,wcoord,ycoord,vocabulary)
    # print(yValues)
 
    mylist = list(dict.fromkeys(yValues))
    # print(mylist)
 
    addresses = get_addresses(var2,mylist,ycoord,wcoord)
    # print(addresses)
 
    addressDetails = preparteArrayWithCoordinatesBasedonWord(var2,mylist,ycoord,wcoord,xcoord, height, width)

    addressDetailsNew = validateAddress(addressDetails)
    print(addressDetailsNew)
 
    tableName = 'markup'
    saveResultsInMarkupTable(session,addressDetailsNew,fileName,dbName, tableName,pngFile)
# add = chunk_address(addresses)
# print(add)
 
# jsonAdd = format_add(add)
# print(jsonAdd)
# # saveToDB(jsonAdd)
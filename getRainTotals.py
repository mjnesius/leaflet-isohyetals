#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      nesiusm
#
# Created:     17/10/2019
# Copyright:   (c) nesiusm 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import urllib2
import json
import xml.etree.ElementTree as etree
import arcpy

def ConvertDateFormat(sDate):
    sDate2 = sDate.replace('/','-')
    sDate3 = sDate2.split(' ')
    year = sDate3[0].split('-')[2]
    month = sDate3[0].split('-')[0]
    day = sDate3[0].split('-')[1]
    if 'PM' in sDate: hour = str(int(sDate3[1].split(':')[0])+12)
    else: hour = str(int(sDate3[1].split(':')[0]))
    minute = sDate3[1].split(':')[1]
##    second = sDate3[1].split(':')[2]
    newDate = '{0}-{1}-{2} {3}:{4}'.format(year, month, day, hour, minute)
##    newDate = '{0}-{1}-{2} {3}:{4}:{5}'.format(year, month, day, hour, minute, second)
    return newDate

def main(date_start, date_end):
    oneRainDataDict = {}
    nwfwmdDataDict = {}


    tz="edt"
##    date_start = "2019-10-14 17:00" # arcpy.GetParameterAsText(0) YYYY-MM-DD 24:00
##    date_end = "2019-10-15 23:00" # arcpy.GetParameterAsText(1) YYYY-MM-DD 24:00
    oneRainSysKey = "79cb5383-a4cb-467c-9e29-fe1ce57b6497"
    baseOneRainURL = "http://cs-022-exchange.onerain.com:8080/OneRain/DataAPI?method=GetSensorData"
    spc = (53 - len("Station Name"))*' '
    arcpy.AddMessage("\nStation Name{0}Rain Total".format(spc))

    # the list is [or_site_id, or_sensor_id]
    oneRainGetDict =	{
        "STREETS AND DRAINAGE (CITY ID# 300)": ["5","1"],
        "JAKE GAITHER GOLF COURSE (CITY ID# 500)": ["2","1"],
        "TALLAHASSEE CITY HALL (CITY ID# 100)": ["4","1"],
        "SENIOR CITIZEN CENTER (CITY ID# 200)": ["6","1"],
        "SOUTHWOOD GOLF COURSE (CITY ID# 600)" : ["1","1"],
        "HILAMAN GOLF COURSE (CITY ID# 400)": ["3","1"]
    }

    for key, value in oneRainGetDict.iteritems():

        queryTemplate = "&or_site_id={0}&or_sensor_id={1}&data_start={2}&data_end={3}&system_key={4}&tz={5}".format( value[0], value[1] , date_start, date_end, oneRainSysKey, tz)
        reqURL =  baseOneRainURL + queryTemplate
        print 'reqURL: ' + reqURL
        resp = urllib2.urlopen(reqURL)
        ##print resp.read()
        ##root = etree.fromstring(resp.read())
        root = etree.XML(resp.read())
        values =  root.findall(".//data_value")
        totalRain = 0

        for val in values:
            ##print(val.text)
            totalRain = totalRain + float(val.text)
        oneRainDataDict[key] = totalRain
    print (oneRainDataDict)
    for key, value in oneRainDataDict.iteritems():
        spc = (56 - len(key))*' '
        arcpy.AddMessage("{0}{1}{2}".format(key, spc, value))


# note: the dataset IDs used with http://aquarius-web.nwfwmd.state.fl.us don't match the NWF_ID
##  sensors without a real-time data feed (the numbers below tie to a specific data feed)
##      Cap Cir Old Landfill, Lake Iamonia, John Knox Pond, St Marks @ San Marco, River Sink Tower, District HQ
##

# Grade codes: -2 is unusable, -3 = GAP, 0 = UNDEF
# "Approvale codes:  -1 is unspecified,  0 is undefined, 1 = working, 2 = in review, 3 = approved, 4 = real time
# RETURNED TIMESTAMPS ARE IN GMT
# chowkeebin precip real-time 761602

    nwfwmdGetDict ={
        "CAPITAL CIRCLE, OLD LANDFILL": 760965,
        "LAKE JACKSON FACILITY": 762684,
        "FOREST SERVICE WORK CENTER - BLOXHAM CUTOFF": 761627,
        "MICCOSUKEE PARK": 761626,
        "LAKE JACKSON - MILLER LANDING ROAD": 761623,
        "LAKE IAMONIA OUTFALL @ MERIDIAN RD": 761595,
        "APALACHEE REGIONAL PARK": 761596,
        "BANNERMAN ROAD NEAR THOMASVILLE RD": 761600,
        "COMMONWEALTH BLVD, WEST - LEON COUNTY": 761604,
        "FT BRADEN RAINFALL 827": 761634,
        "LAKE KANTURK OUTFALL @ CENTERVILLE RD": 761637,
        "LAKE IAMONIA": 761547,
        "HERRON STEEL SITE, SILVER LAKE RD.": 761607,
        "ABUNDANT LIFE FELLOWSHIP": 761601,
        "JOHN KNOX POND, MEGGINNIS TRIBUTARY": 760962,
        "WEMBLEY WAY, EASTGATE NEIGHBORHOOD": 761613,
        "STILL CREEK @ CAPITOLA RD": 761783,
        "MILITARY TRAIL NEAR NATURAL BRIDGE RD.": 761608,
        "TUCK PROPERTY, N. CENTERVILLE RD.": 761628,
        "CHOWKEEBIN NENE NEAR MAGNOLIA DR.": 761602,
        "WAKULLA SPRINGS STATE PARK": 761625,
        "ST. MARKS RIVER @ SAN MARCOS DE APALACHEE S.P.": 762890,
        "RIVER SINK TOWER - RAIN": 762899,
        "District HQ Rain": 760892
    }

    for key, value in nwfwmdGetDict.iteritems():
        reqURL = "http://aquarius-web.nwfwmd.state.fl.us/Data/DatasetGrid?dataset={}&interval=Custom&date={}&endDate={}&timezone=-300&sort=TimeStamp-desc".format(value, date_start, date_end)
        resp = json.load(urllib2.urlopen(reqURL))
        rainTotal = 0
        if len(resp["Data"]) > 0:
            for reading in resp["Data"]:
            # handle nulls
##                if ('Value' not  in reading or len(reading) < 1):
##                    print (reqURL)
                rainTotal = rainTotal + (reading['Value'] if reading['Value'] else 0)
            nwfwmdDataDict[key] = rainTotal
            print( key + " had " + str(rainTotal) + " inches")
        else:
            nwfwmdDataDict[key] = None
            print( key + " had No data")
    for key, value in nwfwmdDataDict.iteritems():
        spc = (56 - len(key))*' '
        arcpy.AddMessage("{0}{1}{2}".format(key, spc, value))
    print (nwfwmdDataDict)
    return oneRainDataDict, nwfwmdDataDict


if __name__ == '__main__':
    ##date_start1 = "10/14/2019 5:00:00 PM" # arcpy.GetParameterAsText(0) YYYY-MM-DD 24:00
    ##date_end1 = "10/15/2019 11:00:00 PM" # arcpy.GetParameterAsText(1) YYYY-MM-DD 24:00
    date_start1 = arcpy.GetParameterAsText(0)    # YYYY-MM-DD 24:00
    date_end1 = arcpy.GetParameterAsText(1)   # YYYY-MM-DD 24:00
    date_start = ConvertDateFormat(date_start1).replace(' ', '%20')    # YYYY-MM-DD 24:00
    date_end = ConvertDateFormat(date_end1).replace(' ', '%20')   # YYYY-MM-DD 24:00
    arcpy.AddMessage('\nConverted dates for\n\tStart: {0}\n\tEnd: {1}'.format(date_start, date_end))
    oneRainDataDict, nwfwmdDataDict = main(date_start, date_end)

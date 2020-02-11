# -*- coding: cp1250 -*-

import arcpy
from math import atan, cos, sin, degrees, pi

arcpy.env.overwriteOutput = True

#FUNKCJE

global toler
global k

#toler = raw_input("Podaj tolerację upraszczania: ")
#k = raw_input("Podaj liczbę wierzchołków: ")

toler = 0.001
k = 4

def Azimuth(X1, Y1, X2, Y2):

    dY = Y2-Y1
    dX = X2-X1

    if dX == 0:
        quadrant = 0
    else:
        quadrant = atan(abs((Y2-Y1)/(X2-X1)))
    #print(quadrant)

    if(dX>0 and dY>0):
        Az = quadrant
    elif(dX>0 and dY<=0):
        Az = pi - quadrant
    elif(dX<=0 and dY<=0):
        Az = pi + quadrant
    else:
        Az = 2*pi - quadrant
    return Az

def Angle(X1, Y1, X2, Y2, X3, Y3):

    Az1 = Azimuth(X2, Y2, X1, Y1)
    Az2 = Azimuth(X2, Y2, X3, Y3)
    angl = abs(Az1 - Az2)
    
    return  angl


def Import():

    data = arcpy.MakeFeatureLayer_management(r".\Dane.shp", "data")

    buildings = []

    for row in arcpy.da.SearchCursor(data, ["OID@", "SHAPE@"]):
        for i in row[1]:
            vertices = []
            for j in i:
                vertices.append((j.X, j.Y))
                #print(j.X, j.Y)
        buildings.append(vertices)

    return buildings


##X1 = buildings[0][0][0]
##Y1 = buildings[0][0][1]
##
##X2 = buildings[0][1][0]
##Y2 = buildings[0][1][1]

##print(X1, Y1, X2, Y2)
##
##Az = Azimuth(X1, Y1, X2, Y2)
##
##print(Az)

def Simplify(buildings):

    sim_build = []

    for build in buildings:
        sim_ver = []
        i = 0
        for pnt in build:
            if i == 0:
                check = Angle(build[-1][0], build[-1][1], build[0][0], build[0][1], build[1][0], build[1][1])
            elif i == len(build)-1:
                check = Angle(build[-2][0], build[-2][1], build[-1][0], build[-1][1], build[0][0], build[0][1])
            else:
                check = Angle(build[i-1][0], build[i-1][1], build[i][0], build[i][1], build[i+1][0], build[i+1][1]) 

            if check <= pi - float(toler) or check >= pi + float(toler):
                sim_ver.append(pnt)

            i+=1
            
        sim_build.append(sim_ver)

    return sim_build


def SaveSHP(data, name):
    shp = arcpy.CreateFeatureclass_management(r'.\\', str(name)+'.shp', 'POLYGON')

    cursor = arcpy.da.InsertCursor(shp, ['SHAPE@'])

    point = arcpy.Point()
    array = arcpy.Array()
    

    for build in data:
        cursor.insertRow([build])

    del cursor
    

def main():
    
    data = Import()
    s_build = Simplify(data)
    SaveSHP(s_build, "nazwa")

main()

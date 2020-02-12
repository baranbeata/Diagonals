# -*- coding: cp1250 -*-

import arcpy
from math import atan, cos, sin, degrees, pi, sqrt

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
        parts = []
        for i in row[1]:
            vertices = []
            for j in i:
                vertices.append((j.X, j.Y))
                #print(j.X, j.Y)
            parts.append(vertices)
        buildings.append(parts)

##    for i in buildings:
##        for j in i:
##            for k in j:
##                print k
##    print ("koniec buildings")
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
        for part in build:
            i = 0
            for pnt in part:
                if i == 0:
                    check = Angle(part[-1][0], part[-1][1], part[0][0], part[0][1], part[1][0], part[1][1])
                elif i == len(part)-1:
                    check = Angle(part[-2][0], part[-2][1], part[-1][0], part[-1][1], part[0][0], part[0][1])
                else:
                    check = Angle(part[i-1][0], part[i-1][1], part[i][0], part[i][1], part[i+1][0], part[i+1][1]) 

                if check <= pi - float(toler) or check >= pi + float(toler):
                    sim_ver.append(pnt)
                i+=1 
        sim_build.append(sim_ver)
            
##    for i in sim_build:
##        for j in i:
##            print j
##    print("koniec sim_build")

##    print(sim_build)
                
    return sim_build


def SaveSHP(data, name):
    shp = arcpy.CreateFeatureclass_management(r'.\\', str(name)+'.shp', 'POLYGON')

    cursor = arcpy.da.InsertCursor(shp, ['SHAPE@'])

    for build in data:
        cursor.insertRow([build])

    del cursor

def Dist(X1, Y1, X2, Y2):
    d = sqrt((X2-X1)**2+(Y2-Y1)**2)
    return d

def CreateDiagonals(building):

    diagonals = []
    
    
    k = 2
    for pnt in building[2:-2]:
        d = Dist(building[0][0], building[0][1], pnt[0], pnt[1])
        s = {'id':k, 'len':d, 'vert':0 }
        diagonals.append(s)
        k += 1
    
    i = 1
    for pnt in building[1:]:
        j = i + 2    
        for oth in building[i+2:-1]:
            d = Dist(pnt[0], pnt[1], oth[0], oth[1])
            s = {'id':int(str(i)+str(j)), 'len':d, 'vert':0 }
            diagonals.append(s)

            j += 1
        i += 1


    print diagonals

        

def main():
    data = Import()
    
    s_build = Simplify(data)
    #SaveSHP(s_build, "name")

    CreateDiagonals(s_build[4])

    

if __name__ == '__main__':
    main()

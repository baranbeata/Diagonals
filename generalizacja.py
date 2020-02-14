# -*- coding: cp1250 -*-

import arcpy
from math import atan, cos, sin, degrees, pi, sqrt

arcpy.env.overwriteOutput = True

#*** FUNCTIONS ***

global toler
global k

toler = float(raw_input("Podaj tolerację upraszczania: "))
k = int(raw_input("Podaj liczbę wierzchołków: "))

def Azimuth(X1, Y1, X2, Y2):

    dY = Y2-Y1
    dX = X2-X1

    if dX == 0:
        quadrant = 0
    else:
        quadrant = atan(abs((Y2-Y1)/(X2-X1)))

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
            parts.append(vertices)
        buildings.append(parts)

    return buildings


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

    ## Creating diagonals that don't cross the building
    ## Structure: dictionary with ID (nodefrom-nodeto), length and numer of cut vertices

    ## UPDATE: Added elements to dictionary: from and to nodes

    diagonals = []
    
    array = arcpy.Array([arcpy.Point(*coords) for coords in building])

    build_geom = arcpy.Geometry("POLYGON", array)
    
    k = 2
    for pnt in building[2:-2]:
        d = Dist(building[0][0], building[0][1], pnt[0], pnt[1])
        s = {'id':str(k), 'len':d, 'vert':k+1, 'from':0, 'to':k }
        geom = arcpy.Geometry("POLYLINE", arcpy.Array([arcpy.Point(building[0][0], building[0][1]), arcpy.Point(*pnt)]))
        if not geom.crosses(build_geom):
            diagonals.append(s)
        k += 1
            
    i = 1
    for pnt in building[1:]:
        j = i + 2    
        for oth in building[i+2:-1]:
            d = Dist(pnt[0], pnt[1], oth[0], oth[1])
            v = j - i + 1
            s = {'id':(str(i)+str(j)), 'len':d, 'vert':v, 'from':i, 'to':j }
            geom = arcpy.Geometry("POLYLINE", arcpy.Array([arcpy.Point(*pnt), arcpy.Point(*oth)]))
            if not geom.crosses(build_geom):
                diagonals.append(s)
            j += 1
        i += 1

    ## Sorting dictioraries by length of a diagonal

    diagonals = sorted(diagonals, key=lambda k: k['len'])
    
    return diagonals

def Generalize(diagonals, building):

    print( 'Generalization in progres...')

    ## Count of building vertices:
    ## (We need to be left with 4 vertices
    ## That means the count is equal to 5,
    ## since the first and last vertice is the same point)


    ## Indexing vertices in building

    xy = {i:building[i] for i in range(len(building))}

    xy_check = {}
    xy_rej = []
    xy_draw = []

    for diag in diagonals:
        if diag['vert'] >= k and diag['from'] not in xy_check.keys() and diag['to'] not in xy_check.keys(): #xy_check.keys()??
            i = 0
            count = len(building) - len(xy_check)
            if count <= 5: break
            xy_rej = []
            for vert in range(diag['from'], diag['to']+1):
                if building[vert] not in xy_rej:
                    if  i != 0 and i != diag['to'] - diag['from']:
                        xy_check[vert] = building[vert]
                    xy_rej.append(building[vert])
                    i += 1
            xy_draw.append(xy_rej)

    rejected = xy_check.keys()

    remain = []

    for pnt in xy:
        if pnt not in xy_check:
            remain.append(xy[pnt])

    return (xy_draw, [remain])

def main():
    
    data = Import()
    
    s_build = Simplify(data)
    SaveSHP(s_build, "name")

    results = [Generalize(CreateDiagonals(i), i) for i in s_build]

    rej = []
    rem = []

    for build in results:
        rej += build[0]
        rem += build[1]

    SaveSHP(rej, "rejected")
    SaveSHP(rem, "remain") 

    
if __name__ == '__main__':
    main()

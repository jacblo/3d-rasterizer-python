#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 20:42:20 2020

@author: y3
"""

import json
import PIL
from PIL import Image
import numpy as np

render = []
    
width = 1000
height = 1000

for y in range(height):
    line = []
    for x in range(width):
        line.append([0,0,0])
    render.append(line)


mesh = {}
with open("meshForRenderer.json",mode = "r")as f:
    mesh = json.loads(f.read())


cameraPos = {"position":[1,0,0],"rotation":[0,0,0]}



def line(Nx0, Ny0, Nx1, Ny1, color = (0,0,0), width = 1):
    x0 = Nx0
    y0 = Ny0
    x1 = Nx1
    y1 = Ny1
    
    for x in range(width):
        x0 = Nx0 + x
        y0 = Ny0 + x
        x1 = Nx1 + x
        y1 = Ny1 + x
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                
                try:
                    render[y][x] = color
                except:
                    pass
                
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                
                try:
                    render[y][x] = color
                except:
                    pass
                
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy        
        
        try:
            render[y][x] = color
        except:
            pass
    
    for x in range(2,width):
        x0 = Nx0 - x
        y0 = Ny0 - x
        x1 = Nx1 - x
        y1 = Ny1 - x
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                try:
                    render[y][x] = color
                except:
                    pass
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                try:
                    render[y][x] = color
                except:
                    pass
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy        
        try:
            render[y][x] = color
        except:
            pass


def Point3dTo2d(xyz = [0,0,0]):
    x = xyz[0]*300
    y = xyz[1]*300 
    return (x,y)
    

def BoundBoxTri(x1, y1, x2, y2, x3, y3):
    
    Xs = [x1,x2,x3]; Xs.sort()
    Ys = [y1,y2,y3]; Ys.sort()
    up = Ys[0]
    down = Ys[-1]
    right = Xs[-1]
    left = Xs[0]
    return ([left,up],[right,down])


def TriArea(x1, y1, x2, y2, x3, y3):
    return abs(0.5 * (((x2-x1)*(y3-y1))-((x3-x1)*(y2-y1))))

def fillTri(x1, y1, x2, y2, x3, y3,color = (255,255,255)):
    bounds = BoundBoxTri(x1, y1, x2, y2, x3, y3)
    fullArea = TriArea(x1, y1, x2, y2, x3, y3)
    for y in range(int(bounds[0][1]),int(bounds[1][1]+1)):
        for x in range(int(bounds[0][0]),int(bounds[1][0]+1)):
            tri1 = TriArea(x1, y1, x2, y2, x,y)
            tri2 = TriArea(x1, y1, x, y, x3,y3)
            tri3 = TriArea(x, y, x2, y2, x3,y3)
            
            if tri1 + tri2 + tri3 == fullArea:
                render[y][x] = color



def Distance3dKey(data):
    point=(0,0,0)
    point1 = [mesh["vertices"][data[0][0]]][0]
    point2 = [mesh["vertices"][data[0][1]]][0]
    point3 = [mesh["vertices"][data[0][2]]][0]
    
    d1 = np.sqrt((point1[0] - point[0])**2+(point1[1] - point[1])**2+(point1[2] - point[2])**2)
    d2 = np.sqrt((point2[0] - point[0])**2+(point2[1] - point[1])**2+(point2[2] - point[2])**2)
    d3 = np.sqrt((point3[0] - point[0])**2+(point3[1] - point[1])**2+(point3[2] - point[2])**2)
    d = (d1+d2+d3)/3
    return d

def clipToVal(num):
    if num < 0:
        return 0
    elif num > 255:
        return 255
    return num
    
def orginizeMeshByDistance():
    mesh["tris"].sort(key=Distance3dKey)

def shade(baseColor = (255,255,255),norm = (0,0,0)):
    xyz = [(norm[0]+3.14159)*40,(norm[1]+3.14159)*40,(norm[2]+3.14159)*40]
    color = (clipToVal(baseColor[0]-xyz[0]),clipToVal(baseColor[1]-xyz[0]),clipToVal(baseColor[2]-xyz[0]))
    return color
    

def determinant_3x3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
            m[1][0] * (m[0][1] * m[2][2] - m[0][2] * m[2][1]) +
            m[2][0] * (m[0][1] * m[1][2] - m[0][2] * m[1][1]))


def subtract(a, b):
    return (a[0] - b[0],
            a[1] - b[1],
            a[2] - b[2])

def tetrahedron_calc_volume(a = [0,0,0], b = [0,0,0], c = [0,0,0], d = [0,0,0]):
    return (abs(determinant_3x3((subtract(a, b),
                                 subtract(b, c),
                                 subtract(c, d),
                                 ))) / 6.0)













def renderImg(path):
    orginizeMeshByDistance()
    for x in mesh["tris"]:
        a = Point3dTo2d(mesh["vertices"][x[0][0]])
        b = Point3dTo2d(mesh["vertices"][x[0][1]])
        c = Point3dTo2d(mesh["vertices"][x[0][2]])
        fillTri(a[0], a[1], b[0], b[1], c[0], c[1],shade((204,200,100),x[1]))
    
    print("saving image")
    data = np.array(render).astype(np.uint8)
    #data = np.random.random((100,100))
    
    #Rescale to 0-255 and convert to uint8
    #rescaled = (255.0 / data.max() * (data - data.min())).astype(np.uint8)
    
    im = Image.fromarray(data)
    im.save(path)
    print("image saved")

renderImg("test.png")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 20:26:30 2022

@author: raulm
"""

#librerias
from openpyxl import*
from gurobipy import*

#1. Cargar los parametros
book = load_workbook('/Users/raulm/Desktop/ParametrosT1OptiAvanzada.xlsx')
sheet = book.active

d = {} #Distancias en metros
for fila in range(3,9):
    for columna in range(3,9):
        estacioni = sheet.cell(2, columna).value
        estacionj = sheet.cell(fila,2).value
        d[estacioni,estacionj] = sheet.cell(fila, columna).value

f = {} #Flujos
for fila in range(11,17):
    for columna in range(3,9):
        procesoi = sheet.cell(10,columna).value
        procesoj = sheet.cell(fila,2).value
        f[procesoi,procesoj] = sheet.cell(fila, columna).value
 

#2. Conjuntos
E = {'Estacion 1','Estacion 2', 'Estacion 3', 'Estacion 4', 'Estacion 5', 'Estacion 6'}
P = {'Moldeo', 'Extrusion', 'Corte', 'Pulido', 'Impresion 3D', 'Empaque'}

#3. Modelo de optimizacion
m = Model('Distribucion')

#4. Variables de decision
x = m.addVars(P,E, vtype = GRB.BINARY, name = 'x')

#5. Restricciones problema

# Cada proceso tiene una estacion
for i in P:
    m.addConstr(quicksum(x[i,j] for j in E) == 1)
    
for j in E:
    m.addConstr(quicksum(x[i,j] for i in P) == 1)

#6. Funcion objetivo
m.setObjective(quicksum(x[i,j]*f[i,k]*d[j,h] for i in P for j in E for k in P for h in E), GRB.MINIMIZE)

#7. Optimizar
m.update()
m.optimize()
m.setParam('Outputflag',0)
m.optimize()

#8. Imprimir resultados en consola
z = m.getObjective().getValue()
print ('La funcion objetivo es', z)
for i,j in x.keys():
    if x[i,j].x>0:
        print('El proceso ',i, ' debe ser asignado a la ',j)

    




















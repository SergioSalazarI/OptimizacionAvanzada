from openpyxl import *
from gurobipy import*

import numpy as np
import pandas as pd
import os

current = os.getcwd()
os.chdir("C:\\Users\\david\\OneDrive - Universidad de los Andes\\2022-2\\Optimización Avanzada\\Tarea 2")

df = pd.read_excel("Tarea 2 - 202220.xlsx",index_col=0,header=1)
df.columns = ["Lugar","Latitud","Longitud","Demanda"]
df.set_index("Lugar", inplace=True)

L = df.index.tolist()
distance = {}

a = 0

for i in range(26):
    
    lat_1 = df.iloc[i,0]
    long_1 = df.iloc[i,1]
    
    for j in range(26):
        lat_2 = df.iloc[j,0] 
        long_2 = df.iloc[j,1]
        
        root = np.sin(np.deg2rad(lat_1-lat_2)/2)**2 + np.cos(np.deg2rad(lat_1))*np.cos(np.deg2rad(lat_2))*(np.sin(np.deg2rad(long_1-long_2)/2)**2)
        root = np.sqrt(root)
        
        d = 2*6378*np.arcsin(root)
        distance[(L[i],L[j])] = d
        
m = Model("MVRP")
x = m.addVars(L,L,vtype=GRB.BINARY,name='x')

# Cada tienda es visitado
for j in L[1:-1]:
    m.addConstr(quicksum(x[i,j] for i in L)==1)
    
# Cada visita sale del nodo
for i in L[1:-1]:
    m.addConstr(quicksum(x[i,j] for j in L)==1)
    
# Del depósito salen K camiones. K=5
m.addConstr(quicksum(x[L[0],j] for j in L[1:-1])==5)

# Al depósito ingresan k camiones. K=5
m.addConstr(quicksum(x[i,L[0]] for i in L[1:-1])==5)

# Evitar ciclos entre ubicaciones
for i in L:
    for j in L:
        m.addConstr(x[i,j]+x[j,i]<=1)

print(L[1:-1])
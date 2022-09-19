from openpyxl import *
from gurobipy import*

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

current = os.getcwd()
os.chdir("C:\\Users\\david\\OneDrive - Universidad de los Andes\\2022-2\\Optimización Avanzada\\Tarea 2")

df = pd.read_excel("Tarea 2 - 202220.xlsx",index_col=0,header=1)
df.columns = ["Lugar","Latitud","Longitud","Demanda"]
df.set_index("Lugar", inplace=True)

L = df.index.tolist()
distance = {}

a = 0

# Calcular distancias
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

# Demandas
d = {}
for i in range(26):
    d[L[i]] = df.iloc[i,2]

m = Model("MVRP");
x = m.addVars(L,L,vtype=GRB.BINARY,name='x')

# Cada tienda es visitado
for j in L[1:]:
    m.addConstr(quicksum(x[i,j] for i in L)==1)
    
# Cada visita sale del nodo
for i in L[1:]:
    m.addConstr(quicksum(x[i,j] for j in L)==1)
    
# Del depósito salen K camiones. K=5
m.addConstr(quicksum(x[L[0],j] for j in L[1:])==5)

# Al depósito ingresan k camiones. K=5
m.addConstr(quicksum(x[i,L[0]] for i in L[1:])==5)

# Evitar ciclos entre ubicaciones
for i in L:
    for j in L:
        m.addConstr(x[i,j]+x[j,i]<=1)

# función objetivo
m.setObjective(quicksum(distance[i,j]*x[i,j] for i in L for j in L),GRB.MINIMIZE)

# no mostrar el optimizador completo
m.update()

def calcular_rutas(i:int):
    r = []
    inicio = rutas[i][0]
    fin = rutas[i][1]
    r.extend((inicio,fin))  #r.append(inicio)  #r.append(fin)
    
    terminar = False
    j = i+5
    
    while (terminar != True) and (j<30):
        inicio = rutas[j][0]
        siguiente = rutas[j][1]
        if inicio==fin and siguiente=="Depósito":
            terminar=True
            r.append("Depósito")
        elif inicio==fin:
            r.append(siguiente)
            fin = siguiente
            j = i+5
        else:
            j = j+1
    return r

def calcular_todas_rutas(i:int):
    r = []
    inicio = rutas[i][0]
    fin = rutas[i][1]
    r.extend((inicio,fin))  #r.append(inicio)  #r.append(fin)
    
    terminar = False
    j = 0
    
    while (terminar != True) and (j<30):
        inicio = rutas[j][0]
        siguiente = rutas[j][1]
        if inicio==fin and siguiente=="Depósito":
            terminar=True
            r.append("Depósito")
        elif inicio==fin:
            r.append(siguiente)
            fin = siguiente
            j = i+1
        else:
            j = j+1
    return r

def calcular_distancias(r:list):
    distancias = []
    for ruta in r:
        dist = 0
        for i in range(len(ruta)-1):
            dist = dist + distance[ruta[i],ruta[i+1]]
        distancias.append(dist)
    return distancias

def calcular_demanda(r:list):
    demanda = []
    for ruta in r:
        dist = 0
        for i in range(len(ruta)-1):
            dist = dist + d[ruta[i]]
        demanda.append(dist)
    return demanda

def rutas_to_dataFrame(r:list):
    dic = {"from":[],"to":[]}
    for ruta in r:
        for i in range(len(ruta)-1):
            dic["from"].append(ruta[i])
            dic["to"].append(ruta[i+1])
    return dic

def ruta_to_dataFrame(r:list):
    dic = {"from":[],"to":[]}
    for i in range(len(r)-1):
        dic["from"].append(r[i])
        dic["to"].append(r[i+1])
    return dic
    
def plot_rutas(r:list):
    dic = rutas_to_dataFrame(r)
    dic = pd.DataFrame(dic)
    G=nx.from_pandas_edgelist(dic, 'from', 'to')
    for i in L:
        G.add_node(i)
    nx.draw(G, pos=nx.spring_layout(G),with_labels=True, node_size=220,width=2, edge_color="skyblue", style="solid", font_size=7)
    plt.show()

m.setParam("Outputflag",0)
m.optimize()

z = m.getObjective().getValue()

rutas = []

for i,j in x.keys():
    if x[i,j].x>0:
        rutas.append((i,j))
        
rutas = [calcular_todas_rutas(i) for i in range(26)]
rutas = [i for i in rutas if i[0]==i[-1]]
num = [i+1 for i in range(len(rutas))]
energia = [ i*1.5 for i in calcular_distancias(rutas)]
demanda = calcular_demanda(rutas)

dic = {"Ruta":num,"Secuencia":rutas,"Energía":energia,"Demanda":demanda}
dic = pd.DataFrame.from_dict(dic)
dic.set_index("Ruta", inplace=True)

print(dic)
print(z)
print(np.sum(calcular_distancias(rutas)))

plot_rutas(rutas)
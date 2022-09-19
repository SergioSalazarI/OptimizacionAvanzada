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

# bateria de un camion
global B
B = 34

# capacidad de un camion
global K
K = 20

# Calcular distancias
for i in range(26):
    # latitud y longitud del lugar 1
    lat_1 = df.iloc[i,0]
    long_1 = df.iloc[i,1]
    
    for j in range(26):
        # latitud y longitud del lugar 2
        lat_2 = df.iloc[j,0] 
        long_2 = df.iloc[j,1]
        
        root = np.sin(np.deg2rad((lat_2-lat_1)/2))**2 + np.cos(np.deg2rad(lat_1))*np.cos(np.deg2rad(lat_2))*(np.sin(np.deg2rad((long_2-long_1)/2))**2)
        root = np.sqrt(root)
        
        #distancia entre el lugar 1 y 2
        d = 2*6378*np.arcsin(root)
        distance[(L[i],L[j])] = d

# Demandas
d = {}
for i in range(26):
    d[L[i]] = df.iloc[i,2]

# crear el modelo de optimización
m = Model("MVRP");
x = m.addVars(L,L,vtype=GRB.BINARY,name='x')

# Cada tienda es visitado
for j in L[1:]:
    m.addConstr(quicksum(x[i,j] for i in L if(i!=j))==1)
    
# Cada visita sale del nodo
for i in L[1:]:
    m.addConstr(quicksum(x[i,j] for j in L if(i!=j))==1)

# Del depósito salen K camiones. K=5
m.addConstr(quicksum(x[L[0],j] for j in L[1:])==5)

# el arco depósito-depósito es cero.
m.addConstr(x[L[0],L[0]]==0)

# Al depósito ingresan k camiones. K=5
m.addConstr(quicksum(x[i,L[0]] for i in L[1:])==5)

# Evitar ciclos entre ubicaciones
for i in L:
    for j in L:
        m.addConstr(x[i,j]+x[j,i]<=1)

# función objetivo
m.setObjective(quicksum(distance[i,j]*x[i,j] for i in L for j in L),GRB.MINIMIZE)

# no mostrar el optimizador completo
m.setParam("Outputflag",0)
m.update()

def calcular_rutas(rutas:list,i:int):
    """
    Reconoce todas las rutas generadas por el optimizador
    _____________________________________
    Parámetros
    rutas[list]: lista con los arcos de la forma (i,j) generados por el optimizador.
    i[int]: Posición de inicio del generador de la ruta.
    _____________________________________
    Sálida
    r[list]: Lista con la ruta que contiene el arco i.
    """
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
    """
    Calcula la distancia que se recorre en cada ruta.
    _____________________________________
    Parámetros
    r[list]: lista con las rutas generadas por el optimizador.
    _____________________________________
    Sálida
    distancias[list]: Lista que contiene la distancia que recorre cada ruta.
    """
    distancias = []
    for ruta in r:
        dist = 0
        for i in range(len(ruta)-1):
            dist = dist + distance[ruta[i],ruta[i+1]]
        distancias.append(dist)
    return distancias

def calcular_demanda(r:list):
    """
    Calcula la demanda total de la ruta r.
    _____________________________________
    Parámetros
    r[list]: Lista con los lugares que visita una ruta.
    _____________________________________
    Sálida
    demanda[int]: Demanda total de los lugares que visita la ruta.
    """
    demanda = 0
    for i in range(len(r)-1):
        demanda = demanda + d[r[i]]
    return demanda

def generar_reporte(rutas:list):
    """
    Genera el reporte de la solucion.
    _____________________________________
    Parámetros
    rutas[list]: lista con las rutas generadas por el optimizador.
    _____________________________________
    Sálida
    dic[DataFrame]: Tabla que reporta la solución, i.e. formato Tabla 2.
    """
    rutas = [calcular_rutas(rutas,i) for i in range(26)]
    rutas = [i for i in rutas if i[0]==i[-1]]
    num = [i+1 for i in range(len(rutas))]
    energia = [ i*0.5 for i in calcular_distancias(rutas)]
    demanda = [calcular_demanda(i) for i in rutas]

    dic = {"Ruta":num,"Secuencia":rutas,"Energía":energia,"Demanda":demanda}
    dic = pd.DataFrame.from_dict(dic)
    dic.set_index("Ruta", inplace=True)
    
    return dic

def rutas_to_dataFrame(r:list):
    """
    Genera un dataFrame que indica los nodos de inicio y los nodos de fin.
    _____________________________________
    Parámetros
    rutas[list]: lista con las rutas generadas por el optimizador.
    _____________________________________
    Sálida
    dic[DataFrame]: Tabla que reporta el nodo de inicio (i) y el nodo de llegada (j) del arco (i,j).
    """
    dic = {"from":[],"to":[]}
    for ruta in r:
        for i in range(len(ruta)-1):
            dic["from"].append(ruta[i])
            dic["to"].append(ruta[i+1])
    return dic
 
def plot_rutas(r:list):
    """
    Genera el grafo de la solución.
    _____________________________________
    Parámetros
    rutas[list]: lista con las rutas generadas por el optimizador.
    _____________________________________
    Sálida
    Gráfico de los lugares (nodos) y los arcos definidos por el optimizador.
    """
    dic = rutas_to_dataFrame(r)
    dic = pd.DataFrame(dic)
    G=nx.from_pandas_edgelist(dic, 'from', 'to')
    for i in L:
        G.add_node(i)
    nx.draw(G, pos=nx.spring_layout(G),with_labels=True, node_size=220,width=2, edge_color="skyblue", style="solid", font_size=7)
    plt.show()
        
def eliminar_exceso_capacidad(dic):
    """
    Genera restricciones para evitar el exceso de capacidad de una ruta.
    _____________________________________
    Parámetros
    dic[DataFrame]: Tabla que reporta la solución, i.e. formato Tabla 2.
    
    Nota: Las restricciones limitan la demanda acumulada por una ruta.
    """
    for row in range(dic.shape[0]):
        demanda = dic.iloc[row,2]
        if demanda > K:
            secuencia = dic.iloc[row,0]
            m.addConstr(quicksum(d[j]*x[i,j] for i in secuencia[:-1] for j in secuencia[1:])<=K)
            
def eliminar_exceso_capacidad_v2(dic):
    """
    Genera restricciones para evitar el exceso de capacidad de una ruta.
    _____________________________________
    Parámetros
    dic[DataFrame]: Tabla que reporta la solución, i.e. formato Tabla 2.
    
    Nota: Las restricciones definen la cantidad de camiones que deben ingresar a una ruta.
    """
    for row in range(dic.shape[0]):
        demanda = dic.iloc[row,2]
        if demanda > K and row <5:
            cota = np.ceil(demanda/K)
            secuencia = dic.iloc[row,0]

            L_copy = [x for x in L if(x not in secuencia)]
            L_copy.extend(["Depósito"])
            
            m.addConstr(quicksum(x[i,j] for i in L_copy for j in secuencia[1:-1])>=cota)
            
def eliminar_exceso_energia(dic):
    """
    Genera restricciones para evitar que la batería del camión se agote.
    _____________________________________
    Parámetros
    dic[DataFrame]: Tabla que reporta la solución, i.e. formato Tabla 2.
    
    Nota: Las restricciones definen la cantidad de camiones que deben ingresar a una ruta
          de modo que el camión asignado no agote su batería.
    """
    for row in range(dic.shape[0]):
        energia = dic.iloc[row,1]
        if energia > B and row<5:
            print(f'** La energia de la ruta {row+1} es: {energia}. Por tanto se debe cortar la ruta. **')
            secuencia = dic.iloc[row,0]
            cota = np.ceil(energia/B)
            
            L_copy = [x for x in L if(x not in secuencia)]
            L_copy.extend(["Depósito"])
            
            m.addConstr(quicksum(x[i,j] for i in L_copy for j in secuencia[1:-1])>=cota)

def eliminar_ciclos(dic):
    """
    Genera restricciones para evitar ciclos que no cruzan por el depósito.
    _____________________________________
    Parámetros
    dic[DataFrame]: Tabla que reporta la solución, i.e. formato Tabla 2.
    
    Nota: Las restricciones definen la cantidad de camiones que deben ingresar a una ruta
          de modo que la ruta incluya el depósito.
    """
    for row in range(5,dic.shape[0]):
        secuencia = dic.iloc[row,0]
        L_copy = [x for x in L if(x not in secuencia)]
        demanda = dic.iloc[row,2]
        cota = np.ceil(demanda/K)
        m.addConstr(quicksum(x[i,j] for i in L_copy for j in secuencia[1:])>=cota)

def correr_modelo():
    """
    Compila el modelo
    _____________________________________
    Parámetros
    _____________________________________
    Sálida
    rutas[list]: lista con los arcos de la forma (i,j) generados por el optimizador.
    """
    m.optimize()
    z = m.getObjective().getValue()
    rutas = []
    for i,j in x.keys():
        if x[i,j].x>0:
            rutas.append((i,j))
    print(f'El Status del modelo es: {m.Status}')
    print(f'La distancia total recorrida es:   {z} km')
    print(f'La energía total consumida es:     {z*0.5} KWh')
    return rutas

# Boleanos que indican el estado del modelo
exceso_capacidad = True
exceso_energia = True
hay_ciclos = True

i = 0
while (exceso_capacidad or exceso_energia or hay_ciclos) and i<100:
    print("================================================================================")
    print(f'------------------------------ Iteración:  {i+1} -----------------------------')
    rutas = correr_modelo()
    dic = generar_reporte(rutas)
    print("\n Resultado del modelo de optimización.")
    print(dic)
    
    exceso_capacidad = any(dic["Demanda"]>K)
    if (exceso_capacidad==True):
        eliminar_exceso_capacidad_v2(dic)
        
    exceso_energia = any(dic["Energía"]>B)
    if (exceso_energia==True):
        eliminar_exceso_energia(dic)
        
    hay_ciclos = (dic.shape[0]!=5)
    if (hay_ciclos == True):
        eliminar_ciclos(dic) 

    i = i + 1

# Almacenar la solución en formato .xlsx
#dic.to_excel("resultado_inicial.xlsx")
plot_rutas(rutas)
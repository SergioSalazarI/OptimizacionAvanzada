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
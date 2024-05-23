# -*- coding: utf-8 -*-
"""
Created on Mon May 20 12:23:08 2024

@author: USUARIO
"""

import pandas as pd
import re

# Ruta del archivo Excel (acá hay que colocar donde está el excel)
ruta = "C:/Users/USUARIO/Downloads/W By Last Available EpiWeek.xlsx"

# Leer el archivo Excel
df = pd.read_excel(ruta, engine='openpyxl')

# Eliminar la última fila (dato "total" que no va)
df = df.drop(df.index[-1])
df.drop(['Año.1','In / Out of Subregions'], axis=1, inplace=True)

# Lista de columnas en las que se desea rellenar los valores faltantes
columnas = ['ID', 'País o Subregion', 'Serotipo']

# Rellenar los valores faltantes hacia adelante en las columnas especificadas
df[columnas] = df[columnas].fillna(method='ffill')

# Crear una columna 'ID' con un número para cada fila
df['ID'] = df.reset_index().index + 1

#cambiar estructura de datos

columnas_a_convertir = ['Semana Epidemiológica (a)', 'Total de Casos de Dengue (b)',"Confirmados Laboratorio","Muertes",'Población X 1000',
                        'Dengue Grave (d)']
df[columnas_a_convertir] = df[columnas_a_convertir].apply(pd.to_numeric, errors='coerce').astype('Int64')

#cambiar formato a decimal
columnas_format = ['% Lab Conf (x100)', '(DG/D) x100 (e)', 'Tasa de Incidencia (c)']

# Aplicar formato a las columnas
df[columnas_format] = df[columnas_format].applymap(lambda x: '{:,.5f}'.format(x).replace(',', '@').replace('.', ',').replace('@', '.'))
df[columnas_format] = df[columnas_format].replace('nan', '')

# 1 - Tabla de dimensiones País o Subregión
dim_pais_subregion = df[['País o Subregion']].drop_duplicates().reset_index(drop=True)
dim_pais_subregion['ID_Pais_Subregion'] = dim_pais_subregion.index + 1  # Crear un ID único para cada País o Subregión
dim_pais_subregion = dim_pais_subregion[['ID_Pais_Subregion','País o Subregion']]
# Obtener un diccionario de mapeo de país a número
mapeo_pais = dict(zip(dim_pais_subregion['País o Subregion'], dim_pais_subregion['ID_Pais_Subregion']))

# Reemplazar el nombre del país o subregión por el número
df['ID_Pais_Subregion'] = df['País o Subregion'].map(mapeo_pais)

# Eliminar la columna 'País o Subregión' si es necesario
df.drop('País o Subregion', axis=1, inplace=True)

# 2 - Tabla de dimensiones Serotipo
dim_serotipo = df[['Serotipo']].drop_duplicates().reset_index(drop=True)
dim_serotipo['ID_Serotipo'] = dim_serotipo.index + 1  # Crear un ID único para cada Serotipo

# Obtener un diccionario de mapeo de país a número
mapeo_serotipo = dict(zip(dim_serotipo['Serotipo'], dim_serotipo['ID_Serotipo']))

# Reemplazar el nombre del serotipo por el número
df['ID_Serotipo'] = df['Serotipo'].map(mapeo_serotipo)

# Eliminar la columna 'serotipo' si es necesario
df.drop('Serotipo', axis=1, inplace=True)

# Función para limpiar los serotipos y extraer los números
def limpiar_serotipo(serotipo):
    if serotipo == '':
        return []
    numeros = re.findall(r'\d+', serotipo)
    return [int(num) for num in numeros]

#3 - tabla calendario
dim_calendario = df[['Año']].drop_duplicates().reset_index(drop=True)
dim_calendario['ID_Calendario'] = dim_calendario.index + 1  # Crear un ID único para cada Serotipo
dim_calendario["Mes"] = 1
dim_calendario["Dia"] = 1
dim_calendario = dim_calendario[['ID_Calendario','Año','Mes', 'Dia']]

# Obtener un diccionario de mapeo de calendario a número
mapeo_calendario = dict(zip(dim_calendario['Año'], dim_calendario['ID_Calendario']))

# Reemplazar el nombre del calendario por el número
df['ID_Calendario'] = df['Año'].map(mapeo_calendario)

# Aplicar la función a la columna 'Serotipo'
dim_serotipo['Serotipo_numericos'] = dim_serotipo['Serotipo'].apply(limpiar_serotipo)

serotipos_unicos = sorted(set([serotipo for sublist in dim_serotipo['Serotipo_numericos'] for serotipo in sublist]))

# Crear columnas flag para cada serotipo único
for serotipo in serotipos_unicos:
    dim_serotipo[f'Serotipo_{serotipo}'] = dim_serotipo['Serotipo_numericos'].apply(lambda x: 1 if serotipo in x else 0)

# Crear columna "sin datos" para indicar si la lista está vacía
dim_serotipo['Sin datos'] = dim_serotipo['Serotipo_numericos'].apply(lambda x: 1 if len(x) == 0 else 0)
dim_serotipo.drop('Serotipo_numericos', axis=1, inplace=True)
dim_serotipo = dim_serotipo[['ID_Serotipo','Serotipo', 'Serotipo_1', 'Serotipo_2', 'Serotipo_3','Serotipo_4', 'Sin datos']]

#Exportar a csv (colocar donde quieres que vayan csv)
ruta_final = "C:/Users/USUARIO/Documents/bd_ari/"

df.fillna(value=pd.NA, inplace=True)
df.to_csv(ruta_final + "casos_dengue.csv", index=False, encoding='utf-8-sig', float_format='%.5f')
dim_pais_subregion.to_csv(ruta_final + "paises.csv", index=False, encoding='utf-8-sig')
dim_serotipo.to_csv(ruta_final + "serotipo.csv", index=False, encoding='utf-8-sig')
dim_calendario.to_csv(ruta_final + "fecha.csv", index=False, encoding='utf-8-sig')




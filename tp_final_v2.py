# -*- coding: utf-8 -*-
"""TP FINAL V2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TeiaQLpWQs9Md86QkJBpPGwiX_cYdnG3

# Librerias Utilizadas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

pd.set_option('display.float_format', lambda x: '%.2f' % x)

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.compose import ColumnTransformer

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score

from sklearn.decomposition import PCA
import matplotlib.colors as mcolors

import itertools

from sklearn import tree
import graphviz
import itertools

import seaborn as sns

"""# Carga del DataSets"""

from google.colab import files
import io

uploaded = files.upload()

nombre_archivo_subido = '2023_12_01_tabla_NAVEGACION.csv'
df_data = pd.read_csv(io.BytesIO(uploaded[nombre_archivo_subido]),
                  encoding='latin-1',
                  sep=','
                  )
display(df_data)

from google.colab import files
import io

uploaded = files.upload()

nombre_archivo_subido = '2023_12_01_tabla_USUARIOS.csv'
df_data2 = pd.read_csv(io.BytesIO(uploaded[nombre_archivo_subido]),
                  encoding='latin-1',
                  sep=','
                  )
display(df_data2)

"""# Analisis y Limpieza de los Datos"""

#Lo que se realiza en el siguiente es unir ambos data sets por el código de cliente y forma una tabla que integre ambos datos y tener todas las dimensiones disponibles para trabajar
df =  pd.DataFrame(df_data)
df2 = pd.DataFrame(df_data2)

tabla_combinada = pd.merge(df, df2, on='usuario', how='left')
tabla_combinada.head()

tabla_combinada.info()

# Realiza un left join para combinar las tablas basándote en la columna 'usuario'
tabla_combinada = pd.merge(df, df2, on='usuario', how='left', indicator=True)

# Cuenta la cantidad de usuarios únicos en df que no tienen correspondencia en df2
usuarios_unicos_df = tabla_combinada[tabla_combinada['_merge'] == 'left_only']['usuario'].nunique()

# Cuenta la cantidad de usuarios únicos en df2 que no tienen correspondencia en df
usuarios_unicos_df2 = tabla_combinada[tabla_combinada['_merge'] == 'right_only']['usuario'].nunique()

#  (por ejemplo, si lo aplican a la columna 'sexo', .unique() devuelve 'masculino', 'femenino', 's/d', mientras que .nunique() devuelve 3).

# Muestra los resultados
print(f"Cantidad de usuarios únicos en df sin correspondencia en df2: {usuarios_unicos_df}")
print(f"Cantidad de usuarios únicos en df2 sin correspondencia en df: {usuarios_unicos_df2}")

# Que me arroje 14 usuarios que existieron en la tabla transaccional , sin estar dado de alta en el abm de clientes es un alerta ! (¿Como se puede vender a alguien que no es cliente?)
# El resultado esperado es 0 y 0.

# Verificamos si tenemos datos duplicados..
tabla_combinada.duplicated().sum()

# Agrupa los datos por las columnas "usuario", "fecha" y "identificador_nota" y selecciona el primer valor de las demás columnas

tabla_agrupada = tabla_combinada.groupby(['usuario', 'fecha', 'identificador_nota']).agg({
    'seccion': 'first',
    'plataforma': 'first',
    'origen': 'first',
    'pais': 'first',
    'genero': 'first',
    'edad': 'first',
    'indice_fidelidad': 'first',
}).reset_index()

tabla_agrupada.head()

tabla_agrupada.duplicated().sum()

tabla_agrupada.info()

# Crea un gráfico de barras para el conteo por género
sns.set(style="whitegrid")
plt.figure(figsize=(8, 6))
sns.countplot(x='genero', data=tabla_agrupada, palette='pastel')

# Añade etiquetas y título
plt.xlabel('Género')
plt.ylabel('Cantidad')
plt.title('Conteo de personas por género')

# Muestra el gráfico
plt.show()

tabla_agrupada['pais'].value_counts()

#Aca depuramos a todos menos los del pais Argentina
tabla_agrupada = tabla_agrupada[tabla_agrupada['pais'] == 'Argentina']
#Aca depuramos los que pertenecen al genero S/D.
tabla_agrupada = tabla_agrupada[tabla_agrupada['genero'] != 'S/D']

#Filtramos por Edad
# Calcular el rango intercuartílico (IQR)
q1 = tabla_agrupada['edad'].quantile(0.25)
q3 = tabla_agrupada['edad'].quantile(0.85)
iqr = q3 - q1

# Definir límites para identificar outliers
lower_limit = q1 - 1.5 * iqr
upper_limit = q3 + 1.5 * iqr

# Filtrar valores atípicos
tabla_agrupada = tabla_agrupada[(tabla_agrupada['edad'] >= lower_limit) & (tabla_agrupada['edad'] <= upper_limit)]

# Mostrar el dataset sin outliers
#print("Dataset sin outliers:")
#print(filtra_outliers)

# Realizar un histograma del dataset filtrado
plt.hist(tabla_agrupada['edad'], bins=10, edgecolor='black')
plt.title('Histograma de Edades (sin outliers)')
plt.xlabel('Edades')
plt.ylabel('Frecuencia')
plt.show()

# El Rango donde se marcan los limites y las edades que se toman son las suguintes.
# Viendo los filtros que toman. ¿Es lo que realmente desean?
print(f'''Quitamos las personas con menor edad que: {lower_limit}''')
print(f'''Quitamos las personas con mayor edad que: {upper_limit}''')

# Lo que se realiza es la conversion de edades entre rangos y clasificar a cada una de ellas
# Definir los rangos y las categorías
bins = [-1, 29, 42, 59, 79, 116]
labels = ['Hasta 29', 'Entre 30 - 42', 'Entre 43- 59', 'Entre 60 - 79', 'Mas 80']

# Aplicar la reclasificación usando pd.cut
tabla_agrupada['categoria_edad'] = pd.cut(tabla_agrupada['edad'], bins=bins, labels=labels, right=False)
tabla_agrupada = tabla_agrupada.drop(['edad'], axis=1)

tabla_agrupada = tabla_agrupada.drop(['indice_fidelidad', 'plataforma','origen','pais','identificador_nota','fecha'], axis=1)
display(tabla_agrupada)

sns.countplot(x='seccion',
              data=tabla_agrupada,
              palette='pastel',
              order = tabla_agrupada['seccion'].value_counts().index  # <-----<<
             )

# Añadir etiquetas y título
plt.xlabel('Sección')
plt.ylabel('Cantidad')
plt.title('Sección que miran las Personas')

# Mostrar el gráfico
plt.xticks(rotation=45, ha='right')  # Rotar las etiquetas del eje x para mejorar la legibilidad <-----<<
plt.show()

tabla_agrupada = tabla_agrupada[~tabla_agrupada['seccion'].isin(['especiales','loterias','cartas','arquitectura','relaciones','familias','general','revistaviva','astrologia','autos','historias','viajes','rural','next',''])]

tabla_agrupada = tabla_agrupada

# Filtrar la tabla para obtener solo los datos de Argentina y género masculino

#tabla_argentina_masculino = tabla_agrupada[(tabla_agrupada['pais'] == 'Argentina') & (tabla_agrupada['genero'] == 'Masculino')]
tabla_argentina_masculino = tabla_agrupada[(tabla_agrupada['genero'] == 'Masculino')]
sns.countplot(x='seccion',
              data=tabla_argentina_masculino,
              palette='pastel',
              order = tabla_argentina_masculino['seccion'].value_counts().index  # <-----<<
             )

# Añadir etiquetas y título
plt.xlabel('Sección',)
plt.ylabel('Cantidad')
plt.title('Sección que miran los hombres en Argentina')

# Mostrar el gráfico
plt.xticks(rotation=45, ha='right')  # Rotar las etiquetas del eje x para mejorar la legibilidad <-----<<
plt.show()

# Filtrar la tabla para obtener solo los datos de Argentina y género Femenino
tabla_argentina_femenino = tabla_agrupada[ (tabla_agrupada['genero'] == 'Femenino')]

sns.countplot(x='seccion',
              data=tabla_argentina_femenino,
              palette='pastel',
              order = tabla_argentina_masculino['seccion'].value_counts().index  # <-----<<
             )

# Añadir etiquetas y título
plt.xlabel('Sección')
plt.ylabel('Cantidad')
plt.title('Sección que miran los mujeres en Argentina')

# Mostrar el gráfico
plt.xticks(rotation=45, ha='right')  # Rotar las etiquetas del eje x para mejorar la legibilidad <-----<<
plt.show()

### Miramos cuantos valores en cero tiene cada una de las columnas

{f"{col}": (tabla_agrupada[col]==0).sum() for col in tabla_agrupada.select_dtypes("number").columns}

# Cantidad total de datos no nulos en cada columna
cantidad_no_nulos = tabla_agrupada.count()

# Muestra la cantidad total de datos no nulos en cada columna
print(cantidad_no_nulos)

# Cantidad total de datos no nulos en todo el DataFrame
total_no_nulos = tabla_agrupada.count().sum()

# Muestra la cantidad total de datos no nulos en todo el DataFrame
print(f"Cantidad total de datos no nulos: {total_no_nulos}")

print("-----------------------------------------------------------------------------")

# Cantidad total de valores nulos en cada columna
cantidad_nulos = tabla_agrupada.isnull().sum()

# Muestra la cantidad total de valores nulos en cada columna
print(cantidad_nulos)

# Cantidad total de valores nulos en todo el DataFrame
total_nulos = tabla_agrupada.isnull().sum().sum()

# Muestra la cantidad total de valores nulos en todo el DataFrame
print(f"Cantidad total de valores nulos: {total_nulos}")

print("-----------------------------------------------------------------------------")

Participacion_Datos = (total_nulos / total_no_nulos )
print(f"El grado de incidencia es de: {Participacion_Datos}")

# Crea un gráfico de barras para el conteo por género
sns.set(style="whitegrid")
plt.figure(figsize=(8, 6))
sns.countplot(x='genero', data=tabla_agrupada, palette='pastel')

# Añade etiquetas y título
plt.xlabel('Género')
plt.ylabel('Cantidad')
plt.title('Conteo de personas por género')

# Muestra el gráfico
plt.show()

sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))

# Crear un gráfico de barras con colores por la categoría de edad
sns.countplot(x='seccion',
              hue='categoria_edad',
              data=tabla_agrupada,
              palette='pastel',
              order=tabla_agrupada['seccion'].value_counts().index
             )

# Añadir etiquetas y título
plt.xlabel('Sección')
plt.ylabel('Cantidad')
plt.title('Sección que miran las personas en Argentina por Categoría de Edad')

# Mostrar el gráfico
plt.xticks(rotation=45, ha='right')
plt.legend(title='Categoría de Edad', loc='upper right')  # Eliminado el argumento title_format
plt.show()

sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))

# Crear un gráfico de barras con colores por la categoría de edad
sns.countplot(x='seccion',
              hue='categoria_edad',
              data=tabla_argentina_masculino,
              palette='pastel',
              order=tabla_argentina_masculino['seccion'].value_counts().index
             )

# Añadir etiquetas y título
plt.xlabel('Sección')
plt.ylabel('Cantidad')
plt.title('Sección que miran los Hombres en Argentina por Categoría de Edad')

# Mostrar el gráfico
plt.xticks(rotation=45, ha='right')
plt.legend(title='Categoría de Edad', loc='upper right')  # Eliminado el argumento title_format
plt.show()

sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))

# Crear un gráfico de barras con colores por la categoría de edad
sns.countplot(x='seccion',
              hue='categoria_edad',
              data=tabla_argentina_femenino,
              palette='pastel',
              order=tabla_argentina_femenino['seccion'].value_counts().index
             )

# Añadir etiquetas y título
plt.xlabel('Sección')
plt.ylabel('Cantidad')
plt.title('Sección que miran las Mujeres en Argentina por Categoría de Edad')

# Mostrar el gráfico
plt.xticks(rotation=45, ha='right')
plt.legend(title='Categoría de Edad', loc='upper right')  # Eliminado el argumento title_format
plt.show()

"""# Armado de Matrices

**PARA SISTEMA DE RECOMENDACIÓN**
"""

display(tabla_argentina_femenino)

tabla_argentina_femenino = tabla_argentina_femenino.drop(['genero'], axis=1)


# Crear columnas adicionales para cada tipo de sección
secciones = tabla_argentina_femenino['seccion'].unique()

for seccion in secciones:
    tabla_argentina_femenino[seccion] = (tabla_argentina_femenino['seccion'] == seccion).astype(int)

# Agrupar por usuario y sumar las secciones leídas
tabla_argentina_femenino = tabla_argentina_femenino.groupby(['usuario']).agg({seccion: 'sum' for seccion in secciones}).reset_index()


display(tabla_argentina_femenino)



# Calcular la suma total de cada fila (usuario)
tabla_argentina_femenino['total'] = tabla_argentina_femenino.iloc[:, 1:].sum(axis=1)

# Dividir cada valor en las columnas de secciones por el total de la fila
for seccion in secciones:
    tabla_argentina_femenino[seccion] = tabla_argentina_femenino[seccion] / tabla_argentina_femenino['total']

# Eliminar la columna temporal 'total' si ya no es necesaria
tabla_argentina_femenino = tabla_argentina_femenino.drop(columns=['total'])

display(tabla_argentina_femenino)

"""**PARA ALGORITMOS**"""

display(tabla_agrupada)

tabla_algoritmos_1= tabla_agrupada

# Crear columnas adicionales para cada tipo de sección
secciones_unicas_algoritmos_1 = tabla_algoritmos_1['seccion'].unique()

for seccion in secciones_unicas_algoritmos_1:
    tabla_algoritmos_1[seccion] = (tabla_algoritmos_1['seccion'] == seccion).astype(int)

# Agrupar por usuario y sumar las secciones leídas
resultado = tabla_algoritmos_1.groupby(['usuario']).agg({seccion: 'sum' for seccion in secciones_unicas_algoritmos_1}).reset_index()

display(resultado)

# Calcular la suma total de cada fila (usuario)
resultado['total'] = resultado.iloc[:,1:].sum(axis=1)

# Dividir cada valor en las columnas de secciones por el total de la fila
for seccion in secciones_unicas_algoritmos_1:
    resultado[seccion] = resultado[seccion] / resultado['total']

# Eliminar la columna temporal 'total' si ya no es necesaria
resultado = resultado.drop(columns=['total'])

# Mostrar el resultado final
display(resultado)

# Crear columnas adicionales para cada tipo de sección
secciones_unicas_algoritmos_1 = tabla_algoritmos_1['seccion'].unique()

for seccion in secciones_unicas_algoritmos_1:
    tabla_algoritmos_1[seccion] = (tabla_algoritmos_1['seccion'] == seccion).astype(int)

# Agrupar por usuario y contar las secciones leídas
resultado_V1 = tabla_algoritmos_1.groupby('usuario').agg({seccion: 'sum' for seccion in secciones_unicas_algoritmos_1}).reset_index()

# Buscar la categoría de edad correspondiente a cada usuario y el genero correspondiente
usuarios_categorias = tabla_algoritmos_1[['usuario', 'categoria_edad','genero']].drop_duplicates()

# Fusionar los resultados para agregar la columna 'categoria_edad' al DataFrame final
resultado_V1 = pd.merge(resultado_V1, usuarios_categorias, on='usuario')

# Calcular la suma total de cada fila (usuario)
resultado_V1['total'] = resultado_V1[secciones_unicas_algoritmos_1].sum(axis=1)

# Dividir cada valor en las columnas de secciones por el total de la fila
for seccion in secciones_unicas_algoritmos_1:
    resultado_V1[seccion] = resultado_V1[seccion] / resultado_V1['total']

# Eliminar la columna temporal 'total' si ya no es necesaria
resultado_V1 = resultado_V1.drop(columns=['total'])

# Mostrar el resultado
display(resultado_V1)

resultado_V1 = resultado_V1.drop(columns=['usuario'])
resultado_V1 = resultado_V1.drop(columns=['categoria_edad'])
# Mapea los valores de la columna 'genero' a 1 y 0
resultado_V1['genero'] = resultado_V1['genero'].map({'Masculino': 1, 'Femenino': 0})


# Muestra el DataFrame final
display(resultado_V1)

"""PARA PROBAR"""



"""# Modelo"""

# ¿DIME QUE LEES Y TE DIRE QUE GENERO ERES?

# Separamos los datos en dos conjuntos: train - test
from sklearn.model_selection import train_test_split

# Los argumentos de la siguiente función son:
# (1) "los datos de entrada",
# (2) "las etiquetas de los datos de entrada",
# (3) test_size = "la fracción del total dei filas que se destinarán a test" (0.2 significa que el 20% del total va a test)
# (4) stratify = "la columna donde están las clases".
# Esto es para que los conjuntos de train y test tenga, en proporción, la misma cantidad de elementos por clase que el conjunto
# original.
# (5) random_state = cualquier número, para que cada vez que se corra esta celda devuelva los mismos resultados "al azar".
# La salida son 4 objetos: los datos de train (X_train), los datos de test (X_test),
# las etiquetas de los datos de train (y_train) y las de test (y_test).
X_train,X_test,y_train,y_test = train_test_split(resultado_V1.drop(['genero'],axis=1), #dropea la tabla para que quede todos menos eso y despues la vuelve a meter.
                                                 resultado_V1['genero'],
                                                 test_size = 0.20,
                                                 stratify = resultado_V1['genero'],
                                                 random_state = 1
                                                )

# tabla_final , es la variable que estaba antes con 76% de acierto

print("Sobre un total de \033[95m" + str(len(resultado_V1)) + "\033[00m datos se separó en un conjunto de \033[92mtrain\033[00m con \033[92m" + str(len(X_train)) + "\033[00m elementos y otro de \033[91mtest\033[00m con \033[91m" + str(len(X_test)) + "\033[00m elementos.")

# A modo de chequeo, verificamos que la cantidad de registros por clase se mantenga
print("\nCantidad de datos por clase en los \033[95mdatos originales\033[00m :")
display(resultado_V1['genero'].value_counts())

print("\nCantidad de datos por clase en el subconjunto \033[92mtrain\033[00m:")
display(y_train.value_counts())

"""# Algoritmo KNN"""

# Creamos una función "scaler" para estandarizar los datos y la "entrenamos" con los datos de train
# (toma cualquier número, le resta la media de train y lo divide por la varianza de train)
scaler = StandardScaler()
scaler.fit(X_train)

# Con el reescalador, se los aplicamos a los conjuntos de train y test
X_train_standard = pd.DataFrame(scaler.transform(X_train),columns=(X_train.columns))
X_test_standard = pd.DataFrame(scaler.transform(X_test),columns=(X_test.columns))

# Preparamos ahora la función que hará KNN
# (acá podemos jugar con los hiperparámetros 'n_neigbors' y weights = 'uniform' o 'distance') <----------------<<
# PRUEBEN VARIANDO EL n_neighbors Y EL weights Y REPORTEN UNA DE LAS MÉTRICAS (LA QUE MÁS LES GUSTE / CREAN CONVENIENTE)

knn = KNeighborsClassifier(n_neighbors = 20,
                           weights = 'distance'
                          )

# Entrenamos al modelo
# (imprimirá 'KNeighborsClassifier' con los hiperparámetros utilizados)
knn.fit(X_train_standard,y_train)

from sklearn.metrics import f1_score


# Queremos evaluar el modelo, para ello predecimos las etiquetas de todo el conjunto de test
prediccion_test =  knn.predict(X_test_standard)

# Calculamos el accuracy de las predicciones con las "posta"
metrica_acuracy = accuracy_score(prediccion_test,y_test)
precision = precision_score(y_test, prediccion_test, average='weighted')
recall = recall_score(y_test, prediccion_test, average='weighted')
f1 = f1_score(y_test, prediccion_test, average='weighted')


print("El accuracy del modelo es \033[91m" + str(metrica_acuracy) + "\033[00m")
print("El precision del modelo es \033[91m" + str(precision) + "\033[00m")
print("El recall del modelo es \033[91m" + str(recall) + "\033[00m")
print(f"F1-Score (weighted): {f1}" )



"""# Algoritmo Random Forest"""

# Preparamos la función que hará la regresión logística
# (acá podemos jugar con el hiperparámetros 'criterion' -entropy o gini- y max_depth -profundidad del árbol
# y n_estimators, la cantidad de árboles en el ensamble -por default: 100-)
# PRUEBEN VARIANDO EL MAX_DEPTH Y REPORTEN UNA DE LAS MÉTRICAS (LA QUE MÁS LES GUSTE / CREAN CONVENIENTE)

bosque = RandomForestClassifier(criterion = 'entropy',
                               max_depth = 2000,
                               random_state = 42,
                               n_estimators = 45
                              )
# Entrenamos al modelo
# (imprimirá 'DecisionTreeClassifier' con los hiperparámetros utilizados)
bosque.fit(X_train, y_train)

# Queremos evaluar el modelo, para ello predecimos las etiquetas de todo el conjunto de test
prediccion_test =  bosque.predict(X_test)

# Calculamos el accuracy de las predicciones con las "posta"
metrica_acuracy = accuracy_score(prediccion_test,y_test)
precision = precision_score(y_test, prediccion_test, average='weighted')
recall = recall_score(y_test, prediccion_test, average='weighted')
f1 = f1_score(y_test, prediccion_test, average='weighted')

print("El accuracy del modelo es \033[91m" + str(metrica_acuracy) + "\033[00m")
print("El precision del modelo es \033[91m" + str(precision) + "\033[00m")
print("El recall del modelo es \033[91m" + str(recall) + "\033[00m")
print(f"F1-Score (weighted): {f1}" )

# Podemos ver la performance mediante la matriz de confusión
graficador_matriz_confusion(y_test, prediccion_test)



"""# Algoritmo CART"""

# Armamos el árbol
# PRUEBEN VARIANDO EL MAX_DEPTH Y REPORTEN UNA DE LAS MÉTRICAS (LA QUE MÁS LES GUSTE / CREAN CONVENIENTE)
arbol = DecisionTreeClassifier(criterion = 'gini',
                               max_depth = 42,
                               random_state = 42
                              )

# Entrenamos
arbol.fit(X_train, y_train)

# Queremos evaluar el modelo, para ello predecimos las etiquetas de todo el conjunto de test
prediccion_test =  arbol.predict(X_test)

# Calculamos el accuracy de las predicciones con las "posta"
metrica_acuracy = accuracy_score(prediccion_test,y_test)
precision = precision_score(y_test, prediccion_test, average='weighted')
recall = recall_score(y_test, prediccion_test, average='weighted')
f1 = f1_score(y_test, prediccion_test, average='weighted')

print("El accuracy del modelo es \033[91m" + str(metrica_acuracy) + "\033[00m")
print("El precision del modelo es \033[91m" + str(precision) + "\033[00m")
print("El recall del modelo es \033[91m" + str(recall) + "\033[00m")
print(f"F1-Score (weighted): {f1}" )

# Podemos ver la performance mediante la matriz de confusión
graficador_matriz_confusion(y_test, prediccion_test)

"""# Sistema de Recomendación

ESTA ENFOCADO 100 % EN EL PÚBLICO FEMENINO

Basada en Usuarios
"""

from sklearn.metrics.pairwise import cosine_similarity

# Suponiendo que 'tabla_argentina_femenino' es tu DataFrame
usuario_similitud = cosine_similarity(tabla_argentina_femenino[['espectaculos', 'deportes', 'sociedad','policiales','economia','politica','fama','ciudades','mundo','otros','internacional','opinion','gourmet','servicios','buena-vida','viste']])
usuario_similitud_df = pd.DataFrame(usuario_similitud, index=tabla_argentina_femenino['usuario'], columns=tabla_argentina_femenino['usuario'])

# Obtener usuarios similares a un usuario dado (por ejemplo, '002c5e9b31ca2460158b7ca5b661ce17')
usuarios_similares = usuario_similitud_df['002c5e9b31ca2460158b7ca5b661ce17'].sort_values(ascending=False).index[1:]

# Recomendar categorías para 'usuario1' basándose en lo que les gustó a usuarios similares
categorias_recomendadas = tabla_argentina_femenino.loc[tabla_argentina_femenino['usuario'].isin(usuarios_similares), ['espectaculos', 'deportes', 'sociedad','policiales','economia','politica','fama','ciudades','mundo','otros',
                                                                                                                      'internacional','opinion','gourmet','servicios','buena-vida','viste']].mean().sort_values(ascending=False).index

print("Categorías recomendadas para 'usuario1':", categorias_recomendadas)

"""Basada en items"""

from sklearn.metrics.pairwise import cosine_similarity

# Transponer el DataFrame para que las columnas representen ítems (categorías)
item_similitud = cosine_similarity(tabla_argentina_femenino[['espectaculos', 'deportes', 'sociedad','policiales','economia','politica','fama','ciudades','mundo','otros','internacional','opinion','gourmet','servicios','buena-vida','viste']].T)
item_similitud_df = pd.DataFrame(item_similitud, index=tabla_argentina_femenino.columns[1:], columns=tabla_argentina_femenino.columns[1:])

# Obtener ítems similares a un ítem dado (por ejemplo, 'espectaculos')
items_similares = item_similitud_df['espectaculos'].sort_values(ascending=False).index[1:]

# Recomendar ítems para un usuario dado (por ejemplo, 'usuario1') basándose en ítems similares
categorias_recomendadas = tabla_argentina_femenino[items_similares].loc[tabla_argentina_femenino['usuario'] == '002c5e9b31ca2460158b7ca5b661ce17'].mean().sort_values(ascending=False).index

print("Categorías recomendadas para 'usuario1' basadas en ítems similares:", categorias_recomendadas)

"""Recomendaciones para incrementar el trafico - Enfocado basado en la diversificación"""

from sklearn.metrics.pairwise import cosine_similarity

# Transponer el DataFrame para que las columnas representen ítems (categorías)
item_similitud = cosine_similarity(tabla_argentina_femenino[['espectaculos', 'deportes', 'sociedad','policiales','economia','politica','fama','ciudades','mundo','otros','internacional','opinion','gourmet','servicios','buena-vida','viste']].T)
item_similitud_df = pd.DataFrame(item_similitud, index=tabla_argentina_femenino.columns[1:], columns=tabla_argentina_femenino.columns[1:])

# Obtener ítems similares a un ítem dado (por ejemplo, 'espectaculos')
items_similares = item_similitud_df['espectaculos'].sort_values(ascending=False).index[1:]

# Recomendar ítems para un usuario dado (por ejemplo, 'usuario1') basándose en ítems similares con penalización por preferencias habituales
usuario_actual = '002c5e9b31ca2460158b7ca5b661ce17'
categorias_habituales = tabla_argentina_femenino.loc[tabla_argentina_femenino['usuario'] == usuario_actual, items_similares].mean()
categorias_recomendadas = categorias_habituales[categorias_habituales < categorias_habituales.median()].sort_values(ascending=False).index

print("Categorías recomendadas para '{}' con diversificación:".format(usuario_actual), categorias_recomendadas)

from sklearn.metrics.pairwise import cosine_similarity

# Calcular la similitud entre las categorías (ítems)
item_similitud = cosine_similarity(tabla_argentina_femenino[['espectaculos', 'deportes', 'sociedad','policiales','economia','politica','fama','ciudades','mundo','otros','internacional','opinion','gourmet','servicios','buena-vida','viste']].T)
item_similitud_df = pd.DataFrame(item_similitud, index=tabla_argentina_femenino.columns[1:], columns=tabla_argentina_femenino.columns[1:])

# Obtener ítems similares a un ítem dado (por ejemplo, 'espectaculos')
item_a_considerar = 'espectaculos'
items_similares = item_similitud_df[item_a_considerar].sort_values(ascending=False).index[1:]

# Recomendar ítems basándose en ítems similares con penalización por popularidad
categorias_populares = tabla_argentina_femenino[items_similares].mean()
categorias_recomendadas = categorias_populares[categorias_populares < categorias_populares.median()].sort_values(ascending=False).index

print("Categorías recomendadas basadas en diversificación (sin tener en cuenta usuarios específicos):", categorias_recomendadas)
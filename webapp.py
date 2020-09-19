import streamlit as st
import pandas as pd
import requests as req
from datetime import datetime
import requests_cache as rq_cache
import altair as alt

rq_cache.install_cache('req_cache')

# Ocultamos la hamburguesa de opciones de cache
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

URLConsolidado  =  "https://raw.githubusercontent.com/FavazCL/WS-Ofertas/master/consolidado/"
FechaProceso = pd.read_csv("master_files/FechasProcesos.csv", sep=';') 
FechaProceso2 = FechaProceso.copy()
FechaProceso.head()

now = datetime.now()
Fechahoy = int(now.strftime("%Y%m%d"))

# Obtenemos la información de los consolidados desde el Repo oficial y almacenamos en chache los datos.
@st.cache
def getData():
  tmp_data = []

  for ind in FechaProceso.index:
    FechaArchivo = FechaProceso['fecha2'][ind]
  
    if FechaArchivo <= Fechahoy:
      url = URLConsolidado + 'Consolidado-' + FechaProceso['fecha1'][ind] +'.json'
      res = req.get(url)

      if res.status_code == 200:
        consolidado = res.json()
        tmp_data.append(consolidado)

  return tmp_data

# Limpiamos los datos y creamos una lista con nuevos objetos.
@st.cache
def generateData(data):
  tmp_graph = []

  for index, item in enumerate(data, start = 0):
    tmp_obj = {}
    tmp_categories = []
    categories = []
    tmp_fecha = 0

    for attr, value in item.items():
      if (attr == 'FechaDato'):
        for attrF, valueF in value.items():
          if (valueF == FechaProceso['fecha2'][index]):
            tmp_fecha = FechaProceso['fecha1'][index]
            continue
  
      if (attr == 'Categoria'):
        for attrC, valueC in value.items():
          if valueC not in tmp_categories:
            tmp_categories.append(valueC)

        for cat in tmp_categories:
          tmp_obj_int = {}
          tmp_obj_int['Categoria'] = cat
          tmp_keys = []
          for keye, valuee in value.items():
            if str(valuee) == cat:
              tmp_keys.append(keye)

          tmp_obj_int['Ids'] = tmp_keys            
          categories.append(tmp_obj_int)
      
      if (attr == 'Count'):
        for category in categories:
          tmp_obj['Fecha'] = tmp_fecha
          tmp_obj['Categoria'] = category['Categoria']
          count = 0

          for ids in category['Ids']:
            for attrCo, valueCo in value.items():
              if attrCo == ids:
                count = count + valueCo

          tmp_obj['Cantidad'] = count;  
          tmp_graph.append(tmp_obj)
          tmp_obj = {}

  return tmp_graph

# Con los datos limpios, refactorizamos las fechas y las pasamos a formato yyyy/mm/dd
@st.cache
def refactorDate(generate):
  tmp_date = []

  for info in generate:
    if info['Fecha']:
      parsed = datetime.strptime(info['Fecha'], '%d-%m-%Y').strftime('%Y-%m-%d')
      tmp_date.append(parsed)

  return tmp_date

# Con los datos limpios, refactorizamos las categorias
@st.cache
def refactorCategory(generate):
  tmp_category = []

  for info in generate:
    if info['Categoria']:
      tmp_category.append(info['Categoria'])
  
  return tmp_category

# Con los datos limpios, refactorizamos las categorias
@st.cache
def refactorQuantity(generate):
  tmp_quantity = []

  for info in generate:
    if info['Cantidad']:
      tmp_quantity.append(info['Cantidad'])
  
  return tmp_quantity

# Creamos una lista con todas las categorias sin repetidos.
@st.cache
def uniqueCategories(categories):
  tmp_cat = []

  for cat in categories:
    if cat not in tmp_cat:
      tmp_cat.append(cat)
  
  return tmp_cat

# Realizamos el filtro dependiendo de lo seleccionado por el usuario.
@st.cache(allow_output_mutation=True)
def filter(categories_selected, range_date_selected):
  if len(categories_selected) > 0 and len(range_date_selected) == 0:
    tmp_cat = []
    tmp_dates = []
    tmp_quantity = []
    
    for cat_sel in categories_selected:
      for index, cat in enumerate(categories, start = 0):
        if cat == cat_sel:
          tmp_cat.append(cat)
          tmp_dates.append(dates[index])
          tmp_quantity.append(quantities[index])

    return createChart(createDataFrame(tmp_dates, tmp_cat, tmp_quantity))

  elif len(categories_selected) == 0 and len(range_date_selected) > 0:
    tmp_cat = []
    tmp_dates = []
    tmp_quantity = []

    if (len(range_date_selected) <= 1):
      range_date_selected = range_date_selected + (range_date_selected[0],)

    for index, date in enumerate(dates, start = 0):
      parsed = datetime.strptime(date, '%Y-%m-%d').date()
      if parsed >= range_date_selected[0] and parsed <= range_date_selected[-1]:
        tmp_dates.append(date)
        tmp_cat.append(categories[index])
        tmp_quantity.append(quantities[index])

    return createChart(createDataFrame(tmp_dates, tmp_cat, tmp_quantity))
  
  else:
    tmp_cat = []
    tmp_dates = []
    tmp_quantity = []

    if (len(range_date_selected) <= 1):
      range_date_selected = range_date_selected + (range_date_selected[0],)

    for index, date in enumerate(dates, start = 0):
      parsed = datetime.strptime(date, '%Y-%m-%d').date()
      
      if parsed >= range_date_selected[0] and parsed <= range_date_selected[-1]:
        tmp_dates.append(date)
        tmp_cat.append(categories[index])
        tmp_quantity.append(quantities[index])

    tmp_cat2 = []
    tmp_dates2 = []
    tmp_quantity2 = []

    for cat_sel in categories_selected:
      for index, cat in enumerate(tmp_cat, start = 0):
        if cat == cat_sel:
          tmp_cat2.append(cat)
          tmp_dates2.append(dates[index])
          tmp_quantity2.append(quantities[index])
    
    return createChart(createDataFrame(tmp_dates2, tmp_cat2, tmp_quantity2))

# Creamos el dataFrame con la información final.
def createDataFrame(dates, categories, quantities):
  return pd.DataFrame({
    'Fecha': dates,
    'Categoria': categories,
    'N° de Ofertas': quantities
  })

# Creamos el gráfico
def createChart(series):
  return alt.Chart(series).mark_line().encode(
    x='Fecha',
    y='N° de Ofertas:Q',
    color=alt.Color('Categoria:N'),
    tooltip=['Categoria', 'N° de Ofertas', 'Fecha']
  ).properties(width=800).interactive()

data = getData()
generate = generateData(data)
dates = refactorDate(generate)
categories = refactorCategory(generate)
quantities = refactorQuantity(generate)
use_categories = uniqueCategories(categories)

# Title Sidebar
st.sidebar.title(':mag: Filtros')
st.sidebar.text('Añade filtros para modificar \nlos graficos.')

# Category Sidebar
categories_selected = []

st.sidebar.header(':pushpin: Categorías')
status_cat = st.sidebar.radio('Agregar todas las categorías', ('Si', 'No'))

if status_cat == 'Si':
  categories_selected = []
else:
  categories_selected = st.sidebar.multiselect('Seleccione las categorías', use_categories)

# Range Date Sidebar
range_date_selected = []

st.sidebar.header(':calendar: Rango de fechas')
status_date = st.sidebar.radio('Seleccionar el historico', ('Si', 'No'))

if status_date == 'Si':
  range_date_selected = []
else:
  # range_date_selected = st.sidebar.date_input('Seleccione el rango de fechas', [datetime.strptime(dates[0], '%d-%m-%Y').date(), datetime.strptime(dates[-1], '%d-%m-%Y').date()])
  range_date_selected = st.sidebar.date_input('Fecha inicial - Fecha final', [datetime.strptime(dates[0], '%Y-%m-%d')])

# Portal Sidebar - TO DO..

# Contacto
st.sidebar.markdown('* * *')
st.sidebar.title(':information_source: Información General')
st.sidebar.text('Responsables del proyecto:')
st.sidebar.markdown('**Felipe Vergara**  \n_fvergaraa5@correo.uss.cl_')
st.sidebar.markdown('**Mauricio Sepulveda**  \n_mauricio.sepulveda@uss.cl_')
st.sidebar.text('Version: 0.1')

# Body webapp
st.title('Análisis de empleos')
st.write('Esta es una aplicación en Streamlit utilizado para el análisis de ofertas de empleos de distintos portales. ')

st.subheader('Número de ofertas de trabajos diarios por categoría.')
st.write('Esta incluye la información acumulada de todos los portales.')
st.write('')

# Configuración de filtros
if len(categories_selected) == 0 and len(range_date_selected) == 0:
  st.altair_chart(createChart(createDataFrame(dates, categories, quantities)))
else:
  st.altair_chart(filter(categories_selected, range_date_selected))

show_first_btn = st.checkbox('Mostrar tabla de datos del Número de ofertas de trabajos diarios por categoría.')

if show_first_btn:
  st.dataframe(createDataFrame(dates, categories, quantities).style.highlight_max(axis=0))

import time
import json
import schedule
import os
import requests
import pandas as pd 
from time import gmtime, strftime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from safe_schedule import SafeScheduler
from consolidated_functions import CargaDic
from consolidated_functions import DiaAnterior
from consolidated_functions import DIVIDETEXTO
from consolidated_functions import MAPEA
from consolidated_functions import VerificaArchivoDatos
from bs4 import BeautifulSoup
from numpy import array
from datetime import datetime
from datetime import date
from github import Github

# Configuración inicial de Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

def chiletrabajos():
    # Abrimos el navegador Chrome
    driver = webdriver.Chrome(executable_path=os.environ.get(
        "CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    # Nos logeamos en el portal para obtener los datos restringidos.
    driver.get("https://www.chiletrabajos.cl/chtlogin")

    # En versiones superiores se debe cambiar a un correo y contraseña privado.***
    username = driver.find_element_by_id("username")
    password = driver.find_element_by_id("password")

    username.send_keys("favazcl@gmail.com")
    password.send_keys("fv001995")

    driver.find_element_by_name("login").click()

    time.sleep(10)

    # Inicializamos las variables
    firstPage = "https://www.chiletrabajos.cl/encuentra-un-empleo?2=&13=&fecha=1&categoria=&8=&14=&inclusion=&f=2"
    paginations = []
    links = []
    benefits = []
    offers = []
    tmp_array = []

    # Obtenemos todos los links de las paginaciones del dia actual.
    driver.get(firstPage)
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")

    for pagination in soup.findAll('a', attrs={'class': 'page-link'}):
        paginations.append(pagination.get('href'))

    paginations = list(set(paginations))
    paginations.insert(0, firstPage)

    # Obtenemos todos los links de las ofertas de trabajo por paginación
    for pag in paginations:
        driver.get(str(pag))

        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")

        for a in soup.findAll('div', attrs={'class': 'job-item'}):
            tmp_link = a.find('a')

            if tmp_link is not None:
                links.append(tmp_link.get('href'))

        time.sleep(10)

    links = list(set(links))

    # Obtenemos toda la información de cada oferta
    for offer in links:
        driver.get(offer)

        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")

        data = {}

        for head in soup.findAll('div', attrs={'class': 'no-pointer'}):
            title = head.find('h1', attrs={'class': 'title'})
            if title is not None:
                data['titulo'] = title.text.strip()

            head_trs = head.findAll('tr')

            if len(head_trs) > 0:
                for tr in head_trs:
                    if (len(tmp_array) > 0):
                        data[tmp_array[0]] = tmp_array[1]

                    tmp_array = []

                    for td in tr.find_all('td'):
                        if td is not None:
                            text = td.text.strip()
                            tmp_array.append(text)

            else:
                break

        for body in soup.findAll('div', attrs={'class': 'p-x-3'}):
            description = body.find('p', attrs={'class': 'mb-0'})

            if description is not None:
                data['descripción'] = description.text.strip()

            benefits = body.find_all('div', attrs={'class': 'beneficio-title'})

            if (len(benefits) > 0):
                tmp_benefits = []

                for benefit in benefits:
                    if benefit is not None:
                        tmp_benefits.append(benefit.text.strip())

                data['beneficios'] = tmp_benefits

        data['ref'] = offer
        offers.append(data)

        time.sleep(10)

    # Creamos un archivo json de las ofertas.
    now = datetime.now()
    filename = "chiletrabajos-" + now.strftime("%d-%m-%Y") + ".json"
    result = json.dumps(offers, ensure_ascii=False)

    # Enviamos el archivo creado a github
    token = "29e578fceb764670077aee08fb42dba51b7eb744"
    repo = "FavazCL/WS-Ofertas"
    g = Github(token)
    repo = g.get_repo(repo)
    repo.create_file(
        path='chiletrabajos/' + filename,
        message="Se agregaron nuevas ofertas desde: " + filename,
        content=result,
        branch="master"
    )

def laborum():
    # Abrimos el navegador Chrome
    driver = webdriver.Chrome(executable_path=os.environ.get(
        "CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    # Inicializamos las variables
    firstPage = "https://www.laborum.cl/empleos-publicacion-hoy.html"
    offers = []
    links = []

    # Abrimos la pagina principal
    driver.get(firstPage)

    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")

    # Seleccionamos el número de paginación inicial y final
    first_pag = soup.find('button', attrs={'class': 'gENuBC'}).text.strip()
    last_pag = soup.find('button', attrs={'class': 'eDchar'})

    if last_pag is None:
      tmp_pages = soup.findAll('button', attrs={'class': 'cmiCfE'})
      if tmp_pages is not None:
        last_pag = tmp_pages[-1].text.strip()
      else:
        last_pag = first_pag
    else:
      last_pag = last_pag.text.strip()

    first_pag = int(first_pag)
    last_pag = int(last_pag) 
  
    # Recorremos todas las ofertas de principio a fin
    while first_pag <= last_pag:
      content = driver.page_source
      soup = BeautifulSoup(content, "html.parser")

      for offer in soup.findAll('a', attrs={'class': 'cdmEkq'}):
        tmp_link = offer.get('href')
        if tmp_link not in links:
            links.append(tmp_link)

      element = driver.find_element_by_class_name('jnOlzC')
      actions = ActionChains(driver)
      actions.move_to_element(element).click().perform()

      time.sleep(10)
      first_pag = first_pag + 1

    # Obtenemos toda la información de cada oferta
    for link in links:
      driver.get("https://www.laborum.cl" + str(link))

      data = {}
 
      try:
          WebDriverWait(driver, 10).until(
              EC.presence_of_element_located((By.CLASS_NAME, 'dmYIZt')))
          content = driver.page_source
          soup = BeautifulSoup(content, "html.parser")

          title = soup.find('h1', attrs={'class': 'dmYIZt'})
          if title is not None:
              if title.text.strip() == "No encontramos la página que buscás":
                  continue
              else:
                  date_loc = soup.findAll('li', attrs = {'class': 'kgBqbG'})
                  if date_loc is not None and len(date_loc) >= 2:
                      data['title'] = title.text.strip()
                  else:
                      continue

          company = soup.find('h2', attrs = {'class': 'bkFDjf'})
          if company is not None:
              data['company'] = company.text.strip()
            
          description = soup.find('div', attrs = {'class': 'jxRQZd'})
          if description is not None:
              data['description'] = description.text.strip()
        
          date_loc = soup.findAll('li', attrs = {'class': 'kgBqbG'})
          if date_loc is not None:
              now = datetime.now()
              data['fecha'] = now.strftime("%d-%m-%Y %H:%M:%S")
              if date_loc[-1].text.strip() is None:
                data['location'] = 'No definido'
              else:
                data['location'] = date_loc[-1].text.strip()
    
          dur_sal_cat = soup.findAll('li', attrs = {'class': 'flsJOs'})
          if dur_sal_cat is not None:
              data['duration'] = dur_sal_cat[0].text.strip()
              data['salary'] = dur_sal_cat[1].text.strip()
              data['category'] = dur_sal_cat[-1].text.strip()
      except TimeoutException:
          print("Looking for much time..")
    
      offers.append(data)
      time.sleep(10)

    # Creamos un archivo json de las ofertas.
    now = datetime.now()
    filename = "laborum-" + now.strftime("%d-%m-%Y") + ".json"
    result = json.dumps(offers, ensure_ascii=False)

    # Enviamos el archivo creado a github
    token = "29e578fceb764670077aee08fb42dba51b7eb744"
    repo = "FavazCL/WS-Ofertas"
    g = Github(token)
    repo = g.get_repo(repo)
    repo.create_file(
        path='laborum/' + filename,
        message="Se agregaron nuevas ofertas desde: " + filename,
        content=result,
        branch="master"
    )

def bne():
    # Abrimos el navegador Chrome
    driver = webdriver.Chrome(executable_path=os.environ.get(
        "CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    # Obtenemos la fecha actual del sistema
    today = str(date.today())
    today = today.split('-')

    # Inicializamos las variables
    day = today[2]
    month = today[1]
    year = today[0]
    firstPage = "https://www.bne.cl/ofertas?mostrar=empleo&fechaIniPublicacion=" + day + "%2F" + month + "%2F" + year + "&numPaginaRecuperar=1&numResultadosPorPagina=10&clasificarYPaginar=true"
    offers = []
    links = []
    data = {}

    # Abrimos chrome
    driver.get(firstPage)

    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'paginacionOfertas')))

        # Seleccionamos el número de paginacion inicial y final.
        paginations = soup.findAll('a', attrs = {'data-pagina': True})

        init = 0
        finish = 0

        if (len(paginations) > 0):
            if (len(paginations) == 1):
                init = int(paginations[0].get('data-pagina'))
                finish = init
            else:
                init = int(paginations[0].get('data-pagina'))
                finish = int(paginations[-1].get('data-pagina'))
    except TimeoutException:
        print('Looking for much time..')
        init = 100
        finish = 0

    # Implementar while desde la primera pagina, hasta la ultima
    init = init
    finish = finish
    while init <= finish:
        driver.get("https://www.bne.cl/ofertas?mostrar=empleo&fechaIniPublicacion=" + day + "%2F" + month + "%2F" + year + "&numPaginaRecuperar=" + str(init) + "&numResultadosPorPagina=10&clasificarYPaginar=true")

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'resultadoOfertas')))
            content = driver.page_source
            soup = BeautifulSoup(content, "html.parser")
            
            for col in soup.findAll('article', attrs = {'class': 'resultadoOfertas'}):
                for a in col.findAll('a'):
                    if a is not None:
                        tmp_link = str(a.get('href'))
                        if (tmp_link.find('oferta') == 1):
                            if tmp_link not in links:
                                links.append(tmp_link)
                            
        except TimeoutException:
            print("Looking for much time..")
    
        init = init + 1
        time.sleep(7)
    
    # Ingresamos a cada oferta laboral
    for offer in links:
        driver.get("https://www.bne.cl" + str(offer))
    
        data = {}
        tmp_title = []
    
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'width1000')))
            content = driver.page_source
            soup = BeautifulSoup(content, "html.parser")
        
            title = soup.find('div', attrs = {'class': 'titulo'})
            if title is None:
                continue
            
            tmp_title = title.findAll('span')
        
            if (len(tmp_title) > 2):
                title_name = str(tmp_title[0].text.strip()).split(')')
                data['Titulo'] = tmp_title[2].text.strip()
                data['Ocupacion'] = title_name[-1].strip()
                vacancies = tmp_title[2].text.strip().split('(')
                vacancies = vacancies[-1].split(' ')
                data['Vacantes'] = int(vacancies[0])
            else:
                title_name = str(tmp_title[0].text.strip()).split(')')
                data['Titulo'] = tmp_title[1].text.strip()
                data['Ocupacion'] = title_name[-1].strip()
                vacancies = tmp_title[1].text.strip().split('(')
                vacancies = vacancies[-1].split(' ')
                data['Vacantes'] = int(vacancies[0])
            
            tmp_array = []

            for panel in soup.findAll('article', attrs = {'class': 'panel'}):
                title_category = panel.find('h3', attrs = {'panel-title'})
                if title_category is not None:
                    title_category = title_category.text.strip()
                    if title_category == 'DATOS DE CONTACTO':
                        for item in panel.findAll('span'):
                            if item is not None:
                                text = item.text.strip()
                                tmp_array.append(text)
                    
                            if len(tmp_array) == 2:
                                tmp_array[0] = str(tmp_array[0]).split(':')[0]
                                data[tmp_array[0]] = tmp_array[-1]
                                tmp_array = []
        
                    if title_category == 'DESCRIPCIÓN':
                        description = panel.find('p').text.strip()
            
                        items = panel.findAll('span')
                        data['Ubicacion'] = items[0].text.strip()
                        data['Fecha'] = items[1].text.strip()
                        salary = str(items[3].text.strip()).replace(" ", "").replace(u'\xa0', u' ')
                        data['Salario'] = salary.replace(u'\xa0', u' ')
                        data['Tipo'] = items[-1].text.strip()
            
                    if title_category == 'REQUISITOS SOLICITADOS':
                        for item in panel.findAll('span'):
                            if item is not None:
                                text = item.text.strip()
                                tmp_array.append(text)
                    
                            if len(tmp_array) == 2:
                                tmp_array[0] = str(tmp_array[0]).split(':')[0]
                                data[tmp_array[0]] = tmp_array[-1]
                                tmp_array = []
                    
                    if title_category == 'CARACTERÍSTICAS':
                        for item in panel.findAll('span'):
                            if item is not None:
                                text = item.text.strip()
                                tmp_array.append(text)
                    
                            if len(tmp_array) == 2:
                                tmp_array[0] = str(tmp_array[0]).split(':')[0]
                                data[tmp_array[0]] = tmp_array[-1]
                                tmp_array = []
                    
                        prof = panel.find('label')
                        if prof is not None:
                            data['Oferta de tipo práctica profesional'] = prof.text.strip()

        except TimeoutException:
            print("Looking for much time..")
    
        offers.append(data)
        time.sleep(5)

    # Creamos un archivo json de las ofertas.
    now = datetime.now()
    filename = "bne-" + now.strftime("%d-%m-%Y") + ".json"
    result = json.dumps(offers, ensure_ascii=False)

    # Enviamos el archivo creado a github
    token = "29e578fceb764670077aee08fb42dba51b7eb744"
    repo = "FavazCL/WS-Ofertas"
    g = Github(token)
    repo = g.get_repo(repo)
    repo.create_file(
        path='bne/' + filename,
        message="Se agregaron nuevas ofertas desde: " + filename,
        content=result,
        branch="master"
    )

def runConsolidated():
  PathArchivosMaestros = 'master_files/'
  URLConsolidado  =  "https://raw.githubusercontent.com/FavazCL/WS-Ofertas/master/consolidado/"
  URLLabPrefijo = 'https://raw.githubusercontent.com/FavazCL/WS-Ofertas/master/laborum/laborum-'
  URLChiPrefijo = 'https://raw.githubusercontent.com/FavazCL/WS-Ofertas/master/chiletrabajos/chiletrabajos-'
  URLBnePrefijo = 'https://raw.githubusercontent.com/FavazCL/WS-Ofertas/master/bne/bne-'

  #Carga archivo de control de fechas de carga
  FechaProceso = pd.read_csv(PathArchivosMaestros + "FechasProcesos.csv", sep=';') 
  FechaProceso2 = FechaProceso.copy()
  FechaProceso.head()
  
  #Carga diccionarios para el mapeo
  region_dict , categoriaLABORUM_dict, categoriaCHILETRABAJO_dict , categoriaBNE_dict = CargaDic(PathArchivosMaestros)

  Fechahoy = int(strftime("%Y%m%d", gmtime()))
  print(Fechahoy,';')

  for ind in FechaProceso.index: 
    FechaArchivo = FechaProceso['fecha2'][ind]
    print(Fechahoy,'/')
    if FechaArchivo <= Fechahoy:
        url=URLConsolidado + 'Consolidado-' + FechaProceso['fecha1'][ind] +'.json'
        #url = 'https://raw.githubusercontent.com/FavazCL/WS-Ofertas/master/Consolidado-' + FechaProceso['fecha1'][ind] +'.json'
        print(url)
        request = requests.get(url)
        if request.status_code == 200:
            print('la pagina existe')
        else:
            #Procesa archivo Laborum
            url = VerificaArchivoDatos(URLLabPrefijo, FechaArchivo, FechaProceso2, FechaProceso['fecha1'][ind], FechaProceso['fecha2'][ind])
            request = requests.get(url)
            if request.status_code == 200:
                #print('Web site exists')
                #CArga Archivo
                print(url)
                dataLab = pd.read_json(url)
                dfLaborum = pd.DataFrame(dataLab)
                dfLaborum['FechaDato'] = FechaArchivo
                dfLaborum['Num'] = 1
                #toma las columnas a trabajar y las agrupa
                dfLaborum2 = dfLaborum[["location", "category", "FechaDato", "Num"]].copy()
                dfLaborum2['Origen'] = 'Laborum'
                dfLaborum2['Region'] = 'Otros'
                dfLaborum2['Categoria'] = 'Otros'
                for ind2 in dfLaborum2.index: 
                    comuna = dfLaborum2['location'][ind2]
                    comuna2 = DIVIDETEXTO(comuna, 0)
                    Region = MAPEA(region_dict, comuna2) 
                    #comuna2 = comuna.split(',')
                    #Region = MAPEA(region_dict, comuna2[0]) 
                    category = dfLaborum2['category'][ind2]
                    Categoria = MAPEA(categoriaLABORUM_dict, category) 
                    dfLaborum2.loc[ind2,'Region'] = Region
                    dfLaborum2.loc[ind2, 'Categoria'] = Categoria
                dfLaborum3 = dfLaborum2.groupby(["Origen", "Region", "Categoria", "FechaDato"])['Num'].count().reset_index(name='Count')
                #dfLaborum3

            #Procesa archivo chiletrabajos
            url = VerificaArchivoDatos(URLChiPrefijo, FechaArchivo, FechaProceso2, FechaProceso['fecha1'][ind], FechaProceso['fecha2'][ind])
            request = requests.get(url)
            if request.status_code == 200:
                #print('Web site exists')
                #CArga Archivo
                dataLab = pd.read_json(url)
                chiletrabajos = pd.DataFrame(dataLab)
                chiletrabajos['FechaDato'] = FechaArchivo
                chiletrabajos['Num'] = 1
                #toma las columnas a trabjar y las agrupa
                chiletrabajos2 = chiletrabajos[["Ubicación", "Categoría", "FechaDato", "Num"]].copy()
                chiletrabajos2['Origen'] = 'Chiletrabajos2'
                chiletrabajos2['Region'] = 'Otros'
                chiletrabajos2['Categoria'] = 'Otros'
                for ind2 in chiletrabajos2.index: 
                    comuna = chiletrabajos2['Ubicación'][ind2] 
                    Region = MAPEA(region_dict, comuna) 
                    category = chiletrabajos2['Categoría'][ind2]
                    Categoria = MAPEA(categoriaCHILETRABAJO_dict, category) 
                    chiletrabajos2.loc[ind2,'Region'] = Region
                    chiletrabajos2.loc[ind2, 'Categoria'] = Categoria
                dfchiletrabajos3 = chiletrabajos2.groupby(["Origen", "Region", "Categoria", "FechaDato"])['Num'].count().reset_index(name='Count')
                #dfchiletrabajos3                   


                
            #Procesa archivo bne
            url = VerificaArchivoDatos(URLBnePrefijo, FechaArchivo, FechaProceso2, FechaProceso['fecha1'][ind], FechaProceso['fecha2'][ind])
            request = requests.get(url)
            if request.status_code == 200:
                #print('Web site exists')
                #CArga Archivo
                dataLab = pd.read_json(url)
                bne = pd.DataFrame(dataLab)
                bne['FechaDato'] = FechaArchivo
                bne['Num'] = 1                
                #toma las columnas a trabjar y las agrupa
                bne2 = bne[["Ubicacion", "Ocupacion", "FechaDato", "Num"]].copy()
                bne2['Origen'] = 'Bolsa Nacional de Empleo'
                bne2['Region'] = 'Otros'
                bne2['Categoria'] = 'Otros'
                for ind2 in bne2.index: 
                    comuna = bne2['Ubicacion'][ind2] 
                    comuna2 = DIVIDETEXTO(comuna, 1)
                    Region = MAPEA(region_dict, comuna2)                     
                    #comuna2 = comuna.split(',')                    
                    #Region = MAPEA(region_dict, comuna2[1]) 
                    category = bne2['Ocupacion'][ind2]
                    Categoria = MAPEA(categoriaBNE_dict, category) 
                    bne2.loc[ind2,'Region'] = Region
                    bne2.loc[ind2, 'Categoria'] = Categoria
                dfbne3 = bne2.groupby(["Origen", "Region", "Categoria", "FechaDato"])['Num'].count().reset_index(name='Count')
                #bne3  
                
                #Une los datos
                UnePrimeros = pd.concat([dfLaborum3, dfchiletrabajos3], axis=0)
                UneTodos = pd.concat([UnePrimeros, dfbne3], axis=0)
                
                #Genera agregados pais                
                dfpais = UneTodos.groupby(["Origen", "Categoria", "FechaDato"])['Count'].sum().reset_index(name='Count')
                dfpais['Region'] = 'Chile'
                dfTotalEmpleo = UneTodos.groupby(["Region", "Categoria", "FechaDato"])['Count'].sum().reset_index(name='Count')
                dfTotalEmpleo['Origen'] = 'Laborum+ChileTrabajos+Bne'
                dfPaisTodosPortales = UneTodos.groupby(["Categoria", "FechaDato"])['Count'].sum().reset_index(name='Count')
                dfPaisTodosPortales['Region'] = 'Chile'
                dfPaisTodosPortales['Origen'] = 'Laborum+ChileTrabajos+Bne'
                
                dfTotalCategoria = UneTodos.groupby(["Origen", "Region", "FechaDato"])['Count'].sum().reset_index(name='Count')
                dfTotalCategoria['Categoria'] = 'TodasLasCategorias'
                dfPaisTodasCategorias = UneTodos.groupby(["Origen", "FechaDato"])['Count'].sum().reset_index(name='Count')
                dfPaisTodasCategorias['Region'] = 'Chile'
                dfPaisTodasCategorias['Categoria'] = 'TodasLasCategorias'

                dfPaisTodasCategoriasRegion = UneTodos.groupby(["FechaDato"])['Count'].sum().reset_index(name='Count')
                dfPaisTodasCategoriasRegion['Region'] = 'Chile'
                dfPaisTodasCategoriasRegion['Categoria'] = 'TodasLasCategorias'                
                dfPaisTodasCategoriasRegion['Origen'] = 'Laborum+ChileTrabajos+Bne'            
                
                UneTodos = pd.concat([UneTodos, dfpais], axis=0)
                UneTodos = pd.concat([UneTodos, dfTotalEmpleo], axis=0)
                UneTodos = pd.concat([UneTodos, dfPaisTodosPortales], axis=0)
                UneTodos = pd.concat([UneTodos, dfTotalCategoria], axis=0)
                UneTodos = pd.concat([UneTodos, dfPaisTodasCategorias], axis=0)
                UneTodos = pd.concat([UneTodos, dfPaisTodasCategoriasRegion], axis=0)
                print(UneTodos)
                UneTodos.reset_index(drop=True, inplace=True)
                
                nombre = 'Consolidado-' + FechaProceso['fecha1'][ind] +'.json'
                print(nombre)
                json = UneTodos.to_json()
                print(json)
                
                # Enviamos el archivo creado a github
                token = "4dd77f18017dcbfe07d2446ee6190b88e0bf1b90"
                repo = "FavazCL/WS-Ofertas"
                g = Github(token)
                repo = g.get_repo(repo)
                repo.create_file(
                    path = 'consolidado-test/' + nombre,
                    message = "Se agregaró un nuevo consolidado " + nombre,
                    content = json,
                    branch = "master"
                )
                
    else:
        break

# Señalamos que se ejecute todos los días a la hora fijada.
scheduler = SafeScheduler()
#scheduler.every().day.at('18:00').do(chiletrabajos)
#scheduler.every().day.at('18:00').do(laborum)
#scheduler.every().day.at('18:00').do(bne)
scheduler.every().day.at('23:26').do(runConsolidated)

while True:
    scheduler.run_pending()
    time.sleep(1)

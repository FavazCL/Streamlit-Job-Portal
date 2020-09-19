from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from numpy import array
from datetime import datetime
import json
import time
import schedule
import os
from github import Github

# Chrome Options
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

def chiletrabajos():
    # Abrimos el navegador Chrome
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    
    # Nos logeamos en el portal para obtener los datos restringidos.
    driver.get("https://www.chiletrabajos.cl/chtlogin")
    
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

    for pagination in soup.findAll('a', attrs = {'class': 'page-link'}):
        paginations.append(pagination.get('href'))

    # Eliminamos links duplicados
    paginations = list(set(paginations))

    # Agregamos el link inicial
    paginations.insert(0, firstPage)

    # Obtenemos todos los links de las ofertas de trabajo por paginación
    for pag in paginations:
        driver.get(str(pag))

        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")

        for a in soup.findAll('div', attrs = {'class': 'job-item'}):
            tmp_link = a.find('a')

            if tmp_link is not None:
                links.append(tmp_link.get('href'))

        time.sleep(10)

    # Eliminamos links duplicados
    links = list(set(links))

    # Obtenemos toda la información de cada oferta
    for offer in links:
        driver.get(offer)

        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")

        data = {}

        for head in soup.findAll('div', attrs = {'class': 'no-pointer'}):
            title = head.find('h1', attrs = {'class': 'title'})
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

        for body in soup.findAll('div', attrs = {'class': 'p-x-3'}):
            description = body.find('p', attrs = {'class':'mb-0'})

            if description is not None:
                data['descripción'] = description.text.strip()

            benefits = body.find_all('div', attrs = {'class': 'beneficio-title'})

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
    filename = "chiletrabajos-" + now.strftime("%d-%m-%Y %H:%M:%S") + ".json"
    result = json.dumps(offers, ensure_ascii=False)

    # Enviamos el archivo creado a github
    token = "29e578fceb764670077aee08fb42dba51b7eb744"

    repo = "FavazCL/WS-Ofertas"

    g = Github(token)

    repo = g.get_repo(repo)
    repo.create_file(
        path = 'chiletrabajos/' + filename,
        message = "Se agregaron nuevas ofertas desde: " + filename,
        content = result,
        branch = "master"
    )

# Señalamos que se ejecute todos los días a la hora fijada.
schedule.every().day.at('19:40').do(chiletrabajos)

while True:
    schedule.run_pending()
    time.sleep(1)

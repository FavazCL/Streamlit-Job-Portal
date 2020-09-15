import pandas as pd 
import requests

def DiaAnterior(dfFproceso, fecha):
    xx = dfFproceso.loc[dfFproceso['fecha2'] < fecha]
    yy = xx.tail(1)
    return yy.iloc[0,0], yy.iloc[0,1]


def VerificaArchivoDatos(Prefijo, FechaArchivo, FechaProceso2, FechaTrabajoForm, FechaTrabajo):
    url = Prefijo + FechaTrabajoForm +'.json'
    #print(url)
    request = requests.get(url)
    if request.status_code == 200:
        #print('Web site exists')
        return url
    else:
        #Si archivo no existe se toma el atrazado mas cercano.
        FechaArchivoAnt = FechaArchivo
        #print('FechaArchivoAnt ', FechaArchivoAnt)
        while True:
            FechaArchivoAntForm, FechaArchivoAnt = DiaAnterior(FechaProceso2, FechaArchivoAnt)
            #print (FechaArchivoAntForm, FechaArchivoAnt)
            url = Prefijo + FechaArchivoAntForm +'.json'
            print('archivo no existe se toma el atrazado mas cercano.')
            print(url)
            request = requests.get(url)
            if request.status_code == 200:
                print('Web site ant exists')
                return url                
                break
            print (FechaArchivoAnt)
            if FechaArchivoAnt == 20200901:  #Controla que no pase de esta fecha
                return ''

            
def CargaDic(Ruta):

    data = pd.read_csv(Ruta +'ComunaRegion.csv', sep=';') 
    # dropping null value columns to avoid errors 
    data.dropna(inplace = True) 
    data.head()  
    # converting to dict 
    region_dict = data.set_index('Comuna')['Region'].to_dict() 
    #region_dict 
    
    data = pd.read_csv(Ruta +'categoriaLABORUM.csv', sep=';') 
    # dropping null value columns to avoid errors 
    data.dropna(inplace = True) 
    data.head()  
    # converting to dict 
    categoriaLABORUM_dict = data.set_index('Categoria')['Categoriacomun'].to_dict() 
    #categoriaLABORUM_dict 
    
    data = pd.read_csv(Ruta +'categoriaCHILETRABAJO.csv', sep=';') 
    # dropping null value columns to avoid errors 
    data.dropna(inplace = True) 
    data.head()  
    # converting to dict 
    categoriaCHILETRABAJO_dict = data.set_index('Categoria')['Categoriacomun'].to_dict() 
    #categoriaCHILETRABAJO_dict 
    
    data = pd.read_csv(Ruta +'categoriaBNE.csv', sep=';') 
    # dropping null value columns to avoid errors 
    data.dropna(inplace = True) 
    data.head()  
    # converting to dict 
    categoriaBNE_dict = data.set_index('Categoria')['Categoriacomun'].to_dict() 
    #categoriaBNE_dict
    
    return region_dict , categoriaLABORUM_dict, categoriaCHILETRABAJO_dict , categoriaBNE_dict            
            
def MAPEA(Diccionario, Valor):
    try:
        if pd.isna(Valor):
            return 'Otros'
        xx = Diccionario[Valor.strip()]
        if xx == None:
            return 'Otros'
        return xx
    except KeyError:
        return 'Otros'

def DIVIDETEXTO(Texto, Campo):
    try:
        if Texto == None:
            return 'Otros'
        if pd.isna(Texto):
            return 'Otros'
        dividido = Texto.split(',')
        if dividido[Campo] == None:
            return 'Otros'
        if pd.isna(dividido[Campo]):
            return 'Otros'
        return dividido[Campo]
    except KeyError:
        return 'Otros'

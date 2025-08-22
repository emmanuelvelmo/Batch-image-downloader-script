import os # 
import time # 
import re # 
import requests # 
import urllib.parse # 
import selenium.webdriver # 
from selenium.webdriver.common.by import By # 
from selenium.webdriver.chrome.service import Service # 
from selenium.webdriver.chrome.options import Options # 

# 
while True:
    # Solicitar descripción de imagen y cantidad
    texto_buscar = input("Image description: ").strip('"\'')
    
    num_imgs = 0
    
    # Solicitar lado mínimo de imagen
    while True:
        num_imgs = input("Number of images: ")
        
        # Únicamente número
        if num_imgs.isdigit():
            num_imgs = int(num_imgs)
            
            break
        else:
            print("Wrong format\n")
    
    # Crear carpeta de salida
    if not os.path.exists(texto_buscar):
        os.makedirs(texto_buscar)
    
    # Configuración de Selenium
    opciones_chrome = Options()
    opciones_chrome.add_argument("--headless") # corre sin ventana
    opciones_chrome.add_argument("--disable-gpu") # 
    opciones_chrome.add_argument("--log-level=3") # 
    opciones_chrome.add_argument("--window-size=1280,720") # 
    
    # 
    driver_val = selenium.webdriver.Chrome(service = Service(), options = opciones_chrome)
    
    # Generar URL de búsqueda
    # 
    texto_codificado = urllib.parse.quote(texto_buscar)
    
    # 
    url_busqueda = f"https://www.pinterest.com/search/pins/?q={texto_codificado}&rs=typed"
    
    # 
    driver_val.get(url_busqueda)
    
    # 
    print("Cargando Pinterest y haciendo scroll...")
    
    # Extraer enlaces de imágenes en página cargada
    enlaces = set() # 
    
    scroll_pause = 2 # 
    
    last_height = driver_val.execute_script("return document.body.scrollHeight") # 
    
    patron_img = re.compile(r"/(\d{3,})x/") # busca carpetas con formato mayor a 200 seguido x
    
    # 
    while len(enlaces) < num_imgs:
        # 
        imgs = driver_val.find_elements(By.TAG_NAME, "img")
        
        # 
        for img in imgs:
            src = img.get_attribute("src") # 
            
            # 
            if src and src.endswith(".jpg") and patron_img.search(src):
                # solo contar si es nuevo
                if src not in enlaces:
                    enlaces.add(src) # 
                    
                    # 
                    print(f"Progreso: {len(enlaces)}/{num_imgs} imágenes encontradas", end="\r")
            
            if len(enlaces) >= num_imgs:
                break
        
        # Hacer scroll hacia abajo
        driver_val.execute_script("window.scrollTo(0, document.body.scrollHeight);") # 
        
        time.sleep(scroll_pause) # 
        
        # Revisar si llegamos al final
        new_height = driver_val.execute_script("return document.body.scrollHeight") # 
        
        # 
        if new_height == last_height:
            break
        
        # 
        last_height = new_height
    
    # 
    driver_val.quit()
    
    # 
    print(f"\nEnlaces encontrados: {len(enlaces)}")
    
    # Descargar imágenes
    # 
    print("Descargando imágenes...")
    
    cont_img = 0 # 
    
    # 
    for iter_val, url_val in enumerate(list(enlaces)[:num_imgs], 1):
        try:
            r_val = requests.get(url_val, timeout = 10) # 
            
            # 
            if r_val.status_code == 200:
                # Extraer el nombre original de la URL
                nombre_archivo_original = os.path.basename(urllib.parse.urlparse(url_val).path)
                
                ruta_archivo = os.path.join(texto_buscar, nombre_archivo_original)
                
                # Guardar imagen
                with open(ruta_archivo, "wb") as f_val:
                    f_val.write(r_val.content) 
                    
                cont_img += 1 # 
                
                # 
                print(f"Imagen {iter_val} descargada como {nombre_archivo_original}")
        except Exception as e:
            continue # 
    
    print(f"Descarga finalizada. Total de imágenes descargadas: {cont_img}\n")

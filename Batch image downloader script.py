import os
import time
import re
import requests
from urllib.parse import quote, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ----- ENTRADAS DEL USUARIO -----
texto_buscar = input("Image description: ").strip()
num_imgs = int(input("Number of images: ").strip())

# ----- PREPARAR CARPETA -----
carpeta = texto_buscar.replace(" ", "_")
if not os.path.exists(carpeta):
    os.makedirs(carpeta)

# ----- CONFIGURAR SELENIUM -----
chrome_options = Options()
chrome_options.add_argument("--headless")  # corre sin ventana
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(), options=chrome_options)

# ----- URL DE BÚSQUEDA -----
texto_codificado = quote(texto_buscar)
url_busqueda = f"https://www.pinterest.com/search/pins/?q={texto_codificado}&rs=typed"

driver.get(url_busqueda)
print("Cargando Pinterest y haciendo scroll...")

# ----- EXTRAER ENLACES DINÁMICAMENTE -----
enlaces = set()
scroll_pause = 2
last_height = driver.execute_script("return document.body.scrollHeight")

patron_img = re.compile(r"/(\d{3,})x/")  # busca carpetas como 236x, 474x, etc.

while len(enlaces) < num_imgs:
    # Extraer todas las imágenes cargadas
    imgs = driver.find_elements(By.TAG_NAME, "img")
    for img in imgs:
        src = img.get_attribute("src")
        if src and src.endswith(".jpg") and patron_img.search(src):
            enlaces.add(src)
        if len(enlaces) >= num_imgs:
            break

    # Hacer scroll hacia abajo
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause)

    # Revisar si llegamos al final
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

driver.quit()
print(f"Enlaces encontrados: {len(enlaces)}")

# ----- DESCARGAR IMAGENES -----
print("Descargando imagenes...")
cont_img = 0
for i, url in enumerate(list(enlaces)[:num_imgs], 1):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            # Extraer el nombre original de la URL
            nombre_archivo_original = os.path.basename(urlparse(url).path)
            ruta_archivo = os.path.join(carpeta, nombre_archivo_original)

            # Guardar imagen
            with open(ruta_archivo, "wb") as f:
                f.write(r.content)
            cont_img += 1
            print(f"Imagen {i} descargada como {nombre_archivo_original}")
    except Exception as e:
        print(f"Error descargando imagen {i}: {e}")

print(f"Descarga finalizada. Total de imagenes descargadas: {cont_img}")

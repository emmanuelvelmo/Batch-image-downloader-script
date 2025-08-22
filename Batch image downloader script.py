import os # Para operaciones del sistema de archivos
import time # Para pausas y delays
import re # Para expresiones regulares
import requests # Para realizar peticiones HTTP
import urllib.parse # Para codificar URLs
import selenium.webdriver # Para automatización del navegador web
from selenium.webdriver.common.by import By # Para localizar elementos en la página
from selenium.webdriver.chrome.service import Service # Para el servicio de ChromeDriver
from selenium.webdriver.chrome.options import Options # Para configurar opciones de Chrome

# Bucle principal del programa
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
    opciones_chrome.add_argument("--disable-gpu") # Desactiva la aceleración GPU
    opciones_chrome.add_argument("--log-level=3") # Reduce mensajes de log
    opciones_chrome.add_argument("--window-size=1280,720") # Define tamaño de ventana
    opciones_chrome.add_argument("--no-sandbox") # Mejora compatibilidad
    opciones_chrome.add_argument("--disable-dev-shm-usage") # Evita problemas de memoria
    opciones_chrome.add_argument("--disable-extensions") # Desactiva extensiones
    opciones_chrome.add_argument("--disable-logging") # Desactiva logging adicional
    opciones_chrome.add_argument("--silent") # Modo silencioso
    opciones_chrome.add_argument("--disable-web-security") # Desactiva seguridad web
    opciones_chrome.add_argument("--remote-debugging-port=0") # Desactiva puerto de depuración remota
    
    # Suprimir logs adicionales del servicio
    service_val = Service()
    service_val.creation_flags = 0x08000000  # CREATE_NO_WINDOW en Windows
    
    # Inicializar el driver de Chrome
    driver_val = selenium.webdriver.Chrome(service = service_val, options = opciones_chrome)
    
    # Generar URL de búsqueda
    # Codificar el texto para URL
    texto_codificado = urllib.parse.quote(texto_buscar)
    
    # Construir URL de búsqueda de Pinterest
    url_busqueda = f"https://www.pinterest.com/search/pins/?q={texto_codificado}&rs=typed"
    
    # Navegar a la página de búsqueda
    driver_val.get(url_busqueda)
    
    # Mensaje de progreso
    print("Cargando Pinterest y haciendo scroll...")
    
    # Extraer enlaces de imágenes en página cargada
    enlaces_val = set() # Usar set para evitar duplicados
    
    scroll_pause = 2 # Tiempo de pausa entre scrolls
    
    last_height = driver_val.execute_script("return document.body.scrollHeight") # Obtener altura inicial de la página
    
    patron_img = re.compile(r"/(\d{3,})x/") # busca carpetas con formato mayor a 200 seguido x
    
    # Buscar imágenes haciendo scroll hasta encontrar la cantidad deseada
    while len(enlaces_val) < num_imgs:
        # Encontrar todas las imágenes en la página actual
        imgs = driver_val.find_elements(By.TAG_NAME, "img")
        
        # Procesar cada imagen encontrada
        for img in imgs:
            src = img.get_attribute("src") # Obtener URL de la imagen
            
            # Filtrar solo imágenes JPG de alta resolución
            if src and src.endswith(".jpg") and patron_img.search(src):
                # solo contar si es nuevo
                if src not in enlaces_val:
                    enlaces_val.add(src) # Agregar al conjunto de enlaces
                    
                    # Mostrar progreso
                    print(f"Progreso: {len(enlaces_val)}/{num_imgs} imágenes encontradas", end="\r")
            
            if len(enlaces_val) >= num_imgs:
                break
        
        # Hacer scroll hacia abajo
        driver_val.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scroll al final de la página
        
        time.sleep(scroll_pause) # Pausa para cargar contenido
        
        # Revisar si llegamos al final
        new_height = driver_val.execute_script("return document.body.scrollHeight") # Nueva altura después del scroll
        
        # Si la altura no cambió, hemos llegado al final
        if new_height == last_height:
            break
        
        # Actualizar altura anterior
        last_height = new_height
    
    # Cerrar el navegador
    driver_val.quit()
    
    # Mostrar cantidad de enlaces encontrados
    print(f"\nEnlaces encontrados: {len(enlaces_val)}")
    
    # Descargar imágenes
    # Mensaje de inicio de descarga
    print("Descargando imágenes...")
    
    cont_img = 0 # Contador de imágenes descargadas exitosamente
    
    # Iterar sobre los enlaces y descargar cada imagen
    for iter_val, url_val in enumerate(list(enlaces_val)[:num_imgs], 1):
        try:
            r_val = requests.get(url_val, timeout = 10) # Realizar petición HTTP con timeout
            
            # Verificar si la descarga fue exitosa
            if r_val.status_code == 200:
                # Extraer el nombre original de la URL
                nombre_archivo_original = os.path.basename(urllib.parse.urlparse(url_val).path)
                
                ruta_archivo = os.path.join(texto_buscar, nombre_archivo_original)
                
                # Guardar imagen
                with open(ruta_archivo, "wb") as f_val:
                    f_val.write(r_val.content) 
                    
                cont_img += 1 # Incrementar contador de éxitos
                
                # Mostrar progreso de descarga
                print(f"Imagen {iter_val} descargada como {nombre_archivo_original}")
        except Exception as e:
            continue # Continuar con la siguiente imagen si hay error
    
    print(f"Descarga finalizada. Total de imágenes descargadas: {cont_img}\n")

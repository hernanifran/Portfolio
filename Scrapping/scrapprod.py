import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# Configura el controlador de Chrome (ajusta el path a tu ubicación)
driver = webdriver.Chrome()

def iniciar_sesion():
    # Navega a la página de inicio de sesión
    driver.get('https://comunidad.fundaciontrauma.org.ar/Account/Login')

    # Encuentra los elementos de usuario y contraseña e ingresa las credenciales
    driver.find_element(By.ID, 'Username').send_keys('')
    driver.find_element(By.ID, 'Password').send_keys('')

    # Envía el formulario de inicio de sesión
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    # Espera a que se cargue la página de selección de organización y selecciona una organización
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'ddlOrganizaciones'))
    )

    # Selecciona la organización con el valor '2112'
    select_element = Select(driver.find_element(By.ID, 'ddlOrganizaciones'))
    select_element.select_by_value('2112')
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    # Espera a que la página de aplicaciones se cargue completamente
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'img[alt="Registro Pre-hospitalario"]'))
    )

    # Usa JavaScript para hacer clic en el elemento
    element = driver.find_element(By.CSS_SELECTOR, 'img[alt="Registro Pre-hospitalario"]')
    driver.execute_script("arguments[0].click();", element)

def obtener_datos(numero_hecho):
    try:
        # Navega a la página de detalles específica
        target_url = f"https://registros.fundaciontrauma.org.ar/pre/Hecho/Detalle/{numero_hecho}#Paciente"
        driver.get(target_url)
        
        # Espera a que se cargue el elemento que contiene la historia clínica
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'historial-clinica-item'))
        )
        
        # Agrega un retraso adicional para asegurar que el contenido esté completamente cargado
        time.sleep(1)
        
        # Extrae el valor de la historia clínica
        historia_clinica_element = driver.find_element(By.ID, 'historial-clinica-item')
        historia_clinica = historia_clinica_element.get_attribute('value')
        
        # Extrae el número de hecho de la imagen
        numero_hecho_element = driver.find_element(By.ID, 'cur-number').find_element(By.TAG_NAME, 'strong')
        CUR = numero_hecho_element.text.replace('.', '').replace('-', '')
        
        return historia_clinica, CUR
    
    except Exception as e:
        print(f"Error al obtener los datos para el número de hecho {numero_hecho}: {e}")
        return 'Error', 'Error'

# Inicia sesión una vez
iniciar_sesion()

# Lee los números de hecho del archivo 'prueba1.txt'
path = r'C:\Users\Hernán Ifrán\Downloads\input rph 1.csv'
numeros_hecho = pd.read_csv(path, header=None)[0].tolist()

# Configura el total de registros a procesar en esta ejecución
total_registros = 8261  # Puedes ajustar este valor según tus necesidades

# Divide los números de hecho en lotes de 1000
batch_size = 1000
batches = [numeros_hecho[i:i + batch_size] for i in range(0, min(total_registros, len(numeros_hecho)), batch_size)]

# Inicializa una lista para almacenar todos los resultados
resultados_totales = []

# Procesa cada lote
for i, batch in enumerate(batches, start=1):
    start_time = time.time()
    resultados = []

    for numero_hecho in batch:
        historia_clinica, CUR = obtener_datos(numero_hecho)
        resultados.append({'NumeroHecho': numero_hecho, 'HistoriaClinica': historia_clinica, 'CUR': CUR})

    # Agrega los resultados del lote actual a la lista total
    resultados_totales.extend(resultados)

    # Guarda los resultados acumulados en un archivo Excel
    output_path = r'C:\Users\Hernán Ifrán\Downloads\Mapeo.xlsx'
    df_resultados_totales = pd.DataFrame(resultados_totales)
    df_resultados_totales.to_excel(output_path, index=False)

    # Calcula y muestra el tiempo transcurrido y el tiempo estimado restante
    elapsed_time = time.time() - start_time
    total_batches = len(batches)
    remaining_batches = total_batches - i
    estimated_time_remaining = remaining_batches * elapsed_time
    print(f'Lote {i}/{total_batches} procesado en {elapsed_time:.2f} segundos.')
    print(f'Tiempo estimado restante: {estimated_time_remaining / 60:.2f} minutos.')

# Cierra el navegador al finalizar
driver.quit()

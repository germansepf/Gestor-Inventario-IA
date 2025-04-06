import openai
import concurrent.futures
import pandas as pd
import time
import os
import certifi
from config import OPENAI_API_KEY, OPENAI_ENGINE
import sys
import os

def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Ruta temporal donde PyInstaller extrae los archivos
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# Configurar la clave de la API de OpenAI
openai.api_key = OPENAI_API_KEY

CACHE_FILE = resource_path("cache_descriptions.csv")

def load_cache():
    """Carga el caché desde un archivo CSV."""
    if not os.path.exists(CACHE_FILE):
        return {}
    df_cache = pd.read_csv(CACHE_FILE)
    return df_cache.set_index("generic_name").to_dict(orient="index")

def save_cache(cache):
    """Guarda el caché en un archivo CSV."""
    df = pd.DataFrame.from_dict(cache, orient="index").reset_index()
    df.columns = ["generic_name", "commercial_name", "description"]
    df.to_csv(CACHE_FILE, index=False, encoding='utf-8')

cache = load_cache()

def generate_commercial_name(product_name: str, retries=3) -> str:
    """
    Genera un nombre comercial atractivo para un producto.
    """
    prompt = (
        f"Extrae únicamente el nombre real del modelo del celular a partir del siguiente nombre genérico: '{product_name}'. "
        "El resultado debe ser el nombre exacto del celular sin agregar palabras adicionales. "
        "Si el nombre tiene 'KIT', 'APPLE', 'EDICIÓN ESPECIAL', 'PROMOCIÓN', 'NACIONAL', 'OFERTA', 'CONTADO', elimínalos. "
        "Ejemplo: Si el nombre genérico es 'MOT EDG50FUS512G VR KIT CONTADO', tu respuesta debe ser 'Motorola Edge 50 Fusion 512GB Verde'. Solo responde con el nombre del celular, color, capacidad y accesorio (ten en cuenta el acceserio, generalmente viene seguido de un mas + ej: + BUDS) si lo tiene, nada mas, sin explicaciones"
    )
    
    wait_time = 5
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_ENGINE,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=40,
                temperature=0.7
            )
            
            # Acceder correctamente a la respuesta
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                print(f"⚠️ Respuesta inválida de OpenAI para '{product_name}': {response}")
                return product_name  # Devolver el nombre original si la respuesta es inválida

        except openai.error.RateLimitError:
            print(f"⚠️ Límite de tokens alcanzado ({attempt+1}/{retries}). Esperando {wait_time} segundos...")
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, 30)
            
        except Exception as e:
            print(f"❌ Error generando nombre comercial para '{product_name}': {e}")
            return product_name
    return product_name

def generate_description(product_name: str, retries=3) -> str:
    """
    Genera una descripción detallada para un producto.
    """
    prompt = (
        f"Genera una descripción técnica y promocional para '{product_name}'.\n"
        "- Pantalla: Tipo de pantalla, resolución y tecnología.\n"
        "- Dimensiones y Peso: Medidas y peso aproximado.\n"
        "- Capacidad: Opciones de almacenamiento y RAM.\n"
        "- Cámara: Características principales.\n"
        "- Procesador: Tipo de chip y arquitectura.\n"
        "- Batería: Capacidad y duración estimada.\n"
        "No uses * o # en el texto, no inventes caracteristicas que no existe, utiliza los datos reales del modelo, y en el texto no utilices el nombre genérico, usa el nombre comercial."
    )
    
    wait_time = 5
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_ENGINE,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=350,
                temperature=0.7
            )
            
            # Acceder correctamente a la respuesta
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                print(f"⚠️ Respuesta inválida de OpenAI para '{product_name}': {response}")
                return "Descripción no disponible"

        except openai.error.RateLimitError:
            print(f"⚠️ Límite de tokens alcanzado ({attempt+1}/{retries}). Esperando {wait_time} segundos...")
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, 30)
        except Exception as e:
            print(f"❌ Error generando descripción para '{product_name}': {e}")
            return "Descripción no disponible"
    return "Descripción no disponible"

def generate_commercial_names_in_parallel(list_of_product_names, max_workers=5):
    """
    Genera nombres comerciales en paralelo.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_name = {
            executor.submit(generate_commercial_name, product_name): product_name
            for product_name in list_of_product_names if product_name not in cache
        }
        for future in concurrent.futures.as_completed(future_to_name):
            product_name = future_to_name[future]
            try:
                result = future.result()
                if result:
                    cache[product_name] = {"commercial_name": result, "description": ""}
            except Exception as e:
                print(f"❌ Error generando nombre comercial para '{product_name}': {e}")

    save_cache(cache)
    return result

def generate_descriptions_in_parallel(list_of_product_info, max_workers=5):
    """
    Genera descripciones en paralelo utilizando el generic_name de los productos,
    y sobrescribe las descripciones existentes en el caché.
    """
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Crear tareas para cada producto en la lista
        future_to_generic_name = {
            executor.submit(
                generate_description,
                product_info["name"]  # Usar siempre el nombre comercial
            ): product_info["generic_name"]
            for product_info in list_of_product_info if product_info["generic_name"] in cache
        }

        # Procesar los resultados a medida que se completan
        for future in concurrent.futures.as_completed(future_to_generic_name):
            generic_name = future_to_generic_name[future]
            try:
                result = future.result()
                if result:
                    # Sobrescribir la descripción en el caché usando generic_name
                    cache[generic_name]["description"] = result
                    results.append(result)
                else:
                    # Manejar el caso de descripción no disponible
                    cache[generic_name]["description"] = "Descripción no disponible"
                    results.append("Descripción no disponible")
            except Exception as e:
                print(f"❌ Error generando descripción para '{generic_name}': {e}")
                # Manejar errores y sobrescribir con "Descripción no disponible"
                cache[generic_name]["description"] = "Descripción no disponible"
                results.append("Descripción no disponible")

    # Guardar el caché actualizado en el archivo
    save_cache(cache)
    return results
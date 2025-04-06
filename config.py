import os



# Variables de entorno para las APIs (opcional, si no quieres leerlas en otros archivos)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "TU-API-KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "TU-API")
GOOGLE_CX = os.getenv("GOOGLE_CX", "API")

# Ajustes para la generación de descripciones
OPENAI_ENGINE = "gpt-4o"

# Ajustes para la búsqueda de imágenes
IMAGES_PER_PRODUCT = 4  # Número de imágenes a buscar (máximo)

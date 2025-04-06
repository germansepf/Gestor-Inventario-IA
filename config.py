import os



# Variables de entorno para las APIs (opcional, si no quieres leerlas en otros archivos)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBv1XNHwjFe5SvzkPK0PN1kf1hhzA_QF_c")
GOOGLE_CX = os.getenv("GOOGLE_CX", "54361eb35c4e04805")

# Ajustes para la generación de descripciones
OPENAI_ENGINE = "gpt-4o"

# Ajustes para la búsqueda de imágenes
IMAGES_PER_PRODUCT = 4  # Número de imágenes a buscar (máximo)

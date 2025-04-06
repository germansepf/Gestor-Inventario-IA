# 📦 Gestor de Inventario con Inteligencia Artificial

Este es un software desarrollado para **Conexiones Celulares**, una empresa nacional dedicada a la venta de dispositivos móviles. 
El programa automatiza el procesamiento del inventario diario de productos, generando nombres comerciales y descripciones con ayuda de IA, además de permitir aplicar filtros personalizados y exportar el archivo listo para plataformas como **Wix**.

---

## 🚀 Funcionalidades principales

- 📂 Carga de inventario desde archivos Excel.
- 🧠 Generación automática de nombres comerciales con IA (OpenAI).
- ✍️ Descripciones técnicas y promocionales generadas por IA.
- 🔎 Filtros por sucursal y precio.
- 🖼️ Asignación automática de imágenes a cada producto.
- 📊 Exportación a formato compatible con el panel de Wix.
- 💾 Almacenamiento inteligente en caché para evitar llamadas innecesarias a la API.
- ✅ Interfaz gráfica amigable desarrollada con Tkinter.

---

## 🛠️ Tecnologías usadas

- Python 3
- OpenAI API
- Tkinter (GUI)
- Pandas
- PyInstaller (para crear el ejecutable)
- Git

---

## 📁 Estructura del proyecto

```bash
venta_celulares_pag/
│
├── modules/
│   ├── ai_description.py          # Generación de nombres comerciales y descripciones con IA
│   ├── data_cleaner.py            # Limpieza, transformación y estructura del DataFrame
│   ├── excel_handler.py           # Lectura y escritura de archivos Excel
│
├── cache_descriptions.csv         # Memoria de IA (nombres y descripciones generadas)
├── urls_celulares.csv             # Archivo con las imágenes por modelo
├── gui.py                         # Interfaz gráfica
├── config.py                      # Llave API y configuraciones
├── README.md

📦 Cómo usar el programa
Ejecuta el archivo gui.py (o el ejecutable si ya fue compilado).

1. Carga el archivo de inventario (.xlsx).
2. Aplica los filtros necesarios.
3. Haz clic en “Generar con IA”.
4. Guarda el archivo final.

⚖️ Licencia
Este software fue desarrollado como encargo exclusivo para Conexiones Celulares. No se permite su distribución sin autorización previa.

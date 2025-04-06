import pandas as pd
from modules.ai_description import generate_commercial_names_in_parallel, generate_descriptions_in_parallel, cache, save_cache
import sys
import os

def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Ruta temporal donde PyInstaller extrae los archivos
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def clean_and_transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma los datos del inventario eliminando duplicados, agregando columnas necesarias
    y calculando el conteo de inventario por producto y sucursal.
    """
    # Seleccionar y copiar las columnas necesarias
    df = df[['Sucursal', 'Código Producto', 'Marca', 'Costo de compra', 'Producto']].copy()

    # Normalizar y agregar columnas iniciales
    df["name"] = df["Producto"].astype(str).fillna("")
    df["sku"] = df["Código Producto"]
    df["collection"] = df["Marca"].str.upper().str.strip().replace({"APPLE": "IPHONE"})
    df["brand"] = df["Sucursal"]
    df["price"] = df["Costo de compra"]
    df["visible"] = "TRUE"
    df["fieldType"] = "Product"

    # Calcular el conteo de inventario por Producto y Sucursal
    inventory_counts = df.groupby(["Producto", "Sucursal"]).size().reset_index(name="inventory")

    # Agrupar por Producto y Sucursal, seleccionando los primeros valores relevantes
    df_grouped = df.groupby(["Producto", "Sucursal"], as_index=False).agg({
        "sku": "first",
        "collection": "first",
        "brand": "first",
        "price": "first",
        "visible": "first",
        "fieldType": "first",
        "Código Producto": "first",
    })

    # Unir el conteo de inventario al DataFrame agrupado
    df_grouped = df_grouped.merge(inventory_counts, on=["Producto", "Sucursal"], how="left")

    # 1. Asignar 'name' y 'description' desde el caché usando SIEMPRE la clave 'Producto'.
    df_grouped["name"] = df_grouped["Producto"].apply(
        lambda p: cache.get(p, {}).get("commercial_name", p)
    )
    df_grouped["description"] = df_grouped["Producto"].apply(
        lambda p: cache.get(p, {}).get("description", "")
    )

    # 2. Identificar qué productos NO tienen nombre comercial o descripción
    products_without_commercial_name = [
        p for p in df_grouped["Producto"] if p not in cache
    ]
    products_without_description = [
        p for p in df_grouped["Producto"] if not cache.get(p, {}).get("description")
    ]

    # 3. Generar nombres comerciales si faltan
    if products_without_commercial_name:
        print(f"🔍 Generando nombres comerciales para {len(products_without_commercial_name)} productos...")
        generate_commercial_names_in_parallel(products_without_commercial_name, max_workers=5)

    # 4. Generar descripciones si faltan
    if products_without_description:
        print(f"🔍 Generando descripciones para {len(products_without_description)} productos...")
        product_info_list = [{"name": p} for p in products_without_description]
        generate_descriptions_in_parallel(product_info_list, max_workers=5)

    # Guardar cambios en el caché inmediatamente después de generar los datos
    save_cache(cache)
    
    # 5. Volver a asignar 'name' y 'description' desde el caché ya actualizado
    df_grouped["name"] = df_grouped["Producto"].apply(
        lambda p: cache.get(p, {}).get("commercial_name", p)
    )
    df_grouped["description"] = df_grouped["Producto"].apply(
        lambda p: cache.get(p, {}).get("description", "")
    )
    
    # ====== Asignar URLs de imágenes ======
    # Cargar el archivo CSV con los URLs de las imágenes
    image_urls_path = resource_path("image_urls.csv")
    image_urls_df = pd.read_csv(image_urls_path, delimiter=";")

    # Seleccionar solo las columnas relevantes
    image_urls_df = image_urls_df[["Nombre_comercial", "Url_Imagnes"]].copy()

    # Asegurarnos de que no haya valores nulos
    image_urls_df.dropna(subset=["Nombre_comercial", "Url_Imagnes"], inplace=True)

    # Opcional: Si deseas usar solo el primer URL de cada celda
    # Mantener todos los URLs concatenados
    image_urls_df["Url_Imagnes"] = image_urls_df["Url_Imagnes"].apply(lambda x: ";".join(x.split(";")))

    # Realizar la unión entre df_grouped y image_urls_df
    df_grouped = df_grouped.merge(
        image_urls_df,
        left_on="name",  # Columna en df_grouped
        right_on="Nombre_comercial",  # Columna en image_urls_df
        how="left"  # Unión izquierda para mantener todos los productos en df_grouped
    )

    # Asignar los valores de Url_Imagnes a la columna productImageUrl
    df_grouped["productImageUrl"] = df_grouped["Url_Imagnes"]

    # Eliminar columnas adicionales si no son necesarias
    df_grouped.drop(columns=["Nombre_comercial", "Url_Imagnes"], inplace=True)

    # ====== EJEMPLO DE COLUMNAS FINALES ======
    df_grouped["handleld"] = df_grouped.index.map(lambda i: f"Product_{i+1}")

    final_columns = [
        "handleld", "fieldType", "name", "description", "productImageUrl",
        "collection", "sku", "price", "inventory", "visible", "brand"
    ]
    
    # Guardar cambios en caché
    save_cache(cache)
    
    return df_grouped[final_columns]

def apply_filters(df: pd.DataFrame, selected_sucursales: list, min_price: float, max_price: float) -> pd.DataFrame:
    """
    Aplica filtros de sucursales y precios al DataFrame transformado.
    """
    # Filtrar por sucursales seleccionadas
    if selected_sucursales:
        df = df[df["brand"].isin(selected_sucursales)]

    # Filtrar por rango de precios
    if min_price is not None:
        df = df[df["price"] >= min_price]
    if max_price is not None:
        df = df[df["price"] <= max_price]

    return df
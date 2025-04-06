import pandas as pd
import os
from modules.excel_handler import read_excel, write_excel
from modules.data_cleaner import clean_and_transform_data

def main():
    try:
        input_file = "inventario_fisico.xlsx"  # Se asume que el archivo base es este

        # Verificar si el archivo existe
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"❌ El archivo '{input_file}' no fue encontrado.")

        print(f"📖 Leyendo archivo: {input_file}...")
        df_inventario_fisico = read_excel(input_file)

        print("🛠 Aplicando limpieza y transformación de datos...")
        df_final = clean_and_transform_data(df_inventario_fisico)

        output_file = "inventario_final.xlsx"
        print(f"💾 Guardando archivo final en: {output_file}...")
        write_excel(df_final, output_file)

        print("✅ ¡Archivo final generado con éxito!")

    except FileNotFoundError as fnf_error:
        print(f"⚠️ Error: {fnf_error}")
    except Exception as e:
        print(f"❌ Error inesperado durante el proceso: {e}")

if __name__ == "__main__":
    main()

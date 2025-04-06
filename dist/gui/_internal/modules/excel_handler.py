import pandas as pd

def read_excel(file_path: str) -> pd.DataFrame:
    """
    Lee un archivo Excel (.xlsx o .xls) y retorna un DataFrame.
    
    Parámetros:
      - file_path: Ruta del archivo Excel a leer.
    
    Retorna:
      - Un DataFrame con el contenido del archivo.
    
    Lanza una excepción si ocurre algún error en la lectura.
    """
    try:
        if file_path.endswith(".xls"):
            df = pd.read_excel(file_path, engine="xlrd")  # Para archivos .xls
        else:
            df = pd.read_excel(file_path, engine="openpyxl")  # Para archivos .xlsx
        return df
    except Exception as e:
        print(f"Error al leer el archivo {file_path}: {e}")
        raise


def write_excel(df: pd.DataFrame, output_path: str) -> None:
    """
    Escribe un DataFrame en un archivo Excel.
    
    Parámetros:
      - df: DataFrame a guardar.
      - output_path: Ruta donde se creará el archivo Excel.
    
    Lanza una excepción si ocurre algún error durante la escritura.
    """
    try:
        df.to_excel(output_path, index=False, engine="openpyxl")
    except Exception as e:
        print(f"Error al escribir el archivo {output_path}: {e}")
        raise

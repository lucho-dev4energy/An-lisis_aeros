import pandas as pd
import numpy as np

# Rutas de archivos
scada_path = r'c:\Users\lvidal\Documents\SCADA\PEM\Limpieza_SCADA\2.SCADA_PEM_con_PD.csv'
pc4_path = r'c:\Users\lvidal\Documents\SCADA\PEM\Analisis_Real_vs_Teorico\PowerCurve_SWT-2.3MW.csv'
pc5_path = r'c:\Users\lvidal\Documents\SCADA\PEM\Analisis_Real_vs_Teorico\PowerCurve_SWT-3.15MW.csv'
output_path = r'c:\Users\lvidal\Documents\SCADA\PEM\Analisis_Real_vs_Teorico\1.SCADA_PEM_con_PT.csv'

def main():
    print("Cargando datos...")
    # Cargar datos
    df_scada = pd.read_csv(scada_path, sep=';', low_memory=False)
    df_pc4 = pd.read_csv(pc4_path, sep=';')
    df_pc5 = pd.read_csv(pc5_path, sep=';')

    print("Limpiando columnas...")
    # Eliminar columnas TimeStamp y Potencia Disponible
    columnas_a_eliminar = ['TimeStamp', 'Potencia Disponible']
    df_scada.drop(columns=[col for col in columnas_a_eliminar if col in df_scada.columns], inplace=True)

    print("Calculando Potencia Teórica por interpolación...")
    # Extraer arrays para interpolación
    pc4_x = df_pc4['WindSpeed'].values
    pc4_y = df_pc4['Potencia Teórica'].values
    
    pc5_x = df_pc5['WindSpeed'].values
    pc5_y = df_pc5['Potencia Teórica'].values

    # Máscaras booleanas por tipo de estación
    mask_4 = df_scada['StationTypeId'] == 4.0
    mask_5 = df_scada['StationTypeId'] == 5.0

    # Inicializar columna en NaN
    df_scada['Potencia Teórica'] = np.nan

    # Interpolar vectorizadamente
    df_scada.loc[mask_4, 'Potencia Teórica'] = np.interp(df_scada.loc[mask_4, 'WindSpeed'], pc4_x, pc4_y)
    df_scada.loc[mask_5, 'Potencia Teórica'] = np.interp(df_scada.loc[mask_5, 'WindSpeed'], pc5_x, pc5_y)

    print("Calculando Potencia Perdida y Error...")
    
    # Crear columna ActivePower_MW (en MW)
    try:
        col_idx = df_scada.columns.get_loc('ActivePower') + 1
        df_scada.insert(col_idx, 'ActivePower_MW', df_scada['ActivePower'] / 1000)
    except Exception:
        df_scada['ActivePower_MW'] = df_scada['ActivePower'] / 1000

    # 1. Potencia Perdida en MW (Potencia Teórica - ActivePower_MW), mínimo 0
    df_scada['Potencia Perdida'] = df_scada['Potencia Teórica'] - df_scada['ActivePower_MW']
    df_scada['Potencia Perdida'] = df_scada['Potencia Perdida'].clip(lower=0)
    
    # 2. Error (%): Valor absoluto calculado con ActivePower en MW
    df_scada['Error (%)'] = np.where(df_scada['Potencia Teórica'] > 0, 
                                     np.abs((df_scada['Potencia Teórica'] - df_scada['ActivePower_MW']) / df_scada['Potencia Teórica'] * 100), 
                                     0)

    print("Guardando resultado...")
    # Guardar a CSV
    df_scada.to_csv(output_path, sep=';', index=False)
    print(f"¡Proceso completado! Archivo guardado en: {output_path}")

if __name__ == "__main__":
    main()

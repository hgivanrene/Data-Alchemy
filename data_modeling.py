def data_alchemy():
    import json
    import pandas as pd
    import sqlite3
    import matplotlib.pyplot as plt
    import seaborn as sns

    # obtener los datos apartir del archivo de data,json dentro del folder
    with open('data.json', 'r') as file:
        data = json.load(file)
   
    # Convertir el archivo que se recive a un dataframe, adicional se retiran los campos redundantes y se unifica fecha y hora en un solo registo.
    # Adicional, se define el tipo de dato de cada uno de los datos.
    df = pd.DataFrame(data)
    df = df[['orden', 'fecha', 'hora', 'gravedad', 'peaton', 'automovil', 'campero', 'camioneta',
             'micro', 'buseta', 'bus', 'camion', 'volqueta', 'moto', 'bicicleta', 'otro', 'barrio',
             'entidad', 'propietario_de_veh_culo', 'diurnio_nocturno']]
    df['orden'] = df['orden'].astype(int)
    df['fecha_hora'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y') + pd.to_timedelta(df['hora'])
    df['gravedad'] = df['gravedad'].astype(str)
    df['peaton'] = df['peaton'].astype(int)
    df['automovil'] = df['automovil'].astype(int)
    df['campero'] = df['campero'].astype(int)
    df['camioneta'] = df['camioneta'].astype(int)
    df['micro'] = df['micro'].astype(int)
    df['buseta'] = df['buseta'].astype(int)
    df['bus'] = df['bus'].astype(int)
    df['camion'] = df['camion'].astype(int)
    df['volqueta'] = df['volqueta'].astype(int)
    df['moto'] = df['moto'].astype(int)
    df['bicicleta'] = df['bicicleta'].astype(int)
    df['otro'] = df['otro'].astype(int)
    df['barrio'] = df['barrio'].astype(str)
    df['entidad'] = df['entidad'].astype(str)
    df['propietario_de_veh_culo'] = df['propietario_de_veh_culo'].astype(str)
    df['diurnio_nocturno'] = df['diurnio_nocturno'].astype(str)
    df = df.drop(columns=['fecha', 'hora'])

    # connexión de forma local para modelar el DataFrame con SQL
    conn = sqlite3.connect(':memory:')

    df.to_sql('base', conn, index=False, if_exists='replace')

    # Consultas al dataframe a partir de SQL
    diurno_nocturno = '''SELECT GRAVEDAD
                         , DIURNIO_NOCTURNO
                         , COUNT(DISTINCT ORDEN) AS ACCIDENTES
                  FROM base
                  GROUP BY GRAVEDAD, DIURNIO_NOCTURNO'''

    accidentes_dia = '''SELECT CASE WHEN strftime('%w',FECHA_HORA) = '0' THEN 'DOMINGO'
                                 WHEN strftime('%w',FECHA_HORA) = '1' THEN 'LUNES'
                                 WHEN strftime('%w',FECHA_HORA) = '2' THEN 'MARTES'
                                 WHEN strftime('%w',FECHA_HORA) = '3' THEN 'MIERCOLES'
                                 WHEN strftime('%w',FECHA_HORA) = '4' THEN 'JUEVES'
                                 WHEN strftime('%w',FECHA_HORA) = '5' THEN 'VIERNES'
                                 WHEN strftime('%w',FECHA_HORA) = '6' THEN 'SABADO'
                             END AS DAY
                          , GRAVEDAD
                          , COUNT(DISTINCT ORDEN) AS ACCIDENTES
                  FROM base
                  GROUP BY 1,2 
                  ORDER BY strftime('%w',FECHA_HORA) ASC'''
    
    vehiculos_implicados = '''SELECT COUNT(CASE WHEN PEATON > 0 THEN 1 END) AS PEATON
                          , COUNT(CASE WHEN AUTOMOVIL > 0 THEN 1 END) AS AUTOMOVIL
                          , COUNT(CASE WHEN CAMPERO > 0 THEN 1 END) AS CAMPERO
                          , COUNT(CASE WHEN CAMIONETA > 0 THEN 1 END) AS CAMIONETA
                          , COUNT(CASE WHEN MICRO > 0 THEN 1 END) AS MICRO
                          , COUNT(CASE WHEN BUSETA > 0 THEN 1 END) AS BUSETA
                          , COUNT(CASE WHEN BUS > 0 THEN 1 END) AS BUS
                          , COUNT(CASE WHEN CAMION > 0 THEN 1 END) AS CAMION
                          , COUNT(CASE WHEN VOLQUETA > 0 THEN 1 END) AS VOLQUETA
                          , COUNT(CASE WHEN MOTO > 0 THEN 1 END) AS MOTO
                          , COUNT(CASE WHEN BICICLETA > 0 THEN 1 END) AS BICICLETA
                          , COUNT(CASE WHEN OTRO > 0 THEN 1 END) AS OTRO
                  FROM base'''
    
    diurno_nocturno_value = pd.read_sql(diurno_nocturno, conn)
    accidentes_dia_value = pd.read_sql(accidentes_dia, conn)
    vehiculos_implicados_value = pd.read_sql(vehiculos_implicados, conn)
    # Pivoteo del output de vehiculos implicados ya que el output viene a nivel de columnas.
    df_pivot = pd.melt(vehiculos_implicados_value, var_name='Vehiculo', value_name='Cantidad')


    # Cierre conexión local SQLite
    conn.close()

    # Crear un gráfico de barras apiladas
    plt.figure(figsize=(10, 6))
    bar_plot = sns.barplot(x='gravedad', y='ACCIDENTES', hue='diurnio_nocturno', data=diurno_nocturno_value, palette='viridis')

    # Configurar el gráfico de barras apiladas
    plt.title('GRAVEDAD_ACCIDENTES')
    plt.xlabel('GRAVEDAD')
    plt.ylabel('ACCIDENTES')
    plt.xticks(rotation=45)
    plt.legend(title='DIURNIO_NOCTURNO')
    plt.tight_layout()

    # Agregar etiquetas en las barras
    for p in bar_plot.patches:
        bar_plot.annotate(f'{p.get_height()}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', 
                        fontsize=10, color='black', 
                        xytext=(0, 5),  # Desplazar un poco hacia arriba
                        textcoords='offset points')

    # Guardad y mostrar el gráfico
    plt.savefig('gravedad_accidentes.png')
    # plt.show()

    # Crear el gráfico de líneas
    plt.figure(figsize=(10, 6))
    line_plot = sns.lineplot(data=accidentes_dia_value, x='DAY', y='ACCIDENTES', hue='gravedad', marker='o')

    # Configurar el gráfico de líneas
    plt.title('Accidentes_por_dia_de_la_semana')
    plt.xlabel('DAY')
    plt.ylabel('ACCIDENTES')
    plt.xticks(rotation=45)
    plt.legend(title='gravedad')
    plt.tight_layout()

    # Agregar etiquetas en los puntos
    for line in line_plot.lines:
        # Obtener las coordenadas de cada punto
        for x, y in zip(line.get_xdata(), line.get_ydata()):
            line_plot.text(x, y, f'{y}', 
                        horizontalalignment='center', 
                        verticalalignment='bottom', 
                        fontsize=10, color='black')

    # Guardad y mostrar el gráfico
    plt.savefig('accidentes_dia.png')
    # plt.show()

    # Crear un gráfico de barras apiladas
    plt.figure(figsize=(10, 6))
    bar_plot = sns.barplot(x='Vehiculo', y='Cantidad', data=df_pivot, palette='viridis')

    # Configurar el gráfico de barras apiladas
    plt.title('Vehiculos_implicados')
    plt.xlabel('Vehiculo')
    plt.ylabel('Cantidad')
    plt.xticks(rotation=45)
    plt.legend(title='Vehiculos_implicados')
    plt.tight_layout()

    # Agregar etiquetas en las barras
    for p in bar_plot.patches:
        bar_plot.annotate(f'{p.get_height()}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', 
                        fontsize=10, color='black', 
                        xytext=(0, 5),  # Desplazar un poco hacia arriba
                        textcoords='offset points')

    # Guardad y mostrar el gráfico
    plt.savefig('Vehiculos_implicados.png')
    # plt.show()


if __name__ == '__main__':
    data_alchemy()
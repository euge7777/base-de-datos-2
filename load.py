import pandas as pd
from sqlalchemy import create_engine, text

USER = "root"
PWD = "123456"
HOST = "localhost"
PORT = "3306"
DB = "crimenes_db_clean"

engine = create_engine(f"mysql+pymysql://{USER}:{PWD}@{HOST}:{PORT}/{DB}")

df = pd.read_excel("crimenes_db_clean.xlsx", sheet_name = "Crimenes")

dim_fecha = (
    df[["Year", "Month", "Day"]]
)
dim_fecha.to_sql("dim_fecha", con = engine, if_exists = "append", index = False)

dim_hora = (
    df[["Time"]]
)
dim_hora.to_sql("dim_hora", con = engine, if_exists = "append", index = False)


print("Datos cargados correctamente") 


import pandas as pd
from sqlalchemy import create_engine, text

USER = "root"
PWD = "123456"
HOST = "localhost"
PORT = "3306"
DB = "crimenes_db_clean"

engine = create_engine(f"mysql+pymysql://{USER}:{PWD}@{HOST}:{PORT}/{DB}")
                       
df.to_sql("crimenes", con = engine, if_exists = "replace", index = False)

print("Datos cargados correctamente")


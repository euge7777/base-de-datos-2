import pandas as pd
from sqlalchemy import create_engine, text

USER = "root"
PWD = "123456"
HOST = "localhost"
PORT = "3306"
DB = "crimenes_db_clean"

engine = create_engine(f"mysql+pymysql://{USER}:{PWD}@{HOST}:{PORT}/{DB}")

df = pd.read_excel("crimenes_db_clean.xlsx", sheet_name = "Crimenes")

df = df.drop_duplicates(subset = ["CaseNumber"])

df["Year"] = pd.to_numeric(df["Year"], errors = "coerce" ).astype("Int64")
df["Month"] = pd.to_numeric(df["Month"], errors = "coerce" ).astype("Int64")
df["Day"] = pd.to_numeric(df["Day"], errors = "coerce" ).astype("Int64")

df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S", errors="coerce").dt.time

df["Description"] = df["Description"].astype(str).str.upper()
df["LocationDescription"] = df["LocationDescription"].astype(str).str.upper()

df["Description"] = df["Description"].str.replace(r"\s*,\s*", ", ", regex=True)
df["LocationDescription"] = df["LocationDescription"].str.replace(r"\s*,\s*", ", ", regex=True)

df["Description"] = df["Description"].str.replace(r"\s*-\s*", " - ", regex=True)
df["LocationDescription"] = df["LocationDescription"].str.replace(r"\s*-\s*", " - ", regex=True)

df["District"] = pd.to_numeric(df["District"], errors="coerce").astype("Int64")
df["CommunityArea"] = pd.to_numeric(df["CommunityArea"], errors="coerce").astype("Int64")


with engine.connect() as conn: 
    conn.execute(text("SET FOREING_KEY_CHECKS =  0"))
    conn.execute(text("TRUNCATE TABLE hecho_crimenes"))
    conn.execute(text("TRUNCATE TABLE dim_fecha"))
    conn.execute(text("TRUNCATE TABLE dim_hora"))
    conn.execute(text("TRUNCATE TABLE dim_ubicacion"))
    conn.execute(text("TRUNCATE TABLE dim_tipo"))
    conn.execute(text("TRUNCATE TABLE dim_arresto"))
    conn.execute(text("SET FOREING_KEY_CHECKS =  1"))
 
dim_fecha = (
    df[["Year", "Month", "Day"]]
)
dim_fecha.to_sql("dim_fecha", con = engine, if_exists = "append", index = False)
fecha_db = pd.read_sql("SELECT id_fecha, year, month, day FROM dim_fecha", con = engine)

dim_hora = (
    df[["Time"]]
)
dim_hora.to_sql("dim_hora", con = engine, if_exists = "append", index = False)
hora_db = pd.read_sql("SELECT id_hora, time FROM dim_hora", con = engine)

dim_ubicacion = (
    df[["District", "CommunnityArea", "LocationDescription"]]
)
dim_ubicacion.to_sql("dim_ubicacion", con = engine, if_exists = "append", index = False)
ubicacion_db = pd.read_sql("SELECT id_ubicacion, district, community_area, location_description FROM dim_ubicacion", con = engine)

dim_tipo = (
    df[["IUCR", "Description"]]
)
dim_tipo.to_sql("dim_tipo", con = engine, if_exists = "append", index = False)
tipo_db = pd.read_sql("SELECT id_tipo, iucr, description FROM dim_tipo", con = engine)

dim_arresto = (
    df[["Arrest"]]
)
dim_arresto.to_sql("dim_arresto", con = engine, if_exists = "append", index = False)
arresto_db = pd.read_sql("SELECT id_arresto, arrest FROM dim_arresto", con = engine)

db_hecho_crimenes = df[["CaseNumber", "Updated_Date", "Year", "Month", "Day", "Time", "District", "CommunityArea", "IUCR", "Description", "LocationDescription", "Arrest"]]

df_hecho_crimenes = df_hecho_crimenes.merge(
    fecha_db,
    how = "left",
    left_on = ["Year", "Month", "Day"],
    right_on = ["year", "month", "day"]
)

df_hecho_crimenes = df_hecho_crimenes.merge(
    hora_db,
    how = "left",
    left_on = "Time",
    right_on = "time"
)

df_hecho_crimenes = df_hecho_crimenes.merge(
    ubicacion_db,
    how = "left",
    left_on = ["District", "CommunityArea", "LocationDescription"],
    right_on = ["district", "community_area", "location_description"]
)

df_hecho_crimenes = df_hecho_crimenes.merge(
    tipo_db,
    how = "left",
    left_on = ["IUCR", "Description"],
    right_on = ["iucr", "description"]
)

df_hecho_crimenes = df_hecho_crimenes.merge(
    arresto_db,
    how = "left",
    left_on = "Arrest",
    right_on = "arrest"
)

df_hecho_crimenes_final = df_hecho_crimenes[[
    "CaseNumber",
    "Updated_Date",
    "id_fecha",
    "id_hora",
    "id_ubicacion",
    "id_tipo",
    "id_arresto"
]].dropna(subset = ["id_fecha", "id_hora", "id_ubicacion", "id_tipo", "id_arresto"])

df_hecho_crimenes_final.to_sql("hecho_crimenes", con = engine, if_exists = "append", index = False)

print("Datos cargados correctamente") 




import pandas as pd
from sqlalchemy import create_engine, text

USER = "root"
PWD = "123456"
HOST = "localhost"
PORT = "3306"
DB = "crimenes_db_clean"

engine = create_engine(f"mysql+pymysql://{USER}:{PWD}@{HOST}:{PORT}/{DB}")


df = pd.read_excel("crimenes_db_clean.xlsx", sheet_name="Sheet1")
df = df.drop_duplicates(subset=["CaseNumber"])

df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
df["Month"] = pd.to_numeric(df["Month"], errors="coerce").astype("Int64")
df["Day"] = pd.to_numeric(df["Day"], errors="coerce").astype("Int64")
df["District"] = pd.to_numeric(df["District"], errors="coerce").astype("Int64")
df["CommunityArea"] = pd.to_numeric(df["CommunityArea"], errors="coerce").astype("Int64")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df["Arrest"] = pd.to_numeric(df["Arrest"], errors="coerce").fillna(0).astype("Int64")

df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S", errors="coerce")
df["Time"] = df["Time"].apply(lambda x: x.strftime("%H:%M:%S") if not pd.isnull(x) else None)

string_cols = ["IUCR", "Description", "LocationDescription"]
for col in string_cols:
    df[col] = df[col].astype(str).str.upper().str.strip()
    df[col] = df[col].str.replace(r"\s*,\s*", ", ", regex=True)
    df[col] = df[col].str.replace(r"\s*-\s*", " - ", regex=True)

with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    conn.execute(text("TRUNCATE TABLE hecho_crimenes"))
    conn.execute(text("TRUNCATE TABLE dim_fecha"))
    conn.execute(text("TRUNCATE TABLE dim_hora"))
    conn.execute(text("TRUNCATE TABLE dim_ubicacion"))
    conn.execute(text("TRUNCATE TABLE dim_tipo"))
    conn.execute(text("TRUNCATE TABLE dim_arresto"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

dim_fecha = df[["Year", "Month", "Day"]].rename(columns={
    "Year":"year",
    "Month":"month",
    "Day":"day"
}).drop_duplicates()
dim_fecha.to_sql("dim_fecha", con=engine, if_exists="append", index=False)
fecha_db = pd.read_sql("SELECT id_fecha, year, month, day FROM dim_fecha", con=engine)
fecha_db[["year","month","day"]] = fecha_db[["year","month","day"]].astype("Int64")

dim_hora = df[["Time"]].rename(columns={
    "Time":"time"
}).drop_duplicates()
dim_hora.to_sql("dim_hora", con=engine, if_exists="append", index=False)
hora_db = pd.read_sql("SELECT id_hora, time FROM dim_hora", con=engine)
hora_db['time'] = hora_db['time'].apply(lambda x: str(x).split()[-1] if pd.notnull(x) else None)

dim_ubicacion = df[["District","CommunityArea","LocationDescription","Latitude","Longitude"]].rename(columns={
"District":"district",
"CommunityArea":"community_area",
"LocationDescription":"location_description",
"Latitude":"latitude",
"Longitude":"longitude"
}).drop_duplicates()
dim_ubicacion.to_sql("dim_ubicacion", con=engine, if_exists="append", index=False)
ubicacion_db = pd.read_sql("SELECT id_ubicacion, district, community_area, location_description, latitude, longitude FROM dim_ubicacion", con=engine)
ubicacion_db["district"] = ubicacion_db["district"].astype("Int64")
ubicacion_db["community_area"] = ubicacion_db["community_area"].astype("Int64")
ubicacion_db["location_description"] = ubicacion_db["location_description"].str.upper().str.strip()

# Tipo

dim_tipo = df[["IUCR","Description"]].rename(columns={
    "IUCR":"iucr",
    "Description":"description"
}).drop_duplicates()
dim_tipo["iucr"] = dim_tipo["iucr"].astype(str).str.upper().str.strip()
dim_tipo["description"] = dim_tipo["description"].astype(str).str.upper().str.strip()
dim_tipo.to_sql("dim_tipo", con=engine, if_exists="append", index=False)
tipo_db = pd.read_sql("SELECT id_tipo, iucr, description FROM dim_tipo", con=engine)
tipo_db["iucr"] = tipo_db["iucr"].astype(str).str.upper().str.strip()
tipo_db["description"] = tipo_db["description"].astype(str).str.upper().str.strip()

dim_arresto = df[["Arrest"]].rename(columns={
    "Arrest":"arrest"
}).drop_duplicates()
dim_arresto.to_sql("dim_arresto", con=engine, if_exists="append", index=False)
arresto_db = pd.read_sql("SELECT id_arresto, arrest FROM dim_arresto", con=engine)
arresto_db["arrest"] = arresto_db["arrest"].astype("Int64")

df_hecho_crimenes = df.merge(
    fecha_db, 
    how="left", 
    left_on=["Year","Month","Day"], 
    right_on=["year","month","day"]
)

df_hecho_crimenes = df_hecho_crimenes.merge(
    hora_db, 
    how="left", 
    left_on="Time", 
    right_on="time"
)

df_hecho_crimenes = df_hecho_crimenes.merge(
    ubicacion_db, 
    how="left",
    left_on=["District","CommunityArea","LocationDescription","Latitude","Longitude"],
    right_on=["district","community_area","location_description","latitude","longitude"]
)

df_hecho_crimenes = df_hecho_crimenes.merge(
    tipo_db, 
    how="left", 
    left_on=["IUCR","Description"], 
    right_on=["iucr","description"]
)

df_hecho_crimenes = df_hecho_crimenes.merge(
    arresto_db, 
    how="left", 
    left_on="Arrest", 
    right_on="arrest"
)

df_hecho_crimenes_final = df_hecho_crimenes[[
"CaseNumber","id_fecha","id_hora","id_ubicacion","id_tipo","id_arresto"
]].dropna(subset=["id_fecha","id_hora","id_ubicacion","id_tipo","id_arresto"]).rename(columns={"CaseNumber":"case_number"})

df_hecho_crimenes_final.to_sql("hecho_crimenes", con=engine, if_exists="append", index=False)
print("Datos cargados correctamente")

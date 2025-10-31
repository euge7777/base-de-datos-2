import pandas as pd 

# df = pd.read_csv("crimnenes_db.csv")
df_copia = pd.read_csv("crimenes_db.csv")
df = df_copia.copy()

df = df.drop(columns=["Latitude", "Longitude", "Location", "XCoordinate", "YCoordinate", "FBICode", "Beat", "Ward", "Block", "Year"])

df = df.rename(columns={"date_only": "Date"})

df["Date"] = pd.to_datetime(df["Date"], errors="coerce") 

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Day"] = df["Date"].dt.day

numeric_columns = ["IUCR", "District", "CommunityArea"]
for col in numeric_columns :
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset = "IUCR")

text_columns = ["Description", "LocationDescription"]
for col in text_columns :
    df[col] = df[col].astype(str).str.upper().str.strip()

for col in text_columns :
    df[col] = df[col].str.replace(r"\s*,\s*", ", ", regex = True)
    df[col] = df[col].str.replace(r"\s*-\s*", " - ", regex = True)

df = df.rename(columns={"UpdatedOn": "Updated_Date"})
df["Updated_Date"] = pd.to_datetime(df["Updated_Date"], errors="coerce")
df["Updated_Date"] = df["Updated_Date"].dt.date

df = df.rename(columns = {"time_only" : "Time"})
df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S", errors="coerce").dt.time

df["Arrest"] = pd.to_numeric(df["Arrest"], errors = "coerce").fillna(0)

df = df.drop_duplicates(subset=["CaseNumber"])

df.to_csv("crimenes_db_clean.csv", index = False)

df.to_excel("crimenes_db_clean.xlsx", index = False)

print("ETL compltado. Archivo generado con exito")
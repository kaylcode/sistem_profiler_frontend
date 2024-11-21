import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql import text

# Database configuration
DB_NAME = "profiling_students"
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Database connection for admin operations
ADMIN_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/"
admin_engine = create_engine(ADMIN_DATABASE_URL)
metadata = MetaData()

def create_new_database(engine: Engine, db_name: str):
    """Drop and create a new database."""
    with engine.connect() as connection:
        try:
            # Drop the database if it exists
            connection.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
            print(f"Database {db_name} dropped successfully.")
        except ProgrammingError:
            print(f"Database {db_name} does not exist or cannot be dropped.")
        
        # Create a new database
        connection.execute(text(f"CREATE DATABASE {db_name}"))
        print(f"Database {db_name} created successfully.")


# Step 1: Drop and create the database
create_new_database(admin_engine, DB_NAME)

# Step 2: Reconnect to the newly created database
engine = create_engine(DATABASE_URL)

# Define tables
data_mahasiswa_table = Table(
    "data_mahasiswa",
    metadata,
    Column("npm_mahasiswa", String(20), primary_key=True),
    Column("nama_mahasiswa", String(100)),
    Column("status_mahasiswa", String(50)),
    Column("prodi_mahasiswa", String(100)),
    Column("angkatan_mahasiswa", String(50)), 
    Column("ipk_mahasiswa", Float),
    Column("pembimbing_tugas_akhir", String(50)),
)

data_krs_mahasiswa_table = Table(
    "data_krs_mahasiswa",
    metadata,
    Column("npm_mahasiswa", String(20)),
    Column("tahun_semester", String(50)),
    Column("kode_matkul", String(20)),
    Column("nama_matkul", String(100)),
    Column("kategori_matakuliah", String(50)),
    Column("kode_nilai", String(10)),
    Column("total_hadir", Integer),
    Column("total_terlaksana", Integer),
)

data_kegiatan_mahasiswa_table = Table(
    "data_kegiatan_mahasiswa",
    metadata,
    Column("npm_mahasiswa", String(20)),
    Column("bank_id", String(20)),
    Column("nama_kegiatan", Text),  # Use Text to allow longer strings
    Column("tingkat_kegiatan", String(50)),
    Column("tanggal_kegiatan", String(20)),
)

# Step 3: Create tables in the database
metadata.create_all(engine)

# Load data from Excel files
data_mahasiswa = pd.read_excel("Data Mahasiswa.xlsx")
data_krs_mahasiswa = pd.read_excel("Data KRS Mahasiswa.xlsx")
data_kegiatan_mahasiswa = pd.read_excel("Data Kegiatan Mahasiswa.xlsx")

# Step 4: Save data to the database
with engine.begin() as connection:
    data_mahasiswa.to_sql("data_mahasiswa", con=connection, if_exists="replace", index=False, dtype={
        "npm_mahasiswa": String(20),
        "nama_mahasiswa": String(100),
        "status_mahasiswa": String(50),
        "prodi_mahasiswa": String(100),
        "ipk_mahasiswa": Float,
        "angkatan_mahasiswa": String(50),
        "pembimbing_tugas_akhir": String(50),
    })
    data_krs_mahasiswa.to_sql("data_krs_mahasiswa", con=connection, if_exists="replace", index=False, dtype={
        "npm_mahasiswa": String(20),
        "kode_matkul": String(20),
        "nama_matkul": String(100),
        "kategori_matakuliah": String(50),
        "kode_nilai": String(10),
        "total_hadir": Integer,
        "total_terlaksana": Integer,
        "tahun_semester": String(50),
    })
    data_kegiatan_mahasiswa.to_sql("data_kegiatan_mahasiswa", con=connection, if_exists="replace", index=False, dtype={
        "npm_mahasiswa": String(20),
        "nama_kegiatan": Text,  # Updated to Text
        "tingkat_kegiatan": String(50),
        "tanggal_kegiatan": String(20),
        "bank_id": String(50),
    })

print("Database refreshed, tables created, and data imported successfully!")
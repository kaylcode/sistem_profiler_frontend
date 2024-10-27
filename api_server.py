from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np

app = FastAPI()

# Load data and models
data_mhs = pd.read_excel('./Data Mahasiswa.xlsx')
data_krs = pd.read_excel('./Data KRS Mahasiswa.xlsx')
data_kegiatan = pd.read_excel('./Data Kegiatan Mahasiswa.xlsx')

# Menggabungkan data KRS dan Kegiatan dengan Data Mahasiswa berdasarkan 'npm_mahasiswa'
merged_data = pd.merge(data_mhs, data_krs, on="npm_mahasiswa", how="inner")
merged_data = pd.merge(merged_data, data_kegiatan, on="npm_mahasiswa", how="left")

# Load pre-trained models
graduation_model = joblib.load('student_graduation_model.pkl')
achievement_model = joblib.load('student_achievement_model.pkl')

# Konversi nilai huruf ke angka
def convert_grade_to_score(grade):
    grade_dict = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'E': 0.0}
    return grade_dict.get(grade, None)

# Define input model for API
class StudentInput(BaseModel):
    npm_mahasiswa: int

# Endpoint untuk prediksi kelulusan dan prestasi
@app.post("/predict")
def predict_student_status(data: StudentInput):
    npm = data.npm_mahasiswa
    student_data = merged_data[merged_data['npm_mahasiswa'] == npm]

    if student_data.empty:
        return {"error": "Data mahasiswa tidak ditemukan"}

    # Convert letter grades to numeric scores for prediction purposes
    student_data['nilai'] = student_data['kode_nilai'].apply(convert_grade_to_score)
    student_data['nilai_rata_rata'] = student_data['nilai'].mean()

    # Handle NaN values by replacing them with defaults
    student_data['ipk_mahasiswa'].fillna(0, inplace=True)
    student_data['nilai_rata_rata'] = student_data['nilai_rata_rata'] if not np.isnan(student_data['nilai_rata_rata']) else 0

    # Prepare features for prediction
    X_new = student_data[['ipk_mahasiswa', 'nilai_rata_rata']].values
    graduation_prob = graduation_model.predict_proba(X_new)[0][1] * 100  # Graduation probability
    achievement_prob = achievement_model.predict_proba(X_new)[0][1] * 100  # Achievement probability

    # Return JSON response with NaN-safe values
    return {
        "npm_mahasiswa": npm,
        "nama_mahasiswa": student_data['nama_mahasiswa'].values[0],
        "status_mahasiswa": student_data['status_mahasiswa'].values[0],
        "prodi_mahasiswa": student_data['prodi_mahasiswa'].values[0],
        "ipk_mahasiswa": float(student_data['ipk_mahasiswa'].values[0]),  # Ensure float
        "persentase_kelulusan": float(graduation_prob),  # Ensure float
        "persentase_berprestasi": float(achievement_prob),  # Ensure float
        "jumlah_prestasi": int(student_data['jumlah_prestasi'].values[0]) if 'jumlah_prestasi' in student_data else 0
    }

# Endpoint untuk menampilkan list semua mahasiswa
@app.get("/students")
def get_students():
    # Mengambil hanya informasi dari data mahasiswa untuk mencegah data yang berlebihan
    students_list = data_mhs[['npm_mahasiswa', 'nama_mahasiswa', 'status_mahasiswa', 'prodi_mahasiswa', 'ipk_mahasiswa']].fillna(0).to_dict(orient='records')
    return students_list

# Jalankan server API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
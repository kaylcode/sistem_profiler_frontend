from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np

app = FastAPI()

# Load cleaned data and models
data_mhs = pd.read_excel('Data Mahasiswa.xlsx')
data_krs = pd.read_excel('Data KRS Mahasiswa.xlsx')  # Memuat data KRS Mahasiswa
data_kegiatan = pd.read_excel('Data Kegiatan Mahasiswa.xlsx')  # Memuat data kegiatan mahasiswa
merged_data = pd.read_excel('cleaned_data.xlsx')  # Menggunakan hasil pembersihan dari cleaned_data.xlsx
graduation_model = joblib.load('student_graduation_model.pkl')
achievement_model = joblib.load('student_achievement_model.pkl')

# Define input model for API
class StudentInput(BaseModel):
    npm_mahasiswa: int

# Endpoint untuk prediksi kelulusan dan prestasi
@app.post("/predict")
def predict_student_status(data: StudentInput):
    npm = data.npm_mahasiswa
    student_data = merged_data[merged_data['npm_mahasiswa'] == npm]

    if student_data.empty:
        raise HTTPException(status_code=404, detail="Data mahasiswa tidak ditemukan")

    nilai_rata_rata = student_data['nilai_rata_rata'].values[0]
    ipk_mahasiswa = student_data['ipk_mahasiswa'].values[0]
    keterlibatan_kegiatan = student_data['keterlibatan_kegiatan'].fillna(0).values[0]

    # Prediksi kelulusan dengan dua fitur (Opsi 2)
    X_new_graduation = np.array([[ipk_mahasiswa, nilai_rata_rata]])
    graduation_prob = (graduation_model.predict_proba(X_new_graduation)[0][1] * 100)

    # Prediksi prestasi dengan tiga fitur
    X_new_achievement = np.array([[ipk_mahasiswa, nilai_rata_rata, keterlibatan_kegiatan]])
    achievement_prob = achievement_model.predict_proba(X_new_achievement)[0][1] * 100
    
     # Mendapatkan daftar mata kuliah yang diambil dan kode nilai
    student_courses = data_krs[data_krs['npm_mahasiswa'] == npm][['nama_matkul','kategori_matakuliah', 'kode_nilai','total_hadir','total_terlaksana']]
    course_list = student_courses.to_dict(orient='records')  # Mengonversi ke format yang bisa dikembalikan oleh API

     # Mendapatkan daftar kegiatan yang diikuti mahasiswa
    student_activities = data_kegiatan[data_kegiatan['npm_mahasiswa'] == npm][['nama_kegiatan', 'tingkat_kegiatan','tanggal_kegiatan']]
    activity_list = student_activities.to_dict(orient='records')  # Mengonversi ke format yang bisa dikembalikan oleh API
    return {
        "npm_mahasiswa": npm,
        "nama_mahasiswa": student_data['nama_mahasiswa'].values[0],
        "status_mahasiswa": student_data['status_mahasiswa'].values[0],
        "prodi_mahasiswa": student_data['prodi_mahasiswa'].values[0],
        "ipk_mahasiswa": float(ipk_mahasiswa),
        "persentase_kelulusan": float(graduation_prob),
        "persentase_berprestasi": float(achievement_prob),
        "keterlibatan_kegiatan": int(keterlibatan_kegiatan),
        "daftar_mata_kuliah": course_list,  # Menambahkan daftar mata kuliah dan kode nilai
        "daftar_kegiatan": activity_list     # Daftar kegiatan yang diikuti
    }


# Endpoint untuk menampilkan list semua mahasiswa
@app.get("/students")
def get_students():
    # Menampilkan daftar mahasiswa dengan kolom yang relevan
    students_list = data_mhs[['npm_mahasiswa', 'nama_mahasiswa', 'status_mahasiswa', 'prodi_mahasiswa', 'ipk_mahasiswa']].fillna(0).to_dict(orient='records')
    return students_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

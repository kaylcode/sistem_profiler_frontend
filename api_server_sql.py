from flask import Flask, jsonify, request, abort
from sqlalchemy import create_engine, text
import joblib
import numpy as np

app = Flask(__name__)

# Menghubungkan ke database
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/profiling_students"  # Ganti dengan kredensial database Anda
engine = create_engine(DATABASE_URL)

# Memuat model machine learning yang telah disimpan
graduation_model = joblib.load('student_graduation_model.pkl')
achievement_model = joblib.load('student_achievement_model.pkl')

# Fungsi untuk mengonversi nilai huruf menjadi skor numerik
def convert_grade_to_score(grade):
    """Konversi nilai huruf ke skor numerik."""
    grade_dict = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'E': 0.0}
    return grade_dict.get(grade, None)

# Fungsi untuk mengambil data mahasiswa berdasarkan NPM
def get_student_data(npm):
    with engine.connect() as connection:
        # Mengambil data mahasiswa
        student_query = text("""
            SELECT m.npm_mahasiswa, m.nama_mahasiswa, m.status_mahasiswa, 
                   m.prodi_mahasiswa, m.ipk_mahasiswa
            FROM data_mahasiswa m
            WHERE m.npm_mahasiswa = :npm
        """)
        result = connection.execute(student_query, {"npm": npm}).fetchone()
        
        if result:
            # Mengubah hasil query menjadi dictionary
            student_data = dict(result._mapping)

            # Mengambil jumlah keterlibatan kegiatan
            activities_query = text("""
                SELECT COUNT(*) AS keterlibatan_kegiatan
                FROM data_kegiatan_mahasiswa
                WHERE npm_mahasiswa = :npm
            """)
            activities_result = connection.execute(activities_query, {"npm": npm}).fetchone()
            student_data['keterlibatan_kegiatan'] = activities_result[0] if activities_result else 0

            # Mengambil nilai rata-rata mahasiswa
            krs_query = text("""
                SELECT kode_nilai
                FROM data_krs_mahasiswa
                WHERE npm_mahasiswa = :npm
            """)
            krs_result = connection.execute(krs_query, {"npm": npm}).fetchall()
            numeric_scores = [convert_grade_to_score(row[0]) for row in krs_result if convert_grade_to_score(row[0]) is not None]
            student_data['nilai_rata_rata'] = np.mean(numeric_scores) if numeric_scores else 0

            return student_data
        return None

# Endpoint untuk memprediksi status mahasiswa
@app.route("/predict", methods=["POST"])
def predict_student_status():
    # Mengambil NPM dari permintaan
    npm = request.form.get("npm_mahasiswa")
    if not npm:
        return jsonify({"error": "npm_mahasiswa wajib diisi"}), 400

    try:
        npm = int(npm)
    except ValueError:
        return jsonify({"error": "npm_mahasiswa harus berupa angka"}), 400

    student_data = get_student_data(npm)
    if not student_data:
        abort(404, description="Data mahasiswa tidak ditemukan")

    # Mengambil data mahasiswa untuk prediksi
    ipk_mahasiswa = student_data['ipk_mahasiswa']
    nilai_rata_rata = student_data['nilai_rata_rata']
    keterlibatan_kegiatan = student_data['keterlibatan_kegiatan']

    # Prediksi peluang kelulusan
    X_new_graduation = np.array([[ipk_mahasiswa, nilai_rata_rata]])
    graduation_prob = (graduation_model.predict_proba(X_new_graduation)[0][1] * 100)

    # Prediksi peluang berprestasi
    X_new_achievement = np.array([[ipk_mahasiswa, nilai_rata_rata, keterlibatan_kegiatan]])
    achievement_prob = (achievement_model.predict_proba(X_new_achievement)[0][1] * 100)

    # Mengambil data mata kuliah mahasiswa
    with engine.connect() as connection:
        courses_query = text("""
            SELECT nama_matkul, kategori_matakuliah, kode_nilai, total_hadir, total_terlaksana
            FROM data_krs_mahasiswa
            WHERE npm_mahasiswa = :npm
        """)
        course_list = [dict(row._mapping) for row in connection.execute(courses_query, {"npm": npm})]

    # Mengambil data kegiatan mahasiswa
    with engine.connect() as connection:
        activities_query = text("""
            SELECT nama_kegiatan, tingkat_kegiatan, tanggal_kegiatan
            FROM data_kegiatan_mahasiswa
            WHERE npm_mahasiswa = :npm
        """)
        activity_list = [dict(row._mapping) for row in connection.execute(activities_query, {"npm": npm})]

    # Mengembalikan hasil prediksi dalam format JSON
    return jsonify({
        "npm_mahasiswa": npm,
        "nama_mahasiswa": student_data['nama_mahasiswa'],
        "status_mahasiswa": student_data['status_mahasiswa'],
        "prodi_mahasiswa": student_data['prodi_mahasiswa'],
        "ipk_mahasiswa": float(ipk_mahasiswa),
        "persentase_kelulusan": float(graduation_prob),
        "persentase_berprestasi": float(achievement_prob),
        "keterlibatan_kegiatan": int(keterlibatan_kegiatan),
        "daftar_mata_kuliah": course_list,
        "daftar_kegiatan": activity_list
    })

# Endpoint untuk mengambil daftar mahasiswa
@app.route("/students", methods=["GET"])
def get_students():
    with engine.connect() as connection:
        # Query untuk mengambil data semua mahasiswa
        students_query = text("""
            SELECT npm_mahasiswa, nama_mahasiswa, status_mahasiswa, 
                   prodi_mahasiswa, ipk_mahasiswa
            FROM data_mahasiswa
        """)
        result = connection.execute(students_query)
        students_list = [dict(row._mapping) for row in result]
    return jsonify(students_list)

# Menjalankan aplikasi Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
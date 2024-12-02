from flask import Flask, jsonify, request, abort
from sqlalchemy import create_engine, text
import joblib
import numpy as np

app = Flask(__name__)

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/profiling_students"  # Ganti dengan kredensial database Anda
engine = create_engine(DATABASE_URL)

graduation_model = joblib.load('student_graduation_model.pkl')
achievement_model = joblib.load('student_achievement_model.pkl')

def convert_grade_to_score(grade):
    grade_dict = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'E': 0.0}
    return grade_dict.get(grade, None)

# Fungsi untuk mengambil data mahasiswa berdasarkan NPM
def get_student_data(npm):
    try:
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
    except Exception as e:
        raise RuntimeError(f"Error saat mengambil data mahasiswa: {str(e)}")

# @app.route("/predict", methods=["POST"])
# def predict_student_status():
#     """
#     Endpoint untuk memprediksi status mahasiswa berdasarkan NPM.
#     """
#     npm = request.form.get("npm_mahasiswa")
#     if not npm:
#         return jsonify({"error": "npm_mahasiswa wajib diisi"}), 400

#     try:
#         npm = int(npm)
#     except ValueError:
#         return jsonify({"error": "npm_mahasiswa harus berupa angka"}), 400

#     student_data = get_student_data(npm)
#     if not student_data:
#         abort(404, description="Data mahasiswa tidak ditemukan")

#     ipk_mahasiswa = student_data['ipk_mahasiswa']
#     nilai_rata_rata = student_data['nilai_rata_rata']
#     keterlibatan_kegiatan = student_data['keterlibatan_kegiatan']

#     X_new_graduation = np.array([[ipk_mahasiswa, nilai_rata_rata]])
#     graduation_prob = graduation_model.predict_proba(X_new_graduation)[0][1] * 100

#     X_new_achievement = np.array([[ipk_mahasiswa, nilai_rata_rata, keterlibatan_kegiatan]])
#     achievement_prob = achievement_model.predict_proba(X_new_achievement)[0][1] * 100

#     return jsonify({
#         "persentase_kelulusan": float(graduation_prob),
#         "persentase_berprestasi": float(achievement_prob)
#     })

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


@app.route("/students", methods=["GET"])
def list_students():
    """
    Mengembalikan daftar semua mahasiswa yang tersimpan di database.
    """
    try:
        # Membuka koneksi
        with engine.connect() as connection:
            query = text("""
                SELECT npm_mahasiswa, nama_mahasiswa, prodi_mahasiswa,status_mahasiswa, ipk_mahasiswa
                FROM data_mahasiswa
            """)
            result = connection.execute(query).mappings()

            # Membentuk daftar mahasiswa dari hasil query
            students = [
                {
                    "npm_mahasiswa": row["npm_mahasiswa"],
                    "nama_mahasiswa": row["nama_mahasiswa"],
                    "prodi_mahasiswa": row["prodi_mahasiswa"],
                    "status_mahasiswa": row["status_mahasiswa"],
                    "ipk_mahasiswa": row["ipk_mahasiswa"]
                }
                for row in result
            ]

        # Jika tidak ada data mahasiswa
        if not students:
            return jsonify({"message": "Tidak ada data mahasiswa"}), 404

        # Mengembalikan hasil dalam format JSON
        return jsonify({"students": students}), 200

    except Exception as e:
        # Penanganan error
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

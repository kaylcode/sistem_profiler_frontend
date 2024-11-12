from flask import Flask, jsonify, request, abort
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)

# Load cleaned data and models
data_mhs = pd.read_excel('Data Mahasiswa.xlsx')
data_krs = pd.read_excel('Data KRS Mahasiswa.xlsx')  # Load KRS Mahasiswa data
data_kegiatan = pd.read_excel('Data Kegiatan Mahasiswa.xlsx')  # Load kegiatan mahasiswa data
merged_data = pd.read_excel('cleaned_data.xlsx')  # Load cleaned data
graduation_model = joblib.load('student_graduation_model.pkl')
achievement_model = joblib.load('student_achievement_model.pkl')

# Endpoint for predicting graduation and achievement
@app.route("/predict", methods=["POST"])
def predict_student_status():
    # Get `npm_mahasiswa` from form data
    npm = request.form.get("npm_mahasiswa")
    if npm is None:
        return jsonify({"error": "npm_mahasiswa is required"}), 400

    try:
        npm = int(npm)
    except ValueError:
        return jsonify({"error": "npm_mahasiswa must be an integer"}), 400

    student_data = merged_data[merged_data['npm_mahasiswa'] == npm]

    if student_data.empty:
        abort(404, description="Data mahasiswa tidak ditemukan")

    # Extract student details
    nilai_rata_rata = student_data['nilai_rata_rata'].values[0]
    ipk_mahasiswa = student_data['ipk_mahasiswa'].values[0]
    keterlibatan_kegiatan = student_data['keterlibatan_kegiatan'].fillna(0).values[0]

    # Predict graduation with two features
    X_new_graduation = np.array([[ipk_mahasiswa, nilai_rata_rata]])
    graduation_prob = (graduation_model.predict_proba(X_new_graduation)[0][1] * 100)

    # Predict achievement with three features
    X_new_achievement = np.array([[ipk_mahasiswa, nilai_rata_rata, keterlibatan_kegiatan]])
    achievement_prob = achievement_model.predict_proba(X_new_achievement)[0][1] * 100

    # Get list of student courses
    student_courses = data_krs[data_krs['npm_mahasiswa'] == npm][['nama_matkul', 'kategori_matakuliah', 'kode_nilai', 'total_hadir', 'total_terlaksana']]
    course_list = student_courses.to_dict(orient='records')

    # Get list of student activities
    student_activities = data_kegiatan[data_kegiatan['npm_mahasiswa'] == npm][['nama_kegiatan', 'tingkat_kegiatan', 'tanggal_kegiatan']]
    activity_list = student_activities.to_dict(orient='records')

    return jsonify({
        "npm_mahasiswa": npm,
        "nama_mahasiswa": student_data['nama_mahasiswa'].values[0],
        "status_mahasiswa": student_data['status_mahasiswa'].values[0],
        "prodi_mahasiswa": student_data['prodi_mahasiswa'].values[0],
        "ipk_mahasiswa": float(ipk_mahasiswa),
        "persentase_kelulusan": float(graduation_prob),
        "persentase_berprestasi": float(achievement_prob),
        "keterlibatan_kegiatan": int(keterlibatan_kegiatan),
        "daftar_mata_kuliah": course_list,
        "daftar_kegiatan": activity_list
    })

# Endpoint for listing all students
@app.route("/students", methods=["GET"])
def get_students():
    students_list = data_mhs[['npm_mahasiswa', 'nama_mahasiswa', 'status_mahasiswa', 'prodi_mahasiswa', 'ipk_mahasiswa']].fillna(0).to_dict(orient='records')
    return jsonify(students_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
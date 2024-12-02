import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import numpy as np
from sklearn.metrics import classification_report

# Koneksi ke database
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/profiling_students"  # Ganti dengan kredensial MySQL Anda
engine = create_engine(DATABASE_URL)

# Fungsi untuk membaca, membersihkan, dan menggabungkan data
def load_and_clean_data():
    print("Memulai proses pembersihan data...")
    
    # Membaca data dari tabel di database
    data_mahasiswa = pd.read_sql("SELECT * FROM data_mahasiswa", engine)
    data_krs_mahasiswa = pd.read_sql("SELECT * FROM data_krs_mahasiswa", engine)
    data_kegiatan_mahasiswa = pd.read_sql("SELECT * FROM data_kegiatan_mahasiswa", engine)

    # Konversi nilai huruf (A, B, C, dst.) menjadi angka
    def convert_grade_to_score(grade):
        grade_dict = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'E': 0.0}
        return grade_dict.get(grade, None)

    data_krs_mahasiswa['nilai'] = data_krs_mahasiswa['kode_nilai'].apply(convert_grade_to_score)
    data_krs_mahasiswa.dropna(subset=['npm_mahasiswa', 'nilai'], inplace=True)

    # Menghapus duplikat dan memperbaiki data yang kosong
    data_mahasiswa.drop_duplicates(subset=['npm_mahasiswa'], inplace=True)
    data_krs_mahasiswa.drop_duplicates(subset=['npm_mahasiswa', 'kode_matkul'], inplace=True)
    data_kegiatan_mahasiswa.drop_duplicates(subset=['npm_mahasiswa', 'nama_kegiatan'], inplace=True)

    data_kegiatan_mahasiswa['keterlibatan_kegiatan'] = data_kegiatan_mahasiswa.groupby('npm_mahasiswa')['npm_mahasiswa'].transform('count')
    data_kegiatan_mahasiswa = data_kegiatan_mahasiswa[['npm_mahasiswa', 'keterlibatan_kegiatan']].drop_duplicates()
    data_kegiatan_mahasiswa['keterlibatan_kegiatan'].fillna(0, inplace=True)

    # Gabungkan data
    merged_data = pd.merge(data_mahasiswa, data_krs_mahasiswa, on="npm_mahasiswa", how="inner")
    merged_data = pd.merge(merged_data, data_kegiatan_mahasiswa, on="npm_mahasiswa", how="left")
    merged_data['keterlibatan_kegiatan'].fillna(0, inplace=True)
    merged_data['nilai_rata_rata'] = merged_data.groupby('npm_mahasiswa')['nilai'].transform('mean')
    merged_data['ipk_mahasiswa'].fillna(0, inplace=True)

    print("Pembersihan data selesai.")
    return merged_data

# Fungsi untuk melatih model dan menyimpannya
def train_and_export_models(merged_data):
    print("Memulai proses pelatihan model...")
    
    # Fitur dan label
    X = merged_data[['ipk_mahasiswa', 'nilai_rata_rata', 'keterlibatan_kegiatan']].fillna(0)
    y_graduation = merged_data['status_mahasiswa'].apply(lambda x: 1 if str(x).lower() == 'lulus' else 0)
    y_achievement = merged_data.apply(
        lambda row: 1 if row['ipk_mahasiswa'] >= 3.5 and row['nilai_rata_rata'] >= 3.5 and row['keterlibatan_kegiatan'] > 0 else 0, axis=1
    )

    # Model kelulusan
    X_train_grad, X_test_grad, y_train_grad, y_test_grad = train_test_split(
        X[['ipk_mahasiswa', 'nilai_rata_rata']], y_graduation, test_size=0.3, random_state=0
    )
    graduation_model = RandomForestClassifier(n_estimators=100, random_state=0)
    graduation_model.fit(X_train_grad, y_train_grad)
    joblib.dump(graduation_model, 'student_graduation_model.pkl')
    y_pred_grad = graduation_model.predict(X_test_grad)
    print('Evaluasi Model Kelulusan:\n', classification_report(y_test_grad, y_pred_grad))

    # Model prestasi
    X_train_ach, X_test_ach, y_train_ach, y_test_ach = train_test_split(X, y_achievement, test_size=0.3, random_state=0)
    achievement_model = RandomForestClassifier(n_estimators=100, random_state=0)
    achievement_model.fit(X_train_ach, y_train_ach)
    joblib.dump(achievement_model, 'student_achievement_model.pkl')
    y_pred_ach = achievement_model.predict(X_test_ach)
    print('Evaluasi Model Prestasi:\n', classification_report(y_test_ach, y_pred_ach))

    print("Model berhasil dilatih dan disimpan.")

# Eksekusi utama
merged_data = load_and_clean_data()
train_and_export_models(merged_data)

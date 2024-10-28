import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import numpy as np

# Fungsi konversi nilai huruf ke angka
def convert_grade_to_score(grade):
    grade_dict = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'E': 0.0}
    return grade_dict.get(grade, None)

# Step 1: Load and Clean Data
def load_and_clean_data():
    # Load datasets
    data_mahasiswa = pd.read_excel('./Data Mahasiswa.xlsx')
    data_krs_mahasiswa = pd.read_excel('./Data KRS Mahasiswa.xlsx')
    data_kegiatan_mahasiswa = pd.read_excel('./Data Kegiatan Mahasiswa.xlsx')

    # Konversi nilai huruf ke angka dan bersihkan data KRS
    data_krs_mahasiswa['nilai'] = data_krs_mahasiswa['kode_nilai'].apply(convert_grade_to_score)
    data_krs_mahasiswa.dropna(subset=['npm_mahasiswa', 'nilai'], inplace=True)
    data_kegiatan_mahasiswa.dropna(subset=['npm_mahasiswa'], inplace=True)

    # Hapus duplikat
    data_mahasiswa.drop_duplicates(subset=['npm_mahasiswa'], inplace=True)
    data_krs_mahasiswa.drop_duplicates(subset=['npm_mahasiswa', 'kode_matkul'], inplace=True)
    data_kegiatan_mahasiswa.drop_duplicates(subset=['npm_mahasiswa', 'nama_kegiatan'], inplace=True)

    # Hitung keterlibatan mahasiswa dalam kegiatan
    data_kegiatan_mahasiswa['keterlibatan_kegiatan'] = data_kegiatan_mahasiswa.groupby('npm_mahasiswa')['npm_mahasiswa'].transform('count')
    data_kegiatan_mahasiswa = data_kegiatan_mahasiswa[['npm_mahasiswa', 'keterlibatan_kegiatan']].drop_duplicates()

    # Merge data
    merged_data = pd.merge(data_mahasiswa, data_krs_mahasiswa, on="npm_mahasiswa", how="inner")
    merged_data = pd.merge(merged_data, data_kegiatan_mahasiswa, on="npm_mahasiswa", how="left")

    # Mengganti NaN dengan 0 untuk kolom keterlibatan_kegiatan dan menghitung rata-rata nilai
    merged_data['keterlibatan_kegiatan'].fillna(0, inplace=True)
    merged_data['nilai_rata_rata'] = merged_data.groupby('npm_mahasiswa')['nilai'].transform('mean')
    merged_data['ipk_mahasiswa'].fillna(0, inplace=True)

    # Export cleaned data to Excel
    merged_data.to_excel('cleaned_data.xlsx', index=False)
    return merged_data

# Step 2: Train and Export Models
def train_and_export_models(merged_data):
    # Prepare features and labels
    X = merged_data[['ipk_mahasiswa', 'nilai_rata_rata', 'keterlibatan_kegiatan']].fillna(0)

    # Label prediksi kelulusan
    y_graduation = merged_data['status_mahasiswa'].apply(lambda x: 1 if str(x).lower() == 'lulus' else 0)

    # Label prediksi prestasi
    y_achievement = merged_data.apply(
        lambda row: 1 if row['ipk_mahasiswa'] >= 3.5 and row['nilai_rata_rata'] >= 3.5 and row['keterlibatan_kegiatan'] > 0 else 0, axis=1
    )

    # Training Graduation Model
    X_train_grad, X_test_grad, y_train_grad, y_test_grad = train_test_split(X[['ipk_mahasiswa', 'nilai_rata_rata']], y_graduation, test_size=0.3, random_state=42)
    graduation_model = RandomForestClassifier(random_state=42)
    graduation_model.fit(X_train_grad, y_train_grad)
    joblib.dump(graduation_model, 'student_graduation_model.pkl')

    # Training Achievement Model
    X_train_ach, X_test_ach, y_train_ach, y_test_ach = train_test_split(X, y_achievement, test_size=0.3, random_state=42)
    achievement_model = RandomForestClassifier(random_state=42)
    achievement_model.fit(X_train_ach, y_train_ach)
    joblib.dump(achievement_model, 'student_achievement_model.pkl')

    print("Training completed and models exported.")

# Run the data loading, cleaning, and model training
merged_data = load_and_clean_data()
train_and_export_models(merged_data)
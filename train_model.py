import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

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

    # Renaming columns to match expected structure
    data_krs_mahasiswa['nilai'] = data_krs_mahasiswa['kode_nilai'].apply(convert_grade_to_score)

    # Data Cleaning: Drop rows with any NaN values
    data_krs_mahasiswa = data_krs_mahasiswa.dropna(subset=['npm_mahasiswa', 'nilai'])
    data_kegiatan_mahasiswa = data_kegiatan_mahasiswa.dropna(subset=['npm_mahasiswa'])

    # Merge data
    merged_data = pd.merge(data_mahasiswa, data_krs_mahasiswa, on="npm_mahasiswa", how="inner")
    merged_data = pd.merge(merged_data, data_kegiatan_mahasiswa, on="npm_mahasiswa", how="left")

    # Calculate average score per student
    merged_data['nilai_rata_rata'] = merged_data.groupby('npm_mahasiswa')['nilai'].transform('mean')
    return merged_data

# Step 2: Train and Export Models
def train_and_export_models(merged_data):
    # Prepare features and labels
    X = merged_data[['ipk_mahasiswa', 'nilai_rata_rata']].copy()
    
    # Label for graduation status
    y_graduation = merged_data['status_mahasiswa'].apply(lambda x: 1 if x.lower() == 'lulus' else 0)
    # Label for achievement status based on IPK and average score threshold (>=3.5)
    y_achievement = merged_data.apply(lambda row: 1 if row['ipk_mahasiswa'] >= 3.5 and row['nilai_rata_rata'] >= 3.5 else 0, axis=1)

    # Train Graduation Model
    X_train_grad, X_test_grad, y_train_grad, y_test_grad = train_test_split(X, y_graduation, test_size=0.3, random_state=42)
    graduation_model = RandomForestClassifier(random_state=42)
    graduation_model.fit(X_train_grad, y_train_grad)
    joblib.dump(graduation_model, 'student_graduation_model.pkl')

    # Train Achievement Model
    X_train_ach, X_test_ach, y_train_ach, y_test_ach = train_test_split(X, y_achievement, test_size=0.3, random_state=42)
    achievement_model = RandomForestClassifier(random_state=42)
    achievement_model.fit(X_train_ach, y_train_ach)
    joblib.dump(achievement_model, 'student_achievement_model.pkl')

    print("Training completed and models exported.")

# Load and clean data
merged_data = load_and_clean_data()
# Train and export models
train_and_export_models(merged_data)
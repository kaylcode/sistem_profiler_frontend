import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

# Fungsi untuk memuat data uji dan memisahkan label serta fitur
def load_test_data():
    # Load cleaned data
    merged_data = pd.read_csv('cleaned_data.csv')
    
    # Fitur dan label
    X = merged_data[['ipk_mahasiswa', 'nilai_rata_rata']].fillna(0)
    y_graduation = merged_data['status_mahasiswa'].apply(lambda x: 1 if str(x).lower() == 'lulus' else 0)
    y_achievement = merged_data.apply(
        lambda row: 1 if row['ipk_mahasiswa'] >= 3.5 and row['nilai_rata_rata'] >= 3.5 else 0, axis=1
    )
    
    # Split data into train and test
    X_train_grad, X_test_grad, y_train_grad, y_test_grad = train_test_split(X, y_graduation, test_size=0.3, random_state=42)
    X_train_ach, X_test_ach, y_train_ach, y_test_ach = train_test_split(X, y_achievement, test_size=0.3, random_state=42)
    
    return X_test_grad, y_test_grad, X_test_ach, y_test_ach

# Fungsi untuk evaluasi model
def evaluate_model(model, X_test, y_test, model_name):
    y_pred = model.predict(X_test)
    
    # Evaluasi metrik
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Print hasil
    print(f"{model_name} Model Evaluation:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("-" * 50)

# Load test data
X_test_grad, y_test_grad, X_test_ach, y_test_ach = load_test_data()

# Load models
graduation_model = joblib.load('student_graduation_model.pkl')
achievement_model = joblib.load('student_achievement_model.pkl')

# Evaluate Graduation Model
evaluate_model(graduation_model, X_test_grad, y_test_grad, "Graduation")

# Evaluate Achievement Model
evaluate_model(achievement_model, X_test_ach, y_test_ach, "Achievement")
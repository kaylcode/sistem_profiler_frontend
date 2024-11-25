# profiler_student

Sistem Profiler - kecerdasan buatan

- jalankan python train_model.py untuk training model
- jalankan python app.py untuk server backend

- hostname adalah: http://localhost:8000/
- endpoint ada 2 yaitu: /students atau http://localhost:8000/students untuk dapatkan list semua mahasiswa
- /predict atau http://localhost:8000/predict untuk profiling mahasiswa, diharapkan agar mengirimkan parameter NPM dengan metode post
- pip install pandas scikit-learn fastapi uvicorn joblib openpyxl flask sqlalchemy

Menjalankan sistem profiler

- membuat dan mengimpor database
- jalankan sql server lewat laragon atau xampp dan jalankan kode script convert_excel_to_sql.py dgn kode python convert_excel_to_sql.py
- jalankan kode script python train_model_with_sql.py
- jalankan kode script python api_server_sql.py

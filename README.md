# profiler_student

Sistem Profiler - kecerdasan buatan

- jalankan python train_model.py untuk training model
- jalankan python app.py untuk server backend

- hostname adalah: http://localhost:8000/
- endpoint ada 2 yaitu: /students atau http://localhost:8000/students untuk dapatkan list semua mahasiswa
- /predict atau http://localhost:8000/predict untuk profiling mahasiswa, diharapkan agar mengirimkan parameter NPM dengan metode post
- pip install pandas scikit-learn fastapi uvicorn joblib openpyxl

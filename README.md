| Nama                           | NRP        |
| ------------------------------ | ---------- |
| Aswalia Novitriasari           | 5027231012 |
| Agnes Zenobia Griselda Petrina | 5027231034 |
| Tsaldia Hukma Cita             | 5027231036 |

# 🛍️ Project Big Data 2 - Retail Rocket Event Processing

Proyek ini mensimulasikan pemrosesan data stream dari event e-commerce **Retail Rocket** menggunakan **Apache Kafka** untuk ingestion, **Apache Spark** untuk pemrosesan batch dan training model, serta **API** untuk menyajikan hasil model machine learning.

---

## 📦 Dataset: Retail Rocket E-commerce Events

- **Sumber:** [Retail Rocket Recommender System Dataset (Kaggle)](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset)  
- **File yang Digunakan:** `events.csv`  
- **Ukuran:** ± 2.7 juta baris (event)  
- **Deskripsi:** Dataset ini berisi log perilaku pengguna dari sebuah platform e-commerce. Setiap baris merepresentasikan satu aksi yang dilakukan oleh pengunjung.

### Kolom Utama di `events.csv`:
- `timestamp` — Waktu event (Unix timestamp dalam milidetik)  
- `visitorid` — ID unik pengunjung  
- `event` — Jenis aksi: `view`, `addtocart`, `transaction`  
- `itemid` — ID produk  
- `transactionid` — Hanya ada jika `event = transaction`

---

## 🎯 Tujuan Proyek

Membangun pipeline data end-to-end untuk:

1. **Simulasi Streaming:** Menggunakan Kafka untuk ingest data dari `events.csv` secara real-time.
2. **Batch Processing:** Menggunakan Spark untuk preprocessing & feature engineering.
3. **Pelatihan Model ML Iteratif:**  
   Contoh model yang mungkin dikembangkan:
   - Sistem Rekomendasi Produk
   - Prediksi Perilaku Pengguna
   - Segmentasi Pengguna
4. **Expose Hasil Model via API:** Untuk sistem downstream.
5. **Demonstrasi Arsitektur Big Data:** Dengan komponen Kafka + Spark.

---

## 🧱 Arsitektur dan Struktur Direktori

### 📂 Struktur Proyek
```
.
├── data/
│   ├── raw/                    # events.csv asli
│   └── processed_batches/      # Output CSV dari Kafka Consumer
├── kafka_pipeline/
│   ├── docker-compose.yaml     # Setup Kafka + Zookeeper
│   ├── producer.py             # Kafka Producer
│   ├── consumer.py             # Kafka Consumer
│   ├── requirements_kafka.txt  # Dependensi Python
│   └── venv_kafka/             # Virtual environment (jangan di-commit)
└── README.md
```

---

## ⚙️ Bagian 1: Kafka Pipeline – Ingesti Data Event

### 🔧 Prasyarat

- **Docker Desktop**  
- **Python ≥ 3.8**  
- **Dataset** `events.csv` di `data/raw/`

---

### 🚀 Cara Menjalankan Kafka Pipeline

#### 1. Jalankan Kafka & Zookeeper via Docker
```bash
docker-compose -f kafka_pipeline/docker-compose.yaml up -d
```
Cek status:
```bash
docker-compose -f kafka_pipeline/docker-compose.yaml ps
```

#### 2. Siapkan Virtual Environment dan Install Dependensi
```bash
cd kafka_pipeline
python -m venv venv_kafka
venv_kafka\Scripts\activate
pip install -r requirements_kafka.txt
```

#### 3. Jalankan Kafka Consumer
```bash
python consumer.py
```

#### 4. Jalankan Kafka Producer (Terminal Baru)
```bash
python producer.py
```
Producer akan mengirim event dari `events.csv` secara bertahap ke Kafka.

---

### ✅ Hasil & Observasi

- File hasil batch akan muncul di: `data/processed_batches/`
- Consumer berhenti otomatis setelah timeout (`consumer_timeout_ms`)
- Producer berhenti setelah semua pesan terkirim
- Dokumentasi 
![image](https://github.com/user-attachments/assets/d370686e-b817-4ec2-90cd-1a6ce9132060)

![image](https://github.com/user-attachments/assets/fb7793a3-0a7a-458b-826d-d41dcefc6a28)

---

### 🛑 Menghentikan Kafka (Opsional)
```bash
docker-compose -f kafka_pipeline/docker-compose.yaml down
```

---
## ✨ Bagian 2: Spark Processing & Model Training

Setelah data event berhasil di-ingest oleh Kafka dan disimpan sebagai file-file batch CSV di `data/processed_batches/`, tahap selanjutnya adalah melakukan pemrosesan data dan pelatihan model machine learning menggunakan Apache Spark (PySpark).

### 📂 Struktur Direktori untuk Spark
```
├── spark_processor/
│ ├── train_model.py # Skrip utama Spark untuk training model
│ ├── models/ # Direktori output untuk model yang sudah dilatih
│ │ ├── recommender_model_v1/
│ │ ├── transaction_predictor_model_v1/
│ │ └── user_segmentation_model_v1/
│ ├── requirements_spark.txt # File requirements untuk Spark
│ └── venv_spark/ # Virtual environment 
└── ... (bagian lain proyek)
```

### 🔧 Prasyarat untuk Spark

- **Java Development Kit (JDK):** Disarankan versi 17 (minimal 11). Pastikan `JAVA_HOME` sudah diset dan `%JAVA_HOME%\bin` masuk dalam `PATH`.
- **`winutils.exe` (untuk pengguna Windows):**
  - Unduh `winutils.exe` sesuai versi mayor Hadoop yang digunakan oleh PySpark.
  - Buat folder `C:\hadoop\bin` dan simpan `winutils.exe` di dalamnya.
  - Set `HADOOP_HOME=C:\hadoop` dan tambahkan `%HADOOP_HOME%\bin` ke `PATH`.
- **Python ≥ 3.8**
- **File-file Batch Data:** Tersimpan di `data/processed_batches/` dengan nama seperti `batch_001.csv`, `batch_002.csv`, dst.

### 🚀 Cara Menjalankan Spark Training Pipeline

#### 1. Siapkan Virtual Environment dan Install Dependensi

```bash
cd spark_processor
python -m venv venv_spark
venv_spark\Scripts\activate
pip install -r requirements_spark.txt
```
#### 2. Jalankan Skrip Training Model
```bash
python train_model.py
```

#### 🤖 Model Machine Learning yang Dilatih
Skrip train_model.py akan melatih tiga model berikut:

🔸 Model 1: Recommender (ALS)
Data: Batch 1–50 (~500.000 event)

Tujuan: Rekomendasi produk berdasarkan interaksi pengguna (view, addtocart, transaction) → rating implisit

Output: spark_processor/models/recommender_model_v1/

🔸 Model 2: Transaction Predictor (Random Forest)
Data: Batch 51–100 (~500.000 event)

Tujuan: Prediksi apakah pengunjung akan melakukan transaksi

Output: spark_processor/models/transaction_predictor_model_v1/

🔸 Model 3: User Segmentation (KMeans)
Data: Batch 101–150 (~500.000 event)

Tujuan: Segmentasi pengguna berdasarkan perilaku agregat

Output: spark_processor/models/user_segmentation_model_v1/

#### ✅ Hasil & Observasi Spark Processing
- Log Konsol: Menampilkan progres batch, jumlah data, tahap pre-processing, dan training.
- Model Tersimpan: Tersimpan dalam format direktori MLlib (metadata/, data/, stages/).
- Contoh Output Konsol:

![Screenshot 2025-05-24 151523](https://github.com/user-attachments/assets/9d3d17b8-6a7e-4cc4-b154-c014ed139d90)
  
![Screenshot 2025-05-24 155450](https://github.com/user-attachments/assets/7812b78a-4b53-48c1-9be9-6c155f4b2bf6)

![Screenshot 2025-05-24 151922](https://github.com/user-attachments/assets/ad3c3226-cf08-4cc9-addd-0ba1c2fa7274)

![Screenshot 2025-05-24 151936](https://github.com/user-attachments/assets/0a23191c-aaca-42e8-8bf3-1e170c6a2fd0)

![Screenshot 2025-05-24 152023](https://github.com/user-attachments/assets/d48da90c-e416-4121-93f8-2e712edbdf80)

---
#### 🌐 Bagian 3: API Service
- Tahapan berikutnya adalah membangun layanan API (mis. Flask atau FastAPI) untuk:
- Memuat model dari direktori spark_processor/models/
- Menyediakan endpoint untuk prediksi atau rekomendasi
- Mengembalikan hasil prediksi dalam format JSON

---

> 🧠 *Dengan memproses aliran data event ini, kita dapat memahami pola perilaku pengguna untuk meningkatkan pengalaman pengguna, personalisasi, dan pengambilan keputusan bisnis dalam e-commerce.*

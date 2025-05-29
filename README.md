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
## 🌐 Bagian 3: API Service
- Tahapan berikutnya adalah membangun layanan API (mis. Flask atau FastAPI) untuk:
- Memuat model dari direktori spark_processor/models/
- Menyediakan endpoint untuk prediksi atau rekomendasi
- Mengembalikan hasil prediksi dalam format JSON

---

> 🧠 *Dengan memproses aliran data event ini, kita dapat memahami pola perilaku pengguna untuk meningkatkan pengalaman pengguna, personalisasi, dan pengambilan keputusan bisnis dalam e-commerce.*

### 📂 Struktur Direktori untuk API
```
├── api_services/                           
│   ├── __pycache__/                        # Direktori yang dibuat otomatis oleh Python
│   ├── api_docker_setup/                   # Sub-direktori khusus untuk konfigurasi Docker layanan API.
│   │   ├── Dockerfile.api                  # Resep untuk membangun image Docker layanan API.
│   │   └── docker-compose.api.yml          # Konfigurasi untuk menjalankan layanan API menggunakan Docker Compose 
│   ├── artifacts/                          # Direktori untuk menyimpan artefak lain yang mungkin dihasilkan atau dibutuhkan oleh API, seperti model
│   ├── __init__.py                         
│   ├── app.py                              # File utama aplikasi API, definisi endpoint, logika request/response, dan pemanggilan model
│   ├── models_loader.py                    # Modul Python yang bertanggung jawab untuk memuat model-model machine learning 
│   └── requirements_api.txt                # File teks yang berisi daftar semua library Python dan versinya yang dibutuhkan oleh layanan API
```

### 🔧 Prasyarat untuk Menjalankan Layanan API (via Docker)

- **Docker Engine dan Docker Compose Terinstal:** Pastikan `Docker Desktop` sudah terinstal dan berjalan dengan baik
- **Model Machine Learning yang Sudah Dilatih**
- **Kode Sumber API dan Konfigurasi Docker:**
  - api_services/app.py
  - api_services/models_loader.py
  - api_services/requirements_api.txt (dengan dependensi seperti pyspark, fastapi, uvicorn, pydantic, pandas, numpy)
  - api_services/__init__.py (kosong)
  - api_services/api_docker_setup/Dockerfile.api (membangun image API)
  - api_services/api_docker_setup/docker-compose.api.yml (menjalankan layanan API)
- **File-file Batch Data:** Tersimpan di `data/processed_batches/` dengan nama seperti `batch_001.csv`, `batch_002.csv`, dst.

### 🚀 Cara Menjalankan Layanan API (via Docker)

#### 1. Navigasi ke Direktori Setup Docker API

```bash
cd api_services
cd api_docker_setup
```
#### 2. Navigasi ke Direktori Setup Docker API
```bash
docker-compose -f docker-compose.api.yml up --build
```

---

### 🧪 Endpoint API dan Cara Penggunaan

Setelah layanan API berjalan (di Docker melalui `http://localhost:8001` atau sesuai port yang Anda map), Anda dapat menguji endpoint berikut menggunakan alat seperti Postman, `curl`, atau antarmuka Swagger UI yang tersedia di `/docs`.

#### 1. Health Check

*   **Endpoint:** `GET /health`
*   **Fungsi Singkat:** Memeriksa status operasional layanan API, keaktifan `SparkSession`, model mana saja yang berhasil dimuat, dan menampilkan peringatan jika ada masalah saat startup.
*   **Cara Tes (curl):**
    ```bash
    curl http://localhost:8001/health
    ```
*   **Contoh Respons Sukses (JSON):**
    ```json
    {
      "status": "ok",
      "spark_session_active": true,
      "models_loaded": [
        "recommender",
        "transaction_predictor",
        "user_segmentation"
      ],
      "warnings": []
    }
    ```
![image](https://github.com/user-attachments/assets/9f640cbc-0398-41be-a866-11df733c754b)


#### 2. Dokumentasi API Interaktif (Swagger UI)

*   **Endpoint:** `GET /docs`
*   **Fungsi Singkat:** Menyediakan antarmuka web interaktif (Swagger UI) untuk melihat semua endpoint yang tersedia, skema request dan response, serta memungkinkan Anda mengirim request uji coba langsung dari browser.
*   **Cara Tes:** Buka `http://localhost:8001/docs` di browser web Anda.

![image](https://github.com/user-attachments/assets/abae1de8-4355-4cda-92a1-e34c8c161e04)  
![image](https://github.com/user-attachments/assets/c8266911-9659-4123-95df-92e6d11c0999)



#### 3. Rekomendasi Produk untuk Pengguna

*   **Endpoint:** `GET /recommendations/{visitorid_int}`
*   **Fungsi Singkat:** Memberikan sejumlah rekomendasi produk yang dipersonalisasi untuk `visitorid_int` tertentu berdasarkan model ALS.
*   **Path Parameter:**
    *   `visitorid_int` (integer): ID numerik dari pengunjung.
*   **Query Parameter (Opsional):**
    *   `num_recommendations` (integer, default: 5): Jumlah item yang ingin direkomendasikan.
*   **Cara Tes (curl):**
    ```bash
    # Mendapatkan 5 rekomendasi untuk visitorid 123
    curl "http://localhost:8001/recommendations/123"

    # Mendapatkan 3 rekomendasi untuk visitorid 456
    curl "http://localhost:8001/recommendations/456?num_recommendations=3"
    ```
#### Jika ID Tidak Ditemukan dalam Dataset  
![image](https://github.com/user-attachments/assets/d9234b2a-064c-4c67-98f9-c8c50564cc4c)  

#### Jika ID Ditemukan dalam Dataset
![image](https://github.com/user-attachments/assets/b48890bb-111b-4402-bb6f-2b712c048f53)  

#### Mengambil 3 rekomendasi   
![image](https://github.com/user-attachments/assets/6e6e6b2c-ba1e-448b-94ca-b1e141cd3fe8)

#### Log Docker  
![image](https://github.com/user-attachments/assets/d6f5d204-948c-498f-bae2-2c334085bc60)


#### 4. Prediksi Transaksi

*   **Endpoint:** `POST /predict-transaction`
*   **Fungsi Singkat:** Memprediksi apakah seorang pengunjung akan melakukan transaksi berdasarkan fitur perilaku agregat mereka, menggunakan model klasifikasi (Random Forest).
*   **Request Body (JSON):**
    ```json
    {
        "visitorid_to_identify": "user_test_predict_01",
        "num_views": 15,
        "num_addtocart": 2,
        "distinct_items_interacted": 8
    }
    ```
*   **Cara Tes (curl):**
    ```bash
    curl -X POST http://localhost:8001/predict-transaction \
    -H "Content-Type: application/json" \
    -d '{"visitorid_to_identify": "user_test_predict_01", "num_views": 15, "num_addtocart": 2, "distinct_items_interacted": 8}'
    ```
*   **Contoh Respons Sukses (JSON):**
    ```json
    {
      "visitorid": "user_test_predict_01",
      "will_transact": true,
      "probability": 0.8234
    }
    ```
*   **Analisis Respons:**
    *   `"will_transact"`: `true` jika model memprediksi pengguna akan bertransaksi, `false` jika tidak.
    *   `"probability"`: Probabilitas pengguna tersebut termasuk dalam kelas positif (akan bertransaksi).

#### User yang sering melihat produk dan add cart  
```bash
{
    "visitorid_to_identify": "power_shopper_candidate_789",
    "num_views": 120,
    "num_addtocart": 7,
    "distinct_items_interacted": 45
}
```  
![image](https://github.com/user-attachments/assets/df9e4212-3398-4a95-aacf-e2b0d472e793)  


#### User yang hanya melihat produk tanpa add cart  
```bash
{
    "visitorid_to_identify": "casual_browser_001",
    "num_views": 5,
    "num_addtocart": 0,
    "distinct_items_interacted": 3
}
```
![image](https://github.com/user-attachments/assets/522e4308-194a-4ff2-88d4-e2e8aabc015b)

#### Log Docker  
![image](https://github.com/user-attachments/assets/333b959a-ff8a-4d10-9b55-006c18b67c25)



#### 5. Segmentasi Pengguna

*   **Endpoint:** `POST /segment-user`
*   **Fungsi Singkat:** Mengklasifikasikan seorang pengunjung ke dalam segmen pengguna tertentu berdasarkan pola perilaku agregat mereka, menggunakan model klastering (misalnya, KMeans).
*   **Request Body (JSON):**
    ```json
    {
        "visitorid_to_identify": "user_test_segment_01",
        "total_events": 60,
        "total_views": 45,
        "total_addtocart": 6,
        "total_transactions": 3,
        "view_ratio": 0.75,
        "addtocart_ratio": 0.10,
        "transaction_ratio": 0.0667
    }
    ```
*   **Cara Tes (curl):**
    ```bash
    curl -X POST http://localhost:8001/segment-user \
    -H "Content-Type: application/json" \
    -d '{"visitorid_to_identify": "user_test_segment_01", "total_events": 60, "total_views": 45, "total_addtocart": 6, "total_transactions": 3, "view_ratio": 0.75, "addtocart_ratio": 0.10, "transaction_ratio": 0.0667}'
    ```
*   **Contoh Respons Sukses (JSON):**
    ```json
    {
      "visitorid": "user_test_segment_01",
      "cluster_id": 2 
    }
    ```
*   **Analisis Respons:**
    *   `"cluster_id"`: ID numerik dari segmen (klaster) tempat pengguna tersebut diklasifikasikan oleh model KMeans (misalnya, 0, 1, 2, 3, atau 4 jika `k=5`).

#### Loyal Customer
```bash
{
    "visitorid_to_identify": "loyal_customer_007",
    "total_events": 500,
    "total_views": 350,
    "total_addtocart": 50,
    "total_transactions": 25,
    "view_ratio": 0.7,    // 350 / 500
    "addtocart_ratio": 0.1,   // 50 / 500
    "transaction_ratio": 0.0714 // 25 / 350
}
```
![image](https://github.com/user-attachments/assets/210f6ce4-dcfc-4a53-a9d0-7f386474bafd)

#### Window Shopper
```bash
{
    "visitorid_to_identify": "window_shopper_999",
    "total_events": 150,
    "total_views": 140,
    "total_addtocart": 2,
    "total_transactions": 0,
    "view_ratio": 0.933, // 140 / 150
    "addtocart_ratio": 0.013, // 2 / 150
    "transaction_ratio": 0.0    // 0 / 140
}
```
![image](https://github.com/user-attachments/assets/f5b4a69e-8b0c-4a77-bf6f-0b9feca0680f)  

#### Log Docker  
![image](https://github.com/user-attachments/assets/8488aa69-61c8-42a7-848b-4d84f72ca8f6)


---

### 📊 Hasil dan Analisis API Service

Layanan API yang di-Dockerize berhasil menyediakan antarmuka untuk mengakses kemampuan prediktif dari model-model Spark yang telah dilatih.

*   **Keberhasilan Startup:** Log startup dari kontainer API menunjukkan bahwa `SparkSession` berhasil diinisialisasi dan ketiga model (Rekomendasi, Prediksi Transaksi, Segmentasi Pengguna) berhasil dimuat dari volume yang di-mount. Ini memvalidasi konfigurasi Docker, path model, dan kode pemuatan model.
    ```
    standalone_api_service_container  | SparkSession initialized (inside Docker).
    standalone_api_service_container  | Loading 'Recommender (ALS)' model...
    standalone_api_service_container  | 'Recommender (ALS)' model loaded successfully.
    standalone_api_service_container  | Loading 'Transaction Predictor' model...
    standalone_api_service_container  | 'Transaction Predictor' model loaded successfully.
    standalone_api_service_container  | Loading 'User Segmentation' model...
    standalone_api_service_container  | 'User Segmentation' model loaded successfully.
    standalone_api_service_container  | INFO:     Application startup complete.
    standalone_api_service_container  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    ```

*   **Fungsionalitas Endpoint:**
    *   Endpoint `/health` memberikan konfirmasi status "ok" dan daftar model yang dimuat, berguna untuk pemantauan.
    *   Endpoint `/recommendations/{visitorid_int}` berhasil mengembalikan daftar rekomendasi produk yang dipersonalisasi ketika diberikan `visitorid_int` yang valid (ada dalam data pelatihan model ALS). Untuk ID yang tidak dikenal atau kurang data, respons berupa daftar kosong, sesuai dengan strategi `coldStartStrategy="drop"`.
    *   Endpoint `/predict-transaction` dan `/segment-user` berhasil menerima fitur input dalam format JSON, memprosesnya dengan model Spark yang sesuai, dan mengembalikan prediksi (transaksi atau segmen) dalam format JSON.

*   **Performa (Observasi Awal):** Waktu respons untuk endpoint yang melibatkan inferensi Spark mungkin bervariasi tergantung pada kompleksitas model dan beban pada SparkSession. Untuk data tunggal seperti dalam contoh request, respons biasanya cukup cepat setelah *cold start* awal dari pemanggilan model. Penggunaan kembali `SparkSession` yang sudah ada membantu mengurangi latensi.

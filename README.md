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

## 🔜 Tahap Selanjutnya: Spark Processing

- File `batch_*.csv` dari `data/processed_batches/` digunakan untuk Spark.
- Tiap file berisi ±10.000 event (kecuali batch terakhir).
- Pastikan Spark dapat membaca file CSV ini sebagai input untuk ML pipeline.

---

> 🧠 *Dengan memproses aliran data event ini, kita dapat memahami pola perilaku pengguna untuk meningkatkan pengalaman pengguna, personalisasi, dan pengambilan keputusan bisnis dalam e-commerce.*

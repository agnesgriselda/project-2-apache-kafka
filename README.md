# Project Big Data 2 - Retail Rocket Event Processing

Proyek ini mensimulasikan pemrosesan data stream dari event e-commerce Retail Rocket menggunakan Apache Kafka untuk ingestion, Apache Spark untuk pemrosesan batch dan training model, serta API untuk melayani hasil model.

## Deskripsi Dataset: Retail Rocket E-commerce Events

*   **Sumber:** [Retail Rocket Recommender System Dataset (Kaggle)](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset)
*   **File yang Digunakan:** `events.csv`
*   **Ukuran:** Sekitar 2.7 juta baris (event).
*   **Deskripsi Konten:** Dataset ini berisi log perilaku pengguna (event) dari sebuah platform e-commerce. Setiap baris merepresentasikan satu aksi yang dilakukan oleh pengunjung.
*   **Kolom Utama di `events.csv`:**
    *   `timestamp`: Waktu terjadinya event (dalam format Unix timestamp milliseconds).
    *   `visitorid`: ID unik untuk setiap pengunjung.
    *   `event`: Jenis aksi yang dilakukan oleh pengunjung. Nilai tipikal:
        *   `view`: Pengunjung melihat detail produk.
        *   `addtocart`: Pengunjung menambahkan produk ke keranjang belanja.
        *   `transaction`: Pengunjung menyelesaikan pembelian (transaksi).
    *   `itemid`: ID unik untuk setiap produk/item.
    *   `transactionid`: ID unik untuk transaksi (hanya ada jika `event` adalah `transaction`, selain itu `null`/kosong).

## Tujuan Proyek dengan Dataset Ini

Tujuan utama proyek ini adalah untuk membangun sebuah pipeline data end-to-end yang mampu menangani aliran data event e-commerce secara simulasi, melakukan analisis, dan menghasilkan insight melalui model machine learning. Dengan menggunakan dataset Retail Rocket `events.csv`, proyek ini bertujuan untuk:

1.  **Simulasi Data Stream:** Menggunakan Apache Kafka untuk meng-ingest data event dari `events.csv` seolah-olah data tersebut datang secara real-time (streaming).
2.  **Pemrosesan Batch:** Menggunakan Apache Spark untuk memproses data event yang telah dikumpulkan dalam batch. Ini mencakup pra-pemrosesan data dan feature engineering.
3.  **Pelatihan Model Machine Learning (Secara Iteratif):**
    *   Melatih beberapa model machine learning berdasarkan segmen data yang masuk secara bertahap.
    *   Contoh potensi model yang bisa dikembangkan (tergantung implementasi tim):
        *   **Sistem Rekomendasi Produk:** Memberikan rekomendasi item kepada pengunjung berdasarkan histori interaksi mereka.
        *   **Prediksi Perilaku Pengguna:** Misalnya, memprediksi apakah seorang pengunjung akan melakukan transaksi.
        *   **Segmentasi Pengguna:** Mengelompokkan pengunjung berdasarkan pola perilaku belanja mereka.
4.  **Penyediaan Hasil Model melalui API:** Mengekspos model-model yang telah dilatih melalui endpoint API, sehingga hasil prediksi atau rekomendasi dapat diakses oleh pengguna atau sistem lain.
5.  **Demonstrasi Arsitektur Big Data:** Menunjukkan pemahaman dan implementasi komponen-komponen kunci dalam arsitektur pemrosesan data besar seperti Kafka dan Spark untuk kasus penggunaan data stream dan batch.

Dengan memproses data event ini, kita dapat mengeksplorasi bagaimana pola perilaku pengguna dapat dianalisis untuk meningkatkan pengalaman pengguna, personalisasi, dan pengambilan keputusan bisnis di platform e-commerce.

## Bagian 1: Kafka Pipeline - Ingesti Data Event

Bagian ini bertanggung jawab untuk membaca data mentah dari file `events.csv`, mengirimkannya ke topic Kafka sebagai simulasi stream, dan kemudian mengonsumsi data tersebut dari Kafka untuk disimpan dalam bentuk file batch CSV yang siap diproses oleh Spark.

**Struktur Direktori Terkait:**
```
.
├── data/
│   ├── raw/
│   │   └── events.csv         # Data sumber mentah
│   └── processed_batches/     # Output dari Kafka Consumer (file batch CSV)
├── kafka_pipeline/
│   ├── docker-compose.yaml    # Konfigurasi Docker untuk Kafka & Zookeeper
│   ├── producer.py            # Script Kafka Producer
│   ├── consumer.py            # Script Kafka Consumer
│   ├── requirements_kafka.txt # Dependensi Python untuk kafka_pipeline
│   └── venv_kafka/            # Virtual environment (jangan di-commit ke Git)
└── README.md                  # File ini
```

### Prasyarat

1.  **Docker Desktop:** Terinstall dan berjalan. (Download: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/))
2.  **Python:** Versi 3.8 atau lebih tinggi. (Download: [https://www.python.org/](https://www.python.org/))
3.  **Dataset:** File `events.csv` dari dataset Retail Rocket tersedia di `data/raw/events.csv`.

### Langkah-Langkah Menjalankan Kafka Pipeline

**1. Setup Lingkungan Kafka dengan Docker:**

   *   Buka terminal atau Command Prompt (CMD).
   *   Navigasi ke **root direktori proyek** (`project-bigdata-retailrocket`).
   *   Jalankan perintah berikut untuk memulai Kafka dan Zookeeper menggunakan Docker Compose:
     ```bash
     docker-compose -f kafka_pipeline\docker-compose.yaml up -d
     ```
   *   Tunggu beberapa saat hingga kedua container (`zookeeper_guardian` dan `kafka_streamliner`) berjalan. Kamu bisa cek statusnya dengan:
     ```bash
     docker-compose -f kafka_pipeline\docker-compose.yaml ps
     ```
     Outputnya seharusnya menunjukkan status `Up` untuk kedua service.

**2. Setup Virtual Environment dan Install Dependensi Python:**

   *   Buka terminal/CMD baru.
   *   Navigasi ke direktori `kafka_pipeline`:
     ```bash
     cd path\to\your\project-bigdata-retailrocket\kafka_pipeline
     ```
   *   Buat virtual environment (jika belum ada):
     ```bash
     python -m venv venv_kafka
     ```
   *   Aktifkan virtual environment:
     *   Windows CMD: `venv_kafka\Scripts\activate`
     *   Git Bash / Linux / macOS: `source venv_kafka/bin/activate`
     (Prompt terminal akan berubah, diawali dengan `(venv_kafka)`)
   *   Install dependensi yang dibutuhkan:
     ```bash
     pip install -r requirements_kafka.txt
     ```
     *(Pastikan file `requirements_kafka.txt` sudah berisi `kafka-python`, `pandas`, dan dependensinya).*

**3. Menjalankan Kafka Consumer:**

   *   Pastikan virtual environment `(venv_kafka)` aktif.
   *   Di terminal yang sama (atau terminal baru dengan venv aktif di direktori `kafka_pipeline`), jalankan script Consumer:
     ```bash
     python consumer.py
     ```
   *   Consumer akan mulai berjalan dan menunggu pesan dari topic Kafka (`retail_events_topic`).

**4. Menjalankan Kafka Producer:**

   *   Buka terminal/CMD **BARU**.
   *   Navigasi ke direktori `kafka_pipeline`:
     ```bash
     cd path\to\your\project-bigdata-retailrocket\kafka_pipeline
     ```
   *   Aktifkan virtual environment:
     *   Windows CMD: `venv_kafka\Scripts\activate`
     *   Git Bash / Linux / macOS: `source venv_kafka/bin/activate`
   *   Jalankan script Producer:
     ```bash
     python producer.py
     ```
   *   Producer akan mulai membaca file `data/raw/events.csv` dan mengirimkan setiap baris sebagai pesan ke Kafka. Kamu akan melihat log progres di terminal Producer.
   *   Di terminal Consumer, kamu akan melihat pesan-pesan diterima dan file-file batch CSV mulai dibuat di direktori `data/processed_batches/`.

**5. Observasi dan Penyelesaian:**

   *   **Producer:** Akan berhenti secara otomatis setelah semua data dari `events.csv` terkirim dan mencetak pesan "Producer: All ... messages sent...".
   *   **Consumer:** Setelah Producer selesai dan tidak ada pesan baru yang masuk ke topic Kafka selama durasi `consumer_timeout_ms` (default 30-60 detik di script), Consumer akan berhenti secara otomatis, menyimpan batch terakhir (jika ada), dan menutup koneksi. Terminal akan kembali ke prompt biasa.
   *   Hasil dari proses ini adalah sejumlah file `batch_XXX.csv` di dalam direktori `data/processed_batches/`. File-file ini siap untuk diproses oleh Apache Spark di tahap selanjutnya.

**6. Menghentikan Lingkungan Kafka Docker (Setelah Selesai):**

   *   Jika sudah tidak digunakan lagi, kamu bisa menghentikan dan menghapus container Kafka dan Zookeeper.
   *   Buka terminal di **root direktori proyek**.
   *   Jalankan:
     ```bash
     docker-compose -f kafka_pipeline\docker-compose.yaml down
     ```

### Catatan Penting untuk Tahap Selanjutnya (Spark Processing):

*   File-file batch hasil dari Kafka Consumer (`data/processed_batches/*.csv`) adalah input untuk script Apache Spark.
*   Setiap file batch berisi sekumpulan event (default 10.000 event per file, kecuali file `_final.csv`).
*   Pastikan Spark dapat membaca format CSV dari file-file ini.
```
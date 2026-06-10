# 🧭 AI Career Compass

**AI-Based Career & Major Recommendation System**
Capstone Project - DSGA CAMP Batch 4 | Kelompok 6

---

## 📁 Struktur Folder

```
career_ai_app/
├── app.py                          # Main app (Halaman Home)
├── pages/
│   ├── 1_📋_Input_Profil.py       # Halaman input profil siswa
│   ├── 2_🎯_Hasil_Rekomendasi.py  # Halaman hasil rekomendasijurusan
│   ├── 3_🤖_Chatbot_AI.py         # Halaman chatbot AI
│   ├── 4_📊_Analisis_Data.py       # Halaman EDA & visualisasi data
│   └── 5_⚙️_Training_Model.py    # Halaman training model ML
├── src/
│   └── sidebar_nav.py             # Komponen reusable sidebar navigation
├── db_connector.py                # Koneksi MySQL database
├── chatbot_agent.py               # LangChain + Gemini chatbot agent
├── ml_model.py                  # ML training & prediksi
├── visualizations.py            # Chart & visualisasi Plotly
├── best_model.pkl             # Model ML terbaik (Random Forest)
├── random_forest.pkl          # Model Random Forest
├── xgboost.pkl                # Model XGBoost
├── mlp.pkl                    # Model MLP
├── scaler.pkl                 # StandardScaler
├── label_encoder.pkl         # LabelEncoder
├── requirements.txt          # Python dependencies
└── README.md                  # Dokumentasi ini
```

---

## 🚀 Cara Install & Menjalankan

### 1. Persiapan
```bash
# Pastikan Python 3.9+ sudah terinstall
python --version

# Buka folder project
cd career_ai_app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Environment
```bash
# Buat file .env jika belum ada
# Isi dengan API Key Gemini (GRATIS di aistudio.google.com)
GOOGLE_API_KEY=your_api_key_here
```

### 4. Pastikan Database Aktif
- Buka XAMPP → Start Apache & MySQL
- Pastikan database `career_recommendation_db` sudah diimport

### 5. Jalankan Aplikasi
```bash
# Dari folder career_ai_app/
streamlit run app.py
```

Buka browser: **http://localhost:8501**

---

## 📋 Alur Penggunaan

1. **Training Model** (Opsional) → Buka halaman `⚙️ Training Model` → Training ulang model jika diperlukan
2. **Input Profil** → Buka halaman `📋 Input Profil` → Isi data diri, minat, dan preferensi
3. **Hasil Rekomendasi** → Buka halaman `🎯 Hasil Rekomendasi` → Lihat hasil prediksi jurusan
4. **Chat AI** → Buka halaman `🤖 Chatbot AI` → Tanya tentang karir, gaji, kampus, dll
5. **Analisis Data** → Buka halaman `📊 Analisis Data` → Eksplorasi data danvisualisasi

---

## 🤖 Mendapatkan Google Gemini API Key (GRATIS)

1. Buka [aistudio.google.com](https://aistudio.google.com)
2. Login dengan akun Google
3. Klik **"Get API Key"** → **"Create API Key"**
4. Copy API Key
5. Tempel di sidebar aplikasi (halaman Chatbot AI) atau di file `.env`

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|---|---|
| Frontend | Streamlit |
| ML Models | Random Forest, XGBoost, MLP (scikit-learn) |
| Generative AI | Google Gemini 2.5 Flash |
| AI Framework | LangChain |
| Database | MySQL (XAMPP) |
| Visualisasi | Plotly, Seaborn, Matplotlib |
| Language | Python 3.9+ |
# 🧭 AI Career Compass
**AI-Based Career & Major Recommendation System**  
Capstone Project - DSGA CAMP Batch 4 | Kelompok 6

---

## 📁 Struktur Folder

```
career_ai_app/
├── streamlit_app/
│   ├── app.py                    ← Main app (Home)
│   └── pages/
│       ├── 1_📋_Input_Profil.py
│       ├── 2_🎯_Hasil_Rekomendasi.py
│       ├── 3_🤖_Chatbot_AI.py
│       ├── 4_📊_Analisis_Data.py
│       ├── 5_⚙️_Training_Model.py
│       └── 6_ℹ️_About.py
├── src/
│   ├── database/
│   │   └── db_connector.py       ← Koneksi MySQL
│   ├── models/
│   │   └── ml_model.py           ← ML training & prediksi
│   ├── agents/
│   │   └── chatbot_agent.py      ← LangChain + Gemini chatbot
│   └── utils/
│       └── visualizations.py    ← Chart & visualisasi
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Cara Install & Menjalankan

### 1. Persiapan
```bash
# Pastikan Python 3.9+ sudah terinstall
python --version

# Clone / buka folder project di VS Code
cd career_ai_app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Environment
```bash
# Salin file contoh env
copy .env.example .env   # Windows
# atau
cp .env.example .env     # Mac/Linux

# Edit .env - isi API Key Gemini (GRATIS di aistudio.google.com)
```

### 4. Pastikan Database Aktif
- Buka XAMPP → Start Apache & MySQL
- Pastikan database `career_recommendation_db` sudah diimport

### 5. Jalankan Aplikasi
```bash
# Dari folder career_ai_app/
streamlit run streamlit_app/app.py
```

Buka browser: **http://localhost:8501**

---

## 📋 Alur Penggunaan

1. **Training Model** → Buka halaman `⚙️ Training Model` → Klik "Mulai Training"
2. **Input Profil** → Isi data diri di `📋 Input Profil`
3. **Lihat Hasil** → Cek rekomendasi di `🎯 Hasil Rekomendasi`
4. **Chat AI** → Tanya lebih lanjut di `🤖 Chatbot AI`
5. **Eksplorasi Data** → Lihat EDA di `📊 Analisis Data`

---

## 🤖 Mendapatkan Google Gemini API Key (GRATIS)

1. Buka [aistudio.google.com](https://aistudio.google.com)
2. Login dengan akun Google
3. Klik **"Get API Key"** → **"Create API Key"**
4. Copy API Key
5. Tempel di sidebar aplikasi atau di file `.env`

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|---|---|
| Frontend | Streamlit |
| ML Models | Random Forest, XGBoost, MLP |
| Generative AI | Google Gemini 1.5 Flash |
| AI Framework | LangChain |
| Database | MySQL (XAMPP) |
| Visualisasi | Plotly |
| Language | Python 3.9+ |

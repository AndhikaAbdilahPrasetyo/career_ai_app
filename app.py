"""
AI Career Compass - Main Streamlit Application
Sistem Rekomendasi Jurusan & Karir Berbasis AI

Jalankan dengan: streamlit run app.py
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

# ─── Konfigurasi Halaman ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1B2A 0%, #1C2B3A 100%);
    border-right: 1px solid rgba(79, 142, 247, 0.2);
  }

  /* Cards */
  .metric-card {
    background: linear-gradient(135deg, #1C2B3A, #0D1B2A);
    border: 1px solid rgba(79,142,247,0.3);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    margin-bottom: 12px;
    transition: transform 0.2s, border-color 0.2s;
  }
  .metric-card:hover {
    transform: translateY(-3px);
    border-color: rgba(79,142,247,0.7);
  }
  .metric-card h2 {
    color: #4F8EF7;
    font-size: 2.5rem;
    margin: 0;
    font-weight: 700;
  }
  .metric-card p {
    color: rgba(255,255,255,0.7);
    margin: 4px 0 0;
    font-size: 0.9rem;
  }

  /* Result card */
  .result-card {
    background: linear-gradient(135deg, #1C2B3A, #131C27);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 14px;
    border-left: 4px solid #4F8EF7;
    transition: border-color 0.2s;
  }
  .result-card.top1 { border-left-color: #F7924F; }
  .result-card h3 { color: white; margin: 0 0 6px; font-size: 1.15rem; }
  .result-card .score-badge {
    display: inline-block;
    padding: 2px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    background: rgba(79,142,247,0.2);
    color: #4F8EF7;
    font-family: 'JetBrains Mono', monospace;
  }

  /* Hero banner */
  .hero-banner {
    background: linear-gradient(135deg, #0D1B2A 0%, #1a2744 50%, #0D1B2A 100%);
    border: 1px solid rgba(79,142,247,0.2);
    border-radius: 24px;
    padding: 40px 48px;
    margin-bottom: 32px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .hero-banner::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at center, rgba(79,142,247,0.08) 0%, transparent 70%);
    pointer-events: none;
  }
  .hero-banner h1 {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4F8EF7, #9B4FF7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 12px;
  }
  .hero-banner p {
    color: rgba(255,255,255,0.7);
    font-size: 1.15rem;
    margin: 0;
  }

  /* Status badge */
  .status-ok { color: #4FF78E; font-weight: 600; }
  .status-err { color: #F74F4F; font-weight: 600; }

  /* Divider */
  .section-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: white;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(79,142,247,0.4);
    margin-bottom: 20px;
  }

  /* Chat bubbles */
  .chat-user {
    background: rgba(79,142,247,0.15);
    border-radius: 16px 16px 4px 16px;
    padding: 12px 16px;
    margin: 8px 0 8px auto;
    max-width: 80%;
    color: white;
    border: 1px solid rgba(79,142,247,0.3);
  }
  .chat-bot {
    background: rgba(28,43,58,0.8);
    border-radius: 16px 16px 16px 4px;
    padding: 12px 16px;
    margin: 8px auto 8px 0;
    max-width: 85%;
    color: rgba(255,255,255,0.9);
    border: 1px solid rgba(255,255,255,0.08);
  }

  /* Stmetric override */
  [data-testid="stMetric"] {
    background: linear-gradient(135deg, #1C2B3A, #0D1B2A);
    border: 1px solid rgba(79,142,247,0.25);
    border-radius: 12px;
    padding: 16px;
  }

  /* Sidebar Navigation Buttons - row layout */
  [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
    align-items: center;
    padding: 0;
    gap: 0;
  }
  [data-testid="stSidebar"] .nav-icon-col {
    width: 36px !important;
    min-width: 36px !important;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
  }
  [data-testid="stSidebar"] .nav-btn-col {
    flex: 1;
    padding: 0;
  }
  [data-testid="stSidebar"] .nav-btn-col > button {
    width: 100%;
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(79,142,247,0.15) !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 8px 12px !important;
    transition: all 0.2s ease !important;
    text-align: left !important;
  }
  [data-testid="stSidebar"] .nav-btn-col > button:hover {
    background: rgba(79,142,247,0.12) !important;
    border-color: rgba(79,142,247,0.5) !important;
    color: white !important;
  }
  [data-testid="stSidebar"] .stButton > button:focus:not(:active) {
    background: rgba(79,142,247,0.15) !important;
    border-color: #4F8EF7 !important;
    color: white !important;
    box-shadow: none !important;
  }
  .nav-section-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: rgba(255,255,255,0.35);
    margin: 14px 0 6px 4px;
  }

  /* Sidebar branding */
  .sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
  }
  .sidebar-brand h1 {
    font-size: 1.1rem;
    font-weight: 700;
    color: white;
    margin: 0;
  }
  .sidebar-brand .brand-icon {
    font-size: 1.6rem;
    line-height: 1;
  }

  /* Hide Streamlit auto-generated sidebar nav */
  [data-testid="stSidebarNav"] {
    display: none !important;
  }
  [data-testid="stSidebarNav"] > ul {
    display: none !important;
  }
</style>
""", unsafe_allow_html=True)

# ─── Import modules ───────────────────────────────────────────────────────────
from db_connector import test_connection

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown("""
    <div class="sidebar-brand">
        <span class="brand-icon">🧭</span>
        <h1>AI Career Compass</h1>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Capstone Project - DSGA CAMP Batch 4")
    st.divider()

    # Status koneksi
    db_ok = test_connection()
    if db_ok:
        st.markdown('<p class="status-ok">✅ Database Terhubung</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-err">❌ Database Terputus</p>', unsafe_allow_html=True)
        st.warning("Pastikan XAMPP MySQL aktif!")

    st.divider()

    # API Key input
    st.markdown("**🤖 Konfigurasi AI Chatbot**")
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="Masukkan API Key...",
        help="Dapatkan gratis di: aistudio.google.com",
        value=os.getenv("GOOGLE_API_KEY", ""),
    )
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        st.caption("✅ API Key tersimpan sementara")
    else:
        st.caption("⚠️ Chatbot AI memerlukan API Key")

    st.markdown("[🔑 Dapatkan API Key Gratis](https://aistudio.google.com/app/apikey)")

    st.divider()
    st.markdown('<p class="nav-section-label">Menu Navigasi</p>', unsafe_allow_html=True)

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("🏠")
    with col_btn:
        if st.button("Home", use_container_width=True):
            st.switch_page("app.py")

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("📋")
    with col_btn:
        if st.button("Input Profil", use_container_width=True):
            st.switch_page("pages/1_📋_Input_Profil.py")

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("🎯")
    with col_btn:
        if st.button("Hasil Rekomendasi", use_container_width=True):
            st.switch_page("pages/2_🎯_Hasil_Rekomendasi.py")

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("🤖")
    with col_btn:
        if st.button("Chatbot AI", use_container_width=True):
            st.switch_page("pages/3_🤖_Chatbot_AI.py")

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("📊")
    with col_btn:
        if st.button("Analisis Data", use_container_width=True):
            st.switch_page("pages/4_📊_Analisis_Data.py")

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("⚙️")
    with col_btn:
        if st.button("Training Model", use_container_width=True):
            st.switch_page("pages/5_⚙️_Training_Model.py")

    st.divider()
    st.caption("Kelompok 6 | Celerates CAMP Batch 4")

# ─── HOME PAGE ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <h1>🧭 AI Career Compass</h1>
  <p>Sistem Rekomendasi Jurusan & Karir Berbasis Kecerdasan Buatan</p>
  <p style="margin-top:8px; font-size:0.95rem; opacity:0.6;">
    Powered by Machine Learning + Generative AI | Celerates CAMP Batch 4
  </p>
</div>
""", unsafe_allow_html=True)

# ─── Quick Stats ──────────────────────────────────────────────────────────────
if db_ok:
    from db_connector import query_df
    try:
        n_students = query_df("SELECT COUNT(*) as n FROM student_profiles").iloc[0]["n"]
        n_jurusan  = query_df("SELECT COUNT(DISTINCT jurusan) as n FROM jurusan_metadata").iloc[0]["n"]
        n_kampus   = query_df("SELECT COUNT(DISTINCT Kampus) as n FROM jurusan_kampus_info").iloc[0]["n"]
        n_karir    = query_df("SELECT COUNT(*) as n FROM career_path").iloc[0]["n"]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><h2>{n_students}</h2><p>Data Siswa</p></div>',
                        unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><h2>{n_jurusan}</h2><p>Jurusan Tersedia</p></div>',
                        unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><h2>{n_kampus}</h2><p>Kampus Partner</p></div>',
                        unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><h2>{n_karir}</h2><p>Pilihan Karir</p></div>',
                        unsafe_allow_html=True)
    except:
        pass

st.divider()

# ─── Fitur Aplikasi ───────────────────────────────────────────────────────────
st.markdown('<p class="section-title">🚀 Fitur Unggulan</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.info("""
    **🎯 Prediksi Jurusan**
    
    Masukkan nilai akademik dan profil kepribadianmu. 
    AI akan memprediksi jurusan kuliah terbaik menggunakan 
    **Random Forest, XGBoost, dan Neural Network**.
    """)
with col2:
    st.info("""
    **🤖 Chatbot AI**
    
    Tanya apa saja seputar jurusan, karir, dan kampus kepada 
    asisten AI kami yang didukung **Google Gemini + LangChain Agent**.
    """)
with col3:
    st.info("""
    **📊 Analisis Lengkap**
    
    Lihat visualisasi interaktif profil kemampuanmu, 
    perbandingan karir, gaji, serta kampus-kampus terbaik 
    di Indonesia.
    """)

st.divider()

# ─── Cara Penggunaan ─────────────────────────────────────────────────────────
st.markdown('<p class="section-title">📖 Cara Menggunakan</p>', unsafe_allow_html=True)

cols = st.columns(4)

with cols[0]:
    st.markdown("""
    <div class="metric-card" style="min-height:140px;">
        <div style="font-size:2rem;">1️⃣</div>
        <div style="color:white; font-weight:600; margin:8px 0 4px;">Input Profil</div>
        <div style="color:rgba(255,255,255,0.6); font-size:0.85rem;">Isi form data akademik, minat, dan kepribadianmu</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("👉 Buka Input Profil", use_container_width=True):
        st.switch_page("pages/1_📋_Input_Profil.py")

with cols[1]:
    st.markdown("""
    <div class="metric-card" style="min-height:140px;">
        <div style="font-size:2rem;">2️⃣</div>
        <div style="color:white; font-weight:600; margin:8px 0 4px;">Training Model</div>
        <div style="color:rgba(255,255,255,0.6); font-size:0.85rem;">Jalankan training model ML jika belum ada</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("👉 Buka Training Model", use_container_width=True):
        st.switch_page("pages/5_⚙️_Training_Model.py")

with cols[2]:
    st.markdown("""
    <div class="metric-card" style="min-height:140px;">
        <div style="font-size:2rem;">3️⃣</div>
        <div style="color:white; font-weight:600; margin:8px 0 4px;">Lihat Hasil</div>
        <div style="color:rgba(255,255,255,0.6); font-size:0.85rem;">Dapatkan rekomendasi jurusan + info kampus & karir</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("👉 Buka Hasil Rekomendasi", use_container_width=True):
        st.switch_page("pages/2_🎯_Hasil_Rekomendasi.py")

with cols[3]:
    st.markdown("""
    <div class="metric-card" style="min-height:140px;">
        <div style="font-size:2rem;">4️⃣</div>
        <div style="color:white; font-weight:600; margin:8px 0 4px;">Tanya AI</div>
        <div style="color:rgba(255,255,255,0.6); font-size:0.85rem;">Diskusikan lebih lanjut dengan chatbot AI</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("👉 Buka Chatbot AI", use_container_width=True):
        st.switch_page("pages/3_🤖_Chatbot_AI.py")

st.divider()
st.caption("💡 **Tip:** Gunakan menu navigasi di sebelah kiri untuk berpindah halaman.")

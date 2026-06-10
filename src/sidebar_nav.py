"""
Sidebar Navigation Component
Dipakai di semua halaman untuk konsistensi tampilan navigasi.
"""
import os
import streamlit as st


def render_sidebar():
    """Render navigasi sidebar dengan styling yang sama seperti app.py"""

    st.markdown("""
    <div class="sidebar-brand">
        <span class="brand-icon">🧭</span>
        <h1>AI Career Compass</h1>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Capstone Project - DSGA CAMP Batch 4")
    st.divider()

    # Status koneksi
    from db_connector import test_connection
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

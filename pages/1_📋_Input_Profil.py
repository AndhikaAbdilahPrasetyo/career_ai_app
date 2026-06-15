"""
Halaman Input Profil Siswa
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

st.set_page_config(page_title="Input Profil | AI Career Compass", page_icon="📋", layout="wide", initial_sidebar_state="expanded")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.section-title { font-size:1.3rem; font-weight:600; color:white; border-bottom:2px solid rgba(79,142,247,0.4); padding-bottom:6px; margin-bottom:16px; }

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
.status-ok { color: #4FF78E; font-weight: 600; }
.status-err { color: #F74F4F; font-weight: 600; }

/* Hide Streamlit auto-generated sidebar nav */
[data-testid="stSidebarNav"] { display: none !important; }

/* Sidebar background */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1B2A 0%, #1C2B3A 100%);
    border-right: 1px solid rgba(79, 142, 247, 0.2);
}
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    from src.sidebar_nav import render_sidebar
    render_sidebar()

st.title("📋 Input Profil Siswa")
st.caption("Isi data dengan jujur untuk mendapatkan rekomendasi yang akurat.")
st.divider()

with st.form("profil_form"):

    # ── Identitas ────────────────────────────────────────────────────────────
    st.markdown('<p class="section-title">👤 Data Identitas</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        nama = st.text_input("Nama Lengkap", placeholder="Contoh: Budi Santoso")
    with c2:
        jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    with c3:
        asal_sekolah = st.selectbox(
            "Asal Sekolah / Jurusan SMA",
            ["IPA", "IPS", "SMK-TI", "SMK-Bisnis", "SMK-Kesehatan"]
        )

    st.divider()

    # ── Nilai Akademik ───────────────────────────────────────────────────────
    st.markdown('<p class="section-title">📚 Nilai Mata Pelajaran (0–100)</p>', unsafe_allow_html=True)

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        mtk = st.number_input("Matematika", 0, 100, 75, help="Nilai rapor/rata-rata")
    with r1c2:
        indo = st.number_input("Bahasa Indonesia", 0, 100, 78)
    with r1c3:
        eng = st.number_input("Bahasa Inggris", 0, 100, 75)
    with r1c4:
        ipa = st.number_input("IPA / Sains", 0, 100, 75)

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        fis = st.number_input("Fisika", 0, 100, 70)
    with r2c2:
        kim = st.number_input("Kimia", 0, 100, 70)
    with r2c3:
        bio = st.number_input("Biologi", 0, 100, 72)
    with r2c4:
        eko = st.number_input("Ekonomi", 0, 100, 75)

    r3c1, r3c2 = st.columns(2)
    with r3c1:
        geo = st.number_input("Geografi", 0, 100, 70)
    with r3c2:
        sos = st.number_input("Sosiologi", 0, 100, 70)

    st.divider()

    # ── Minat & Kepribadian ──────────────────────────────────────────────────
    st.markdown('<p class="section-title">💡 Minat & Kepribadian</p>', unsafe_allow_html=True)

    MINAT_OPTIONS = [
        "Teknologi & Komputer", "Bisnis & Keuangan", "Hukum & Sosial",
        "Kesehatan & Medis", "Sains & Penelitian", "Teknik & Konstruksi",
        "Seni & Desain", "Pendidikan & Pengajaran",
    ]

    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        minat_utama = st.selectbox("Minat Utama", MINAT_OPTIONS, index=0)

    # Default index untuk Minat Sekunder (samakan dengan Minat Utama)
    default_idx = MINAT_OPTIONS.index(minat_utama) if minat_utama in MINAT_OPTIONS else 0
    with mc2:
        minat_sek = st.selectbox(
            "Minat Sekunder",
            MINAT_OPTIONS,
            index=default_idx,
            help="Bisa sama dengan Minat Utama"
        )
    with mc3:
        kepribadian = st.selectbox(
            "Tipe Kepribadian",
            ["Analyst", "Diplomat", "Sentinel", "Explorer"],
            help="Analyst=Logis & Analitis | Diplomat=Empati & Kreatif | Sentinel=Teratur | Explorer=Spontan"
        )

    st.divider()

    # ── Soft Skills ──────────────────────────────────────────────────────────
    st.markdown('<p class="section-title">🌟 Kemampuan Diri (Skala 1–10)</p>', unsafe_allow_html=True)

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        analitis = st.slider("Kemampuan Analitis", 1, 10, 6,
                             help="Kemampuan berpikir logis, memecahkan masalah")
    with sc2:
        kreatif = st.slider("Kemampuan Kreatif", 1, 10, 6,
                            help="Kemampuan berpikir out-of-the-box, inovatif")
    with sc3:
        sosial = st.slider("Kemampuan Sosial", 1, 10, 6,
                           help="Kemampuan komunikasi, kerja tim, bersosialisasi")
    with sc4:
        leadership = st.slider("Kemampuan Leadership", 1, 10, 6,
                               help="Kemampuan memimpin, mengorganisir, mengambil keputusan")

    st.divider()

    # ── Preferensi ───────────────────────────────────────────────────────────
    st.markdown('<p class="section-title">🏫 Preferensi Kampus</p>', unsafe_allow_html=True)

    pc1, pc2 = st.columns(2)
    with pc1:
        target_kampus = st.multiselect(
            "Kampus yang Diminati",
            ["UI", "ITB", "UGM", "ITS", "UNAIR", "UNPAD", "UNDIP",
             "BRAWIJAYA", "TELKOM", "BINUS", "Lainnya"],
            default=["UGM", "ITS"]
        )
    with pc2:
        budget = st.selectbox(
            "Budget Kuliah per Semester",
            ["< 5 juta/semester", "5-10 juta/semester",
             "10-20 juta/semester", "> 20 juta/semester"]
        )

    st.divider()

    submitted = st.form_submit_button("🚀 Analisis & Rekomendasikan", use_container_width=True,
                                      type="primary")

if submitted:
    if not nama.strip():
        st.error("⚠️ Mohon isi nama lengkap!")
    else:
        # Simpan ke session state
        st.session_state["student_data"] = {
            "nama": nama,
            "jenis_kelamin": jenis_kelamin,
            "Asal_Sekolah_Tipe": asal_sekolah,
            "Nilai_Matematika": mtk,
            "Nilai_Bahasa_Indonesia": indo,
            "Nilai_Bahasa_Inggris": eng,
            "Nilai_IPA": ipa,
            "Nilai_Fisika": fis,
            "Nilai_Kimia": kim,
            "Nilai_Biologi": bio,
            "Nilai_Ekonomi": eko,
            "Nilai_Geografi": geo,
            "Nilai_Sosiologi": sos,
            "Minat_Utama": minat_utama,
            "Minat_Sekunder": minat_sek,
            "Tipe_Kepribadian": kepribadian,
            "Kemampuan_Analitis": analitis,
            "Kemampuan_Kreatif": kreatif,
            "Kemampuan_Sosial": sosial,
            "Kemampuan_Leadership": leadership,
            "Target_Kampus": target_kampus,
            "Budget_Kuliah": budget,
        }

        st.success(f"✅ Data **{nama}** berhasil disimpan!")
        st.info("👉 Lanjut ke halaman **Hasil Rekomendasi** di menu kiri.")

        # Preview
        st.divider()
        st.markdown("**Preview Data:**")
        import pandas as pd
        preview = {
            "Nama": nama, "Sekolah": asal_sekolah,
            "Matematika": mtk, "Bahasa Inggris": eng,
            "Minat Utama": minat_utama, "Kepribadian": kepribadian,
        }
        st.dataframe(pd.DataFrame([preview]), use_container_width=True)
elif "student_data" in st.session_state:
    st.info(f"ℹ️ Data terakhir: **{st.session_state['student_data']['nama']}**. "
            f"Isi form baru untuk mengubah.")

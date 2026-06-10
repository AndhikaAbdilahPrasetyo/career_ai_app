"""
Halaman Analisis Data & EDA
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Analisis Data | AI Career Compass", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

/* Sidebar Navigation Buttons */
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

st.title("📊 Analisis Data (EDA)")
st.caption("Eksplorasi dataset training untuk memahami pola data siswa.")
st.divider()

from db_connector import (
    get_student_profiles, get_jurusan_metadata,
    get_career_paths, get_kampus_info, test_connection
)

if not test_connection():
    st.error("❌ Database tidak terhubung. Pastikan XAMPP MySQL aktif.")
    st.stop()

# Load data
with st.spinner("Memuat data dari database..."):
    try:
        df = get_student_profiles()
        career_df = get_career_paths()
        kampus_df = get_kampus_info()
    except Exception as e:
        st.error(f"Error memuat data: {e}")
        st.stop()

# ─── Overview ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Siswa", f"{len(df):,}")
c2.metric("Jumlah Jurusan", df["Jurusan_Label"].nunique())
c3.metric("Kota Asal", df["Kota"].nunique())
c4.metric("Tipe Kepribadian", df["Tipe_Kepribadian"].nunique())

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📈 Distribusi Data", "🗺️ Demografi", "📚 Jurusan & Karir", "🏫 Kampus"])

# ─── Tab 1: Distribusi ────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        # Distribusi Jurusan
        jurusan_counts = df["Jurusan_Label"].value_counts()
        fig = px.bar(
            x=jurusan_counts.values, y=jurusan_counts.index,
            orientation="h",
            title="Distribusi Jurusan (Top 15)",
            color=jurusan_counts.values,
            color_continuous_scale="Blues",
            labels={"x": "Jumlah", "y": "Jurusan"},
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          title_font_color="white", showlegend=False,
                          yaxis=dict(color="white"), xaxis=dict(color="white"),
                          height=450)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Distribusi Kepribadian
        kep_counts = df["Tipe_Kepribadian"].value_counts()
        fig2 = px.pie(
            values=kep_counts.values, names=kep_counts.index,
            title="Distribusi Tipe Kepribadian",
            color_discrete_sequence=["#4F8EF7", "#F7924F", "#4FF78E", "#9B4FF7"],
            hole=0.4,
        )
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                           title_font_color="white",
                           legend=dict(font=dict(color="white")))
        st.plotly_chart(fig2, use_container_width=True)

    # Distribusi Nilai
    nilai_cols = ["Nilai_Matematika", "Nilai_Bahasa_Inggris", "Nilai_IPA",
                  "Nilai_Fisika", "Nilai_Kimia", "Nilai_Biologi"]

    selected_nilai = st.selectbox("Pilih Mata Pelajaran untuk Distribusi:", nilai_cols)
    fig3 = px.histogram(
        df, x=selected_nilai, nbins=20,
        title=f"Distribusi {selected_nilai.replace('_', ' ')}",
        color_discrete_sequence=["#4F8EF7"],
    )
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       title_font_color="white",
                       xaxis=dict(color="white"), yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"))
    st.plotly_chart(fig3, use_container_width=True)

    # Heatmap korelasi
    st.markdown("#### 🔥 Heatmap Korelasi Nilai Akademik")
    corr = df[nilai_cols].corr()
    fig_corr = px.imshow(
        corr, text_auto=True, aspect="auto",
        color_continuous_scale="RdBu",
        title="Korelasi Antar Nilai",
        labels=dict(color="Korelasi"),
    )
    fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                            title_font_color="white",
                            xaxis=dict(color="white"), yaxis=dict(color="white"))
    st.plotly_chart(fig_corr, use_container_width=True)

# ─── Tab 2: Demografi ─────────────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        # Distribusi kota
        kota_counts = df["Kota"].value_counts()
        fig = px.bar(kota_counts, title="Distribusi Kota Asal",
                     color=kota_counts.values, color_continuous_scale="Viridis")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          title_font_color="white", showlegend=False,
                          xaxis=dict(color="white", tickangle=45), yaxis=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Gender vs Jurusan (cross-tab)
        gender_jurusan = df.groupby(["Jenis_Kelamin", "Jurusan_Label"]).size().reset_index(name="count")
        top_jur = df["Jurusan_Label"].value_counts().head(8).index
        filtered = gender_jurusan[gender_jurusan["Jurusan_Label"].isin(top_jur)]
        fig = px.bar(filtered, x="Jurusan_Label", y="count", color="Jenis_Kelamin",
                     barmode="group", title="Gender vs Jurusan (Top 8)",
                     color_discrete_sequence=["#4F8EF7", "#F7924F"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          title_font_color="white",
                          xaxis=dict(color="white", tickangle=45), yaxis=dict(color="white"),
                          legend=dict(font=dict(color="white")))
        st.plotly_chart(fig, use_container_width=True)

    # Sekolah asal
    sekolah_counts = df["Asal_Sekolah_Tipe"].value_counts()
    fig = px.pie(values=sekolah_counts.values, names=sekolah_counts.index,
                 title="Distribusi Asal Sekolah",
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", title_font_color="white",
                      legend=dict(font=dict(color="white")))
    st.plotly_chart(fig, use_container_width=True)

# ─── Tab 3: Jurusan & Karir ───────────────────────────────────────────────────
with tab3:
    if not career_df.empty:
        # Top karir berdasarkan demand
        demand_counts = career_df["Tingkat_Permintaan_Pasar"].value_counts()
        fig = px.bar(demand_counts, title="Distribusi Tingkat Permintaan Karir",
                     color=demand_counts.values, color_continuous_scale="Sunset")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          title_font_color="white", showlegend=False,
                          xaxis=dict(color="white"), yaxis=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)

        # Scatter: gaji awal vs growth
        fig2 = px.scatter(
            career_df, x="Rata_Gaji_Awal_Juta", y="Growth_5yr_Persen",
            color="Tingkat_Permintaan_Pasar", hover_data=["Karir", "Jurusan"],
            title="Gaji Awal vs Growth 5 Tahun",
            labels={"Rata_Gaji_Awal_Juta": "Gaji Awal (jt/bln)",
                    "Growth_5yr_Persen": "Growth 5 Tahun (%)"},
            color_discrete_sequence=["#4FF78E", "#4F8EF7", "#F7E04F", "#F74F4F"],
        )
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           title_font_color="white",
                           xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
                           yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
                           legend=dict(font=dict(color="white")))
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Data karir belum tersedia.")

# ─── Tab 4: Kampus ────────────────────────────────────────────────────────────
with tab4:
    if not kampus_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            # Rating per kampus
            avg_rating = kampus_df.groupby("Kampus")["Rating_Kepuasan"].mean().sort_values(ascending=False)
            fig = px.bar(avg_rating, title="Rata-rata Rating Kepuasan per Kampus",
                         color=avg_rating.values, color_continuous_scale="Greens")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              title_font_color="white", showlegend=False,
                              xaxis=dict(color="white", tickangle=45), yaxis=dict(color="white", range=[0, 5]))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Biaya rata-rata per kampus
            avg_biaya = kampus_df.groupby("Kampus")["Biaya_Per_Semester_Juta"].mean().sort_values(ascending=False)
            fig = px.bar(avg_biaya, title="Rata-rata Biaya per Semester (juta)",
                         color=avg_biaya.values, color_continuous_scale="Reds")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              title_font_color="white", showlegend=False,
                              xaxis=dict(color="white", tickangle=45), yaxis=dict(color="white"))
            st.plotly_chart(fig, use_container_width=True)

        # Tabel lengkap
        st.markdown("#### 📋 Tabel Kampus Lengkap")
        st.dataframe(kampus_df, use_container_width=True, hide_index=True)
    else:
        st.info("Data kampus belum tersedia.")

st.divider()

# ─── Statistik Deskriptif ────────────────────────────────────────────────────
with st.expander("📈 Statistik Deskriptif Data Siswa"):
    numeric_cols = ["Nilai_Matematika", "Nilai_Bahasa_Indonesia", "Nilai_Bahasa_Inggris",
                    "Nilai_IPA", "Nilai_Fisika", "Nilai_Kimia", "Nilai_Biologi",
                    "Nilai_Ekonomi", "Kemampuan_Analitis", "Kemampuan_Kreatif",
                    "Kemampuan_Sosial", "Kemampuan_Leadership", "Skor_UN_Rata"]
    available_cols = [c for c in numeric_cols if c in df.columns]
    st.dataframe(df[available_cols].describe().round(2), use_container_width=True)

with st.expander("🔍 Preview Data Mentah (50 baris pertama)"):
    st.dataframe(df.head(50), use_container_width=True, hide_index=True)

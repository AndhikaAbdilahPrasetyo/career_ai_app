"""
Halaman Hasil Rekomendasi Jurusan
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st

st.set_page_config(page_title="Hasil Rekomendasi | AI Career Compass", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.result-card {
    background: linear-gradient(135deg, #1C2B3A, #131C27);
    border-radius: 16px; padding: 20px 24px; margin-bottom: 14px;
    border-left: 4px solid #4F8EF7;
}
.result-card.top1 { border-left-color: #F7924F; }
.result-card h3 { color: white; margin: 0 0 6px; font-size: 1.2rem; }
.rank-badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 700; margin-right: 8px;
}
.rank-1 { background: linear-gradient(135deg, #F7924F, #F7E04F); color: #000; }
.rank-other { background: rgba(79,142,247,0.2); color: #4F8EF7; }

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

st.title("🎯 Hasil Rekomendasi Jurusan")
st.divider()

# ─── Cek data siswa ───────────────────────────────────────────────────────────
if "student_data" not in st.session_state:
    st.warning("⚠️ Belum ada data profil siswa.")
    st.info("👉 Silakan isi form di halaman **Input Profil** terlebih dahulu.")
    st.stop()

data = st.session_state["student_data"]
st.markdown(f"### Hasil untuk: **{data['nama']}** | {data['Asal_Sekolah_Tipe']} | {data['Minat_Utama']}")
st.divider()

# ─── Import modules ───────────────────────────────────────────────────────────
from ml_model import predict_top_n, is_model_trained
from db_connector import get_jurusan_metadata, get_career_paths, get_kampus_info, test_connection
from visualizations import (
    chart_rekomendasi_bar, chart_radar_kemampuan,
    chart_soft_skills, chart_career_salary, format_score_color, score_badge
)

# ─── Prediksi ─────────────────────────────────────────────────────────────────
if not is_model_trained():
    st.error("❌ Model ML belum ditraining!")
    st.info("👉 Jalankan training model di halaman **Training Model** terlebih dahulu.")
    st.stop()

with st.spinner("🤖 AI sedang menganalisis profil kamu..."):
    try:
        recommendations = predict_top_n(data, n=5)
    except Exception as e:
        st.error(f"❌ Error prediksi: {e}")
        st.stop()

# Simpan ke session
st.session_state["recommendations"] = recommendations

# ─── Layout Hasil ─────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown("### 🏆 Top 5 Rekomendasi Jurusan")

    for i, rec in enumerate(recommendations):
        rank_class = "top1" if i == 0 else ""
        badge_class = "rank-1" if i == 0 else "rank-other"
        color = format_score_color(rec["score"])
        badge = score_badge(rec["score"])

        # Tampilkan indikator kecocokan Minat
        minat_match = rec.get("minat_match", False)
        minat_badge = ""
        if minat_match:
            minat_badge = '<span style="display:inline-block; padding:2px 8px; background:#4FF78E; color:#000; border-radius:10px; font-size:0.75rem; font-weight:600; margin-left:8px;">✓ Cocok Minat</span>'
        else:
            minat_badge = '<span style="display:inline-block; padding:2px 8px; background:rgba(255,255,255,0.15); color:rgba(255,255,255,0.6); border-radius:10px; font-size:0.75rem; font-weight:500; margin-left:8px;">Minat</span>'

        st.markdown(f"""
        <div class="result-card {rank_class}">
            <h3>
                <span class="rank-badge {badge_class}">#{i+1}</span>
                {rec['jurusan']}
                {minat_badge}
            </h3>
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="
                    font-size:1.8rem; font-weight:700; color:{color};
                    font-family:'JetBrains Mono', monospace;">
                    {rec['score']:.1f}%
                </div>
                <div style="color:rgba(255,255,255,0.6);">
                    Skor Kecocokan<br>
                    <span style="font-size:0.9rem;">{badge}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with right_col:
    st.plotly_chart(chart_rekomendasi_bar(recommendations), use_container_width=True)
    st.plotly_chart(chart_radar_kemampuan(data), use_container_width=True)

st.divider()

# ─── Soft Skills Visual ───────────────────────────────────────────────────────
st.markdown("### 🌟 Profil Kemampuan Diri")
st.plotly_chart(chart_soft_skills(data), use_container_width=True)

st.divider()

# ─── Detail per jurusan ───────────────────────────────────────────────────────
if test_connection():
    # Dropdown untuk memilih nomor rekomendasi
    rec_options = [f"#{i+1} - {rec['jurusan']}" for i, rec in enumerate(recommendations)]
    selected_rec_index = st.selectbox(
        "Pilih Rekomendasi Jurusan untuk Dilihat Detailnya:",
        options=range(len(recommendations)),
        format_func=lambda x: rec_options[x],
        index=0,
        key="rec_selector"
    )

    # Gunakan rekomendasi yang dipilih
    selected_rec = recommendations[selected_rec_index]
    selected_jurusan = selected_rec["jurusan"]

    st.markdown(f"### 📊 Detail: **{selected_jurusan}** (Rekomendasi #{selected_rec_index + 1} - Skor {selected_rec['score']:.1f}%)")

    tab1, tab2, tab3 = st.tabs(["📚 Info Jurusan", "💼 Karir & Gaji", "🏫 Kampus Rekomendasi"])

    with tab1:
        try:
            meta_df = get_jurusan_metadata()
            row = meta_df[meta_df["jurusan"].str.contains(selected_jurusan, case=False, na=False)]
            if not row.empty:
                r = row.iloc[0]
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Deskripsi:**\n\n{r['deskripsi']}")

                    # Tampilkan Minat dari siswa
                    student_minat = data.get("Minat_Utama", "")
                    student_sekunder = data.get("Minat_Sekunder", "")

                    # Cek cocok atau tidak
                    is_match = selected_rec.get("minat_match", False)
                    match_badge = "✅ Cocok!" if is_match else "⚠️ Perlu Pertimbangan"
                    match_color = "#4FF78E" if is_match else "#F7E04F"

                    # Tampilkan minat siswa dengan badge kecocokan per juridusan
                    # Cek minat yang cocok untuk juridusan ini
                    from ml_model import JURUSAN_MINAT_MAP
                    Jurusan_minat = JURUSAN_MINAT_MAP.get(selected_jurusan, "")

                    st.markdown(f"**Minat Saya:**")
                    if student_minat or student_sekunder:
                        # Semua minat yang diinput user
                        semua_minat_user = []
                        if student_minat:
                            semua_minat_user.append(student_minat)
                        if student_sekunder and student_sekunder != student_minat:
                            semua_minat_user.append(student_sekunder)

                        # Tampilkan masing-masing dengan badge yang sesuai
                        for m in semua_minat_user:
                            # Cek cocok atau tidak untuk juridusan ini
                            cocok = (m == Jurusan_minat)
                            badge = "✅" if cocok else "⚠️"
                            st.markdown(f"  - `{m}` {badge}")
                    else:
                        st.markdown("- (tidak diisi)")

                    # Status sudah ditampilkan di masing-masing minat di atas

                    # Tampilkan kepribadian siswa
                    student_kepribadian = data.get("Tipe_Kepribadian", "")
                    db_kepribadian = r.get("kepribadian_cocok", "")
                    is_kepribadian_match = student_kepribadian.lower() == db_kepribadian.lower() if student_kepribadian and db_kepribadian else False
                    kepribadian_badge = "✅ Cocok!" if is_kepribadian_match else "⚠️ Perlu Pertimbangan"
                    kepribadian_color = "#4FF78E" if is_kepribadian_match else "#F7E04F"

                    st.markdown(f"**Kepribadian Saya:** `{student_kepribadian}`")
                    st.markdown(f'<span style="color:{kepribadian_color}; font-weight:600;">{kepribadian_badge}</span>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**Prospek Karir:**\n\n{r['prospek_karir']}")
                    skills = [s.strip() for s in str(r['skill_dibutuhkan']).split(",")]
                    st.markdown("**Skill Dibutuhkan:**")
                    for sk in skills:
                        st.markdown(f"  - {sk}")
            else:
                st.info(f"Info detail untuk '{selected_jurusan}' belum tersedia.")
        except Exception as e:
            st.error(f"Error: {e}")

    with tab2:
        try:
            career_df = get_career_paths(selected_jurusan)
            if career_df.empty:
                all_cp = get_career_paths()
                career_df = all_cp[all_cp["Jurusan"].str.contains(selected_jurusan, case=False, na=False)]

            if not career_df.empty:
                # Slider untuk memilih jumlah karir yang ditampilkan
                num_careers = st.slider(
                    "Jumlah Karir yang Ditampilkan",
                    min_value=1,
                    max_value=min(10, len(career_df)),
                    value=min(6, len(career_df))
                )
                
                df_show = career_df.head(num_careers)
                st.plotly_chart(chart_career_salary(df_show), use_container_width=True)
                st.dataframe(
                    df_show[["Karir", "Rata_Gaji_Awal_Juta", "Rata_Gaji_Senior_Juta",
                               "Tingkat_Permintaan_Pasar", "Growth_5yr_Persen"]].rename(columns={
                        "Rata_Gaji_Awal_Juta": "Gaji Awal (jt)",
                        "Rata_Gaji_Senior_Juta": "Gaji Senior (jt)",
                        "Tingkat_Permintaan_Pasar": "Demand Pasar",
                        "Growth_5yr_Persen": "Growth 5yr (%)",
                    }),
                    use_container_width=True, hide_index=True
                )
            else:
                st.info("Data karir belum tersedia untuk jurusan ini.")
        except Exception as e:
            st.error(f"Error: {e}")

    with tab3:
        try:
            kampus_df = get_kampus_info(selected_jurusan)
            if kampus_df.empty:
                all_k = get_kampus_info()
                kampus_df = all_k[all_k["Jurusan"].str.contains(selected_jurusan, case=False, na=False)]

            if not kampus_df.empty:
                # Filter by budget if available
                budget = data.get("Budget_Kuliah", "")
                cols_show = ["Kampus", "Akreditasi", "Biaya_Per_Semester_Juta",
                             "Rating_Kepuasan", "Tipe_Kampus", "Lokasi_Kota"]
                st.dataframe(
                    kampus_df[cols_show].rename(columns={
                        "Biaya_Per_Semester_Juta": "Biaya/Sem (jt)",
                        "Rating_Kepuasan": "Rating",
                        "Tipe_Kampus": "Tipe",
                        "Lokasi_Kota": "Kota",
                    }),
                    use_container_width=True, hide_index=True
                )
            else:
                st.info("Data kampus belum tersedia untuk jurusan ini.")
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# ─── Save hasil & Export PDF ───────────────────────────────────────────────────
col_save, col_pdf = st.columns([1, 1])

with col_save:
    if st.button("💾 Simpan Hasil ke Database", use_container_width=True):
        try:
            from db_connector import save_recommendation
            rec_id = save_recommendation(data["nama"], data, recommendations)
            st.success(f"✅ Tersimpan! ID: {rec_id}")
        except Exception as e:
            st.error(f"Error menyimpan: {e}")

with col_pdf:
    # Get data for PDF
    try:
        # Ambil SEMUA info juridusan untuk setiap rekomendasi
        meta_df = get_jurusan_metadata()
        all_jurusan_info = {}
        for rec in recommendations:
            jur = rec["jurusan"]
            row = meta_df[meta_df["jurusan"].str.contains(jur, case=False, na=False)]
            if not row.empty:
                r = row.iloc[0]
                all_jurusan_info[jur] = {
                    "deskripsi": str(r.get("deskripsi", "")),
                    "prospek_karir": str(r.get("prospek_karir", "")),
                    "skill_dibutuhkan": str(r.get("skill_dibutuhkan", "")),
                }

        # Ambil SEMUA career info untuk setiap rekomendasi
        all_career_info = {}
        for rec in recommendations:
            jur = rec["jurusan"]
            career_df_perjur = get_career_paths(jur)
            if career_df_perjur.empty:
                all_cp = get_career_paths()
                career_df_perjur = all_cp[all_cp["Jurusan"].str.contains(jur, case=False, na=False)]
            if not career_df_perjur.empty:
                all_career_info[jur] = career_df_perjur

        # Campus info (dari juridusan yang dipilih di dropdown)
        campus_df = get_kampus_info(selected_jurusan)
        if not len(campus_df):
            all_k = get_kampus_info()
            campus_df = all_k[all_k["Jurusan"].str.contains(selected_jurusan, case=False, na=False)]

        # Generate PDF
        from pdf_generator import generate_recommendation_pdf
        pdf_bytes = generate_recommendation_pdf(
            student_data=data,
            recommendations=recommendations,
            all_jurusan_info=all_jurusan_info,
            all_career_info=all_career_info,
            campus_info=campus_df if len(campus_df) else None,
        )

        # Download button
        st.download_button(
            label="📄 Download PDF Laporan",
            data=pdf_bytes,
            file_name=f"Laporan_Rekomendasi_{data['nama'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Error membuat PDF: {e}")

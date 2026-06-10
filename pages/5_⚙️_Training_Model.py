"""
Halaman Training Model Machine Learning
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Training Model | AI Career Compass", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.model-card {
    background: linear-gradient(135deg, #1C2B3A, #0D1B2A);
    border: 1px solid rgba(79,142,247,0.25);
    border-radius: 16px; padding: 20px; text-align: center;
}
.model-card h3 { color: white; margin-bottom: 4px; }
.model-card .score {
    font-size: 2rem; font-weight: 700; color: #4F8EF7;
    font-family: 'JetBrains Mono', monospace;
}
.model-card .label { color: rgba(255,255,255,0.6); font-size: 0.85rem; }

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

st.title("⚙️ Training Model Machine Learning")
st.caption("Train 3 model ML: Random Forest, XGBoost, dan Neural Network (MLP)")
st.divider()

from db_connector import get_student_profiles, test_connection
from ml_model import (
    train_models, is_model_trained, get_model_comparison,
    RF_PATH, XGB_PATH, MLP_PATH, BEST_MODEL_PATH
)

if not test_connection():
    st.error("❌ Database tidak terhubung!")
    st.stop()

# ─── Status Model ─────────────────────────────────────────────────────────────
st.markdown("### 📦 Status Model")

model_status = get_model_comparison()
col1, col2, col3, col4 = st.columns(4)

for col, (name, exists) in zip([col1, col2, col3], model_status.items()):
    with col:
        status = "✅ Ada" if exists else "❌ Belum"
        st.markdown(f"""
        <div class="model-card">
            <h3>{name}</h3>
            <div class="score" style="font-size:1.5rem;">{status}</div>
        </div>
        """, unsafe_allow_html=True)

with col4:
    best_exists = os.path.exists(BEST_MODEL_PATH)
    st.markdown(f"""
    <div class="model-card" style="border-color: rgba(247,146,79,0.5);">
        <h3>🏆 Best Model</h3>
        <div class="score" style="color:#F7924F; font-size:1.5rem;">{"✅ Ada" if best_exists else "❌ Belum"}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ─── Training Section ─────────────────────────────────────────────────────────
st.markdown("### 🚀 Mulai Training")

col_info, col_btn = st.columns([2, 1])
with col_info:
    st.info("""
    **Proses Training:**
    1. Ambil data dari tabel `student_profiles` (1200 baris)
    2. Feature engineering & encoding kategorikal
    3. Split data train/test (80:20)
    4. Train 3 model: Random Forest, XGBoost, MLP
    5. Evaluasi & pilih model terbaik (F1-Score tertinggi)
    6. Simpan semua model ke folder `src/models/`
    
    ⏱️ Estimasi waktu: 1-3 menit
    """)

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    force_retrain = st.checkbox("Force retrain (timpa model lama)", value=False)
    train_btn = st.button("🚀 Mulai Training", use_container_width=True,
                          type="primary", disabled=(is_model_trained() and not force_retrain))

    if is_model_trained() and not force_retrain:
        st.caption("✅ Model sudah ada. Centang 'Force retrain' untuk melatih ulang.")

# ─── Training Execution ───────────────────────────────────────────────────────
if train_btn:
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("📥 Mengambil data dari database...")
        progress_bar.progress(10)
        df = get_student_profiles()

        if df.empty:
            st.error("❌ Data student_profiles kosong!")
            st.stop()

        status_text.text(f"✅ Data loaded: {len(df)} baris")
        progress_bar.progress(20)

        status_text.text("🔧 Preprocessing data...")
        progress_bar.progress(30)

        status_text.text("🌲 Training Random Forest...")
        progress_bar.progress(40)

        status_text.text("⚡ Training XGBoost...")
        progress_bar.progress(55)

        status_text.text("🧠 Training Neural Network (MLP)...")
        progress_bar.progress(70)

        # Actual training
        results = train_models(df)

        progress_bar.progress(90)
        status_text.text("💾 Menyimpan model...")

        progress_bar.progress(100)
        status_text.text("✅ Training selesai!")

        st.success("🎉 Training berhasil!")
        st.balloons()

        # Simpan ke session
        st.session_state["training_results"] = results

    except Exception as e:
        st.error(f"❌ Error training: {e}")
        import traceback
        with st.expander("Detail Error"):
            st.code(traceback.format_exc())

# ─── Hasil Training ───────────────────────────────────────────────────────────
if "training_results" in st.session_state:
    results = st.session_state["training_results"]
    st.divider()
    st.markdown("### 📊 Hasil Evaluasi Model")

    col1, col2, col3 = st.columns(3)
    colors = {"Random Forest": "#4F8EF7", "XGBoost": "#F7924F", "Neural Network (MLP)": "#9B4FF7"}
    best_model = max(results, key=results.get)

    for col, (name, score) in zip([col1, col2, col3], results.items()):
        with col:
            is_best = name == best_model
            border_style = "border-color: rgba(247,224,79,0.7);" if is_best else ""
            st.markdown(f"""
            <div class="model-card" style="{border_style}">
                <h3>{"🏆 " if is_best else ""}{name}</h3>
                <div class="score" style="color:{colors[name]};">{score:.4f}</div>
                <div class="label">F1-Score (Weighted)</div>
                {"<div style='color:#F7E04F; font-size:0.85rem; margin-top:4px;'>⭐ Best Model</div>" if is_best else ""}
            </div>
            """, unsafe_allow_html=True)

    # Chart perbandingan
    fig = go.Figure(go.Bar(
        x=list(results.keys()),
        y=[v * 100 for v in results.values()],
        marker=dict(
            color=[colors[k] for k in results.keys()],
            line=dict(color="rgba(255,255,255,0.2)", width=1)
        ),
        text=[f"{v*100:.2f}%" for v in results.values()],
        textposition="outside",
        textfont=dict(color="white"),
    ))

    fig.update_layout(
        title=dict(text="Perbandingan F1-Score Model", font=dict(color="white"), x=0.5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(color="white"), yaxis=dict(color="white", range=[0, 110],
                                               gridcolor="rgba(255,255,255,0.1)"),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(f"✅ **Best Model: {best_model}** dengan F1-Score = **{results[best_model]:.4f}** telah disimpan sebagai model utama.")

st.divider()

# ─── Informasi Feature Importance ────────────────────────────────────────────
if os.path.exists(RF_PATH):
    with st.expander("🔍 Feature Importance (Random Forest)"):
        try:
            import joblib
            from ml_model import FEATURE_COLS
            rf = joblib.load(RF_PATH)
            importances = pd.DataFrame({
                "Feature": FEATURE_COLS,
                "Importance": rf.feature_importances_,
            }).sort_values("Importance", ascending=False)

            fig = px.bar(importances, x="Importance", y="Feature", orientation="h",
                         title="Feature Importance",
                         color="Importance", color_continuous_scale="Blues")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              title_font_color="white",
                              xaxis=dict(color="white"), yaxis=dict(color="white"),
                              showlegend=False)
            fig.update_traces(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Tidak bisa load feature importance: {e}")

"""
Fungsi utilitas untuk visualisasi dan pemrosesan data.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


# ─── Warna tema aplikasi ─────────────────────────────────────────────────────
COLORS = {
    "primary":   "#4F8EF7",
    "secondary": "#F7924F",
    "success":   "#4FF78E",
    "warning":   "#F7E04F",
    "danger":    "#F74F4F",
    "purple":    "#9B4FF7",
    "bg":        "#0F1117",
    "card":      "#1C1F26",
}

GRADIENT_COLORS = ["#4F8EF7", "#9B4FF7", "#F7924F", "#4FF78E", "#F7E04F"]


def chart_rekomendasi_bar(recommendations: list) -> go.Figure:
    """
    Bar chart horizontal untuk top-N rekomendasi jurusan.
    recommendations: [{'jurusan': ..., 'score': ...}, ...]
    """
    df = pd.DataFrame(recommendations)
    df = df.sort_values("score", ascending=True)

    colors = [GRADIENT_COLORS[i % len(GRADIENT_COLORS)] for i in range(len(df))]

    fig = go.Figure(go.Bar(
        x=df["score"],
        y=df["jurusan"],
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color="rgba(255,255,255,0.1)", width=1)
        ),
        text=[f"{s:.1f}%" for s in df["score"]],
        textposition="outside",
        textfont=dict(size=13, color="white"),
    ))

    fig.update_layout(
        title=dict(
            text="🎯 Top Rekomendasi Jurusan",
            font=dict(size=18, color="white"),
            x=0.5,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Skor Kecocokan (%)",
            color="rgba(255,255,255,0.6)",
            gridcolor="rgba(255,255,255,0.1)",
            range=[0, max(df["score"]) * 1.2],
        ),
        yaxis=dict(color="white", tickfont=dict(size=12)),
        margin=dict(l=20, r=60, t=60, b=40),
        height=320,
        showlegend=False,
    )
    return fig


def chart_radar_kemampuan(input_data: dict) -> go.Figure:
    """Radar chart untuk visualisasi kemampuan siswa."""
    categories = [
        "Matematika", "Bahasa Inggris", "IPA",
        "Fisika", "Kimia", "Biologi", "Ekonomi"
    ]
    values = [
        input_data.get("Nilai_Matematika", 0),
        input_data.get("Nilai_Bahasa_Inggris", 0),
        input_data.get("Nilai_IPA", 0),
        input_data.get("Nilai_Fisika", 0),
        input_data.get("Nilai_Kimia", 0),
        input_data.get("Nilai_Biologi", 0),
        input_data.get("Nilai_Ekonomi", 0),
    ]

    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(79, 142, 247, 0.2)",
        line=dict(color=COLORS["primary"], width=2),
        marker=dict(size=6, color=COLORS["primary"]),
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(color="rgba(255,255,255,0.6)", tickfont=dict(size=11)),
            radialaxis=dict(
                visible=True, range=[0, 100],
                color="rgba(255,255,255,0.4)",
                gridcolor="rgba(255,255,255,0.1)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        title=dict(
            text="📊 Profil Nilai Akademik",
            font=dict(size=16, color="white"),
            x=0.5,
        ),
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=False,
    )
    return fig


def chart_soft_skills(input_data: dict) -> go.Figure:
    """Gauge charts untuk soft skills."""
    skills = {
        "Analitis": input_data.get("Kemampuan_Analitis", 5),
        "Kreatif":  input_data.get("Kemampuan_Kreatif", 5),
        "Sosial":   input_data.get("Kemampuan_Sosial", 5),
        "Leadership": input_data.get("Kemampuan_Leadership", 5),
    }

    fig = go.Figure()
    for i, (skill, val) in enumerate(skills.items()):
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=val,
            title=dict(text=skill, font=dict(color="white", size=13)),
            number=dict(font=dict(color="white", size=20)),
            gauge=dict(
                axis=dict(range=[0, 10], tickcolor="white"),
                bar=dict(color=GRADIENT_COLORS[i]),
                bgcolor="rgba(255,255,255,0.05)",
                bordercolor="rgba(255,255,255,0.1)",
            ),
            domain=dict(row=0, column=i),
        ))

    fig.update_layout(
        grid=dict(rows=1, columns=4, pattern="independent"),
        paper_bgcolor="rgba(0,0,0,0)",
        height=180,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig


def chart_career_salary(career_df: pd.DataFrame) -> go.Figure:
    """Bar chart perbandingan gaji awal vs senior untuk beberapa karir."""
    if career_df.empty:
        return go.Figure()

    df = career_df.head(8)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Gaji Awal",
        x=df["Karir"],
        y=df["Rata_Gaji_Awal_Juta"],
        marker_color=COLORS["primary"],
        text=[f"Rp {v:.1f}jt" for v in df["Rata_Gaji_Awal_Juta"]],
        textposition="auto",
    ))
    fig.add_trace(go.Bar(
        name="Gaji Senior",
        x=df["Karir"],
        y=df["Rata_Gaji_Senior_Juta"],
        marker_color=COLORS["secondary"],
        text=[f"Rp {v:.1f}jt" for v in df["Rata_Gaji_Senior_Juta"]],
        textposition="auto",
    ))

    fig.update_layout(
        barmode="group",
        title=dict(text="💰 Perbandingan Gaji (Juta/Bulan)", font=dict(color="white"), x=0.5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(color="rgba(255,255,255,0.6)", tickangle=-30),
        yaxis=dict(color="rgba(255,255,255,0.6)", gridcolor="rgba(255,255,255,0.1)"),
        legend=dict(font=dict(color="white")),
        height=350,
        margin=dict(b=100),
    )
    return fig


def chart_distribusi_jurusan(df_students: pd.DataFrame) -> go.Figure:
    """Pie chart distribusi jurusan dari data training."""
    counts = df_students["Jurusan_Label"].value_counts().head(12)
    fig = px.pie(
        values=counts.values,
        names=counts.index,
        title="Distribusi Jurusan (Data Training)",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(color="white"),
        legend=dict(font=dict(color="white")),
    )
    return fig


def format_score_color(score: float) -> str:
    """Kembalikan warna sesuai skor kecocokan."""
    if score >= 70:
        return "#4FF78E"  # Hijau
    elif score >= 50:
        return "#F7E04F"  # Kuning
    else:
        return "#F74F4F"  # Merah


def score_badge(score: float) -> str:
    """Label tekstual untuk skor."""
    if score >= 70:
        return "🟢 Sangat Cocok"
    elif score >= 50:
        return "🟡 Cukup Cocok"
    else:
        return "🔴 Kurang Cocok"

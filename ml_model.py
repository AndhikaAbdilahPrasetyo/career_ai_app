"""
Modul Machine Learning untuk rekomendasi jurusan.
- Training model Random Forest, XGBoost, Neural Network (MLP)
- Prediksi top-N jurusan + skor kecocokan
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
from xgboost import XGBClassifier

# ─── Path untuk menyimpan model ──────────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(__file__))
RF_PATH   = os.path.join(MODEL_DIR, "random_forest.pkl")
XGB_PATH  = os.path.join(MODEL_DIR, "xgboost.pkl")
MLP_PATH  = os.path.join(MODEL_DIR, "mlp.pkl")
SCALER_PATH  = os.path.join(MODEL_DIR, "scaler.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")
BEST_MODEL_PATH = os.path.join(MODEL_DIR, "best_model.pkl")

# ─── Kolom fitur yang digunakan ───────────────────────────────────────────────
FEATURE_COLS = [
    "Nilai_Matematika", "Nilai_Bahasa_Indonesia", "Nilai_Bahasa_Inggris",
    "Nilai_IPA", "Nilai_Fisika", "Nilai_Kimia", "Nilai_Biologi",
    "Nilai_Ekonomi", "Nilai_Geografi", "Nilai_Sosiologi",
    "Kemampuan_Analitis", "Kemampuan_Kreatif", "Kemampuan_Sosial",
    "Kemampuan_Leadership",
    # Encoded categorical
    "Minat_Utama_enc", "Minat_Sekunder_enc",
    "Tipe_Kepribadian_enc", "Asal_Sekolah_Tipe_enc",
]
TARGET_COL = "Jurusan_Label"

# ─── Encoder untuk kolom kategorikal ─────────────────────────────────────────
CAT_ENCODERS: dict = {}

MINAT_LIST = [
    "Teknologi & Komputer", "Bisnis & Keuangan", "Hukum & Sosial",
    "Kesehatan & Medis", "Sains & Penelitian", "Teknik & Konstruksi",
    "Seni & Desain", "Pendidikan & Pengajaran",
]
KEPRIBADIAN_LIST = ["Analyst", "Diplomat", "Sentinel", "Explorer"]
SEKOLAH_LIST = ["IPA", "IPS", "SMK-TI", "SMK-Bisnis", "SMK-Kesehatan"]


def _encode_categorical(df: pd.DataFrame) -> pd.DataFrame:
    """Encode kolom kategorikal menjadi integer."""
    df = df.copy()
    df["Minat_Utama_enc"] = pd.Categorical(
        df["Minat_Utama"], categories=MINAT_LIST
    ).codes
    df["Minat_Sekunder_enc"] = pd.Categorical(
        df.get("Minat_Sekunder", df["Minat_Utama"]), categories=MINAT_LIST
    ).codes
    df["Tipe_Kepribadian_enc"] = pd.Categorical(
        df["Tipe_Kepribadian"], categories=KEPRIBADIAN_LIST
    ).codes
    df["Asal_Sekolah_Tipe_enc"] = pd.Categorical(
        df["Asal_Sekolah_Tipe"], categories=SEKOLAH_LIST
    ).codes
    return df


def prepare_data(df: pd.DataFrame):
    """Siapkan data training: encode, bersihkan, kembalikan X dan y."""
    df = _encode_categorical(df)
    df = df.dropna(subset=FEATURE_COLS + [TARGET_COL])

    X = df[FEATURE_COLS].astype(float)
    y = df[TARGET_COL]
    return X, y


def train_models(df: pd.DataFrame) -> dict:
    """
    Latih 3 model dan simpan yang terbaik.
    Kembalikan dict berisi nama model → score.
    """
    X, y = prepare_data(df)

    # Label encoder untuk target
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    joblib.dump(le, ENCODER_PATH)

    # Scaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, SCALER_PATH)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    results = {}

    # 1. Random Forest
    rf = RandomForestClassifier(n_estimators=200, max_depth=15,
                                 random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_score = f1_score(y_test, rf.predict(X_test), average="weighted")
    joblib.dump(rf, RF_PATH)
    results["Random Forest"] = rf_score

    # 2. XGBoost
    xgb = XGBClassifier(n_estimators=200, max_depth=6,
                          learning_rate=0.1, eval_metric="mlogloss",
                          random_state=42, n_jobs=-1, verbosity=0)
    xgb.fit(X_train, y_train)
    xgb_score = f1_score(y_test, xgb.predict(X_test), average="weighted")
    joblib.dump(xgb, XGB_PATH)
    results["XGBoost"] = xgb_score

    # 3. MLP (Neural Network)
    mlp = MLPClassifier(hidden_layer_sizes=(256, 128, 64),
                         max_iter=300, random_state=42,
                         early_stopping=True, validation_fraction=0.1)
    mlp.fit(X_train, y_train)
    mlp_score = f1_score(y_test, mlp.predict(X_test), average="weighted")
    joblib.dump(mlp, MLP_PATH)
    results["Neural Network (MLP)"] = mlp_score

    # Pilih best model
    best_name = max(results, key=results.get)
    best_models = {"Random Forest": rf, "XGBoost": xgb, "Neural Network (MLP)": mlp}
    joblib.dump(best_models[best_name], BEST_MODEL_PATH)

    return results


def load_models():
    """Load model dan artefak. Raise jika belum ditraining."""
    if not os.path.exists(BEST_MODEL_PATH):
        raise FileNotFoundError("Model belum ditraining. Jalankan training terlebih dahulu.")
    model   = joblib.load(BEST_MODEL_PATH)
    scaler  = joblib.load(SCALER_PATH)
    encoder = joblib.load(ENCODER_PATH)
    return model, scaler, encoder


def predict_top_n(input_dict: dict, n: int = 5) -> list:
    """
    Hitung skor kecocokan berdasarkan nilai input siswa secara langsung.
    Skor = Nilai Akademik (40%) + Minat (30%) + Kepribadian (15%) + Soft Skills (15%)
    """
    # Ambil data dari input
    nilai_mtk = input_dict.get("Nilai_Matematika", 0)
    nilai_indo = input_dict.get("Nilai_Bahasa_Indonesia", 0)
    nilai_eng = input_dict.get("Nilai_Bahasa_Inggris", 0)
    nilai_ipa = input_dict.get("Nilai_IPA", 0)
    nilai_fisika = input_dict.get("Nilai_Fisika", 0)
    nilai_kimia = input_dict.get("Nilai_Kimia", 0)
    nilai_bio = input_dict.get("Nilai_Biologi", 0)
    nilai_eko = input_dict.get("Nilai_Ekonomi", 0)
    nilai_geo = input_dict.get("Nilai_Geografi", 0)
    nilai_sos = input_dict.get("Nilai_Sosiologi", 0)

    skill_analitis = input_dict.get("Kemampuan_Analitis", 5)
    skill_kreatif = input_dict.get("Kemampuan_Kreatif", 5)
    skill_sosial = input_dict.get("Kemampuan_Sosial", 5)
    skill_leadership = input_dict.get("Kemampuan_Leadership", 5)

    minat_utama = input_dict.get("Minat_Utama", MINAT_LIST[0])
    minat_sek = input_dict.get("Minat_Sekunder", minat_utama)
    kepribadian = input_dict.get("Tipe_Kepribadian", KEPRIBADIAN_LIST[0])

    # Mapping Minat ke Jurusan
    MINAT_JURUSAN_MAP = {
        "Teknologi & Komputer": ["Informatika", "Teknik Komputer", "Sistem Informasi", "Teknik Elektro"],
        "Bisnis & Keuangan": ["Akuntansi", "Manajemen", "Ekonomi", "Keuangan", "Bisnis Digital"],
        "Hukum & Sosial": ["Hukum", "Ilmu Komunikasi", "Hubungan Internasional", "Sosiologi", "Ilmu Politik"],
        "Kesehatan & Medis": ["Kedokteran", "Kedokteran Gigi", "Farmasi", "Keperawatan"],
        "Sains & Penelitian": ["Fisika", "Kimia", "Biologi", "Matematika"],
        "Teknik & Konstruksi": ["Teknik Sipil", "Arsitektur", "Teknik Mesin", "Teknik Industri"],
        "Seni & Desain": ["Desain Komunikasi Visual", "Seni Rupa", "Desain Interior", "Film"],
        "Pendidikan & Pengajaran": ["Pendidikan Guru", "Pendidikan Bahasa", "Bimbingan Konseling"],
    }

    # Mapping Jurusan ke Minat yang cocok
    JURUSAN_MINAT_MAP = {
        "Informatika": "Teknologi & Komputer",
        "Teknik Komputer": "Teknologi & Komputer",
        "Sistem Informasi": "Teknologi & Komputer",
        "Teknik Elektro": "Teknologi & Komputer",
        "Akuntansi": "Bisnis & Keuangan",
        "Manajemen": "Bisnis & Keuangan",
        "Ekonomi": "Bisnis & Keuangan",
        "Keuangan": "Bisnis & Keuangan",
        "Bisnis Digital": "Bisnis & Keuangan",
        "Hukum": "Hukum & Sosial",
        "Ilmu Komunikasi": "Hukum & Sosial",
        "Hubungan Internasional": "Hukum & Sosial",
        "Sosiologi": "Hukum & Sosial",
        "Ilmu Politik": "Hukum & Sosial",
        "Kedokteran": "Kesehatan & Medis",
        "Kedokteran Gigi": "Kesehatan & Medis",
        "Farmasi": "Kesehatan & Medis",
        "Keperawatan": "Kesehatan & Medis",
        "Fisika": "Sains & Penelitian",
        "Kimia": "Sains & Penelitian",
        "Biologi": "Sains & Penelitian",
        "Matematika": "Sains & Penelitian",
        "Teknik Sipil": "Teknik & Konstruksi",
        "Arsitektur": "Teknik & Konstruksi",
        "Teknik Mesin": "Teknik & Konstruksi",
        "Teknik Industri": "Teknik & Konstruksi",
        "Desain Komunikasi Visual": "Seni & Desain",
        "Seni Rupa": "Seni & Desain",
        "Desain Interior": "Seni & Desain",
        "Film": "Seni & Desain",
        "Pendidikan Guru": "Pendidikan & Pengajaran",
        "Pendidikan Bahasa": "Pendidikan & Pengajaran",
        "Bimbingan Konseling": "Pendidikan & Pengajaran",
    }

    # Mapping Jurusan ke mata pelajaran yang relevan (bobot lebih tinggi)
    JURUSAN_SUBJECTS = {
        "Informatika": ["Nilai_Matematika", "Nilai_Bahasa_Inggris", "Nilai_Fisika"],
        "Teknik Komputer": ["Nilai_Matematika", "Nilai_Fisika", "Nilai_Kimia"],
        "Sistem Informasi": ["Nilai_Matematika", "Nilai_Bahasa_Indonesia", "Nilai_Ekonomi"],
        "Teknik Elektro": ["Nilai_Matematika", "Nilai_Fisika", "Nilai_Kimia"],
        "Akuntansi": ["Nilai_Matematika", "Nilai_Ekonomi", "Nilai_Bahasa_Indonesia"],
        "Manajemen": ["Nilai_Ekonomi", "Nilai_Bahasa_Indonesia", "Nilai_Matematika"],
        "Ekonomi": ["Nilai_Ekonomi", "Nilai_Matematika", "Nilai_Bahasa_Indonesia"],
        "Keuangan": ["Nilai_Matematika", "Nilai_Ekonomi", "Nilai_Bahasa_Inggris"],
        "Bisnis Digital": ["Nilai_Matematika", "Nilai_Bahasa_Inggris", "Nilai_Ekonomi"],
        "Hukum": ["Nilai_Bahasa_Indonesia", "Nilai_Sosiologi", "Nilai_Geografi"],
        "Ilmu Komunikasi": ["Nilai_Bahasa_Indonesia", "Nilai_Bahasa_Inggris", "Nilai_Sosiologi"],
        "Hubungan Internasional": ["Nilai_Bahasa_Inggris", "Nilai_Bahasa_Indonesia", "Nilai_Sosiologi"],
        "Sosiologi": ["Nilai_Sosiologi", "Nilai_Geografi", "Nilai_Bahasa_Indonesia"],
        "Ilmu Politik": ["Nilai_Sosiologi", "Nilai_Geografi", "Nilai_Bahasa_Indonesia"],
        "Kedokteran": ["Nilai_Biologi", "Nilai_Kimia", "Nilai_Fisika"],
        "Kedokteran Gigi": ["Nilai_Biologi", "Nilai_Kimia", "Nilai_Fisika"],
        "Farmasi": ["Nilai_Kimia", "Nilai_Biologi", "Nilai_Fisika"],
        "Keperawatan": ["Nilai_Biologi", "Nilai_Kimia", "Nilai_IPA"],
        "Fisika": ["Nilai_Fisika", "Nilai_Matematika", "Nilai_Kimia"],
        "Kimia": ["Nilai_Kimia", "Nilai_Biologi", "Nilai_Fisika"],
        "Biologi": ["Nilai_Biologi", "Nilai_Kimia", "Nilai_Fisika"],
        "Matematika": ["Nilai_Matematika", "Nilai_Fisika", "Nilai_Bahasa_Inggris"],
        "Teknik Sipil": ["Nilai_Matematika", "Nilai_Fisika", "Nilai_Geografi"],
        "Arsitektur": ["Nilai_Fisika", "Nilai_Matematika", "Nilai_Geografi"],
        "Teknik Mesin": ["Nilai_Matematika", "Nilai_Fisika", "Nilai_Kimia"],
        "Teknik Industri": ["Nilai_Matematika", "Nilai_Ekonomi", "Nilai_Fisika"],
        "Desain Komunikasi Visual": ["Nilai_Biologi", "Nilai_Bahasa_Indonesia", "Nilai_Bahasa_Inggris"],
        "Seni Rupa": ["Nilai_Biologi", "Nilai_Bahasa_Indonesia", "Nilai_Sosiologi"],
        "Desain Interior": ["Nilai_Fisika", "Nilai_Geografi", "Nilai_Biologi"],
        "Film": ["Nilai_Bahasa_Indonesia", "Nilai_Bahasa_Inggris", "Nilai_Sosiologi"],
        "Pendidikan Guru": ["Nilai_Bahasa_Indonesia", "Nilai_Biologi", "Nilai_Sosiologi"],
        "Pendidikan Bahasa": ["Nilai_Bahasa_Indonesia", "Nilai_Bahasa_Inggris", "Nilai_Sosiologi"],
        "Bimbangan Konseling": ["Nilai_Sosiologi", "Nilai_Bahasa_Indonesia", "Nilai_Biologi"],
    }

    # Mapping Jurusan ke soft skill yang relevan
    JURUSAN_SKILLS = {
        "Informatika": ["Kemampuan_Analitis", "Kemampuan_Kreatif"],
        "Teknik Komputer": ["Kemampuan_Analitis", "Kemampuan_Kreatif"],
        "Sistem Informasi": ["Kemampuan_Analitis", "Kemampuan_Sosial"],
        "Teknik Elektro": ["Kemampuan_Analitis", "Kemampuan_Leadership"],
        "Akuntansi": ["Kemampuan_Analitis", "Kemampuan_Sosial"],
        "Manajemen": ["Kemampuan_Leadership", "Kemampuan_Sosial"],
        "Ekonomi": ["Kemampuan_Analitis", "Kemampuan_Sosial"],
        "Keuangan": ["Kemampuan_Analitis", "Kemampuan_Kreatif"],
        "Bisnis Digital": ["Kemampuan_Kreatif", "Kemampuan_Sosial"],
        "Hukum": ["Kemampuan_Analitis", "Kemampuan_Sosial"],
        "Ilmu Komunikasi": ["Kemampuan_Sosial", "Kemampuan_Kreatif"],
        "Hubungan Internasional": ["Kemampuan_Sosial", "Kemampuan_Leadership"],
        "Sosiologi": ["Kemampuan_Sosial", "Kemampuan_Kreatif"],
        "Ilmu Politik": ["Kemampuan_Leadership", "Kemampuan_Sosial"],
        "Kedokteran": ["Kemampuan_Analitis", "Kemampuan_Sosial"],
        "Kedokteran Gigi": ["Kemampuan_Analitis", "Kemampuan_Kreatif"],
        "Farmasi": ["Kemampuan_Analitis", "Kemampuan_Kreatif"],
        "Keperawatan": ["Kemampuan_Sosial", "Kemampuan_Leadership"],
        "Fisika": ["Kemampuan_Analitis", "Kemampuan_Kreatif"],
        "Kimia": ["Kemampuan_Analitis", "Kemampuan_Kreatif"],
        "Biologi": ["Kemampuan_Analitis", "Kemampuan_Kreatif"],
        "Matematika": ["Kemampuan_Analitis", "Kemampuan_Kreatif"],
        "Teknik Sipil": ["Kemampuan_Analitis", "Kemampuan_Leadership"],
        "Arsitektur": ["Kemampuan_Kreatif", "Kemampuan_Analitis"],
        "Teknik Mesin": ["Kemampuan_Analitis", "Kemampuan_Kreatif"],
        "Teknik Industri": ["Kemampuan_Leadership", "Kemampuan_Analitis"],
        "Desain Komunikasi Visual": ["Kemampuan_Kreatif", "Kemampuan_Sosial"],
        "Seni Rupa": ["Kemampuan_Kreatif", "Kemampuan_Analitis"],
        "Desain Interior": ["Kemampuan_Kreatif", "Kemampuan_Analitis"],
        "Film": ["Kemampuan_Kreatif", "Kemampuan_Sosial"],
        "Pendidikan Guru": ["Kemampuan_Sosial", "Kemampuan_Kreatif"],
        "Pendidikan Bahasa": ["Kemampuan_Sosial", "Kemampuan_Kreatif"],
        "Bimbingan Konseling": ["Kemampuan_Sosial", "Kemampuan_Leadership"],
    }

    # Mapping Kepribadian ke Jurusan yang cocok
    KEPRIBADIAN_JURUSAN_MAP = {
        "Analyst": ["Informatika", "Fisika", "Kimia", "Biologi", "Matematika", "Kedokteran", "Farmasi"],
        "Diplomat": ["Hukum", "Ilmu Komunikasi", "Hubungan Internasional", "Pendidikan Guru", "Bimbingan Konseling"],
        "Sentinel": ["Akuntansi", "Manajemen", "Teknik Sipil", "Teknik Mesin", "Teknik Elektro"],
        "Explorer": ["Desain Komunikasi Visual", "Seni Rupa", "Film", "Arsitektur", "Bisnis Digital"],
    }

    # Ambil semua jurusan dari database jika memungkinkan, fallback ke list default
    try:
        _, _, encoder = load_models()
        all_jurusans = list(encoder.classes_)
    except:
        # Fallback ke list default jika model belum ada
        all_jurusans = [
            "Informatika", "Teknik Komputer", "Sistem Informasi", "Teknik Elektro",
            "Akuntansi", "Manajemen", "Ekonomi", "Keuangan", "Bisnis Digital",
            "Hukum", "Ilmu Komunikasi", "Hubungan Internasional", "Sosiologi", "Ilmu Politik",
            "Kedokteran", "Kedokteran Gigi", "Farmasi", "Keperawatan",
            "Fisika", "Kimia", "Biologi", "Matematika",
            "Teknik Sipil", "Arsitektur", "Teknik Mesin", "Teknik Industri",
            "Desain Komunikasi Visual", "Seni Rupa", "Desain Interior", "Film",
            "Pendidikan Guru", "Pendidikan Bahasa", "Bimbingan Konseling",
        ]

    def _calculate_jurusan_score(jurusan: str) -> dict:
        """Hitung skor untuk satu jurusan berdasarkan input siswa."""
        # 1. Nilai Akademik (40%)
        subject_cols = JURUSAN_SUBJECTS.get(jurusan, ["Nilai_Matematika", "Nilai_Bahasa_Indonesia", "Nilai_IPA"])
        nilai_total = 0
        for col in subject_cols:
            nilai_total += input_dict.get(col, 0)
        avg_nilai = nilai_total / len(subject_cols) if subject_cols else 0
        score_nilai = (avg_nilai / 100) * 40  # Maks 40 poin

        # 2. Minat (30%)
        score_minat = 0
        minat_jurusan = JURUSAN_MINAT_MAP.get(jurusan, "")
        is_minat_matched = False

        if minat_jurusan == minat_utama:
            score_minat = 30
            is_minat_matched = True
        elif minat_jurusan == minat_sek:
            score_minat = 15
            is_minat_matched = True
        elif minat_utama == minat_sek:
            # Jika minat utama sama dengan sekunder, berikan 20 poin
            score_minat = 20
            is_minat_matched = True

        # 3. Kepribadian (15%)
        score_kepribadian = 0
        matched_kepribadians = KEPRIBADIAN_JURUSAN_MAP.get(kepribadian, [])
        if any(j.lower() in jurusan.lower() for j in matched_kepribadians):
            score_kepribadian = 15

        # 4. Soft Skills (15%)
        skill_cols = JURUSAN_SKILLS.get(jurusan, ["Kemampuan_Analitis", "Kemampuan_Kreatif"])
        skill_total = 0
        for col in skill_cols:
            skill_total += input_dict.get(col, 5)
        avg_skill = skill_total / len(skill_cols) if skill_cols else 5
        score_skill = (avg_skill / 10) * 15  # Maks 15 poin (karena skala 1-10)

        # Total skor
        total_score = score_nilai + score_minat + score_kepribadian + score_skill

        return {
            "jurusan": jurusan,
            "score": round(total_score, 1),
            "score_nilai": round(score_nilai, 1),
            "score_minat": round(score_minat, 1),
            "score_kepribadian": round(score_kepribadian, 1),
            "score_skill": round(score_skill, 1),
            "minat_match": is_minat_matched,
        }

    # Hitung skor untuk setiap jurusan
    all_scores = []
    for j in all_jurusans:
        result = _calculate_jurusan_score(j)
        all_scores.append(result)

    # Urutkan berdasarkan skor total
    all_scores.sort(key=lambda x: x["score"], reverse=True)

    # Ambil top N
    recommendations = all_scores[:n]

    return recommendations


def is_model_trained() -> bool:
    return os.path.exists(BEST_MODEL_PATH)


def get_model_comparison() -> dict:
    """Load semua model dan kembalikan nama file yang ada."""
    results = {}
    for name, path in [("Random Forest", RF_PATH), ("XGBoost", XGB_PATH), ("Neural Network (MLP)", MLP_PATH)]:
        results[name] = os.path.exists(path)
    return results

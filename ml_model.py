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
    input_dict: dict berisi nilai & info siswa (key = nama kolom asli)
    Kembalikan list of dict: [{'jurusan': ..., 'score': ...}, ...]
    """
    model, scaler, encoder = load_models()

    # Buat dataframe dari input
    row = {col: 0 for col in FEATURE_COLS}

    # Nilai akademik
    for col in [
        "Nilai_Matematika", "Nilai_Bahasa_Indonesia", "Nilai_Bahasa_Inggris",
        "Nilai_IPA", "Nilai_Fisika", "Nilai_Kimia", "Nilai_Biologi",
        "Nilai_Ekonomi", "Nilai_Geografi", "Nilai_Sosiologi",
        "Kemampuan_Analitis", "Kemampuan_Kreatif",
        "Kemampuan_Sosial", "Kemampuan_Leadership",
    ]:
        row[col] = input_dict.get(col, 0)

    # Encode categorical
    minat_utama = input_dict.get("Minat_Utama", MINAT_LIST[0])
    minat_sek   = input_dict.get("Minat_Sekunder", minat_utama)
    kepribadian = input_dict.get("Tipe_Kepribadian", KEPRIBADIAN_LIST[0])
    sekolah     = input_dict.get("Asal_Sekolah_Tipe", SEKOLAH_LIST[0])

    row["Minat_Utama_enc"] = MINAT_LIST.index(minat_utama) if minat_utama in MINAT_LIST else 0
    row["Minat_Sekunder_enc"] = MINAT_LIST.index(minat_sek) if minat_sek in MINAT_LIST else 0
    row["Tipe_Kepribadian_enc"] = KEPRIBADIAN_LIST.index(kepribadian) if kepribadian in KEPRIBADIAN_LIST else 0
    row["Asal_Sekolah_Tipe_enc"] = SEKOLAH_LIST.index(sekolah) if sekolah in SEKOLAH_LIST else 0

    X = np.array([[row[c] for c in FEATURE_COLS]], dtype=float)
    X_scaled = scaler.transform(X)

    # Dapatkan probabilitas untuk setiap kelas
    proba = model.predict_proba(X_scaled)[0]
    classes = encoder.classes_

    # Minat dari siswa
    minat_utama = input_dict.get("Minat_Utama", MINAT_LIST[0])
    minat_sek = input_dict.get("Minat_Sekunder", minat_utama)

    # Mapping Minat ke Jurusan yang cocok
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

    def _calculate_minat_boost(jurr: str, minat_utama: str, minat_sekunder: str = None) -> tuple:
        """Hitung bonus dan cek kecocokan berdasarkan Minat."""
        bonus = 0  # Bonus dalam poin (0-30)
        is_matched = False
        j_lower = jurr.lower()

        # Cek kecocokan utama
        cocok_jurusans = MINAT_JURUSAN_MAP.get(minat_utama, [])
        for j in cocok_jurusans:
            if j.lower() in j_lower:
                bonus = 30  # Bonus 30 poin
                is_matched = True
                break

        # Cek sekunder jika tidak cocok dengan utama
        if not is_matched and minat_sekunder:
            cocok_jurusans = MINAT_JURUSAN_MAP.get(minat_sekunder, [])
            for j in cocok_jurusans:
                if j.lower() in j_lower:
                    bonus = 15  # Bonus 15 poin
                    is_matched = True
                    break

        return bonus, is_matched

    # Hitung skor yang disesuaikan dengan Minat
    adjusted_scores = []
    for idx, p in enumerate(proba):
        universitas = classes[idx]
        bonus, is_matched = _calculate_minat_boost(universitas, minat_utama, minat_sek)
        # Skor dalam %, lalu tambahkan bonus (maks 100 + 30 = 130, lalu di-clamp ke 100)
        base_score = float(p) * 100  # Konversi ke %
        adjusted_score = min(100, base_score + bonus)  # clamp ke max 100%
        adjusted_scores.append({
            "idx": idx,
            "score": p,
            "adjusted_score": adjusted_score,
            "base_score": base_score,
            "bonus": bonus,
            "jurusan": classes[idx],
            "is_minat_matched": is_matched
        })

    # Urutkan berdasarkan adjusted score
    adjusted_scores.sort(key=lambda x: x["adjusted_score"], reverse=True)

    # Ambil top N
    recommendations = []
    for item in adjusted_scores[:n]:
        recommendations.append({
            "jurusan": item["jurusan"],
            "score": round(item["adjusted_score"], 1),
            "base_score": round(item["base_score"], 1),
            "bonus": item["bonus"],
            "minat_match": item["is_minat_matched"],
        })

    return recommendations


def is_model_trained() -> bool:
    return os.path.exists(BEST_MODEL_PATH)


def get_model_comparison() -> dict:
    """Load semua model dan kembalikan nama file yang ada."""
    results = {}
    for name, path in [("Random Forest", RF_PATH), ("XGBoost", XGB_PATH), ("Neural Network (MLP)", MLP_PATH)]:
        results[name] = os.path.exists(path)
    return results

"""
Modul koneksi dan query ke MySQL Database
career_recommendation_db
"""
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Konfigurasi Database ────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "career_recommendation_db"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "charset":  "utf8mb4",
    "use_unicode": True,
}


def get_connection():
    """Buat koneksi baru ke MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        raise ConnectionError(f"Gagal konek ke database: {e}")


def query_df(sql: str, params=None) -> pd.DataFrame:
    """Jalankan query SELECT dan kembalikan sebagai DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql(sql, conn, params=params)
        return df
    finally:
        conn.close()


def execute(sql: str, params=None):
    """Jalankan query INSERT / UPDATE / DELETE."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


# ─── Query Helper Functions ───────────────────────────────────────────────────

def get_student_profiles() -> pd.DataFrame:
    return query_df("SELECT * FROM student_profiles")


def get_jurusan_metadata() -> pd.DataFrame:
    return query_df("SELECT * FROM jurusan_metadata")


def get_career_paths(jurusan: str = None) -> pd.DataFrame:
    if jurusan:
        return query_df(
            "SELECT * FROM career_path WHERE Jurusan = %s", params=(jurusan,)
        )
    return query_df("SELECT * FROM career_path")


def get_kampus_info(jurusan: str = None) -> pd.DataFrame:
    if jurusan:
        return query_df(
            "SELECT * FROM jurusan_kampus_info WHERE Jurusan = %s ORDER BY Rating_Kepuasan DESC",
            params=(jurusan,),
        )
    return query_df("SELECT * FROM jurusan_kampus_info")


def get_compatibility_scores() -> pd.DataFrame:
    return query_df("SELECT * FROM compatibility_scores")


def get_all_jurusan() -> list:
    df = query_df("SELECT DISTINCT Jurusan_Label FROM student_profiles ORDER BY Jurusan_Label")
    return df["Jurusan_Label"].tolist()


def save_recommendation(student_name: str, input_data: dict, results: list):
    """
    Simpan hasil rekomendasi ke tabel recommendations (opsional).
    results: list of dict dengan key 'jurusan' dan 'score'
    """
    # Untuk simplisitas, simpan ke tabel sederhana jika ada
    # Jika belum ada tabelnya, buat dulu
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_recommendations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(100),
                input_json TEXT,
                result_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        import json
        cursor.execute(
            "INSERT INTO saved_recommendations (student_name, input_json, result_json) VALUES (%s, %s, %s)",
            (student_name, json.dumps(input_data, ensure_ascii=False),
             json.dumps(results, ensure_ascii=False))
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_saved_recommendations(limit: int = 20) -> pd.DataFrame:
    return query_df(
        f"SELECT * FROM saved_recommendations ORDER BY created_at DESC LIMIT {limit}"
    )


def test_connection() -> bool:
    try:
        conn = get_connection()
        conn.close()
        return True
    except:
        return False

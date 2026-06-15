"""
Modul untuk generate PDF laporan rekomendasi jurusan.
"""
import os
from datetime import datetime
from fpdf import FPDF


def generate_recommendation_pdf(
    student_data: dict,
    recommendations: list,
    all_jurusan_info: dict = None,
    all_career_info: dict = None,
    campus_info: list = None,
) -> bytes:
    """
    Generate PDF laporan rekomendasi jurusan.
    Returns bytes dari PDF.
    """
    pdf = PDF()
    pdf.add_page()

    # Colors
    PRIMARY_COLOR = (79, 142, 247)  # Blue
    ACCENT_COLOR = (247, 146, 79)   # Orange

    # Header
    pdf.set_fill_color(*PRIMARY_COLOR)
    pdf.rect(0, 0, 210, 40, "F")
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 25, "Laporan Rekomendasi Jurusan", ln=True, align="C")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, "AI Career Compass", ln=True, align="C")
    pdf.ln(15)

    # Reset text color
    pdf.set_text_color(0, 0, 0)

    # Tanggal
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 8, f"Tanggal: {datetime.now().strftime('%d %B %Y')}", ln=True, align="R")
    pdf.ln(5)

    # ─── Bagian 1: Data Siswa ──────────────────────────────────────────────
    pdf.set_font("helvetica", "B", 14)
    pdf.set_fill_color(*PRIMARY_COLOR)
    pdf.cell(0, 10, "1. Data Profil Siswa", ln=True, fill=True)
    pdf.ln(3)

    pdf.set_font("helvetica", "B", 11)
    pdf.cell(50, 8, "Nama:")
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, student_data.get("nama", "-"), ln=True)

    pdf.set_font("helvetica", "B", 11)
    pdf.cell(50, 8, "Jenis Kelamin:")
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, student_data.get("jenis_kelamin", "-"), ln=True)

    pdf.set_font("helvetica", "B", 11)
    pdf.cell(50, 8, "Asal Sekolah / Jurusan:")
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, student_data.get("Asal_Sekolah_Tipe", "-"), ln=True)

    pdf.set_font("helvetica", "B", 11)
    pdf.cell(50, 8, "Minat Utama:")
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, student_data.get("Minat_Utama", "-"), ln=True)

    if student_data.get("Minat_Sekunder"):
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(50, 8, "Minat Sekunder:")
        pdf.set_font("helvetica", "", 11)
        pdf.cell(0, 8, student_data.get("Minat_Sekunder", "-"), ln=True)

    pdf.set_font("helvetica", "B", 11)
    pdf.cell(50, 8, "Tipe Kepribadian:")
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, student_data.get("Tipe_Kepribadian", "-"), ln=True)

    pdf.ln(5)

    # Nilai Akademik
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Nilai Akademik:", ln=True)
    pdf.ln(2)

    nilai_cols = [
        ("Matematika", "Nilai_Matematika"),
        ("Bahasa Indonesia", "Nilai_Bahasa_Indonesia"),
        ("Bahasa Inggris", "Nilai_Bahasa_Inggris"),
        ("IPA", "Nilai_IPA"),
        ("Fisika", "Nilai_Fisika"),
        ("Kimia", "Nilai_Kimia"),
        ("Biologi", "Nilai_Biologi"),
        ("Ekonomi", "Nilai_Ekonomi"),
        ("Geografi", "Nilai_Geografi"),
        ("Sosiologi", "Nilai_Sosiologi"),
    ]

    pdf.set_font("helvetica", "", 10)
    col_width = 190 / 5
    for i in range(0, len(nilai_cols), 5):
        row_items = nilai_cols[i:i+5]
        for label, key in row_items:
            pdf.cell(col_width, 7, f"{label}: {student_data.get(key, 0)}", border=1)
        pdf.ln()

    pdf.ln(5)

    # Kemampuan Diri
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Kemampuan Diri (Skala 1-10):", ln=True)
    pdf.ln(2)

    pdf.set_font("helvetica", "", 10)
    pdf.cell(45, 7, f"Analitis: {student_data.get('Kemampuan_Analitis', 0)}", border=1)
    pdf.cell(45, 7, f"Kreatif: {student_data.get('Kemampuan_Kreatif', 0)}", border=1)
    pdf.cell(45, 7, f"Sosial: {student_data.get('Kemampuan_Sosial', 0)}", border=1)
    pdf.cell(45, 7, f"Leadership: {student_data.get('Kemampuan_Leadership', 0)}", border=1)
    pdf.ln()

    pdf.ln(10)

    # ─── Bagian 2: Rekomendasi Jurusan ─────────────────────────────────
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.set_fill_color(*PRIMARY_COLOR)
    pdf.cell(0, 10, "2. Rekomendasi Jurusan", ln=True, fill=True)
    pdf.ln(3)

    pdf.set_font("helvetica", "", 10)
    for i, rec in enumerate(recommendations):
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(10, 8, f"#{i+1}.")
        pdf.cell(0, 8, rec.get("jurusan", "-"), ln=True)

        pdf.set_font("helvetica", "", 10)
        pdf.cell(30, 7, "Skor Kecocokan:")
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(30, 7, f"{rec.get('score', 0):.1f}%", ln=True)

        match_status = "[Cocok]" if rec.get("minat_match") else ""
        if match_status:
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 7, match_status, ln=True)

        pdf.ln(2)

    pdf.ln(10)

    # ─── Bagian 3: Info Jurusan (Detail) ─────────────────────────────────────
    if all_jurusan_info:
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.set_fill_color(*PRIMARY_COLOR)
        pdf.cell(0, 10, "3. Detail Semua Rekomendasi Jurusan", ln=True, fill=True)
        pdf.ln(3)

        # Loop untuk setiap rekomendasi
        for i, rec in enumerate(recommendations):
            jurusAN = rec.get("jurusan", "-")
            score = rec.get("score", 0)
            minat_match = rec.get("minat_match", False)

            # Cek ruang足够的 di页面, jika tidak buat页面 baru
            if pdf.get_y() > 220:
                pdf.add_page()

            pdf.set_font("helvetica", "B", 12)
            pdf.cell(10, 8, f"#{i+1}.")
            pdf.cell(0, 8, f"{jurusAN} ({score:.1f}%)", ln=True)

            # Ambil info dari all_jurusan_info
            j_info = all_jurusan_info.get(jurusAN, {})

            # Deskripsi
            if j_info.get("deskripsi"):
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 6, "Deskripsi:", ln=True)
                pdf.set_font("helvetica", "", 9)
                pdf.multi_cell(0, 5, j_info.get("deskripsi", "-"))
                pdf.ln(2)

            # Prospek Karir
            if j_info.get("prospek_karir"):
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 6, "Prospek Karir:", ln=True)
                pdf.set_font("helvetica", "", 9)
                pdf.multi_cell(0, 5, j_info.get("prospek_karir", "-"))
                pdf.ln(2)

            # Skill Dibutuhkan
            if j_info.get("skill_dibutuhkan"):
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 6, "Skill Dibutuhkan:", ln=True)
                pdf.set_font("helvetica", "", 9)
                pdf.multi_cell(0, 5, j_info.get("skill_dibutuhkan", "-"))
                pdf.ln(2)

            # Status Minat Cocok
            status_minat = "[Cocok Minat]" if minat_match else ""
            if status_minat:
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 6, status_minat, ln=True)

            pdf.ln(5)
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.set_line_width(0.3)
            pdf.ln(3)

    # ─── Bagian 4: Info Karir & Gaji ────────────────────────────────────
    if all_career_info:
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.set_fill_color(*PRIMARY_COLOR)
        pdf.cell(0, 10, "4. Karir & Prospek Gaji (Semua Rekomendasi)", ln=True, fill=True)
        pdf.ln(3)

        # Loop untuk setiap rekomendasi
        for i, rec in enumerate(recommendations):
            jurusAN = rec.get("jurusan", "-")
            career_df = all_career_info.get(jurusAN)

            # Cek ruang cukup di page, jika tidak buat page baru
            if pdf.get_y() > 200:
                pdf.add_page()

            pdf.set_font("helvetica", "B", 11)
            pdf.cell(10, 8, f"#{i+1}.")
            pdf.cell(0, 8, jurusAN, ln=True)
            pdf.ln(2)

            if career_df is not None and not career_df.empty:
                pdf.set_font("helvetica", "B", 9)
                pdf.cell(50, 6, "Karir", border=1)
                pdf.cell(30, 6, "Gaji Awal", border=1)
                pdf.cell(30, 6, "Gaji Senior", border=1)
                pdf.cell(30, 6, "Demand", border=1)
                pdf.cell(25, 6, "Growth", border=1)
                pdf.ln()

                pdf.set_font("helvetica", "", 8)
                for _, row in career_df.iterrows():
                    pdf.cell(50, 5, str(row.get("Karir", "-"))[:25], border=1)
                    pdf.cell(30, 5, f"Rp {row.get('Rata_Gaji_Awal_Juta', 0)}", border=1)
                    pdf.cell(30, 5, f"Rp {row.get('Rata_Gaji_Senior_Juta', 0)}", border=1)
                    pdf.cell(30, 5, str(row.get("Tingkat_Permintaan_Pasar", "-")), border=1)
                    pdf.cell(25, 5, f"{row.get('Growth_5yr_Persen', 0)}%", border=1)
                    pdf.ln()
            else:
                pdf.set_font("helvetica", "", 9)
                pdf.cell(0, 6, "Data karir belum tersedia", ln=True)

            pdf.ln(5)

    # ─── Bagian 5: Kampus Rekomendasi ────────────────────────────────────────────
    if campus_info is not None and not campus_info.empty:
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.set_fill_color(*PRIMARY_COLOR)
        pdf.cell(0, 10, "5. Rekomendasi Kampus", ln=True, fill=True)
        pdf.ln(3)

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(70, 8, "Kampus", border=1)
        pdf.cell(25, 8, "Akreditasi", border=1)
        pdf.cell(35, 8, "Biaya/Semester", border=1)
        pdf.cell(25, 8, "Rating", border=1)
        pdf.ln()

        pdf.set_font("helvetica", "", 9)
        for _, row in campus_info.iterrows():
            pdf.cell(70, 7, str(row.get("Kampus", "-"))[:35], border=1)
            pdf.cell(25, 7, str(row.get("Akreditasi", "-")), border=1)
            pdf.cell(35, 7, f"Rp {row.get('Biaya_Per_Semester_Juta', 0)} jt", border=1)
            pdf.cell(25, 7, str(row.get("Rating_Kepuasan", "-")), border=1)
            pdf.ln()

    # Footer
    pdf.set_y(-20)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, "Dibuat oleh AI Career Compass -Aplikasi Rekomendasi Jurusan Kuliah", ln=True, align="C")

    return bytes(pdf.output(dest="S"))


class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        pass
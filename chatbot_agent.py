"""
Chatbot Agent berbasis LangChain + Google Gemini (GRATIS)
dengan tools: cari jurusan, info karir, rekomendasi kampus, dll.
"""
import os
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ─── Coba import LangChain & Gemini ──────────────────────────────────────────
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain.tools import tool
    from langchain_community.memory import ConversationBufferWindowMemory
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    LANGCHAIN_OK = True
except ImportError:
    LANGCHAIN_OK = False

# Import database helper
import sys, os
from db_connector import (
    query_df, get_jurusan_metadata, get_career_paths, get_kampus_info
)


# ─────────────────────────────────────────────────────────────────────────────
#  TOOLS untuk Agent
# ─────────────────────────────────────────────────────────────────────────────

def _get_tools():
    """Buat daftar tools untuk agent."""

    @tool
    def cari_info_jurusan(nama_jurusan: str) -> str:
        """
        Cari informasi lengkap tentang sebuah jurusan kuliah.
        Gunakan tool ini ketika user bertanya tentang jurusan tertentu.
        Input: nama jurusan (misal: Teknik Informatika, Kedokteran, dll)
        """
        try:
            df = get_jurusan_metadata()
            # Fuzzy match
            mask = df["jurusan"].str.contains(nama_jurusan, case=False, na=False)
            found = df[mask]
            if found.empty:
                return f"Maaf, informasi jurusan '{nama_jurusan}' tidak ditemukan di database."
            row = found.iloc[0]
            return (
                f"📚 **{row['jurusan']}**\n\n"
                f"**Deskripsi:** {row['deskripsi']}\n\n"
                f"**Prospek Karir:** {row['prospek_karir']}\n\n"
                f"**Skill Dibutuhkan:** {row['skill_dibutuhkan']}\n\n"
                f"**Minat Cocok:** {row['minat_cocok']}\n"
                f"**Kepribadian Cocok:** {row['kepribadian_cocok']}"
            )
        except Exception as e:
            return f"Error mengambil data jurusan: {str(e)}"

    @tool
    def cari_prospek_karir(nama_jurusan: str) -> str:
        """
        Cari informasi karir dan gaji untuk sebuah jurusan.
        Gunakan tool ini ketika user bertanya soal gaji, pekerjaan, atau prospek karir.
        Input: nama jurusan
        """
        try:
            df = get_career_paths(nama_jurusan)
            if df.empty:
                # Try fuzzy
                all_df = get_career_paths()
                mask = all_df["Jurusan"].str.contains(nama_jurusan, case=False, na=False)
                df = all_df[mask]
            if df.empty:
                return f"Data karir untuk '{nama_jurusan}' tidak ditemukan."

            lines = [f"💼 **Prospek Karir - {nama_jurusan}**\n"]
            for _, row in df.iterrows():
                lines.append(
                    f"• **{row['Karir']}**\n"
                    f"  - Gaji Awal: Rp {row['Rata_Gaji_Awal_Juta']:.1f} juta/bulan\n"
                    f"  - Gaji Senior: Rp {row['Rata_Gaji_Senior_Juta']:.1f} juta/bulan\n"
                    f"  - Permintaan Pasar: {row['Tingkat_Permintaan_Pasar']}\n"
                    f"  - Growth 5 Tahun: {row['Growth_5yr_Persen']}%\n"
                    f"  - Skill: {row['Skill_Utama']}\n"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"Error mengambil data karir: {str(e)}"

    @tool
    def cari_rekomendasi_kampus(nama_jurusan: str) -> str:
        """
        Cari kampus terbaik untuk jurusan tertentu, dilengkapi info akreditasi dan biaya.
        Input: nama jurusan
        """
        try:
            df = get_kampus_info(nama_jurusan)
            if df.empty:
                all_df = get_kampus_info()
                mask = all_df["Jurusan"].str.contains(nama_jurusan, case=False, na=False)
                df = all_df[mask]
            if df.empty:
                return f"Data kampus untuk '{nama_jurusan}' tidak ditemukan."

            df = df.head(5)
            lines = [f"🏫 **Kampus Rekomendasi - {nama_jurusan}**\n"]
            for _, row in df.iterrows():
                lines.append(
                    f"• **{row['Kampus']}** ({row['Tipe_Kampus']})\n"
                    f"  - Akreditasi: {row['Akreditasi']}\n"
                    f"  - Biaya/Semester: Rp {row['Biaya_Per_Semester_Juta']:.1f} juta\n"
                    f"  - Rating Kepuasan: {row['Rating_Kepuasan']}/5.0\n"
                    f"  - Lokasi: {row['Lokasi_Kota']}\n"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"Error mengambil data kampus: {str(e)}"

    @tool
    def hitung_skor_kecocokan(
        nilai_matematika: int,
        minat_utama: str,
        jurusan_target: str
    ) -> str:
        """
        Hitung estimasi skor kecocokan siswa dengan jurusan tertentu secara sederhana.
        Input: nilai_matematika (0-100), minat_utama, jurusan_target
        """
        minat_jurusan_map = {
            "Teknologi & Komputer": ["Teknik Informatika", "Ilmu Komputer", "Sistem Informasi"],
            "Bisnis & Keuangan": ["Manajemen", "Akuntansi", "Ekonomi"],
            "Kesehatan & Medis": ["Kedokteran", "Farmasi", "Kesehatan Masyarakat"],
            "Teknik & Konstruksi": ["Teknik Sipil", "Teknik Mesin", "Teknik Elektro"],
            "Hukum & Sosial": ["Hukum", "Ilmu Komunikasi", "Psikologi"],
            "Sains & Penelitian": ["Biologi", "Kimia", "Fisika"],
            "Seni & Desain": ["Arsitektur", "Desain Komunikasi Visual"],
            "Pendidikan & Pengajaran": ["Pendidikan Matematika", "Pendidikan Bahasa Inggris"],
        }

        skor = 50  # Base score
        jurusan_lower = jurusan_target.lower()

        # Bonus jika minat sesuai
        for minat, jurusan_list in minat_jurusan_map.items():
            if minat == minat_utama:
                for j in jurusan_list:
                    if j.lower() in jurusan_lower or jurusan_lower in j.lower():
                        skor += 30
                        break

        # Bonus nilai matematika untuk jurusan sains/teknik
        sains_teknik = ["teknik", "informatika", "komputer", "matematika", "fisika", "kimia"]
        if any(k in jurusan_lower for k in sains_teknik):
            skor += (nilai_matematika - 70) * 0.3 if nilai_matematika > 70 else 0

        skor = max(10, min(95, skor))
        return (
            f"📊 Estimasi kecocokan kamu dengan **{jurusan_target}**: **{skor:.0f}%**\n\n"
            f"Catatan: Ini adalah estimasi kasar. Gunakan fitur '🎯 Prediksi Jurusan' "
            f"untuk hasil yang lebih akurat menggunakan Machine Learning."
        )

    @tool
    def daftar_semua_jurusan() -> str:
        """
        Tampilkan semua jurusan yang tersedia di sistem.
        Gunakan tool ini ketika user ingin tahu ada jurusan apa saja.
        """
        try:
            df = get_jurusan_metadata()
            jurusan_list = df["jurusan"].tolist()
            return "📋 **Jurusan yang tersedia di sistem:**\n\n" + "\n".join(
                f"{i+1}. {j}" for i, j in enumerate(jurusan_list)
            )
        except Exception as e:
            return f"Error: {str(e)}"

    return [cari_info_jurusan, cari_prospek_karir,
            cari_rekomendasi_kampus, hitung_skor_kecocokan, daftar_semua_jurusan]


# ─────────────────────────────────────────────────────────────────────────────
#  AGENT CLASS
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Kamu adalah **AI Career Compass**, asisten cerdas untuk membantu siswa SMA/SMK 
Indonesia memilih jurusan kuliah dan karir yang tepat.

Kamu ramah, supportif, dan berbicara dalam Bahasa Indonesia yang natural dan mudah dipahami.
Kamu memiliki akses ke database berisi informasi jurusan, karir, dan kampus di Indonesia.

**Kemampuanmu:**
- Memberikan informasi detail tentang jurusan kuliah
- Menjelaskan prospek karir dan kisaran gaji
- Merekomendasikan kampus terbaik untuk jurusan tertentu
- Menghitung estimasi kecocokan siswa dengan jurusan
- Menjawab pertanyaan seputar dunia perkuliahan dan karir

**Panduan menjawab:**
- Selalu gunakan tools yang tersedia untuk mendapatkan data akurat dari database
- Berikan jawaban yang komprehensif tapi mudah dipahami
- Sertakan emoji yang relevan agar lebih menarik
- Jika tidak tahu, jujur dan sarankan untuk berkonsultasi dengan guru BK
- Selalu tanyakan apakah ada yang ingin ditanyakan lebih lanjut

Ingat: Kamu membantu masa depan siswa Indonesia! 🇮🇩
"""


class CareerChatbot:
    def __init__(self):
        self.agent_executor = None
        self.memory = None
        self._initialized = False
        self._error_msg = None

    def initialize(self, api_key: str = None) -> bool:
        """Inisialisasi agent. Return True jika berhasil."""
        if not LANGCHAIN_OK:
            self._error_msg = "Paket langchain belum terinstall."
            return False

        key = api_key or os.getenv("GOOGLE_API_KEY", "AIzaSyCd0vBMRZVM62vq36OEV3hD_elwJrY6coY")
        if not key or key == "your_gemini_api_key_here":
            self._error_msg = "API Key Google Gemini belum dikonfigurasi."
            return False

        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=key,
                temperature=0.7,
            )

            tools = _get_tools()

            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            agent = create_tool_calling_agent(llm, tools, prompt)

            self.memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                k=10,
            )

            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                memory=self.memory,
                verbose=False,
                handle_parsing_errors=True,
                max_iterations=5,
            )

            self._initialized = True
            return True

        except Exception as e:
            self._error_msg = str(e)
            return False

    def _fallback_career_lookup(self, keyword: str) -> str:
        """Fallback: Cari data karir langsung dari database."""
        try:
            df = get_career_paths(keyword)
            if df.empty:
                all_df = get_career_paths()
                df = all_df[
                    all_df['Jurusan'].str.contains(keyword, case=False, na=False) |
                    all_df['Karir'].str.contains(keyword, case=False, na=False)
                ]
            if df.empty:
                return None
            lines = [f"💼 **Info Karir - {keyword}**\n"]
            for _, row in df.iterrows():
                lines.append(
                    f"• **{row['Karir']}** ({row['Jurusan']})\n"
                    f"  - Gaji Awal: Rp {row['Rata_Gaji_Awal_Juta']:.1f} juta/bulan\n"
                    f"  - Gaji Senior: Rp {row['Rata_Gaji_Senior_Juta']:.1f} juta/bulan\n"
                    f"  - Permintaan Pasar: {row['Tingkat_Permintaan_Pasar']}\n"
                    f"  - Growth 5 Tahun: {row['Growth_5yr_Persen']}%\n"
                )
            return "\n".join(lines)
        except Exception:
            return None

    def chat(self, user_message: str) -> str:
        """Kirim pesan ke agent dan kembalikan respons."""
        if not self._initialized:
            return (
                "⚠️ Chatbot belum aktif. "
                + (self._error_msg or "Mohon konfigurasi API Key di sidebar.")
            )
        try:
            response = self.agent_executor.invoke({"input": user_message})
            raw_output = response.get("output", "Maaf, terjadi kesalahan.")
            import re
            output = re.sub(r'tool_code\s+.*?tool_code', '', raw_output, flags=re.DOTALL)
            output = re.sub(r'```(?:tool|python)?[\s\S]*?```', '', output)
            output = re.sub(r'<(?:tool_call|tool_code)[\s\S]*?>.*?</(?:tool_call|tool_code)>', '', output)
            output = output.strip()
            # Jika output rusak/pakai tool call failed, fallback ke lookup langsung
            if not output or len(output) < 20 or 'tool_code' in output.lower():
                keywords = re.findall(r'(?:gaji|karir|salary)[\s]+(\w+)', user_message.lower())
                for kw in keywords:
                    result = self._fallback_career_lookup(kw)
                    if result:
                        return result
                # Jika tidak ada keyword spesifik, coba dari raw_output
                career_match = re.search(r'get_career_(\w+)\(["\'](\w+)["\'])', raw_output)
                if career_match:
                    result = self._fallback_career_lookup(career_match.group(3))
                    if result:
                        return result
                return "Maaf, saya sedang mengalami masalah teknis. Silakan coba lagi atau hubungi admin."
            return output
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def reset_memory(self):
        """Reset riwayat percakapan."""
        if self.memory:
            self.memory.clear()

    @property
    def is_ready(self) -> bool:
        return self._initialized

    @property
    def error(self) -> Optional[str]:
        return self._error_msg


# Helper untuk lookup langsung tanpa agent
def _direct_career_lookup(keyword: str) -> str:
    """Lookup career data langsung dari database."""
    try:
        df = get_career_paths(keyword)
        if df.empty:
            all_df = get_career_paths()
            df = all_df[
                all_df['Jurusan'].str.contains(keyword, case=False, na=False) |
                all_df['Karir'].str.contains(keyword, case=False, na=False)
            ]
        if df.empty:
            return None
        lines = [f"💼 **Info Karir - {keyword}**\n"]
        for _, row in df.iterrows():
            lines.append(
                f"• **{row['Karir']}** ({row['Jurusan']})\n"
                f"  - Gaji Awal: Rp {row['Rata_Gaji_Awal_Juta']:.1f} juta/bulan\n"
                f"  - Gaji Senior: Rp {row['Rata_Gaji_Senior_Juta']:.1f} juta/bulan\n"
                f"  - Permintaan Pasar: {row['Tingkat_Permintaan_Pasar']}\n"
                f"  - Growth 5 Tahun: {row['Growth_5yr_Persen']}%\n"
            )
        return "\n".join(lines)
    except Exception:
        return None

# Fallback sederhana jika LangChain tidak tersedia
def simple_chat_fallback(user_message: str, history: list) -> str:
    """Fallback chat tanpa LangChain - menggunakan Google Gemini API langsung."""
    import google.generativeai as genai
    import re

    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        return "⚠️ API Key Google Gemini belum dikonfigurasi. Masukkan API Key di sidebar."

    # Deteksi pertanyaan tentang gaji/prospek karir
    msg_lower = user_message.lower()
    is_career_query = any(kw in msg_lower for kw in ['gaji', 'salary', 'prospek', 'karir', 'pekerjaan', 'income'])

    if is_career_query:
        # Coba extract nama karir/jurusan dari pertanyaan
        # Pattern untuk "gaji [karir]" atau "[karir] gaji"
        career_kw = re.search(r'(?:gaji|salary|prospek)[\s]+(?:dari|untuk|)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', user_message, re.IGNORECASE)
        if not career_kw:
            career_kw = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:gaji|salary|prospek|kerja)', user_message, re.IGNORECASE)
        if career_kw:
            kw = career_kw.group(1).strip()
            result = _direct_career_lookup(kw)
            if result:
                # Append sebagai context, lalu chat dengan LLM
                context_hint = f"\n\n[INFO DATABASE: {result}]"
                user_with_context = user_message + context_hint

                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    "gemini-2.5-flash",
                    system_instruction=SYSTEM_PROMPT + "\n\nJika user bertanya tentang gaji/prospek karir, gunakan data dari INFO DATABASE yang saya berikan."
                )
                chat_history = []
                for msg in history[-10:]:
                    role = "user" if msg["role"] == "user" else "model"
                    chat_history.append({"role": role, "parts": [msg["content"]]})

                chat = model.start_chat(history=chat_history)
                response = chat.send_message(user_with_context)
                return response.text

    # Default: chat normal
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )

        # Format history
        chat_history = []
        for msg in history[-10:]:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=chat_history)
        response = chat.send_message(user_message)
        return response.text

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

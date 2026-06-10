"""
Halaman Chatbot AI - Career Compass Assistant
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st

st.set_page_config(page_title="Chatbot AI | AI Career Compass", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

.chat-container {
    background: linear-gradient(180deg, #0D1B2A 0%, #131C27 100%);
    border: 1px solid rgba(79,142,247,0.2);
    border-radius: 20px;
    padding: 24px;
    min-height: 400px;
    max-height: 600px;
    overflow-y: auto;
}
.msg-user {
    display: flex; justify-content: flex-end; margin: 12px 0;
}
.msg-bot {
    display: flex; justify-content: flex-start; margin: 12px 0;
}
.bubble-user {
    background: linear-gradient(135deg, #4F8EF7, #9B4FF7);
    border-radius: 20px 20px 4px 20px;
    padding: 12px 18px;
    max-width: 75%;
    color: white;
    font-size: 0.95rem;
    line-height: 1.5;
}
.bubble-bot {
    background: rgba(28, 43, 58, 0.9);
    border: 1px solid rgba(79,142,247,0.15);
    border-radius: 20px 20px 20px 4px;
    padding: 12px 18px;
    max-width: 80%;
    color: rgba(255,255,255,0.9);
    font-size: 0.95rem;
    line-height: 1.5;
}
.avatar {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; flex-shrink: 0; margin: 0 10px;
}
.avatar-bot { background: linear-gradient(135deg, #4F8EF7, #9B4FF7); }
.avatar-user { background: linear-gradient(135deg, #F7924F, #F7E04F); }

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

st.title("🤖 AI Career Compass Chatbot")
st.caption("Tanya apa saja tentang jurusan, karir, dan kampus!")
st.divider()

# ─── Import chatbot ───────────────────────────────────────────────────────────
from chatbot_agent import CareerChatbot, simple_chat_fallback

# ─── Init session state ───────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = CareerChatbot()

if "chatbot_mode" not in st.session_state:
    st.session_state.chatbot_mode = "simple"  # simple atau agent

# ─── Sidebar config ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Pengaturan Chatbot")

    api_key = st.text_input("Google Gemini API Key", type="password",
                             value=os.getenv("GOOGLE_API_KEY", ""),
                             placeholder="Masukkan API Key...")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    mode = st.radio("Mode Chatbot",
                    ["Simple (Gemini Direct)", "Agent (LangChain + Tools)"],
                    help="Agent mode lebih canggih tapi butuh LangChain terinstall")
    st.session_state.chatbot_mode = "agent" if "Agent" in mode else "simple"

    if st.session_state.chatbot_mode == "agent":
        if st.button("🔌 Inisialisasi Agent", use_container_width=True):
            with st.spinner("Menginisialisasi agent..."):
                ok = st.session_state.chatbot.initialize(api_key)
                if ok:
                    st.success("✅ Agent siap!")
                else:
                    st.error(f"❌ {st.session_state.chatbot.error}")

    st.divider()

    # Konteks siswa
    if "student_data" in st.session_state:
        sdata = st.session_state["student_data"]
        st.markdown(f"**Konteks Siswa:**")
        st.caption(f"Nama: {sdata['nama']}")
        st.caption(f"Minat: {sdata['Minat_Utama']}")
        if "recommendations" in st.session_state:
            top = st.session_state["recommendations"][0]["jurusan"]
            st.caption(f"Rekomendasi #1: {top}")

    st.divider()

    if st.button("🗑️ Reset Percakapan", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.chatbot.reset_memory()
        st.rerun()

    # Quick questions
    st.markdown("**💬 Pertanyaan Cepat:**")
    quick_qs = [
        "Apa itu Teknik Informatika?",
        "Berapa gaji Data Scientist?",
        "Kampus terbaik untuk Kedokteran?",
        "Jurusan apa yang cocok untuk saya?",
    ]
    for q in quick_qs:
        if st.button(q, use_container_width=True, key=f"qq_{q}"):
            st.session_state["quick_input"] = q

    # ── Navigation Menu ────────────────────────────────────────────────────────
    st.divider()
    st.markdown('<p class="nav-section-label">Menu Navigasi</p>', unsafe_allow_html=True)

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("🏠")
    with col_btn:
        if st.button("Home", use_container_width=True):
            st.switch_page("app.py")

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("📋")
    with col_btn:
        if st.button("Input Profil", use_container_width=True):
            st.switch_page("pages/1_📋_Input_Profil.py")

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("🎯")
    with col_btn:
        if st.button("Hasil Rekomendasi", use_container_width=True):
            st.switch_page("pages/2_🎯_Hasil_Rekomendasi.py")

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("🤖")
    with col_btn:
        if st.button("Chatbot AI", use_container_width=True):
            st.switch_page("pages/3_🤖_Chatbot_AI.py")

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("📊")
    with col_btn:
        if st.button("Analisis Data", use_container_width=True):
            st.switch_page("pages/4_📊_Analisis_Data.py")

    col_icon, col_btn = st.columns([0.25, 1], gap="small")
    with col_icon: st.markdown("⚙️")
    with col_btn:
        if st.button("Training Model", use_container_width=True):
            st.switch_page("pages/5_⚙️_Training_Model.py")

    st.divider()
    st.caption("Kelompok 6 | Celerates CAMP Batch 4")

# ─── Display chat history ─────────────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align:center; padding: 48px; color: rgba(255,255,255,0.4);">
            <div style="font-size:3rem;">🧭</div>
            <div style="font-size:1.1rem; margin-top:12px;">
                Halo! Saya <strong>AI Career Compass</strong>.<br>
                Tanya saya tentang jurusan, karir, atau kampus yang cocok untukmu!
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="🧑‍🎓"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])

# ─── Input area ───────────────────────────────────────────────────────────────
# Handle quick input
default_input = st.session_state.pop("quick_input", "")

user_input = st.chat_input(
    "Ketik pertanyaanmu di sini... (misal: Apa prospek kerja Teknik Informatika?)",
)

# Proses input (dari chat_input atau quick button)
message_to_process = user_input or default_input

if message_to_process:
    # Tambah konteks siswa jika ada
    enriched_message = message_to_process
    if "student_data" in st.session_state and "jurusan apa yang cocok untuk saya" in message_to_process.lower():
        sdata = st.session_state["student_data"]
        recs = st.session_state.get("recommendations", [])
        if recs:
            enriched_message += (
                f"\n\n[Konteks siswa: Nama={sdata['nama']}, "
                f"Minat={sdata['Minat_Utama']}, "
                f"Kepribadian={sdata['Tipe_Kepribadian']}, "
                f"Rekomendasi #1={recs[0]['jurusan']} ({recs[0]['score']}%)]"
            )

    # Tampilkan pesan user
    st.session_state.chat_history.append({"role": "user", "content": message_to_process})

    # Generate response
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        response = "⚠️ Masukkan **Google Gemini API Key** di sidebar untuk mengaktifkan chatbot.\n\n[Dapatkan API Key gratis di aistudio.google.com]"
    elif st.session_state.chatbot_mode == "agent" and st.session_state.chatbot.is_ready:
        with st.spinner("🤖 AI sedang berpikir..."):
            response = st.session_state.chatbot.chat(enriched_message)
    else:
        with st.spinner("🤖 AI sedang menjawab..."):
            response = simple_chat_fallback(enriched_message, st.session_state.chat_history[:-1])

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()

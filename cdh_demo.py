import streamlit as st
import speech_recognition as sr
import ollama
import time
from datetime import datetime

# ==========================================
# 1. SETUP PAGE & THEME (GREY CORPORATE THEME)
# ==========================================
st.set_page_config(page_title="CDH AI Scribe", layout="wide")

# CSS: Design Khas (Background Kelabu ala Gambar Ke-2)
st.markdown("""
    <style>
    /* 1. Background App - Tukar ke Kelabu Lembut (#EEEEEE) */
    .stApp {
        background-color: #EEEEEE;
    }
    
    /* 2. Sidebar - Blend dengan background tapi gelap sikit */
    [data-testid="stSidebar"] {
        background-color: #E8E8E8;
        border-right: 1px solid #D0D0D0;
    }
    
    /* 3. Butang Utama (Kekalkan Merah Synapse supaya menyerlah) */
    div.stButton > button:first-child {
        background-color: #D9534F; 
        color: white;
        border-radius: 6px;
        border: none;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        background-color: #C9302C; 
        color: white;
    }

    /* 4. Tajuk Utama (Header) */
    .header-container {
        padding-bottom: 20px;
        border-bottom: 2px solid #CCCCCC;
        margin-bottom: 20px;
    }
    .header-text {
        font-family: 'Segoe UI', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: #444444;
    }
    .header-text span {
        color: #D9534F; /* Merah pada Clinical AI Scribe */
        font-weight: 400;
    }
    
    /* 5. Kotak Report (Kad Putih di atas background kelabu) */
    .synapse-card {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 10px;
        border: 1px solid #DDDDDD;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIC SUARA (SMART LOOP) - KEKAL SAMA
# ==========================================
def dengar_suara_smart_v2():
    listener = sr.Recognizer()
    full_transcript = []
    
    status_area = st.empty()
    transcript_area = st.empty()
    
    try:
        with sr.Microphone() as source:
            status_area.warning("🎙️ AMBIENT LISTENING ACTIVE... (Say 'STOP RECORDING' to finish)")
            listener.adjust_for_ambient_noise(source, duration=0.5)
            
            while True:
                try:
                    # Dengar tanpa putus
                    audio = listener.listen(source, timeout=3, phrase_time_limit=8)
                    text_chunk = listener.recognize_google(audio, language='ms-MY')
                    full_transcript.append(text_chunk)
                    
                    # Live Update
                    current_text = " ".join(full_transcript)
                    transcript_area.code(f"{current_text}", language="text")
                    
                    # Stop Keyword
                    keywords = ["stop recording", "berhenti", "tamat", "stop record"]
                    if any(word in text_chunk.lower() for word in keywords):
                        status_area.success("✅ Session Ended. Processing...")
                        break 
                        
                except sr.WaitTimeoutError:
                    continue 
                except sr.UnknownValueError:
                    continue
                except Exception:
                    break
            
            return " ".join(full_transcript)
            
    except Exception:
        return None

def generate_report(text):
    prompt = f"""
    Act as a Medical Scribe for Centre for Digital Health. 
    Convert this transcript to a SOAP Note.
    TRANSCRIPT: "{text}"
    
    OUTPUT FORMAT (Professional English):
    Subjective: ...
    Objective: ...
    Assessment: ...
    Plan: ...
    """
    try:
        response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except:
        return "Error: Llama 3 is offline."

# ==========================================
# 3. LAYOUT BARU (CLEAN GREY)
# ==========================================

# HEADER BARU (Sesuai permintaan Puan)
st.markdown("""
<div class="header-container">
    <div class="header-text">
        Centre for Digital Health | <span>Clinical AI Scribe</span>
    </div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR (BUANG MENU NAV, TINGGAL PESAKIT SAHAJA)
with st.sidebar:
    st.markdown("### 🏥 Patient Context")
    # Kad Pesakit
    st.info("**Ali bin Abu (56M)**\n\nMRN: 1099221")
    
    st.markdown("---")
    st.markdown("**Vital Signs (Integrated Device)**")
    c1, c2 = st.columns(2)
    c1.metric("BP", "142/90", "High", delta_color="inverse")
    c2.metric("HR", "98", "Normal")
    
    st.markdown("---")
    st.caption("System: CDH Pilot v1.0")

# MAIN CONTENT
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("1. Consultation Input")
    st.write("Start the ambient listening session.")
    
    # Butang Merah
    if st.button("Start Recording Session"):
        raw_text = dengar_suara_smart_v2()
        if raw_text:
            st.session_state['text_final'] = raw_text

    # Tunjuk Transkrip (Dalam kotak putih supaya kontras dengan kelabu)
    if 'text_final' in st.session_state:
        st.markdown("#### Transcript:")
        st.text_area("", value=st.session_state['text_final'], height=150)
        
        if st.button("Generate Medical Report ⚡"):
            with st.spinner("Analyzing Clinical Data..."):
                report = generate_report(st.session_state['text_final'])
                st.session_state['report_final'] = report

with col_right:
    st.subheader("2. Generated Report")
    
    if 'report_final' in st.session_state:
        # Paparan Kad Putih
        st.markdown(f"""
        <div class="synapse-card">
            <h3 style="margin-top:0; color:#D9534F;">SOAP NOTE</h3>
            <p style="font-size:12px; color:#666;">Attending: Dr. Fatimah | Date: {datetime.now().strftime('%d %b %Y')}</p>
            <hr>
            <div style="font-family: Arial; font-size:14px; white-space: pre-wrap; color:#333;">
{st.session_state['report_final']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Download TXT
        st.download_button(
            label="💾 Save to EMR (.txt)",
            data=st.session_state['report_final'],
            file_name=f"SOAP_Note_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
    else:
        # Placeholder
        st.info("Medical report will appear here.")
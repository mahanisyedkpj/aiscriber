import speech_recognition as sr
import pyttsx3
import ollama
import time

# ==========================================
# 1. SETUP
# ==========================================
engine = pyttsx3.init()
listener = sr.Recognizer()

# List untuk simpan semua ayat sepanjang perbualan
transkrip_penuh = []

def bercakap(text):
    print(f"🤖 SYSTEM: {text}")
    engine.say(text)
    engine.runAndWait()

def dengar_perbualan():
    try:
        with sr.Microphone() as source:
            print("\n🎤 ...Mendengar perbualan (Doktor & Pesakit)...")
            # Adjust sensitiviti mic
            listener.adjust_for_ambient_noise(source, duration=1) 
            
            # Dengar lama sikit (10 saat setiap ayat)
            voice = listener.listen(source, timeout=10, phrase_time_limit=15)
            
            # Tukar ke text
            ayat = listener.recognize_google(voice, language='ms-MY')
            print(f"📝 Transkrip: {ayat}")
            return ayat
            
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# ==========================================
# 2. PROSES: JANA MEDICAL REPORT (SOAP NOTE)
# ==========================================
def generate_soap_note(full_text):
    print("\n🧠 ROG AI sedang menjana Medical Report...")
    
    prompt_khas = f"""
    Anda adalah Medical Scribe AI. Tugas anda adalah menukar transkrip perbualan doktor-pesakit berikut kepada format SOAP Note yang profesional.
    
    TRANSKRIP PERBUALAN:
    "{full_text}"
    
    ARAHAN:
    1. Abaikan ayat-ayat kosong/bual bicara santai.
    2. Fokus pada simptom, sejarah penyakit, dan rawatan.
    3. Output MESTI dalam format berikut:
    
    --- MEDICAL REPORT (SOAP FORMAT) ---
    Patient Name: (Unknown - Not mentioned)
    
    SUBJECTIVE (Simptom pesakit):
    - ...
    
    OBJECTIVE (Pemerhatian doktor):
    - ...
    
    ASSESSMENT (Diagnosis):
    - ...
    
    PLAN (Rawatan/Ubat):
    - ...
    
    (Tulis dalam Bahasa Inggeris Profesional atau Bahasa Melayu Formal)
    """

    response = ollama.chat(model='llama3', messages=[
        {'role': 'system', 'content': 'You are a helpful medical scribe.'},
        {'role': 'user', 'content': prompt_khas},
    ])
    
    return response['message']['content']

# ==========================================
# 3. PROGRAM UTAMA
# ==========================================
if __name__ == "__main__":
    print("=== AI MEDICAL SCRIBE (DEMO) ===")
    print("Arahan: Berborak seperti biasa. Sebut 'STOP RECORDING' bila dah habis.")
    bercakap("Sistem Scribe sedia. Sila mulakan konsultasi.")
    
    while True:
        # Loop ni akan jalan terus untuk dengar perbualan
        ayat_baru = dengar_perbualan()
        
        if ayat_baru:
            # Simpan ayat dalam memori
            transkrip_penuh.append(ayat_baru)
            
            # Keyword untuk berhenti
            if 'stop' in ayat_baru.lower() or 'berhenti' in ayat_baru.lower() or 'tamat' in ayat_baru.lower():
                bercakap("Konsultasi tamat. Menjana laporan sekarang.")
                break
    
    # Bila dah stop, gabungkan semua ayat
    full_conversation = " ".join(transkrip_penuh)
    print(f"\n📄 FULL RAW TRANSCRIPT:\n{full_conversation}\n")
    
    # Hantar ke Llama 3 untuk buat report
    if len(full_conversation) > 10:
        laporan = generate_soap_note(full_conversation)
        print(laporan)
        
        # Save ke file text (boleh tunjuk kat boss)
        with open("Medical_Report.txt", "w") as f:
            f.write(laporan)
        print("\n✅ Report saved to 'Medical_Report.txt'")
    else:
        print("❌ Perbualan terlalu pendek untuk generate report.")
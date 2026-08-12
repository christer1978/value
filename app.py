import os
from PIL import Image
import streamlit as st
from google import genai
from google.genai import types

# ------------------------------------------------------------------------------
# SIDKONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Secondhand Värdering AI",
    page_icon="🏷️",
    layout="centered"
)

st.title("🏷️ Snabbvärdering för Secondhand")
st.caption("Ta en bild för att direkt identifiera och värdera objektet.")

# ------------------------------------------------------------------------------
# API-NYCKEL OCH KLIENT
# API-nyckeln läses i första hand från miljövariabeln GEMINI_API_KEY.
# Om den inte hittas visas ett fält i sidopanelen där du kan skriva in den.
# ------------------------------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("Inställningar")
    if not api_key:
        api_key = st.text_input("Gemini API Key:", type="password")
        st.info("Skaffa en nyckel gratis i Google AI Studio om du saknar en.")

if not api_key:
    st.warning("Vänligen ange din Gemini API-nyckel i sidopanelen för att fortsätta.")
    st.stop()

# Initiera klienten
client = genai.Client(api_key=api_key)

# ------------------------------------------------------------------------------
# KAMERAINPUT & LOGIK
# ------------------------------------------------------------------------------
image_file = st.camera_input("Ta ett kort på objektet")

if image_file:
    # Öppna bilden med PIL
    img = Image.open(image_file)

    # Visa en liten förhandsgranskning och laddningssnurra
    with st.spinner("Analyserar objektet och söker marknadsvärden..."):
        try:
            # Systeminstruktion som döljs helt för användaren
            system_instruction = """
            Du är en expert på loppis, antikviteter och secondhand-värdering på den svenska marknaden.
            Din uppgift är att utifrån en bild snabbt identifiera objektet och ge en rimlig prissättning.
            
            Ge svaret i följande struktur:
            - **Identifiering:** Vad är detta? (Produkt, märke/tillverkare, material, tidsperiod/stil om synligt).
            - **Skick & Detaljer:** Synliga tecken på slitage, stämplar, signaturer eller saknade delar.
            - **Värdering (SEK):** Uppskattat försäljningspris på svensk andrahandsmarknad (Tradera, Vinted, Blocket).
              - *Snabbaffär / Loppispris:* Low-end pris för snabb försäljning.
              - *Marknadsvärde:* Normalt pris vid bra beskrivning online.
            - **Försäljningstext:** En kort och säljande beskrivning (2-3 meningar).
            - **Sökord:** 5-7 relevanta nyckelord utan upprepningar, separerade med kommatecken.
            """

            # Anropa gemini-2.5-flash som är optimerad för snabb bildanalys
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[img, "Identifiera och värdera objektet på bilden."],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2, # Låg temperatur för mer konsekvent/faktaorienterat svar
                )
            )

            st.success("Analys klar!")
            st.markdown("---")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"Ett fel uppstod vid analysen: {e}")
          

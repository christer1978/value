import os
from PIL import Image
import streamlit as st
import google.generativeai as genai

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
# API-NYCKEL
# ------------------------------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("Inställningar")
    if not api_key:
        api_key = st.text_input("Gemini API Key:", type="password")

if not api_key:
    st.warning("Vänligen ange din Gemini API-nyckel i Secrets eller i sidopanelen.")
    st.stop()

# Konfigurera Gemini API
genai.configure(api_key=api_key)

# ------------------------------------------------------------------------------
# KAMERAINPUT & ANALYS
# ------------------------------------------------------------------------------
image_file = st.camera_input("Ta ett kort på objektet")

if image_file:
    img = Image.open(image_file)

    with st.spinner("Analyserar objektet och söker marknadsvärden..."):
        try:
            # Använd den generiska alias-modellen gemini-flash
            model = genai.GenerativeModel("gemini-flash")

            prompt = """
            Du är en expert på loppis, antikviteter och secondhand-värdering på den svenska marknaden.
            Din uppgift är att utifrån bilden snabbt identifiera objektet och ge en rimlig prissättning.
            
            Ge svaret i följande struktur:
            - **Identifiering:** Vad är detta? (Produkt, märke/tillverkare, material, tidsperiod/stil om synligt).
            - **Skick & Detaljer:** Synliga tecken på slitage, stämplar, signaturer eller saknade delar.
            - **Värdering (SEK):** Uppskattat försäljningspris på svensk andrahandsmarknad (Tradera, Vinted, Blocket).
              - *Snabbaffär / Loppispris:* Low-end pris för snabb försäljning.
              - *Marknadsvärde:* Normalt pris vid bra beskrivning online.
            - **Försäljningstext:** En kort och säljande beskrivning (2-3 meningar).
            - **Sökord:** 5-7 relevanta nyckelord utan upprepningar, separerade med kommatecken.
            """

            response = model.generate_content([prompt, img])

            st.success("Analys klar!")
            st.markdown("---")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"Ett fel uppstod vid analysen: {e}")

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
# KAMERAINPUT & DYNAMISK ANALYS
# ------------------------------------------------------------------------------
image_file = st.camera_input("Ta ett kort på objektet")

if image_file:
    img = Image.open(image_file)

    with st.spinner("Hämtar tillgänglig AI-modell och analyserar..."):
        try:
            # 1. Hämta alla tillgängliga modeller för din nyckel
            available_models = [
                m.name for m in genai.list_models() 
                if 'generateContent' in m.supported_generation_methods
            ]

            # 2. Välj automatiskt den bästa modellen (i första hand en Flash-modell)
            chosen_model_name = None
            for m in available_models:
                if "flash" in m:
                    chosen_model_name = m
                    break
            
            # Om ingen flash finns, ta den första tillgängliga modellen
            if not chosen_model_name and available_models:
                chosen_model_name = available_models[0]

            if not chosen_model_name:
                st.error("Ingen kompatibel AI-modell hittades på din API-nyckel.")
                st.stop()

            # 3. Kör analysen med den hittade modellen
            model = genai.GenerativeModel(chosen_model_name)

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

            st.success(f"Analys klar!")
            st.markdown("---")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"Ett fel uppstod vid analysen: {e}")

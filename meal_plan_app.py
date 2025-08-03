# meal_plan_app.py
# Streamlit prototype with GPT integration and clickable PDF export using fpdf2

import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import openai
import unicodedata
import re

# -----------------------------
# SETUP & CONFIGURATION
# -----------------------------
openai.api_key = st.secrets["openai_api_key"] if "openai_api_key" in st.secrets else None

# -----------------------------
# GPT MEAL PLAN FUNCTION
# -----------------------------
def generate_meal_plan_via_gpt(grocery_list):
    prompt = f"""
You are a family meal planner assistant.

Your task is to create a 7-day meal plan with breakfast, lunch, and dinner using ONLY the following grocery items:

{grocery_list}

Each meal should:
- Be named as a realistic dish (e.g. "Tofu Stir Fry", "Baked Chickpea Curry")
- Use ingredients from the list
- Be simple and quick to prepare
- Optionally include a real recipe link (e.g. from BBC Good Food or AllRecipes) if known

Format like this:

Monday:
Breakfast: Meal name — ingredients used
Lunch: Meal name — ingredients used — [Recipe link]
Dinner: Meal name — ingredients used

Repeat for Tuesday through Sunday.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # change to "gpt-4" if available
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating meal plan: {e}"

# -----------------------------
# STREAMLIT APP
# -----------------------------
st.title("🧠 GPT Meal Planner Prototype")
st.write("Paste your grocery list and receive a 7-day meal plan powered by GPT.")

# Input: Grocery List
grocery_input = st.text_area("🛒 Paste your grocery list (one item per line):", height=200)

if st.button("Generate 7-Day Meal Plan"):
    if not grocery_input.strip():
        st.warning("Please enter some grocery items first.")
    elif not openai.api_key:
        st.error("No OpenAI API key found. Please set it via Streamlit secrets.")
    else:
        with st.spinner("Generating meal plan with GPT..."):
            plan_text = generate_meal_plan_via_gpt(grocery_input)
            st.text_area("📋 7-Day Meal Plan:", plan_text, height=600)

            # PDF EXPORT FUNCTION (with hyperlinks using fpdf2)
            class PDF(FPDF):
                def header(self):
                    self.set_font("Helvetica", "B", 14)
                    self.cell(0, 10, "7-Day Meal Plan", ln=True, align="C")
                    self.ln(4)

                def add_meal_plan(self, text):
                    self.set_font("Helvetica", "", 10)
                    lines = text.split("\n")
                    for line in lines:
                        url_match = re.search(r'(https?://\S+)', line)
                        if url_match:
                            url = url_match.group(1)
                            display_text = line.replace(url, "").strip(": ")
                            self.set_text_color(0, 0, 0)
                            if display_text:
                                self.cell(0, 8, f"{display_text}:", ln=True)
                            self.set_text_color(0, 0, 255)
                            self.set_font(style="U")
                            self.cell(0, 8, url, ln=True, link=url)
                            self.set_font(style="")
                            self.set_text_color(0, 0, 0)
                        else:
                            self.cell(0, 8, line, ln=True)

            # Normalize and clean
            safe_text = unicodedata.normalize("NFKD", plan_text).encode("ascii", "ignore").decode("ascii")

            pdf = PDF()
            pdf.add_page()
            pdf.add_meal_plan(safe_text)

            # ✅ Output to memory buffer (fixes encoding issue)
            pdf_bytes = BytesIO()
            pdf.output(pdf_bytes)
            pdf_bytes.seek(0)

            st.download_button("📄 Download Meal Plan PDF", data=pdf_bytes, file_name="7_day_meal_plan.pdf", mime="application/pdf")

# Sidebar instructions
with st.sidebar:
    st.header("💡 How to Use")
    st.markdown("""
    1. Paste your grocery list (one item per line).
    2. Click 'Generate 7-Day Meal Plan'.
    3. GPT will suggest realistic meals based on the ingredients.
    4. View the plan or download it as a PDF with clickable recipe links.

    ✨ Add your OpenAI API key to Streamlit secrets as `openai_api_key`.
    """)




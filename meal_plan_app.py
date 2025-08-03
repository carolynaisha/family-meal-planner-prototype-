# meal_plan_app_prototype.py
# Streamlit prototype for generating a 7-day meal plan from free text grocery input (no fixed keywords or household logic)

import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# -----------------------------
# HELPER FUNCTION
# -----------------------------
def simple_parse_meal_plan(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    ingredients_preview = ", ".join(lines[:5]) + ("..." if len(lines) > 5 else "")
    meals = [
        f"Breakfast: Meal using {ingredients_preview}",
        f"Lunch: Quick meal with {ingredients_preview}",
        f"Dinner: Simple dish from {ingredients_preview}"
    ]
    return meals

# -----------------------------
# STREAMLIT APP
# -----------------------------
st.title("🧠 Minimal Meal Planner Prototype")
st.write("Paste your grocery list and receive a single sample day of meals.")

# Input: Grocery List
grocery_input = st.text_area("🛒 Paste your grocery list (one item per line):", height=200)

if st.button("Generate One-Day Meal Plan"):
    if not grocery_input.strip():
        st.warning("Please enter some grocery items first.")
    else:
        st.success("✅ Sample meal plan generated!")

        meal_texts = simple_parse_meal_plan(grocery_input)
        meal_data = pd.DataFrame({
            "Day": ["Sample Day"],
            "Breakfast": [meal_texts[0]],
            "Lunch": [meal_texts[1]],
            "Dinner": [meal_texts[2]]
        })

        st.dataframe(meal_data)

        # PDF EXPORT FUNCTION
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'One-Day Meal Plan', 0, 1, 'C')

            def meal_section(self, breakfast, lunch, dinner):
                self.set_font('Arial', '', 11)
                self.multi_cell(0, 10, f"Breakfast: {breakfast}\n\nLunch: {lunch}\n\nDinner: {dinner}\n")

        pdf = PDF()
        pdf.add_page()
        pdf.meal_section(meal_texts[0], meal_texts[1], meal_texts[2])

        pdf_output = pdf.output(dest='S').encode('latin-1')
        pdf_bytes = BytesIO(pdf_output)

        st.download_button("📄 Download Meal Plan PDF", data=pdf_bytes, file_name="one_day_meal_plan.pdf", mime="application/pdf")

# Sidebar instructions
with st.sidebar:
    st.header("💡 How to Use")
    st.markdown("""
    1. Paste a free-text grocery list above (one item per line).
    2. Click 'Generate One-Day Meal Plan'.
    3. View your sample day with simple meal descriptions.
    4. Download the plan as a PDF.

    *This version uses your words without fixed meal templates.*
    """)

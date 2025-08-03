# meal_plan_app_prototype.py
# Streamlit prototype with GPT-4 integration for generating a 7-day meal plan from grocery input

import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import openai

# -----------------------------
# SETUP & CONFIGURATION
# -----------------------------
openai.api_key = st.secrets["openai_api_key"] if "openai_api_key" in st.secrets else None

# -----------------------------
# GPT MEAL PLAN FUNCTION
# -----------------------------
def generate_meal_plan_via_gpt(grocery_list):
    prompt = f"""
    You are a helpful meal planner. Given the following grocery list, generate a 7-day meal plan with breakfast, lunch, and dinner.
    Focus on simple, realistic meals that a family could cook with minimal prep. Only use ingredients from this list:

    {grocery_list}

    Output in this format:

    Monday:
    Breakfast: ...
    Lunch: ...
    Dinner: ...

    Tuesday:
    Breakfast: ...
    Lunch: ...
    Dinner: ...

    (Continue this format through Sunday)
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating meal plan: {e}"

# -----------------------------
# STREAMLIT APP
# -----------------------------
st.title("🧠 GPT-4 Meal Planner Prototype")
st.write("Paste your grocery list and receive a 7-day meal plan powered by GPT-4.")

# Input: Grocery List
grocery_input = st.text_area("🛒 Paste your grocery list (one item per line):", height=200)

if st.button("Generate 7-Day Meal Plan"):
    if not grocery_input.strip():
        st.warning("Please enter some grocery items first.")
    elif not openai.api_key:
        st.error("No OpenAI API key found. Please set it via Streamlit secrets.")
    else:
        with st.spinner("Generating meal plan with GPT-4..."):
            plan_text = generate_meal_plan_via_gpt(grocery_input)
            st.text_area("📋 7-Day Meal Plan:", plan_text, height=600)

            # PDF EXPORT FUNCTION
            class PDF(FPDF):
                def header(self):
                    self.set_font('Arial', 'B', 12)
                    self.cell(0, 10, '7-Day Meal Plan', 0, 1, 'C')

                def body(self, text):
                    self.set_font('Arial', '', 10)
                    self.multi_cell(0, 10, text)

            pdf = PDF()
            pdf.add_page()
            pdf.body(plan_text)

            pdf_output = pdf.output(dest='S').encode('latin-1')
            pdf_bytes = BytesIO(pdf_output)

            st.download_button("📄 Download Meal Plan PDF", data=pdf_bytes, file_name="7_day_meal_plan.pdf", mime="application/pdf")

# Sidebar instructions
with st.sidebar:
    st.header("💡 How to Use")
    st.markdown("""
    1. Paste your grocery list (one item per line).
    2. Click 'Generate 7-Day Meal Plan'.
    3. GPT-4 will suggest realistic meals based on the ingredients.
    4. View the plan or download it as a PDF.

    ✨ Add your OpenAI API key to Streamlit secrets as `openai_api_key`.
    """)

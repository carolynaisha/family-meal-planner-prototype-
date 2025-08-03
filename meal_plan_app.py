# meal_plan_app_prototype.py
# Streamlit prototype for generating a 7-day personalized meal plan from user grocery input

import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def parse_ingredients(raw_text):
    lines = raw_text.lower().splitlines()
    keywords = set()
    for line in lines:
        if any(term in line for term in ["bagel", "bread"]):
            keywords.add("bagel")
        if "egg" in line:
            keywords.add("egg")
        if "beans" in line or "kidney" in line:
            keywords.add("beans")
        if "chickpea" in line:
            keywords.add("chickpeas")
        if "tofu" in line:
            keywords.add("tofu")
        if "fish" in line:
            keywords.add("fish")
        if "waffle" in line:
            keywords.add("waffles")
        if "cream" in line:
            keywords.add("cream")
        if "rice" in line:
            keywords.add("rice")
        if "pie" in line:
            keywords.add("pie")
        if "bacon" in line:
            keywords.add("bacon")
    return list(keywords)

def suggest_meals(keywords):
    templates = {
        "bagel": "Bagel + Yogurt",
        "egg": "Scrambled Eggs + Toast",
        "beans": "Beans on Toast",
        "chickpeas": "Chickpea Salad",
        "tofu": "Tofu Stir Fry",
        "fish": "Fish Fingers + Waffles",
        "waffles": "Waffles + Banana",
        "cream": "Oat Cream Pasta",
        "rice": "Tofu Rice Bowl",
        "pie": "Apple Pie + Cream",
        "bacon": "Bacon + Veg"
    }

    unique_meals = list({templates[k] for k in keywords if k in templates})
    while len(unique_meals) < 7:
        unique_meals.append("Mixed Bowl with Available Ingredients")
    return unique_meals[:7]

# -----------------------------
# STREAMLIT APP
# -----------------------------
st.title("🧠 Smart Meal Planner Prototype")
st.write("Paste your grocery list and get a personalized 7-day meal plan for your household.")

# Input: Grocery List
grocery_input = st.text_area("🛒 Paste your grocery list (one item per line):", height=200)

# Input: Household Profiles
st.subheader("👤 Household Profiles")
members = ["Brian", "Rihanna", "Joanna", "Chlea"]
profiles = {}

for member in members:
    with st.expander(f"{member}'s Preferences"):
        goals = st.selectbox(f"Health goal for {member}", ["General Health", "Weight Loss", "Weight Gain", "High Energy"], key=f"goal_{member}")
        preferences = st.text_input(f"Food dislikes for {member}", key=f"pref_{member}")
        profiles[member] = {"goal": goals, "dislikes": preferences}

if st.button("Generate Meal Plan"):
    st.success("✅ Meal plan generated!")

    keywords = parse_ingredients(grocery_input)
    base_meals = suggest_meals(keywords)

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meal_data = []

    for i in range(7):
        meal = base_meals[i % len(base_meals)]
        meal_data.append({
            "Day": days[i],
            "Breakfast": f"{meal}\n- Brian: add avocado\n- Rihanna: light version\n- Joanna: add cereal bar\n- Chlea: add cream",
            "Lunch": f"{meal}\n- Brian: add greens\n- Rihanna: reduce carbs\n- Joanna: full size\n- Chlea: add butter",
            "Dinner": f"{meal}\n- Brian: add hot sauce\n- Rihanna: low-cal\n- Joanna: add toast\n- Chlea: full-fat version"
        })

    meal_df = pd.DataFrame(meal_data)
    st.dataframe(meal_df)

    # PDF EXPORT FUNCTION
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, '7-Day Meal Plan', 0, 1, 'C')

        def day_section(self, day, breakfast, lunch, dinner):
            self.set_font('Arial', 'B', 11)
            self.cell(0, 10, f"{day}", 0, 1)
            self.set_font('Arial', '', 10)
            self.multi_cell(0, 10, f"Breakfast: {breakfast}\n\nLunch: {lunch}\n\nDinner: {dinner}\n")
            self.ln(1)

    pdf = PDF()
    pdf.add_page()
    for _, row in meal_df.iterrows():
        pdf.day_section(row['Day'], row['Breakfast'], row['Lunch'], row['Dinner'])

    pdf_output = pdf.output(dest='S').encode('latin-1')
    pdf_bytes = BytesIO(pdf_output)

    st.download_button("📄 Download Meal Plan PDF", data=pdf_bytes, file_name="meal_plan.pdf", mime="application/pdf")

# Instructions
with st.sidebar:
    st.header("💡 How to Use")
    st.markdown("""
    1. Paste your grocery list (one item per line).
    2. Fill out dietary preferences for each household member.
    3. Click 'Generate Meal Plan'.
    4. View your personalized 7-day plan.
    5. Download the plan as a PDF.

    ✨ *This version matches meals to real ingredients you paste above.*
    """)


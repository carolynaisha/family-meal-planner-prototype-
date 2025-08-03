# meal_plan_app_prototype.py
# Streamlit prototype for generating a 7-day personalized meal plan

import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# -----------------------------
# HOUSEHOLD MEMBER PROFILE FORM
# -----------------------------
st.title("🧠 Smart Meal Planner Prototype")
st.write("Upload your grocery list and get a personalized 7-day meal plan for your household.")

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

    # -----------------------------
    # DYNAMIC MEAL PLAN EXAMPLE
    # -----------------------------
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meals_by_day = [
        {"Breakfast": "Bagel + Yogurt", "Lunch": "Taco Beans", "Dinner": "Tofu Curry"},
        {"Breakfast": "Egg Toast", "Lunch": "Penne + Tomato", "Dinner": "Vegan Sausages + Mash"},
        {"Breakfast": "Waffles + Banana", "Lunch": "Tofu Stir Fry", "Dinner": "Fish Fingers + Beans"},
        {"Breakfast": "Cereal Bar + Buttered Toast", "Lunch": "Black Bean Salad", "Dinner": "Coconut Chickpea Curry"},
        {"Breakfast": "Scrambled Eggs + Bagel", "Lunch": "Chickpeas + Crackers", "Dinner": "Pizza + Greens"},
        {"Breakfast": "Oat Cream + Toast", "Lunch": "Tofu Wrap", "Dinner": "Smoked Bacon + Veg"},
        {"Breakfast": "Fruit Yogurt + Breadsticks", "Lunch": "Egg + Bean Bowl", "Dinner": "Apple Pie + Cream"},
    ]

    meal_data = []
    for i, day in enumerate(days):
        meals = meals_by_day[i]
        meal_data.append({
            "Day": day,
            "Breakfast": f"{meals['Breakfast']}\n- Brian: add avocado\n- Rihanna: light portion\n- Joanna: full portion\n- Chlea: add butter",
            "Lunch": f"{meals['Lunch']}\n- Brian: add chilli\n- Rihanna: low-carb\n- Joanna: add cheese\n- Chlea: add toast",
            "Dinner": f"{meals['Dinner']}\n- Brian: add greens\n- Rihanna: light version\n- Joanna: double beans\n- Chlea: add cream"
        })

    meal_df = pd.DataFrame(meal_data)
    st.dataframe(meal_df)

    # -----------------------------
    # PDF EXPORT FUNCTION
    # -----------------------------
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

# -----------------------------
# INSTRUCTIONS FOR USE
# -----------------------------
with st.sidebar:
    st.header("💡 How to Use")
    st.markdown("""
    1. Paste your grocery list (one item per line).
    2. Fill out dietary preferences for each household member.
    3. Click 'Generate Meal Plan'.
    4. View your personalized 7-day plan.
    5. Download the plan as a PDF.

    ✨ *This is a prototype. Smart recipe matching and dynamic tweaks coming soon!*
    """)


import streamlit as st
from fpdf import FPDF
from io import BytesIO
import openai
import unicodedata
import re

# --- Configuration ---
openai.api_key = st.secrets["openai_api_key"]

# --- GPT Meal Plan Generator ---
def generate_meal_plan(grocery_list, profiles):
    people_lines = "\n".join([
        f"{name}: Goal - {p['goal']}; Dislikes - {p['dislikes']}" for name, p in profiles.items()
    ])

    prompt = f"""
You are a helpful meal planning assistant.

Using ONLY the following grocery list, create a realistic 7-day meal plan with breakfast, lunch, and dinner each day. Keep meals quick and practical. Include a brief recipe link where relevant.

Household dietary needs:
{people_lines}

For each meal, suggest slight modifications for each family member based on their preferences.

Grocery list:
{grocery_list}

Format like:

Monday:
Breakfast: Meal name - ingredients - [recipe link]
  - Brian: tweak
  - Rihanna: tweak
Lunch: ...
Dinner: ...

Repeat through Sunday.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response["choices"][0]["message"]["content"]
st.write("PLAN TEXT for PDF:", plan_text)
# --- PDF Generator (No custom fonts) ---
class PDF(FPDF):
    def __init__(self):
        per().__init__()
        self.set_auto_page_break(auto=True, margin=12)
        self.set_left_margin(12)
        self.set_right_margin(12)
        self.add_page()
        self.set_font("Helvetica", "", 10)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "7-Day Meal Plan", ln=True, align="C")
        self.ln(4)

    def draw_meal_block(self, day, meals):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(230, 240, 255)
        self.cell(0, 8, f"\n{day}", ln=True, fill=True)

        for meal in meals:
            self.set_font("Helvetica", "B", 10)
            self.cell(0, 6, f"{meal['type']}: {meal['title']}", ln=True)
            self.set_font("Helvetica", "", 10)

            # Ingredients
            self.multi_cell(0, 5, f"Ingredients: {meal['ingredients']}")
            self.ln(1)

            # Recipe link
            if meal.get("link"):
                self.set_text_color(0, 0, 255)
                self.set_font("Helvetica", "U", 10)
                self.cell(0, 5, meal["link"], ln=True, link=meal["link"])
                self.set_text_color(0, 0, 0)
                self.set_font("Helvetica", "", 10)
                self.ln(1)

            # Per-person customizations
            if meal.get("tweaks"):
                self.set_font("Helvetica", "I", 10)
                for person, tweak in meal["tweaks"].items():
                    import textwrap
                wrapped = "\n".join(textwrap.wrap(f"  - {person}: {tweak}", width=90))
                self.multi_cell(0, 5, wrapped)
                self.set_font("Helvetica", "", 10)
                self.ln(1)

    def add_plan_from_text(self, raw_text):
        import re
        lines = raw_text.strip().split("\n")
        day = None
        meals = []
        current_meal = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.rstrip(":") in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                if day and meals:
                    self.draw_meal_block(day, meals)
                    day = line.rstrip(":")
                    meals = []

        def add_plan_from_text(self, raw_text):
            import re
            lines = raw_text.strip().split("\n")
                day = None
                meals = []
                current_meal = {}

            for line in lines:
                line = line.strip()
            if not line:
            continue

        # Detect new day
        if line.rstrip(":") in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            if day and meals:
                self.draw_meal_block(day, meals)
            day = line.rstrip(":")
            meals = []
            current_meal = {}

        # Detect new meal
        elif line.startswith(("Breakfast", "Lunch", "Dinner")):
            if current_meal:
                meals.append(current_meal)
            parts = line.split(":", 1)
            meal_type = parts[0].strip()
            details = parts[1].strip() if len(parts) > 1 else ""

            link_match = re.search(r"(https?://\S+)", details)
            link = link_match.group(1) if link_match else None
            details_no_link = details.replace(link, "").strip("- ") if link else details

            title_ingredients = details_no_link.split(" - ", 1)
            title = title_ingredients[0].strip()
            ingredients = title_ingredients[1].strip() if len(title_ingredients) > 1 else ""

            current_meal = {
                "type": meal_type,
                "title": title,
                "ingredients": ingredients,
                "link": link,
                "tweaks": {}
            }

        # Detect per-person tweak
        elif line.startswith("- ") and current_meal:
            try:
                person, tweak = line[2:].split(":", 1)
                current_meal["tweaks"][person.strip()] = tweak.strip()
            except ValueError:
                continue

    # Append last meal and draw final day
    if current_meal:
        meals.append(current_meal)
    if day and meals:
        self.draw_meal_block(day, meals)

# --- Streamlit UI ---
st.title("🧠 7-Day Meal Planner (No Font Dependency)")
grocery_input = st.text_area("🛒 Paste your grocery list (one item per line):", height=200)
st.subheader("👥 Family Member Preferences")


num_members = st.number_input("How many family members to include?", min_value=1, max_value=10, value=4, step=1)

profiles = {}
for i in range(num_members):
    with st.expander(f"Member {i+1}"):
        name = st.text_input("Name", key=f"name_{i}")
        goal = st.selectbox("Health goal", ["General", "Weight Loss", "Energy", "Weight Gain"], key=f"goal_{i}")
        dislikes = st.text_input("Foods to avoid", key=f"dislikes_{i}")
        if name.strip():
            profiles[name] = {"goal": goal, "dislikes": dislikes}


if st.button("Generate Meal Plan"):
    if not grocery_input.strip():
        st.warning("Please enter your grocery list.")
    else:
        with st.spinner("Planning meals..."):
            plan_text = generate_meal_plan(grocery_input, profiles)
            st.text_area("📋 Meal Plan", plan_text, height=600)

            # ✅ Now it's safe to use plan_text here
            safe_text = unicodedata.normalize("NFKD", plan_text).encode("ascii", "ignore").decode("ascii")
            pdf = PDF()
            pdf.add_plan_from_text(safe_text)
            pdf_bytes = BytesIO()
            pdf.output(pdf_bytes)
            pdf_bytes.seek(0)
            st.download_button("📄 Download Meal Plan PDF", data=pdf_bytes, file_name="7_day_meal_plan.pdf", mime="application/pdf")



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
You are a helpful meal planner assistant.

Using ONLY the following grocery list, create a realistic 7-day meal plan with breakfast, lunch, and dinner each day.

Household dietary needs:
{people_lines}

For each meal, suggest slight modifications for each family member based on their preferences.

Grocery list:
{grocery_list}

Format like:

Monday:
Breakfast: Meal name — ingredients — [optional recipe link]
  - Brian: tweak
  - Rihanna: tweak
...
"""


Using ONLY the following grocery list, create a realistic 7-day meal plan with breakfast, lunch, and dinner each day. Keep meals quick and practical. Include a brief recipe link where relevant.

Grocery list:
{grocery_list}

Format like:

Monday:
Breakfast: Meal name — ingredients — [recipe link]
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

# --- PDF Generator (No custom fonts) ---
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=10)
        self.set_left_margin(10)
        self.set_right_margin(10)
        self.add_page()
        self.set_font("Helvetica", "", 10)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "7-Day Meal Plan", ln=True, align="C")
        self.ln(5)

    def draw_meal(self, title, content, url=None):
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 6, title, ln=True, fill=True)
        self.set_font("Helvetica", "", 10)
        if url:
            self.multi_cell(0, 5, content)
            self.set_text_color(0, 0, 255)
            self.set_font("Helvetica", "U", 10)
            self.cell(0, 5, url, ln=True, link=url)
            self.set_font("Helvetica", "", 10)
            self.set_text_color(0, 0, 0)
        else:
            self.multi_cell(0, 5, content)
        self.ln(1)

    def add_plan(self, plan_text):
        lines = plan_text.split("\n")
        for line in lines:
            line = line.strip()
            if line.rstrip(":") in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                self.set_font("Helvetica", "B", 12)
                self.set_fill_color(200, 220, 255)
                self.cell(0, 8, f"\n{line.rstrip(':')}", ln=True, fill=True)
            else:
                meal_type = next((m for m in ["Breakfast", "Lunch", "Dinner"] if line.startswith(m)), None)
                if meal_type:
                    url_match = re.search(r"(https?://\S+)", line)
                    content = line
                    url = None
                    if url_match:
                        url = url_match.group(1)
                        content = line.replace(url, "").strip("- :")
                    self.draw_meal(meal_type, content, url)

# --- Streamlit UI ---
st.title("🧠 7-Day Meal Planner (No Font Dependency)")
grocery_input = st.text_area("🛒 Paste your grocery list (one item per line):", height=200)
st.subheader("👥 Family Member Preferences")
members = ["Brian", "Rihanna", "Joanna", "Chlea"]
profiles = {}

for name in members:
    with st.expander(f"{name}'s Preferences"):
        goal = st.selectbox(f"Health goal for {name}", ["General", "Weight Loss", "Energy", "Weight Gain"], key=f"goal_{name}")
        dislikes = st.text_input(f"Foods to avoid for {name}", key=f"dislikes_{name}")
        profiles[name] = {"goal": goal, "dislikes": dislikes}

if st.button("Generate Meal Plan"):
    if not grocery_input.strip():
        st.warning("Please enter your grocery list.")
    else:
        with st.spinner("Planning meals..."):
            plan_text = generate_meal_plan(grocery_input, profiles)
            st.text_area("📋 Meal Plan", plan_text, height=600)

            # Create and normalize text for PDF
            safe_text = unicodedata.normalize("NFKD", plan_text).encode("ascii", "ignore").decode("ascii")
            pdf = PDF()
            pdf.add_plan(safe_text)
            pdf_bytes = BytesIO()
            pdf.output(pdf_bytes)
            pdf_bytes.seek(0)

            st.download_button("📄 Download Meal Plan PDF", data=pdf_bytes, file_name="7_day_meal_plan.pdf", mime="application/pdf")


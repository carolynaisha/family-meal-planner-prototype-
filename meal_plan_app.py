class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=10)
        self.set_left_margin(10)
        self.set_right_margin(10)
        self.add_page()
        self.set_font("Helvetica", size=9)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "7-Day Meal Plan", ln=True, align="C")
        self.ln(5)

    def draw_meal_box(self, title, content, url=None):
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "B", 9)
        self.cell(0, 6, title, ln=True, fill=True)
        self.set_font("Helvetica", "", 9)
        if url:
            self.multi_cell(0, 5, content)
            self.set_text_color(0, 0, 255)
            self.set_font(style="U")
            self.cell(0, 5, url, ln=True, link=url)
            self.set_font(style="")
            self.set_text_color(0, 0, 0)
        else:
            self.multi_cell(0, 5, content)
        self.ln(1)

    def add_meal_table(self, plan_text):
        import re
        lines = plan_text.split("\n")
        current_day = ""
        icon_map = {"Breakfast": "🍳", "Lunch": "🥪", "Dinner": "🍽️"}

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line[:-1] in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] and line.endswith(":"):
                current_day = line[:-1]
                self.set_font("Helvetica", "B", 11)
                self.set_fill_color(200, 220, 255)
                self.cell(0, 8, f"\n{current_day}", ln=True, fill=True)
            else:
                meal_type = next((key for key in icon_map if line.startswith(key)), None)
                if meal_type:
                    icon = icon_map[meal_type]
                    url_match = re.search(r"(https?://\S+)", line)
                    content = line
                    url = None
                    if url_match:
                        url = url_match.group(1)
                        content = line.replace(url, "").strip("- :")
                    self.draw_meal_box(f"{icon} {meal_type}", content, url)

# Normalize text
import unicodedata
safe_text = unicodedata.normalize("NFKD", plan_text).encode("ascii", "ignore").decode("ascii")

# Create PDF
pdf = PDF()
pdf.add_meal_table(safe_text)

pdf_bytes = BytesIO()
pdf.output(pdf_bytes)
pdf_bytes.seek(0)

st.download_button("📄 Download Meal Plan PDF", data=pdf_bytes, file_name="7_day_meal_plan.pdf", mime="application/pdf")


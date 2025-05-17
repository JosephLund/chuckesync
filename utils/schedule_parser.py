import pdfplumber
import re
from datetime import datetime, timedelta

def parse_schedule(pdf_path):
    shifts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            week_match = re.search(r'Week of ([A-Za-z]+ \d{1,2}, \d{4})', text)
            if not week_match:
                continue

            week_start = datetime.strptime(week_match.group(1), "%B %d, %Y")
            dates = [(week_start + timedelta(days=i)).strftime("%m/%d/%Y") for i in range(7)]

            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row and len(row) == 7:
                        for i, cell in enumerate(row):
                            if cell and '-' in cell:
                                m = re.match(r'(\d{1,2}:\d{2}[ap])-(\d{1,2}:\d{2}[ap])', cell.strip())
                                if m:
                                    s = m.group(1) + 'm'
                                    e = m.group(2) + 'm'
                                    try:
                                        s24 = datetime.strptime(s, "%I:%M%p").strftime("%H:%M")
                                        e24 = datetime.strptime(e, "%I:%M%p").strftime("%H:%M")
                                        shifts.append((dates[i], s24, e24))
                                    except ValueError:
                                        continue
    return shifts

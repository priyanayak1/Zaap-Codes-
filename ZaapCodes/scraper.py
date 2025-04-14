import pdfplumber

def extract_full_pdf_text(pdf_path):
    output = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Handle tables
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    output += "<table>\n"
                    for row in table:
                        output += "  <tr>" + "".join(f"<td>{cell if cell else ''}</td>" for cell in row) + "</tr>\n"
                    output += "</table>\n\n"

            # Handle normal flowing text
            lines = page.extract_text().split('\n') if page.extract_text() else []

            paragraph = ""
            for line in lines:
                clean_line = line.strip()

                if not clean_line:
                    continue  # Skip empty lines
                
                # Detect real headings: longer than 4 letters, all uppercase, very few words
                if clean_line.isupper() and len(clean_line.split()) >= 3 and len(clean_line) > 20:
                    if paragraph:
                        output += f"<p class='indented'>{paragraph.strip()}</p>\n"
                        paragraph = ""
                    output += f"<h2>{clean_line}</h2>\n"

                elif len(clean_line.split()) <= 3 and clean_line.isupper():
                    # VERY small chunks like "LSC IBC" (inside tables or side notes)
                    paragraph += " " + clean_line

                else:
                    # Merge regular flowing lines
                    paragraph += " " + clean_line

            if paragraph:
                output += f"<p class='indented'>{paragraph.strip()}</p>\n"

            output += "\n\n"

    return output

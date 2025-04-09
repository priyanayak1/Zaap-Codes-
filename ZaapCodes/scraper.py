# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time

# def scrape_fulton_building_code():
#     # Setup headless Chrome (real)
#     options = Options()
#     options.add_argument('--headless')  # <-- Correct format
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_argument('--disable-gpu')
#     options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')

#     driver = webdriver.Chrome(options=options)

#     try:
#         url = "https://library.municode.com/ga/fulton_county/codes/code_of_ordinances"
#         driver.get(url)

#         wait = WebDriverWait(driver, 20)  # Wait longer to be safe

#         # 1. Wait until TOC is visible
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "toc-entry-title")))
#         time.sleep(2)  # Municode still loads slowly even after TOC appears

#         # 2. Find Chapter 14 link
#         chapters = driver.find_elements(By.CLASS_NAME, "toc-entry-title")

#         target_chapter = None
#         for chapter in chapters:
#             if "Buildings and Building Regulations" in chapter.text:
#                 target_chapter = chapter
#                 break
        
#         if not target_chapter:
#             return "❌ Could not find Chapter 14 link on the page."

#         print("✅ Found Chapter 14. Clicking...")
#         target_chapter.click()  # Selenium clicks!

#         # 3. Wait for section text to appear
#         time.sleep(5)  # Allow content to load

#         body_text = driver.find_element(By.TAG_NAME, 'body').text

#         if "Sec. 14-41" in body_text:
#             print("✅ Found Section 14-41")
#             start_index = body_text.find("Sec. 14-41")
#             snippet = body_text[start_index:start_index + 3000]
#             return snippet
#         else:
#             return "❌ Could not find Section 14-41 text after clicking Chapter 14."

#     except Exception as e:
#         print(f"❌ Scrape failed: {e}")
#         return f"Scrape error: {e}"

#     finally:
#         driver.quit()
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

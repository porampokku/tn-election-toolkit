import pdfplumber

pdf = "output/2026/01_TIRUVALLUR/AC001_Gummidipoondi.pdf"

with pdfplumber.open(pdf) as document:

    print("Pages:", len(document.pages))

    page = document.pages[0]

    print("\n------ TEXT ------\n")
    print(page.extract_text())

    print("\n------ TABLES ------\n")

    tables = page.extract_tables()

    print("Tables found:", len(tables))

    for i, table in enumerate(tables):
        print(f"\nTable {i + 1}")

        for row in table[:10]:
            print(row)

import os
import re

DOCS_DIR = "docs"

PDF_PAGE_TEMPLATE = """# {title}

[⬇️ Scarica il PDF]({pdf_filename}){{ .md-button .md-button--primary }}

---

<iframe class="pdf" src="../{pdf_filename}"></iframe>
"""

INDEX_PAGE_TEMPLATE = """# {category_name}

<div class="cards" markdown>

{cards_content}

</div>
"""

INDEX_EMPTY_TEMPLATE = """# {category_name}

!!! info "In arrivo"
    Gli appunti del {category_name_lower} non sono ancora stati caricati.
"""

def format_title(filename):
    """Formatta il nome del file PDF in un titolo leggibile."""
    base_name = os.path.splitext(filename)[0]
    title = base_name.replace("_", " ").replace("-", " ").title()
    return base_name, title

def generate_markdown_files():
    for root, dirs, files in os.walk(DOCS_DIR):
        if root == DOCS_DIR:
            continue

        category_name = os.path.basename(root)
        pdf_files = [f for f in files if f.endswith(".pdf")]

        index_filepath = os.path.join(root, "index.md")

        if not pdf_files:
            index_content = INDEX_EMPTY_TEMPLATE.format(
                category_name=category_name,
                category_name_lower=category_name.lower()
            )
            with open(index_filepath, "w", encoding="utf-8") as f:
                f.write(index_content)
            print(f"Creato Index (Vuoto): {index_filepath}")
            continue

        subjects = {}

        for pdf_file in sorted(pdf_files):
            base_name, title = format_title(pdf_file)
            md_filename = f"{base_name}.md"
            md_filepath = os.path.join(root, md_filename)

            # Genera il file .md del singolo PDF
            md_content = PDF_PAGE_TEMPLATE.format(
                title=title,
                pdf_filename=pdf_file
            )
            with open(md_filepath, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"Creato Appunto: {md_filepath}")

            parts = base_name.split("_")
            if len(parts) > 1 and parts[-1].lower() in ["teoria", "domande", "formulario", "esercizio", "esercizi", "modulo", "secondo_modulo"]:
                materia = " ".join(parts[:-1]).title()
                tipo = parts[-1].title()
            else:
                materia = title
                tipo = None

            if materia not in subjects:
                subjects[materia] = []

            subjects[materia].append({
                "title": title,
                "link": md_filename,
                "tipo": tipo
            })

        cards_blocks = []
        for materia, docs in subjects.items():
            icon = ":material-book-open-page-variant:"

            if len(docs) == 1 and not docs[0]["tipo"]:
                card_html = f"""<div markdown>
### {icon} [{materia}]({docs[0]['link']})
Appunti del corso.
</div>"""
            else:
                sub_links = []
                for d in docs:
                    label = d["tipo"] if d["tipo"] else d["title"]
                    sub_links.append(f"[{label}]({d['link']})")

                links_str = " · ".join(sub_links)
                card_html = f"""<div markdown>
### {icon} {materia}
{links_str}
</div>"""

            cards_blocks.append(card_html)

        index_content = INDEX_PAGE_TEMPLATE.format(
            category_name=category_name,
            cards_content="\n\n".join(cards_blocks)
        )

        with open(index_filepath, "w", encoding="utf-8") as f:
            f.write(index_content)
        print(f"Creato Index con Cards: {index_filepath}")

if __name__ == "__main__":
    generate_markdown_files()

from pathlib import Path
from urllib.parse import quote

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
ALLOWED_YEAR_KEYWORDS = ["anno", "year"]
SMALL_WORDS = {"di", "del", "della", "dei", "delle", "e", "il", "la", "le", "in", "per", "a", "da", "con", "ex"}
MARKER = "<!-- auto-generated -->"
SUFFIXES = ["secondo_modulo", "formulario", "teoria", "domande"]

COFFEE_URL = "https://paypal.me/tartaglionemarco"

PDF_PAGE_TEMPLATE = """{marker}
# {title}

[:material-download: Scarica il PDF]({pdf_url}){{ .md-button .md-button--primary download }}

---

<iframe class="pdf" src="../{pdf_url}"></iframe>

---

Ti sono stati utili questi appunti? [:material-coffee: Se vuoi offrirmi un caffè]({coffee_url}){{ target="_blank" rel="noopener" }}
"""

INDEX_PAGE_TEMPLATE = """{marker}
# {category_title}

<div class="cards" markdown>

{cards_content}

</div>
"""

INDEX_EMPTY_TEMPLATE = """{marker}
# {category_title}

!!! info "In arrivo"
    Gli appunti del {category_lower} non sono ancora stati caricati.
"""

CARD_TEMPLATE = """<div markdown>
### :material-book-open-page-variant: [{title}]({md_url})
Appunti del corso.
</div>"""


def format_title(name):
    words = name.replace("_", " ").replace("-", " ").split()
    out = []
    for i, w in enumerate(words):
        out.append(w.capitalize() if i == 0 or w.lower() not in SMALL_WORDS else w.lower())
    return " ".join(out)


def format_pdf_title(stem):
    subject, suffix = stem, None
    for s in SUFFIXES:
        if stem.lower().endswith("_" + s):
            subject, suffix = stem[: -(len(s) + 1)], s
            break

    subject_title = format_title(subject)
    return f"{subject_title} - {format_title(suffix)}" if suffix else subject_title


def is_year_folder(folder_name):
    return any(k in folder_name.lower() for k in ALLOWED_YEAR_KEYWORDS)


def can_write(path):
    if not path.exists():
        return True
    return MARKER in path.read_text(encoding="utf-8")


def write(path, content):
    if not can_write(path):
        print(f"Saltato (modificato a mano): {path}")
        return False
    path.write_text(content, encoding="utf-8")
    print(f"Scritto: {path}")
    return True


def generate_markdown_files():
    for folder in sorted(p for p in DOCS_DIR.iterdir() if p.is_dir()):
        if not is_year_folder(folder.name):
            continue

        category_title = format_title(folder.name)
        pdf_files = [f for f in folder.iterdir() if f.suffix.lower() == ".pdf"]
        index_path = folder / "index.md"

        if not pdf_files:
            write(index_path, INDEX_EMPTY_TEMPLATE.format(
                marker=MARKER,
                category_title=category_title,
                category_lower=category_title.lower(),
            ))
            continue

        entries = sorted(((format_pdf_title(p.stem), p) for p in pdf_files), key=lambda e: e[0].lower())

        cards = []
        for title, pdf in entries:
            md_name = f"{pdf.stem}.md"

            write(folder / md_name, PDF_PAGE_TEMPLATE.format(
                marker=MARKER,
                title=title,
                pdf_url=quote(pdf.name),
                coffee_url=COFFEE_URL
            ))
            cards.append(CARD_TEMPLATE.format(title=title, md_url=quote(md_name)))

        write(index_path, INDEX_PAGE_TEMPLATE.format(
            marker=MARKER,
            category_title=category_title,
            cards_content="\n\n".join(cards),
        ))


if __name__ == "__main__":
    generate_markdown_files()

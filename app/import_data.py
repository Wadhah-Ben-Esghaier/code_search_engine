from pathlib import Path
import xml.etree.ElementTree as ET
from .models import Page
from sqlmodel import Session, select
from .models import Page, Term, TermFrequency
from .storage import BASE_DIR, engine, create_tables
from .textutils import load_stop_words, parse_wiki_text, compute_frequencies

def read_pages(path: Path) -> list[Page]:
    tree = ET.parse(path)
    root = tree.getroot()
    pages = []

    for element in root.findall("{*}page"):
        page_id = element.findtext("{*}id")
        title = element.findtext("{*}title")
        text = element.findtext("{*}revision/{*}text", default="")

        if page_id is None or title is None:
            raise ValueError("Un article ne possède pas d'identifiant ou de titre.")

        page = Page(id=int(page_id), title=title, text=text)
        pages.append(page)

    return pages

def import_xml(path: Path) -> None:
    pages = read_pages(path)
    stop_words = load_stop_words(BASE_DIR / "data" / "stopwords-fr.txt")
    create_tables()

    with Session(engine) as session:
        if session.exec(select(Page.id).limit(1)).first() is not None:
            raise ValueError("La base contient déjà des articles.")

        term_ids: dict[str, int] = {}

        for page in pages:
            session.add(page)

            plain_text = parse_wiki_text(page.text)
            frequencies = compute_frequencies(plain_text, stop_words)

            for word, frequency in frequencies.items():
                if word not in term_ids:
                    term = Term(term=word)
                    session.add(term)
                    session.flush()

                    if term.id is None:
                        raise RuntimeError("L'identifiant du mot n'a pas été généré.")

                    term_ids[word] = term.id

                term_frequency = TermFrequency(term_id=term_ids[word], page_id=page.id, frequency=frequency)
                session.add(term_frequency)

        session.commit()

    print(f"{len(pages)} articles importés.")

if __name__ == "__main__":
    import_xml(BASE_DIR / "data" / "mediawiki-small.xml")
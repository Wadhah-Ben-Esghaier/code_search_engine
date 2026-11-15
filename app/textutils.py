from pathlib import Path
import wikitextparser
import re

def load_stop_words(path: Path) -> set[str]:
    with path.open(encoding="utf-8") as file:
        return {
            word
            for line in file
            if (word := line.strip().lower())
        }

def parse_wiki_text(wiki_text: str) -> str:
    parsed = wikitextparser.parse(wiki_text)

    return parsed.plain_text(
        replace_templates=True,
        replace_parser_functions=True,
        replace_parameters=True,
        replace_tags=True,
        replace_external_links=True,
        replace_wikilinks=True,
        replace_bolds_and_italics=True,
        replace_tables=True,
    )

def compute_frequencies(text: str,ignore: set[str]) -> dict[str, float]:
    occurrences: dict[str, int] = {}
    total = 0

    for word in re.findall(r"\b\w+\b", text.lower()):
        if word not in ignore:
            occurrences[word] = occurrences.get(word, 0) + 1
            total += 1

    return {word: count / total for word, count in occurrences.items()}
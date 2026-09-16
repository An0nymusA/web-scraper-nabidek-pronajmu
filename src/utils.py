import re
from typing import Iterable

def flatten(xs):
    """https://stackoverflow.com/a/2158532
    """
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


_PRICE_PATTERN = re.compile(r"\d+(?:[\s\u00a0]\d{3})*(?:[.,]\d+)?")
_SIZE_PATTERN = re.compile(r"(\d+(?:[.,]\d+)?)\s*m\s*(?:2|²)", re.IGNORECASE)


def parse_price(price: int | float | str) -> float | None:
    """Získá číselnou cenu z hodnoty nabídky

    Args:
        price (int | float | str): Cena tak, jak ji poskytl scraper

    Returns:
        float | None: Cena v Kč, nebo None pokud ji nelze určit
    """

    if isinstance(price, (int, float)):
        return float(price)

    match = _PRICE_PATTERN.search(str(price))
    if match is None:
        return None

    return float(re.sub(r"[^\d.]", "", match.group().replace(",", ".")))


def parse_size(title: str) -> float | None:
    """Získá výměru bytu z názvu nabídky (např. "Pronájem 2+kk 45 m²")

    Args:
        title (str): Název nabídky

    Returns:
        float | None: Výměra v m², nebo None pokud ji nelze určit
    """

    match = _SIZE_PATTERN.search(title or "")
    if match is None:
        return None

    return float(match.group(1).replace(",", "."))

import logging
import traceback

from config import *
from disposition import Disposition
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_base import ScraperBase
from scrapers.scraper_bravis import ScraperBravis
from scrapers.scraper_euro_bydleni import ScraperEuroBydleni
from scrapers.scraper_idnes_reality import ScraperIdnesReality
from scrapers.scraper_realcity import ScraperRealcity
from scrapers.scraper_realingo import ScraperRealingo
from scrapers.scraper_remax import ScraperRemax
from scrapers.scraper_sreality import ScraperSreality
from scrapers.scraper_ulov_domov import ScraperUlovDomov
from scrapers.scraper_bezrealitky import ScraperBezrealitky
from utils import parse_price, parse_size


def create_scrapers(dispositions: Disposition) -> list[ScraperBase]:
    return [
        ScraperBravis(dispositions),
        ScraperEuroBydleni(dispositions),
        ScraperIdnesReality(dispositions),
        ScraperRealcity(dispositions),
        #ScraperRealingo(dispositions),
        ScraperRemax(dispositions),
        ScraperSreality(dispositions),
        ScraperUlovDomov(dispositions),
        ScraperBezrealitky(dispositions),
    ]


def offer_matches_filters(offer: RentalOffer, min_price: int = 0, min_size: int = 0, max_price: int = 0) -> bool:
    """Ověří, zda nabídka splňuje nastavené cenové rozmezí a minimální výměru

    Nabídky, u kterých se cenu nebo výměru nepodařilo určit, jsou ponechány.

    Args:
        offer (RentalOffer): Kontrolovaná nabídka
        min_price (int): Minimální cena v Kč (0 = bez omezení)
        min_size (int): Minimální výměra v m² (0 = bez omezení)
        max_price (int): Maximální cena v Kč (0 = bez omezení)

    Returns:
        bool: True pokud nabídka vyhovuje nastaveným filtrům
    """

    if min_price > 0 or max_price > 0:
        price = parse_price(offer.price)

        if price is not None:
            if min_price > 0 and price < min_price:
                return False

            if max_price > 0 and price > max_price:
                return False

    if min_size > 0:
        size = parse_size(offer.title)
        if size is not None and size < min_size:
            return False

    return True


def fetch_latest_offers(scrapers: list[ScraperBase], min_price: int = 0, min_size: int = 0, max_price: int = 0) -> list[RentalOffer]:
    """Získá všechny nejnovější nabídky z dostupných serverů

    Args:
        scrapers (list[ScraperBase]): Seznam scraperů, ze kterých se nabídky načtou
        min_price (int): Minimální cena v Kč (0 = bez omezení)
        min_size (int): Minimální výměra v m² (0 = bez omezení)
        max_price (int): Maximální cena v Kč (0 = bez omezení)

    Returns:
        list[RentalOffer]: Seznam nabídek
    """

    offers: list[RentalOffer] = []
    for scraper in scrapers:
        try:
            for offer in scraper.get_latest_offers():
                if not offer_matches_filters(offer, min_price, min_size, max_price):
                    logging.debug("Offer filtered out: {} ({})".format(offer.title, offer.link))
                    continue

                offers.append(offer)
        except Exception:
            logging.error(traceback.format_exc())

    return offers

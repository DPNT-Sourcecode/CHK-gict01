from dataclasses import dataclass
import re
from typing import List, Dict, Tuple

PRICE_IDX = 0
SKU_IDX = 1
OFFERS_IDX = 2

RE_FREEBIE = re.compile(r"(?P<qnt_required>\d+)(?P<sku_required>[A-Z]) get (?P<qnt_offered>(one|two|\d+)\s?)(?P<sku_offered>[A-Z])")
RE_DISCOUNT = re.compile(r"(?P<qnt_required>\d+)(?P<sku_required>[A-Z]) for (?P<price>\d+)")


CATALOG_SOURCE = """
+------+-------+------------------------+
| A    | 50    | 3A for 130, 5A for 200 |
| B    | 30    | 2B for 45              |
| C    | 20    |                        |
| D    | 15    |                        |
| E    | 40    | 2E get one B free      |
| F    | 10    | 2F get one F free      |
| G    | 20    |                        |
| H    | 10    | 5H for 45, 10H for 80  |
| I    | 35    |                        |
| J    | 60    |                        |
| K    | 80    | 2K for 150             |
| L    | 90    |                        |
| M    | 15    |                        |
| N    | 40    | 3N get one M free      |
| O    | 10    |                        |
| P    | 50    | 5P for 200             |
| Q    | 30    | 3Q for 80              |
| R    | 50    | 3R get one Q free      |
| S    | 30    |                        |
| T    | 20    |                        |
| U    | 40    | 3U get one U free      |
| V    | 50    | 2V for 90, 3V for 130  |
| W    | 20    |                        |
| X    | 90    |                        |
| Y    | 10    |                        |
| Z    | 50    |                        |
+------+-------+------------------------+
"""


@dataclass
class Freebie:
    sku_required: str
    qnt_required: int
    sku_offered: str
    qnt_offered: int


@dataclass
class Discount:
    qnt_required: int
    price: int


def load_catalog(catalog: str) -> Tuple[Dict[str, int], Dict[str, List[Freebie]], Dict[str, List[Discount]]]:
    price_list = {}
    freebies = {}
    discounts = {}

    for line in str.splitlines('\n'):
        if not line or not line.startswith('|'):
            continue
        tokens = line[1:-1].split('|')
        if len(tokens) != 3:
            raise ValueError("SKU catalog is corrupted!")
        sku = tokens[SKU_IDX].replace(' ', '')
        price = int(tokens[PRICE_IDX].replace(' ', ''))  # Will raise ValueError on invalid integer
        if sku in price_list:
            raise ValueError(f"Duplicate entry found in catalog for {sku}:\n{line}")
        if price <= 0:
            raise ValueError(f"Incorrect price detected for {sku}:\n{line}")
        price_list[sku] = price
        _parse_offers(freebies, discounts, sku, tokens[OFFERS_IDX])
    return price_list, freebies, discounts


def _parse_offers(
        freebies: Dict[str, List[Freebie]],
        discounts: Dict[str, List[Discount]],
        sku: str,
        new_offers: str
) -> None:
    endpos = len(new_offers)

    # Process freebies
    idx = 0
    while idx < endpos:
        m = RE_FREEBIE.search(new_offers, idx, endpos)
        if m is None:
            break
        idx += m.span()
        if sku != m.group('sku_required'):
            raise ValueError(f"Freebie offer for {m.group('sku_required')} specified in wrong SKU entry {sku}")
        if sku not in freebies:
            freebies[sku] = []
        freebies[sku].append(Freebie(
            m.group('sku_required'),
            int(m.group('qnt_required')),
            m.group('sku_offered'),
            _freebies_to_quantity(m.group('qnt_offered'))
        ))

    # Process multi-buy discounts
    idx = 0
    while idx < endpos:
        m = RE_DISCOUNT.search(new_offers, idx, endpos)
        if m is None:
            break
        idx += m.span()
        if sku != m.group('sku_required'):
            raise ValueError(f"Multi-buy offer for {m.group('sku_required')} specified in wrong SKU entry {sku}")
        if sku not in discounts:
            discounts[sku] = []
        discounts[sku].append(Discount(
            int(m.group('qnt_required')),
            int(m.group('price'))
        ))


def _freebies_to_quantity(qnt_offered: str) -> int:
    if qnt_offered == 'one':
        return 1
    if qnt_offered == 'two':
        return 2
    return int(qnt_offered)  # Will raise on bad input


PRICE_TABLE, FREEBIES, SPECIAL_OFFERS = load_catalog(CATALOG_SOURCE)


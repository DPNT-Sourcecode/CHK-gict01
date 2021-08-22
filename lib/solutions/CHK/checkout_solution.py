from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class Freebie:
    qnt_required: int
    sku_offered: str
    qnt_offered: int


@dataclass
class Discount:
    qnt_required: int
    price: int


PRICE_TABLE = {
    'A': 50,
    'B': 30,
    'C': 20,
    'D': 15,
    'E': 40,
}

FREEBIES = {
    'E': [
        Freebie(2, 'B', 1)
    ]
}

# Ongoing special offers for price discounts, must be ordered by quantity required in decreasing order
SPECIAL_OFFERS = {
    'A': [
        Discount(5, 200),
        Discount(3, 130),
    ],
    'B': [
        Discount(2, 45),
    ],
}


# noinspection PyUnusedLocal
# skus = unicode string
def checkout(skus: str) -> int:
    if not isinstance(skus, str):
        # Bad input type, expecting string
        return -1

    order = {}
    for item in skus:
        if item not in order:
            # Unknown SKU detected
            if item not in PRICE_TABLE:
                return -1
            order[item] = 1
        else:
            order[item] += 1

    # Apply freebies
    order = _apply_freebies(order)

    # Apply discounts and compute order total
    return _compute_total_with_discounts(order)


def _apply_freebies(order: Dict[str, int]) -> Dict[str, int]:
    parsed_order = order.copy()
    for sku, freebies in FREEBIES.items():
        qnt_available = order[sku]
        if sku not in order:
            continue
        for details in freebies:
            qnt_available = _apply_single_freebie(parsed_order, qnt_available, details)
    return parsed_order


def _apply_single_freebie(order: Dict[str, int], qnt: int, freebie: Freebie) -> int:
    if freebie.qnt_required <= qnt and freebie.sku_offered in order:
        sets = qnt // freebie.qnt_required
        qnt %= freebie.qnt_required
        order[freebie.sku_offered] = max(0, order[freebie.sku_offered] - sets*freebie.qnt_offered)
    return qnt


def _compute_total_with_discounts(order: Dict[str, int]) -> int:
    total = 0
    for item, qnt in order.items():
        if item not in SPECIAL_OFFERS:
            continue

        for discount in SPECIAL_OFFERS[item]:
            total, qnt = _apply_discount(total, qnt, discount)
        total += qnt * PRICE_TABLE[item]
    return total


def _apply_discount(subtotal: int, qnt: int, discount: Discount) -> Tuple[int, int]:
    if discount.qnt_required <= qnt:
        sets = qnt // discount.qnt_required
        subtotal += sets * discount.price
        qnt %= discount.qnt_required
    return subtotal, qnt

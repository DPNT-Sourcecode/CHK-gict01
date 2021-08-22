from typing import Dict, Tuple

from .sku_catalog import PRICE_TABLE, FREEBIES, SPECIAL_OFFERS, Freebie, Discount

# @dataclass
# class Freebie:
#     sku_required: str
#     qnt_required: int
#     sku_offered: str
#     qnt_offered: int
#
#
# @dataclass
# class Discount:
#     qnt_required: int
#     price: int
#
#
# PRICE_TABLE = {
#     'A': 50,
#     'B': 30,
#     'C': 20,
#     'D': 15,
#     'E': 40,
#     'F': 10,
# }
#
# FREEBIES = {
#     'E': [
#         Freebie('E', 2, 'B', 1)
#     ],
#     'F': [
#         Freebie('F', 2, 'F', 1)
#     ]
# }
#
# # Ongoing special offers for price discounts, must be ordered by quantity required in decreasing order
# SPECIAL_OFFERS = {
#     'A': [
#         Discount(5, 200),
#         Discount(3, 130),
#     ],
#     'B': [
#         Discount(2, 45),
#     ],
# }


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
        if sku not in order:
            continue
        qnt_available = order[sku]
        for details in freebies:
            qnt_available = _apply_single_freebie(parsed_order, qnt_available, details)
    return parsed_order


def _apply_single_freebie(order: Dict[str, int], qnt: int, freebie: Freebie) -> int:
    if freebie.sku_required == freebie.sku_offered:
        qnt_req = freebie.qnt_required + freebie.qnt_offered
    else:
        qnt_req = freebie.qnt_required
    if qnt_req <= qnt and freebie.sku_offered in order:
        sets = qnt // qnt_req
        qnt %= qnt_req
        order[freebie.sku_offered] = max(0, order[freebie.sku_offered] - sets*freebie.qnt_offered)
    return qnt


def _compute_total_with_discounts(order: Dict[str, int]) -> int:
    total = 0
    for item, qnt in order.items():
        if item in SPECIAL_OFFERS:
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

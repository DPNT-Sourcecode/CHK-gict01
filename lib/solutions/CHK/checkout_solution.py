from typing import Dict, Tuple, List

from .sku_catalog import PRICE_TABLE, FREEBIES, GROUPBUYS, SPECIAL_OFFERS, Freebie, Discount, GroupBuy


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

    # Apply group-buy offers
    order, subtotal = _apply_group_buys(order)

    # Apply discounts and compute order total
    return subtotal + _compute_total_with_discounts(order)


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


def _apply_group_buys(order: Dict[str, int]) -> Tuple[Dict[str, int], int]:
    parsed_order = order.copy()
    subtotal = 0
    for sku in order:
        if sku not in GROUPBUYS:
            continue
        for details in GROUPBUYS[sku]:
            # Since we need to favor the customer, we want to discount quantities starting from most expensive item
            sorted_skus = _get_sorted_accepted_skus(details, order)
            qnt_available = sum([parsed_order[acpt] for acpt in sorted_skus])
            if details.qnt_required <= qnt_available:
                sets = qnt_available // details.qnt_required
                subtotal += sets * details.price
                qnt_to_discount = sets * details.qnt_required
                for acpt in sorted_skus:
                    while qnt_to_discount > 0 and parsed_order[acpt] > 0:
                        parsed_order[acpt] -= 1
                        qnt_to_discount -= 1
    return parsed_order, subtotal


def _get_sorted_accepted_skus(groupbuy: GroupBuy, order: Dict[str, int]) -> List[str]:
    """Sorts accepted SKU pertaining to a group-buy offer by price in descending order"""
    price_ordered_skus = []
    for acpt in groupbuy.skus_accepted:
        if acpt not in order:
            continue
        inserted = False
        for idx, other in enumerate(price_ordered_skus):
            if PRICE_TABLE[acpt] > PRICE_TABLE[other]:
                price_ordered_skus.insert(idx, acpt)
                inserted = True
                break
        if not inserted:
            price_ordered_skus.append(acpt)
    return price_ordered_skus


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

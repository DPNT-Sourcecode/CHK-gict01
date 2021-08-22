PRICE_TABLE = {
    'A': 50,
    'B': 30,
    'C': 20,
    'D': 15,
}

SPECIAL_OFFERS = {
    'A': (3, 130),
    'B': (2, 45)
}
SO_QUANTITY = 0
SO_PRICE = 1


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

    total = 0
    for item, qnt in order.items():
        if item in SPECIAL_OFFERS:
            sets = qnt // SPECIAL_OFFERS[item][SO_QUANTITY]
            total += sets * SPECIAL_OFFERS[item][SO_PRICE]
            qnt %= SPECIAL_OFFERS[item][SO_QUANTITY]
        total += qnt * PRICE_TABLE[item]
    return total


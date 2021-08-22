import pytest

from solutions.CHK import checkout, Discount, Freebie
from solutions.CHK.checkout_solution import _apply_discount, _apply_single_freebie


def test_apply_discount():
    subtotal = 50
    remainder_qnt = 1
    assert _apply_discount(0, 3, Discount(2, 50)) == (subtotal, remainder_qnt)


def test_apply_freebie():
    order = {
        'Y': 5,
        'Z': 3
    }
    remainder_qnt = _apply_single_freebie(order, order['Y'], Freebie('Y', 2, 'Z', 2))
    assert order['Z'] == 0
    assert remainder_qnt == 1


class TestCheckout:
    def test_detects_invalid_input(self):
        assert checkout(['A', 'B']) == -1

    @pytest.mark.parametrize('order, expected', [
        ("ABCD", 115),
        ("AABCCDD", 200),
        ("ACBDCDADD", 230),
        ("", 0),
    ])
    def test_order_calculation(self, order, expected):
        assert checkout(order) == expected

    @pytest.mark.parametrize('order, expected', [
        ("AAAAAAAA", 330),
        ("BBBB", 90),
        ("DAABCAB", 210),
    ])
    def test_detects_promotions(self, order, expected):
        assert checkout(order) == expected

    @pytest.mark.parametrize('order, expected', [
        ("EEAA", 180),
        ("EEEBB", 150),
        ('FFF', 20),
    ])
    def test_detects_freebies(self, order, expected):
        assert checkout(order) == expected

    @pytest.mark.parametrize('order, expected', [
        ("EEAAAAABBB", 325),
    ])
    def test_applies_freebies_and_discounts(self, order, expected):
        assert checkout(order) == expected


import pytest

from solutions.CHK import checkout


class TestCheckout:
    def test_detects_invalid_input(self):
        assert checkout(['A', 'B']) == -1

    def test_detects_unknown_sku(self):
        assert checkout('ABF') == -1

    @pytest.mark.parametrize('order, expected', [
        ("ABCD", 115),
        ("AABCCDD", 200),
        ("ACBDCDADD", 230),
        ("", 0),
    ])
    def test_order_calculation(self, order, expected):
        assert checkout(order) == expected

    @pytest.mark.parametrize('order, expected', [
        ("AAAAAAA", 310),
        ("BBBB", 90),
        ("DAABCAB", 210),
    ])
    def test_detects_promotions(self, order, expected):
        assert checkout(order) == expected

import pytest

from model.investment_model import InvestmentModel
from view.investment_view import parse_float_from_entry


class Entry:
    def __init__(self, value): self.value = value
    def get(self): return self.value


@pytest.mark.parametrize("raw,expected", [("1 234,5", 1234.5), ("", 0.0), ("  ", 0.0), ("3.5", 3.5)])
def test_parse_valid_entries(raw, expected):
    assert parse_float_from_entry(Entry(raw)) == pytest.approx(expected)


@pytest.mark.parametrize("raw", ["abc", "12a", "1.2.3"])
def test_parse_invalid_entries_raise(raw):
    with pytest.raises(ValueError, match="n'est pas un nombre"):
        parse_float_from_entry(Entry(raw))


@pytest.mark.parametrize("field,value,message", [
    ("Loyer mensuel (€)", 0, "Loyer mensuel"),
    ("Vacance locative (mois/an)", 15, "Vacance locative"),
    ("Taux d'intérêt annuel (%)", -1, "Taux d'intérêt"),
    ("Durée du prêt (années)", 0, "Durée du prêt"),
    ("Gestion en agence (% du loyer)", 120, "Gestion en agence"),
    ("Apport (€)", -5, "Apport"),
])
def test_compute_rejects_invalid_values(view_inputs, field, value, message):
    view_inputs[field] = value
    with pytest.raises(ValueError, match=message):
        InvestmentModel().compute(view_inputs)


def test_presenter_reports_invalid_input(make_presenter):
    presenter, view = make_presenter()
    view.inputs["Loyer mensuel (€)"] = 0
    view.calculate()
    assert view.errors and "Loyer mensuel" in view.errors[0]
    assert view.recommendation is None

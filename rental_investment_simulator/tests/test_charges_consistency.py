import pytest

from model.investment_model import InvestmentModel

NON_CHARGE_KEYS = {"Mensualité prêt", "Cashflow"}


@pytest.mark.parametrize("vacance", [0, 1, 3])
def test_pie_charges_sum_to_monthly_charges(view_inputs, vacance):
    view_inputs.update({"gli": 240, "pno": 120,
                        "gestion_pct": 7, "vacancy_months": vacance})
    res = InvestmentModel.from_inputs(view_inputs).compute()
    charges = sum(v for k, v in res["pie_data"].items() if k not in NON_CHARGE_KEYS)
    assert charges == pytest.approx(res["monthly_charges"])


def test_report_charges_match_model(make_presenter):
    presenter, view = make_presenter()
    view.inputs.update({"gli": 240, "vacancy_months": 1})
    view.calculate()
    total = sum(presenter.fixed_charges.values()) + sum(presenter.variable_charges.values())
    assert total == pytest.approx(presenter.model.monthly_charges)

import pytest

from presenter.investment_presenter import InvestmentPresenter


def test_credit_cost_excludes_principal(view_inputs):
    from model.investment_model import InvestmentModel
    res = InvestmentModel().compute(view_inputs)
    assert res["credit_cost"] == pytest.approx(res["total_loan_cost"] - res["loan_amount"])
    assert 0 < res["credit_cost"] < res["loan_amount"]


def test_debt_ratio_help_matches_formula():
    text = InvestmentPresenter._get_formula_explanation("Taux d’endettement (%):")
    assert "Mensualité totale / Revenu net mensuel" in text


def test_ltv_help_describes_project_ltv():
    text = InvestmentPresenter._get_formula_explanation("Ratio prêt/valeur (%):")
    assert "Prix total projet" in text


@pytest.mark.parametrize("income,expected_color", [(4000, "green"), (950, "orange"), (780, "red")])  # mensualité ≈ 351 € → 9 %, 37 %, 45 %
def test_debt_ratio_color_matches_scoring(make_presenter, monkeypatch, income, expected_color):
    presenter, view = make_presenter()
    colors = {}
    monkeypatch.setattr(view, "update_indicator",
                        lambda label, value, color=None: colors.__setitem__(label, color))
    view.inputs["Revenu net mensuel (€)"] = float(income)
    view.calculate()
    assert colors["Taux d’endettement (%):"] == expected_color

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


def test_ratio_marche_uses_purchase_price_only():
    from model.investment_model import InvestmentModel
    base = dict(price=100000, surface_carrez=50, prix_moyen_m2=2000, rent=500)
    m = InvestmentModel(**base)
    assert m.ratio_marche == pytest.approx(100.0)
    # Travaux, meubles et frais ne changent pas le ratio marché
    assert InvestmentModel(**base, renovation=20000, furn=5000, other_fees=3000).ratio_marche == pytest.approx(100.0)

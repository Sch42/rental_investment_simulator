import math

import pytest
from model.investment_model import InvestmentModel

@pytest.fixture
def default_model():
    """Model with default parameters (as constructed)."""
    return InvestmentModel()

def test_default_model_is_consistent(default_model):
    m = default_model
    # Valeurs par défaut : price=1, rent=500, years=20, apport=0, Ancien, finance_all=True
    assert m.notary == pytest.approx(m.price * 0.08)
    assert m.total_project == pytest.approx(m.price + m.notary)
    assert m.loan_amount == pytest.approx(m.total_project)
    assert isinstance(m.n_months, int) and m.n_months == 240
    assert m.occupancy_rate == pytest.approx(1.0)
    assert m.effective_annual_rent == pytest.approx(m.rent * 12)
    assert m.monthly_payment == pytest.approx(m.monthly_payment_capital + m.monthly_insurance)
    for name in ("gross_yield", "net_yield", "taux_couv", "ltv_price", "ltv_project",
                 "monthly_cashflow", "price_carrez", "ratio_marche"):
        assert math.isfinite(getattr(m, name)), name

def test_from_inputs_accepts_valid_strings_and_numbers():
    inputs = {
        "price": "100000",
        "furn": 10000,
        "other_fees": "5000",
        "renovation": "15000",
        "surface_carrez": "50",
        "surface_non_validee": "10",
        "taxe": "1200",
        "copro": "600",
        "gestion_pct": "7",
        "gli": "0",
        "pno": "0",
        "compta": "0",
        "autres": "0",
        "maintenance_pct": "1",
        "vacancy_months": "1",
        "rent": "1000",
        "apport": "40000",
        "monthly_income": "2500",
        "years": "20",
        "rate": "3.5",
        "ins_rate": "0.2",
        "prix_moyen_m2": "2000"
    }
    m = InvestmentModel.from_inputs({**inputs, "type_of_property": "Neuf"})
    assert m.price == pytest.approx(100000.0)
    assert m.furn == pytest.approx(10000.0)
    assert m.surface_carrez == pytest.approx(50.0)
    assert m.vacancy_months == 1 and isinstance(m.vacancy_months, int)
    assert m.years == 20 and isinstance(m.years, int)
    assert m.rate == pytest.approx(0.035)       # saisi en %, stocké en décimal
    assert m.ins_rate == pytest.approx(0.002)
    assert m.gestion_pct == pytest.approx(7.0)  # reste en %
    assert m.type_of_property == "Neuf"

@pytest.mark.parametrize("inputs,message", [
    ({"price": "not_a_number"}, "Prix d'achat"),
    ({"rent": "one thousand"}, "Loyer mensuel"),
    ({"years": "twenty"}, "Durée du prêt"),
    ({"years": 12.5}, "nombre entier"),
    ({"vacancy_months": 1.5}, "nombre entier"),
    ({"loyer": 800}, "Champs inconnus"),  # clé inconnue : plus de correspondance approximative
])
def test_from_inputs_rejects_invalid_inputs(inputs, message):
    with pytest.raises(ValueError, match=message):
        InvestmentModel.from_inputs(inputs)


def test_compute_does_not_modify_model():
    m = InvestmentModel(price=100000, rent=800, apport=20000, years=15, rate=0.025,
                        monthly_income=3000, prix_moyen_m2=2000, surface_carrez=40)
    before = dict(vars(m))
    first = m.compute()
    assert vars(m) == before
    second = m.compute()
    assert first["monthly_cashflow"] == second["monthly_cashflow"]


def test_computations_against_manual_calculation():
    # Build a realistic sample project (numbers chosen for easy verification)
    inputs = {
        "price": 200000,
        "furn": 10000,
        "other_fees": 5000,
        "renovation": 15000,
        "surface_carrez": 60,
        "surface_non_validee": 10,
        "taxe": 1200,
        "copro": 600,
        "gestion_pct": 7,            # percent
        "gli": 0,
        "pno": 0,
        "compta": 0,
        "autres": 0,
        "maintenance_pct": 1,        # percent of price per year
        "vacancy_months": 1,   # months per year
        "rent": 1200,           # monthly
        "apport": 40000,
        "monthly_income": 3000,
        "years": 20,
        "rate": 3.5,
        "ins_rate": 0.2,
        "prix_moyen_m2": 2500
    }
    m = InvestmentModel.from_inputs(inputs)
    results = m.compute()

    # manual calculations following the model formulas
    # total_project = price + notary + furn + other_fees + renovation
    expected_total_project = m.price + m.notary + m.furn + m.other_fees + m.renovation
    assert results["total_project"] == pytest.approx(expected_total_project)

    # loan amount (finance_all True): total_project - apport
    expected_loan_amount = max(0.0, expected_total_project - m.apport)
    assert results["loan_amount"] == pytest.approx(expected_loan_amount)

    # monthly rate and payment capital
    monthly_rate = m.rate / 12.0
    n_months = m.n_months
    if monthly_rate > 0:
        expected_monthly_capital = (m.loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** (-n_months))
    else:
        expected_monthly_capital = m.loan_amount / n_months
    assert m.monthly_payment_capital == pytest.approx(expected_monthly_capital)

    # monthly insurance
    expected_monthly_ins = m.loan_amount * m.ins_rate / 12.0
    assert m.monthly_insurance == pytest.approx(expected_monthly_ins)

    # monthly payment
    assert m.monthly_payment == pytest.approx(expected_monthly_capital + expected_monthly_ins)

    # monthly charges
    expected_gestion = (m.gestion_pct / 100.0) * (m.rent * m.occupancy_rate)
    expected_maintenance = (m.maintenance) / 12.0
    expected_monthly_charges = (m.taxe / 12.0 + m.copro / 12.0 + expected_gestion +
                                m.gli / 12.0 + m.pno / 12.0 + m.compta / 12.0 +
                                m.autres / 12.0 + expected_maintenance)
    assert m.monthly_charges == pytest.approx(expected_monthly_charges)

    # effective annual rent
    expected_annual_rent = m.rent * 12 * m.occupancy_rate
    assert results["annual_rent"] == pytest.approx(expected_annual_rent)

    # monthly cashflow
    expected_monthly_cashflow = expected_annual_rent / 12.0 - expected_monthly_charges - m.monthly_payment
    assert results["monthly_cashflow"] == pytest.approx(expected_monthly_cashflow)

    # gros yield
    if expected_total_project > 0:
        expected_gross_yield = expected_annual_rent / expected_total_project * 100
    else:
        expected_gross_yield = 0.0
    assert results["gross_yield"] == pytest.approx(expected_gross_yield)

    # taux de couverture (if monthly payment > 0)
    if m.monthly_payment > 0:
        expected_taux = (expected_annual_rent / 12.0) / m.monthly_payment * 100
    else:
        expected_taux = 0.0
    assert results["taux_couv"] == pytest.approx(expected_taux)

    # principal repaid first year > 0 and < loan amount
    repaid = m.principal_repaid_first_n_months(12)
    assert repaid >= 0
    assert repaid <= m.loan_amount

def test_compute_returns_expected_keys_and_types():
    inputs = {
        "price": 100000,
        "rent": 800,
        "apport": 20000,
        "years": 15,
        "rate": 2.5,
        "ins_rate": 0.2
    }
    res = InvestmentModel.from_inputs(inputs).compute()
    # expected keys
    keys = ["total_project", "notary", "price_carrez", "price_total_pondere",
            "monthly_cashflow", "gross_yield", "net_yield", "ltv",
            "roe", "monthly_payment", "monthly_charges", "annual_rent",
            "maintenance", "ratio_marche", "loan_ratio", "loan_amount",
            "break_even_rent", "equity", "price_per_m2", "total_loan_cost",
            "adjusted_debt_ratio", "pie_data", "cumulative_cashflow",
            "payback_year", "rec_text", "rec_color", "rec_details_text",
            "cashflow", "taux_couv", "debt_ratio"]
    for k in keys:
        assert k in res
    # numeric fields are floats or ints
    assert isinstance(res["total_project"], float)
    assert isinstance(res["monthly_cashflow"], float)
    assert isinstance(res["pie_data"], dict)

def test_model_does_not_import_ui_libraries():
    import subprocess
    import sys
    code = ("import sys; import model.investment_model; "
            "bad = [m for m in ('customtkinter', 'tkinter', 'matplotlib') if m in sys.modules]; "
            "assert not bad, bad")
    subprocess.run([sys.executable, "-c", code], check=True)


def test_fake_view_fields_match_model_fields():
    from tests.conftest import VIEW_DEFAULT_INPUTS
    assert set(VIEW_DEFAULT_INPUTS) == set(InvestmentModel.FIELD_LABELS)

import pytest
from model.investment_model import InvestmentModel, safe_parse_float

@pytest.fixture
def default_model():
    """Model with default parameters (as constructed)."""
    return InvestmentModel()

def test_defaults_properties_are_zero_or_identity(default_model):
    m = default_model
    # Defaults should be zeros where appropriate
    assert m.notary == pytest.approx(0.0)
    assert m.maintenance == pytest.approx(0.0)
    assert m.total_project == pytest.approx(0.0)
    assert m.surface_totale_ponderee == pytest.approx(0.0)
    assert m.price_carrez == pytest.approx(0.0)
    assert m.price_total_pondere == pytest.approx(0.0)
    assert m.ratio_marche == pytest.approx(0.0)
    assert m.loan_amount == pytest.approx(0.0)
    # n_months uses max(1, int(round(years*12))) and default years==0 so should be 1
    assert isinstance(m.n_months, int) and m.n_months == 1
    assert m.monthly_payment_capital == pytest.approx(0.0)
    assert m.monthly_insurance == pytest.approx(0.0)
    assert m.monthly_payment == pytest.approx(0.0)
    assert m.monthly_charges == pytest.approx(0.0)
    assert m.occupancy_rate == pytest.approx(1.0)
    assert m.effective_annual_rent == pytest.approx(0.0)
    assert m.monthly_cashflow == pytest.approx(0.0)
    assert m.gross_yield == pytest.approx(0.0)
    assert m.net_yield == pytest.approx(0.0)
    assert m.taux_couv == pytest.approx(0.0)
    assert m.ltv_price == pytest.approx(0.0)
    assert m.ltv_project == pytest.approx(0.0)
    assert m.equity == pytest.approx(0.0)
    assert m.roe_cashflow == pytest.approx(0.0)
    assert m.principal_repaid_first_n_months(12) == pytest.approx(0.0)
    assert m.roe_patrimonial == pytest.approx(0.0)

def test_load_inputs_accepts_valid_strings_and_numbers():
    m = InvestmentModel()
    inputs = {
        "Prix d'achat": "100000",
        "Meubles": 10000,
        "Autres frais": "5000",
        "Rénovation": "15000",
        "Surface Carrez": "50",
        "Surface non prise en compte": "10",
        "Taxe foncière": "1200",
        "Charges copro": "600",
        "Gestion": "7",
        "GLI": "0",
        "Assurance PNO": "0",
        "Frais compta": "0",
        "Autres charges": "0",
        "Maintenance": "1",
        "Vacance locative": "1",
        "Loyer": "1000",
        "Apport": "40000",
        "Revenu net": "2500",
        "Durée": "20",
        "Taux d'intérêt": "3.5",
        "Assurance prêt": "0.2",
        "Prix moyen": "2000"
    }
    # Should not raise
    m.load_inputs(inputs, "Ancien")
    # After loading, values should be parsed correctly
    assert m.price == pytest.approx(100000.0)
    assert m.furn == pytest.approx(10000.0)
    assert m.surface_carrez == pytest.approx(50.0)
    assert m.vacancy_months == pytest.approx(1.0)
    assert pytest.approx(m.rate) == 0.035

def test_load_inputs_raises_on_invalid_types():
    m = InvestmentModel()
    # For keys where the code calls float(value), invalid strings should raise ValueError
    with pytest.raises(ValueError):
        m.load_inputs({"Prix d'achat": "not_a_number"}, "Ancien")
    with pytest.raises(ValueError):
        m.load_inputs({"Loyer": "one thousand"}, "Ancien")
    with pytest.raises(ValueError):
        m.load_inputs({"Durée": "twenty"}, "Ancien")

def test_computations_against_manual_calculation():
    # Build a realistic sample project (numbers chosen for easy verification)
    m = InvestmentModel()
    inputs = {
        "Prix d'achat": 200000,
        "Meubles": 10000,
        "Autres frais": 5000,
        "Rénovation": 15000,
        "Surface Carrez": 60,
        "Surface non prise en compte": 10,
        "Taxe foncière": 1200,
        "Charges copro": 600,
        "Gestion": 7,            # percent
        "GLI": 0,
        "Assurance PNO": 0,
        "Frais compta": 0,
        "Autres charges": 0,
        "Maintenance": 1,        # percent of price per year
        "Vacance locative": 1,   # months per year
        "Loyer": 1200,           # monthly
        "Apport": 40000,
        "Revenu net": 3000,
        "Durée": 20,
        "Taux d'intérêt": 3.5,
        "Assurance prêt": 0.2,
        "Prix moyen": 2500
    }
    m.load_inputs(inputs, "Ancien")
    results = m.compute(inputs)

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
    m = InvestmentModel()
    inputs = {
        "Prix d'achat": 100000,
        "Loyer": 800,
        "Apport": 20000,
        "Durée": 15,
        "Taux d'intérêt": 2.5,
        "Assurance prêt": 0.2
    }
    m.load_inputs(inputs, "Ancien")
    res = m.compute(inputs)
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

def test_safe_parse_float_behaviour():
    assert safe_parse_float("123,45") == pytest.approx(123.45)
    assert safe_parse_float("   1 234  ") == pytest.approx(1234.0)
    assert safe_parse_float("") == pytest.approx(0.0)
    assert safe_parse_float(None) == pytest.approx(0.0)
    assert safe_parse_float("notnum") == pytest.approx(0.0)

import unittest
import math
from hypothesis import given, strategies as st

from model.investment_model import InvestmentModel


# -------- Helper --------
def try_model(**kwargs):
    """Helper that tries to build an InvestmentModel with kwargs."""
    return InvestmentModel(
        price=kwargs.get("price", 69000),
        prix_moyen_m2=kwargs.get("prix_moyen_m2", 2200.0),
        furn=kwargs.get("furn", 0),
        other_fees=kwargs.get("other_fees", 0),
        renovation=kwargs.get("renovation", 8300),
        surface_carrez=kwargs.get("surface_carrez", 18.38),
        surface_non_validee=kwargs.get("surface_non_validee", 7.48),
        taxe=kwargs.get("taxe", 300),
        copro=kwargs.get("copro", 360),
        gestion_pct=kwargs.get("gestion_pct", 0),
        gli=kwargs.get("gli", 0),
        pno=kwargs.get("pno", 0),
        compta=kwargs.get("compta", 0),
        autres=kwargs.get("autres", 360),
        maintenance_pct=kwargs.get("maintenance_pct", 2),
        vacancy_months=kwargs.get("vacancy_months", 0),
        rent=kwargs.get("rent", 500.0),
        apport=kwargs.get("apport", 15000),
        monthly_income=kwargs.get("monthly_income", 2000),
        years=kwargs.get("years", 25),
        rate=kwargs.get("rate", 0.035),
        ins_rate=kwargs.get("ins_rate", 0.002),
        type_of_property=kwargs.get("type_of_property", "Ancien"),
        finance_all=kwargs.get("finance_all", True),
    )


NUMERIC_FIELDS = [
    "price", "furn", "other_fees", "renovation",
    "surface_carrez", "surface_non_validee",
    "taxe", "copro", "gestion_pct", "gli", "pno",
    "compta", "autres", "maintenance_pct",
    "vacancy_months", "rent", "apport",
    "years", "rate", "ins_rate", "monthly_income",
    "prix_moyen_m2"
]


class TestInvestmentModel(unittest.TestCase):
    
    def setUp(self):
        self.model = try_model()

    # -------- TYPE TESTS --------
    @given(field=st.sampled_from(NUMERIC_FIELDS), bad=st.text())
    def test_numeric_fields_wrong_type(self, field, bad):
        with self.assertRaises(TypeError):
            try_model(**{field: bad})

    @given(bad=st.integers())
    def test_type_of_property_wrong_type(self, bad):
        with self.assertRaises(TypeError):
            try_model(type_of_property=bad)

    @given(bad=st.text())
    def test_finance_all_wrong_type(self, bad):
        with self.assertRaises(TypeError):
            try_model(finance_all=bad)

    # -------- INF TESTS --------
    @given(field=st.sampled_from(NUMERIC_FIELDS),
           val=st.floats(allow_nan=False, allow_infinity=True))
    def test_numeric_inf(self, field, val):
        if math.isinf(val):
            if field in ["years", "vacancy_months"]:
                with self.assertRaises((TypeError, ValueError)):
                    try_model(**{field: val})
            else:
                with self.assertRaises(ValueError):
                    try_model(**{field: val})

    # -------- NAN TESTS --------
    @given(field=st.sampled_from(NUMERIC_FIELDS),
           val=st.floats(allow_nan=True, allow_infinity=False))
    def test_numeric_nan(self, field, val):
        if math.isnan(val):
            if field in ["years", "vacancy_months"]:
                with self.assertRaises((TypeError, ValueError)):
                    try_model(**{field: val})
            else:
                with self.assertRaises(ValueError):
                    try_model(**{field: val})

    # -------- RANGE TESTS --------
    @given(val=st.floats(max_value=0, allow_nan=False, allow_infinity=False))
    def test_price_invalid_range(self, val):
        with self.assertRaises(ValueError):
            try_model(price=val)

    @given(val=st.floats(max_value=-1))
    def test_surface_carrez_invalid_range(self, val):
        with self.assertRaises(ValueError):
            try_model(surface_carrez=val)

    @given(val=st.integers(min_value=-10, max_value=-1))
    def test_vacancy_months_invalid_negative(self, val):
        with self.assertRaises(ValueError):
            try_model(vacancy_months=val)

    @given(val=st.integers(min_value=13, max_value=100))
    def test_vacancy_months_invalid_too_large(self, val):
        with self.assertRaises(ValueError):
            try_model(vacancy_months=val)

    @given(val=st.floats(max_value=0))
    def test_rent_invalid_range(self, val):
        with self.assertRaises(ValueError):
            try_model(rent=val)

    @given(val=st.floats(max_value=-1))
    def test_apport_invalid_range(self, val):
        with self.assertRaises(ValueError):
            try_model(apport=val)

    @given(val=st.integers(max_value=-1))
    def test_years_invalid_range(self, val):
        with self.assertRaises(ValueError):
            try_model(years=val)

    @given(val=st.floats(max_value=-1))
    def test_rate_invalid_range(self, val):
        with self.assertRaises(ValueError):
            try_model(rate=val)

    @given(val=st.floats(max_value=-1))
    def test_ins_rate_invalid_range(self, val):
        with self.assertRaises(ValueError):
            try_model(ins_rate=val)

    @given(val=st.floats(max_value=-1))
    def test_gestion_pct_invalid_range(self, val):
        with self.assertRaises(ValueError):
            try_model(gestion_pct=val)

    @given(val=st.floats(max_value=-1))
    def test_maintenance_pct_invalid_range(self, val):
        with self.assertRaises(ValueError):
            try_model(maintenance_pct=val)

    @given(val=st.floats(max_value=0))
    def test_monthly_income_invalid_range(self, val):
        with self.assertRaises(ValueError):
            try_model(monthly_income=val)

    @given(val=st.floats(max_value=0))
    def test_prix_moyen_m2_invalid_range(self, val):
        with self.assertRaises(ValueError):
            try_model(prix_moyen_m2=val)

    @given(val=st.text().filter(lambda s: s not in ["Ancien", "Neuf"]))
    def test_type_of_property_invalid_value(self, val):
        with self.assertRaises(ValueError):
            try_model(type_of_property=val)

    # -------- BOUNDARY TESTS --------
    def test_boundary_values(self):
        """Deterministic boundary checks for edge conditions of every parameter."""

        # --- Must be strictly positive (>0) ---
        with self.assertRaises(ValueError):
            try_model(price=0)  # price must be > 0
        with self.assertRaises(ValueError):
            try_model(surface_carrez=0)  # must be > 0
        with self.assertRaises(ValueError):
            try_model(rent=0)  # must be > 0
        with self.assertRaises(ValueError):
            try_model(monthly_income=0)  # must be > 0
        with self.assertRaises(ValueError):
            try_model(prix_moyen_m2=0)  # must be > 0

        # --- Must be >= 0 (zero allowed, negative forbidden) ---
        with self.assertRaises(ValueError):
            try_model(furn=-1)
        with self.assertRaises(ValueError):
            try_model(other_fees=-1)
        with self.assertRaises(ValueError):
            try_model(renovation=-1)
        with self.assertRaises(ValueError):
            try_model(surface_non_validee=-1)
        with self.assertRaises(ValueError):
            try_model(taxe=-1)
        with self.assertRaises(ValueError):
            try_model(copro=-1)
        with self.assertRaises(ValueError):
            try_model(gestion_pct=-0.01)
        with self.assertRaises(ValueError):
            try_model(gli=-1)
        with self.assertRaises(ValueError):
            try_model(pno=-1)
        with self.assertRaises(ValueError):
            try_model(compta=-1)
        with self.assertRaises(ValueError):
            try_model(autres=-1)
        with self.assertRaises(ValueError):
            try_model(maintenance_pct=-0.01)
        with self.assertRaises(ValueError):
            try_model(apport=-1)

        # --- vacancy_months: must be int in [0, 12] ---
        with self.assertRaises(ValueError):
            try_model(vacancy_months=-1)
        with self.assertRaises(ValueError):
            try_model(vacancy_months=13)
        with self.assertRaises(TypeError):
            try_model(vacancy_months=3.5)  # must be int

        # --- years: must be int >= 0 ---
        with self.assertRaises(ValueError):
            try_model(years=-1)
        with self.assertRaises(TypeError):
            try_model(years=10.5)  # must be int

        # --- rates/percentages: must be in [0, 1] ---
        try_model(rate=0)  # allowed
        try_model(ins_rate=0)  # allowed
        try_model(gestion_pct=0)  # allowed
        try_model(maintenance_pct=0)  # allowed

        with self.assertRaises(ValueError):
            try_model(rate=-0.01)
        with self.assertRaises(ValueError):
            try_model(rate=1.1)
        with self.assertRaises(ValueError):
            try_model(ins_rate=-0.01)
        with self.assertRaises(ValueError):
            try_model(ins_rate=1.1)
        with self.assertRaises(ValueError):
            try_model(gestion_pct=-0.01)
        with self.assertRaises(ValueError):
            try_model(maintenance_pct=-0.01)

        # --- type_of_property: must be "Ancien" or "Neuf" ---
        with self.assertRaises(ValueError):
            try_model(type_of_property="Old")
        with self.assertRaises(ValueError):
            try_model(type_of_property="XYZ")

        # --- finance_all: must be bool ---
        with self.assertRaises(TypeError):
            try_model(finance_all="yes")
        with self.assertRaises(TypeError):
            try_model(finance_all=123)


    # -------- VALID CASE --------
    @given(price=st.floats(min_value=1, max_value=1e4),
            furn=st.floats(min_value=0, max_value=1e4),
            other_fees=st.floats(min_value=0, max_value=1e4),
            renovation=st.floats(min_value=0, max_value=1e4),
            surface_carrez=st.floats(min_value=0.1, max_value=1e4),
            surface_non_validee=st.floats(min_value=0, max_value=1e4),
            taxe=st.floats(min_value=0, max_value=1e4),
            copro=st.floats(min_value=0, max_value=1e4),
            gestion_pct=st.floats(min_value=0, max_value=1),
            gli=st.floats(min_value=0, max_value=1e4),
            pno=st.floats(min_value=0, max_value=1e4),
            compta=st.floats(min_value=0, max_value=1e4),
            autres=st.floats(min_value=0, max_value=1e4),
            maintenance_pct=st.floats(min_value=0, max_value=1),
            vacancy_months=st.integers(min_value=0, max_value=12),
            rent=st.floats(min_value=100, max_value=5000),
            apport=st.floats(min_value=0, max_value=1e4),
            years=st.integers(min_value=1, max_value=40),
            rate=st.floats(min_value=0, max_value=1),
            ins_rate=st.floats(min_value=0, max_value=1),
            monthly_income=st.floats(min_value=1, max_value=10000),
            prix_moyen_m2=st.floats(min_value=1, max_value=10000),
            type_of_property=st.sampled_from(["Ancien", "Neuf"]),
            finance_all=st.booleans())
    def test_valid_model(self, **kwargs):
        model = try_model(**kwargs)
        for field, value in kwargs.items():
            if isinstance(value, float):
                self.assertAlmostEqual(getattr(model, field), value, places=7)
            else:
                self.assertEqual(getattr(model, field), value)
                
    def test_notary(self):
        self.assertAlmostEqual(self.model.notary, 69000*0.08, places=2)

    def test_total_project(self):
        expected = 69000 + self.model.notary + 8300
        self.assertAlmostEqual(self.model.total_project, expected, places=2)

    def test_surface_totale_ponderee(self):
        expected = 18.38 + 0.3 * 7.48
        self.assertAlmostEqual(self.model.surface_totale_ponderee, expected, places=2)

    def test_price_carrez(self):
        expected = self.model.total_project / 18.38
        self.assertAlmostEqual(self.model.price_carrez, expected, places=2)

    def test_price_total_pondere(self):
        expected = self.model.total_project / self.model.surface_totale_ponderee
        self.assertAlmostEqual(self.model.price_total_pondere, expected, places=2)

    def test_ratio_marche(self):
        expected = self.model.price_total_pondere / 2200 * 100
        self.assertAlmostEqual(self.model.ratio_marche, expected, places=2)

    def test_loan_amount(self):
        expected = self.model.total_project - 15000
        self.assertAlmostEqual(self.model.loan_amount, expected, places=2)

    def test_n_months(self):
        self.assertEqual(self.model.n_months, 25 * 12)

    def test_monthly_payment_capital(self):
        monthly_rate = 0.035 / 12
        expected = (self.model.loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** (-300))
        self.assertAlmostEqual(self.model.monthly_payment_capital, expected, places=2)

    def test_monthly_insurance(self):
        expected = self.model.loan_amount * 0.002 / 12
        self.assertAlmostEqual(self.model.monthly_insurance, expected, places=2)

    def test_monthly_payment(self):
        expected = self.model.monthly_payment_capital + self.model.monthly_insurance
        self.assertAlmostEqual(self.model.monthly_payment, expected, places=2)

    def test_monthly_charges(self):
        taxe_m = 300 / 12
        copro_m = 360 / 12
        autres_m = 360 / 12
        maintenance_m = self.model.maintenance / 12
        expected = taxe_m + copro_m + autres_m + maintenance_m
        self.assertAlmostEqual(self.model.monthly_charges, expected, places=2)

    def test_occupancy_rate(self):
        self.assertAlmostEqual(self.model.occupancy_rate, 1.0, places=2)

    def test_effective_annual_rent(self):
        self.assertAlmostEqual(self.model.effective_annual_rent, 500 * 12, places=2)

    def test_monthly_cashflow(self):
        expected = (500 * 12) / 12 - self.model.monthly_charges - self.model.monthly_payment
        self.assertAlmostEqual(self.model.monthly_cashflow, expected, places=2)

    def test_gross_yield(self):
        expected = self.model.effective_annual_rent / self.model.total_project * 100
        self.assertAlmostEqual(self.model.gross_yield, expected, places=2)

    def test_net_yield(self):
        expected = (self.model.effective_annual_rent - self.model.monthly_charges * 12) / self.model.total_project * 100
        self.assertAlmostEqual(self.model.net_yield, expected, places=2)

    def test_taux_couv(self):
        monthly_rent = 500
        expected = monthly_rent / self.model.monthly_payment * 100
        self.assertAlmostEqual(self.model.taux_couv, expected, places=2)
        
    def test_ltv_price(self):
        expected = self.model.loan_amount / 69000 * 100
        self.assertAlmostEqual(self.model.ltv_price, expected, places=2)

    def test_ltv_project(self):
        expected = self.model.loan_amount / self.model.total_project * 100
        self.assertAlmostEqual(self.model.ltv_project, expected, places=2)

    def test_equity(self):
        # finance_all=True : le prêt couvre notaire et travaux, seul l'apport est investi
        self.assertAlmostEqual(self.model.equity, 15000, places=2)

    def test_equity_price_only_financing(self):
        model = try_model(finance_all=False)
        expected = 15000 + 8300 + model.notary
        self.assertAlmostEqual(model.equity, expected, places=2)
        self.assertAlmostEqual(model.equity + model.loan_amount, model.total_project, places=2)

    def test_roe_cashflow(self):
        annual_cf = (self.model.effective_annual_rent
                      - self.model.monthly_charges * 12
                      - self.model.monthly_payment * 12)
        expected = annual_cf / self.model.equity * 100
        self.assertAlmostEqual(self.model.roe_cashflow, expected, places=2)

    def test_principal_repaid_first_year(self):
        repaid = self.model.principal_repaid_first_n_months(12)
        self.assertTrue(repaid > 0)
        self.assertTrue(repaid < self.model.loan_amount)

    def test_roe_patrimonial(self):
        annual_cf = (self.model.effective_annual_rent
                      - self.model.monthly_charges * 12
                      - self.model.monthly_payment * 12
                      + self.model.principal_repaid_first_n_months(12))
        expected = annual_cf / self.model.equity * 100
        self.assertAlmostEqual(self.model.roe_patrimonial, expected, places=2)



if __name__ == "__main__":
    unittest.main()

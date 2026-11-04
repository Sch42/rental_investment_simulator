"""Fixtures partagées : une fausse vue pour tester le presenter sans interface Tk."""
import matplotlib
import pytest

matplotlib.use("Agg")

# Mêmes clés (noms d'attributs du modèle) et valeurs par défaut que InvestmentView
VIEW_DEFAULT_INPUTS = {
    "price": 69000.0,
    "prix_moyen_m2": 2200.0,
    "furn": 0.0,
    "other_fees": 0.0,
    "renovation": 8300.0,
    "surface_carrez": 18.38,
    "surface_non_validee": 7.48,
    "taxe": 300.0,
    "copro": 360.0,
    "gli": 0.0,
    "pno": 0.0,
    "compta": 0.0,
    "autres": 360.0,
    "gestion_pct": 0.0,
    "maintenance_pct": 2.0,
    "vacancy_months": 0.0,
    "extra_monthly_contrib": 0.0,
    "rent": 500.0,
    "apport": 15000.0,
    "monthly_income": 2000.0,
    "years": 25.0,
    "rate": 3.5,
    "ins_rate": 0.2,
}


class FakeView:
    def __init__(self, inputs=None, property_type="Ancien"):
        self.inputs = dict(VIEW_DEFAULT_INPUTS if inputs is None else inputs)
        self.property_type = property_type
        self.indicators = {}
        self.recommendation = None
        self.errors = []
        self.payback = None
        self.pie = None

    # bindings (ignorés)
    def bind_calculate(self, handler): self.calculate = handler
    def set_pie_hover_handler(self, handler): pass
    def bind_indicator_help(self, handler): pass
    def set_recommendation_info(self, handler): pass

    def get_all_inputs(self): return dict(self.inputs)
    def get_property_type(self): return self.property_type
    def update_recommendation(self, text, color): self.recommendation = (text, color)
    def update_indicator(self, label, value, color=None): self.indicators[label] = value
    def draw_pie(self, data): self.pie = data
    def draw_payback(self, cumulative, years, payback_year): self.payback = (cumulative, years, payback_year)
    def draw_amortization_chart(self, simu): self.amortization = simu
    def show_info_modal(self, title, text): pass
    def show_error(self, title, text): self.errors.append(text)


@pytest.fixture
def view_inputs():
    return dict(VIEW_DEFAULT_INPUTS)


@pytest.fixture
def make_presenter(tmp_path, monkeypatch):
    """Construit un presenter avec une FakeView, dans un dossier temporaire."""
    monkeypatch.chdir(tmp_path)
    from model.investment_model import InvestmentModel
    from presenter.investment_presenter import InvestmentPresenter

    def _make(**view_kwargs):
        view = FakeView(**view_kwargs)
        presenter = InvestmentPresenter(InvestmentModel(), view)
        return presenter, view
    return _make

"""Fixtures partagées : une fausse vue pour tester le presenter sans interface Tk."""
import matplotlib
import pytest

matplotlib.use("Agg")

# Mêmes clés et valeurs par défaut que InvestmentView (libellés sans ':')
VIEW_DEFAULT_INPUTS = {
    "Prix d'achat (€)": 69000.0,
    "Prix moyen au m² (€ / m²)": 2200.0,
    "Meubles / électroménager (€)": 0.0,
    "Autres frais (€)": 0.0,
    "Rénovation / travaux (€)": 8300.0,
    "Surface Carrez (m²)": 18.38,
    "Surface non prise en compte (m²)": 7.48,
    "Taxe foncière (€ / an)": 300.0,
    "Charges copropriété (€ / an)": 360.0,
    "GLI (€ / an)": 0.0,
    "Assurance PNO (€ / an)": 0.0,
    "Frais compta (€ / an)": 0.0,
    "Autres charges (€ / an)": 360.0,
    "Gestion en agence (% du loyer)": 0.0,
    "Maintenance / réparations (% du prix / an)": 2.0,
    "Vacance locative (mois/an)": 0.0,
    "Loyer mensuel (€)": 500.0,
    "Apport (€)": 15000.0,
    "Revenu net mensuel (€)": 2000.0,
    "Durée du prêt (années)": 25.0,
    "Taux d'intérêt annuel (%)": 3.5,
    "Assurance prêt (%)": 0.2,
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

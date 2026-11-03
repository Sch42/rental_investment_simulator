import pytest


def test_property_type_neuf_is_used(make_presenter):
    presenter, view = make_presenter(property_type="Neuf")
    view.calculate()
    assert presenter.model.type_of_property == "Neuf"
    assert presenter.model.notary == pytest.approx(presenter.model.price * 0.025)


def test_property_type_ancien_is_used(make_presenter):
    presenter, view = make_presenter(property_type="Ancien")
    view.calculate()
    assert presenter.model.notary == pytest.approx(presenter.model.price * 0.08)


def test_saved_payback_chart_uses_computed_cashflow(make_presenter, monkeypatch):
    import matplotlib.axes
    presenter, view = make_presenter(inputs=None)
    view.inputs["Apport (€)"] = 0.0
    view.inputs["Loyer mensuel (€)"] = 900.0  # cashflow positif → payback atteint

    bars = {}
    orig_bar = matplotlib.axes.Axes.bar

    def spy_bar(self, x, height, *a, **kw):
        bars["heights"] = list(height)
        return orig_bar(self, x, height, *a, **kw)

    monkeypatch.setattr(matplotlib.axes.Axes, "bar", spy_bar)
    view.calculate()
    cumulative, _, payback_year = view.payback
    assert payback_year is not None
    assert bars["heights"] == pytest.approx(cumulative)
    assert any(h != 0 for h in bars["heights"])

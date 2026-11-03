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
    view.inputs["apport"] = 0.0
    view.inputs["rent"] = 900.0  # cashflow positif → payback atteint

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


def _report_conclusion(path):
    text = open(path, encoding="utf-8").read()
    return text.split("Conclusion pour la banque")[1]


def test_report_conclusion_for_risky_project(make_presenter, tmp_path):
    presenter, view = make_presenter()
    view.inputs["rent"] = 300.0
    view.calculate()
    assert view.recommendation[1] == "red"
    conclusion = _report_conclusion(tmp_path / "rapport_investissement.txt")
    assert "sécurisé" not in conclusion
    assert "risqué" in conclusion
    assert "Effort d'épargne" in conclusion


def test_report_conclusion_for_good_project(make_presenter, tmp_path):
    presenter, view = make_presenter()
    view.inputs.update({"rent": 1000.0, "prix_moyen_m2": 5000.0,
                        "apport": 30000.0})
    view.calculate()
    assert view.recommendation[1] == "green"
    conclusion = _report_conclusion(tmp_path / "rapport_investissement.txt")
    assert "conformes aux standards" in conclusion
    assert "Cashflow positif" in conclusion


def test_no_files_written_at_startup(make_presenter, tmp_path):
    make_presenter()
    assert list(tmp_path.iterdir()) == []


def test_calculate_saves_each_chart_once(make_presenter, tmp_path, monkeypatch):
    import matplotlib.pyplot as plt
    saved = []
    orig = plt.savefig
    monkeypatch.setattr(plt, "savefig", lambda fname, *a, **kw: (saved.append(fname), orig(fname, *a, **kw)))
    presenter, view = make_presenter()
    view.calculate()
    assert sorted(saved) == ["charges_pie.png", "payback_period.png"]
    assert (tmp_path / "rapport_investissement.txt").exists()

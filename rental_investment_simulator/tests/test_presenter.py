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

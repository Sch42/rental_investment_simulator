import math

import pytest

from model.investment_model import InvestmentModel


def make(**kw):
    base = dict(price=69000, renovation=8300, surface_carrez=18.38, taxe=300, copro=360,
                autres=360, maintenance_pct=2, rent=500.0, apport=15000, years=25,
                rate=0.035, ins_rate=0.002, monthly_income=2000, prix_moyen_m2=2200)
    base.update(kw)
    return InvestmentModel(**base)


@pytest.mark.parametrize("gestion,vacance", [(0, 0), (8, 0), (0, 1), (8, 1), (25, 3)])
def test_cashflow_is_zero_at_break_even_rent(gestion, vacance):
    m = make(gestion_pct=gestion, vacancy_months=vacance)
    m.rent = m.break_even_rent
    assert m.monthly_cashflow == pytest.approx(0.0, abs=1e-6)


@pytest.mark.parametrize("kw", [dict(gestion_pct=100), dict(vacancy_months=12)])
def test_break_even_rent_impossible(kw):
    assert make(**kw).break_even_rent == math.inf


def test_compute_does_not_crash_with_full_management_fee(view_inputs):
    view_inputs["gestion_pct"] = 100
    res = InvestmentModel.from_inputs(view_inputs).compute()
    assert res["break_even_rent"] == math.inf

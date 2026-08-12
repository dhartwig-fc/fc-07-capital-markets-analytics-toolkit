"""Tests for the CM005 Wash Trading governed callable (loaded as the runtime loads it)."""

from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent
SCENARIO = BASE_DIR / "scenarios" / "wash_trading.py"

ADAPTER_REQUIRED_COLUMNS = {
    "account_ref", "subject_entity_id", "subject_name", "exposure_score", "exposure_band",
    "alert_type", "risk_reason", "risk_components", "instrument", "clearing_broker_name",
}


def _load():
    spec = spec_from_file_location("fc07_cm005_governed_wash_trading", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def governed():
    return _load()


@pytest.fixture(scope="module")
def frames(governed):
    return governed.build_frames_from_sample_data()


def test_import_is_inert(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = set(p.name for p in tmp_path.iterdir())
    _load()
    assert set(p.name for p in tmp_path.iterdir()) == before


def test_callable_exists(governed):
    assert callable(getattr(governed, "evaluate_wash_trading", None))


@pytest.mark.parametrize("dropped", ["trades", "counterparties"])
def test_each_frame_required(governed, frames, dropped):
    kwargs = dict(frames)
    kwargs[dropped] = None
    with pytest.raises(ValueError) as e:
        governed.evaluate_wash_trading(**kwargs)
    assert dropped in str(e.value)


def test_refuses_unmatched_counterparty(governed, frames):
    kwargs = dict(frames)
    kwargs["counterparties"] = frames["counterparties"].iloc[0:0]
    with pytest.raises(ValueError) as e:
        governed.evaluate_wash_trading(**kwargs)
    assert "counterparty" in str(e.value).lower()


def test_at_least_one_alert_present(governed, frames):
    out = governed.evaluate_wash_trading(**frames)
    assert len(out) >= 1 and ADAPTER_REQUIRED_COLUMNS <= set(out.columns)


def test_every_alert_is_at_or_above_threshold(governed, frames):
    out = governed.evaluate_wash_trading(**frames)
    assert (out["exposure_score"] >= governed.ALERT_THRESHOLD).all()


def test_clean_account_is_not_alerted(governed, frames):
    clean = {**frames, "trades": frames["trades"][frames["trades"]["account_ref"] == "ACC001"]}
    out = governed.evaluate_wash_trading(**clean)
    assert len(out) == 0


def test_the_continental_correspondent_bank_bridge_alerts_critical(governed, frames):
    """ACC019 crosses matched buy and sell orders that produce no genuine change in
    beneficial ownership, cleared through Continental Correspondent Bank -- an entity
    already in the estate network -- and must clear the alert threshold at Critical,
    proving the fusion bridge is a real alerting subject, not a decorative row. It is
    also the single highest-scoring account in the set, which matters: the FC-10
    adapter builds its case/graph from score_all's top row, so the Continental
    Correspondent Bank bridge has to BE that row."""
    scored = governed.score_all(**frames)
    top = scored.iloc[0]
    assert top["account_ref"] == "ACC019" and top["clearing_broker_name"] == "Continental Correspondent Bank"
    row = governed.evaluate_wash_trading(**frames)
    bridge = row[row["account_ref"] == "ACC019"].iloc[0]
    assert bridge["clearing_broker_name"] == "Continental Correspondent Bank"
    assert bridge["exposure_score"] == 90 and bridge["exposure_band"] == "Critical"


def test_working_reconstructs(governed, frames):
    out = governed.evaluate_wash_trading(**frames)
    w = json.loads(out.iloc[0]["risk_components"])
    total = sum(c["contribution"] for c in w["components"].values())
    assert abs(total - w["total"]) < 0.01


def test_one_scorer(governed):
    assert SCENARIO.read_text(encoding="utf-8").count("cm005_exposure_score(") == 1


def test_threshold_named_once(governed):
    assert governed.ALERT_THRESHOLD == 80
    assert ">= 80" not in SCENARIO.read_text(encoding="utf-8")

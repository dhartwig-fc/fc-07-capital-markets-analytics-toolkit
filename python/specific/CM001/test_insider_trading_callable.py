"""Tests for the CM001 Insider Trading governed callable (loaded as the runtime loads it)."""

from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent
SCENARIO = BASE_DIR / "scenarios" / "insider_trading.py"

ADAPTER_REQUIRED_COLUMNS = {
    "account_ref", "subject_entity_id", "subject_name", "exposure_score", "exposure_band",
    "alert_type", "risk_reason", "risk_components", "desk", "issuer_name",
}


def _load():
    spec = spec_from_file_location("fc07_cm001_governed_insider_trading", SCENARIO)
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
    assert callable(getattr(governed, "evaluate_insider_trading", None))


@pytest.mark.parametrize("dropped", ["trading_accounts", "information_sources"])
def test_each_frame_required(governed, frames, dropped):
    kwargs = dict(frames)
    kwargs[dropped] = None
    with pytest.raises(ValueError) as e:
        governed.evaluate_insider_trading(**kwargs)
    assert dropped in str(e.value)


def test_refuses_unmatched_information_source(governed, frames):
    kwargs = dict(frames)
    kwargs["information_sources"] = frames["information_sources"].iloc[0:0]
    with pytest.raises(ValueError) as e:
        governed.evaluate_insider_trading(**kwargs)
    assert "information-source" in str(e.value).lower()


def test_at_least_one_alert_present(governed, frames):
    out = governed.evaluate_insider_trading(**frames)
    assert len(out) >= 1 and ADAPTER_REQUIRED_COLUMNS <= set(out.columns)


def test_every_alert_is_at_or_above_threshold(governed, frames):
    out = governed.evaluate_insider_trading(**frames)
    assert (out["exposure_score"] >= governed.ALERT_THRESHOLD).all()


def test_clean_account_is_not_alerted(governed, frames):
    clean = {**frames, "trading_accounts": frames["trading_accounts"][frames["trading_accounts"]["account_ref"] == "ACC001"]}
    out = governed.evaluate_insider_trading(**clean)
    assert len(out) == 0


def test_the_gamma_imports_bridge_alerts_critical(governed, frames):
    """ACC019 trades ahead of a material non-public event at Gamma Imports Ltd -- an
    entity already in the estate network -- and must clear the alert threshold at
    Critical, proving the fusion bridge is a real alerting subject, not a decorative
    row. It is also the single highest-scoring account in the set, which matters: the
    FC-10 adapter builds its case/graph from score_all's top row, so the Gamma bridge
    has to BE that row."""
    scored = governed.score_all(**frames)
    top = scored.iloc[0]
    assert top["account_ref"] == "ACC019" and top["issuer_name"] == "Gamma Imports Ltd"
    row = governed.evaluate_insider_trading(**frames)
    bridge = row[row["account_ref"] == "ACC019"].iloc[0]
    assert bridge["issuer_name"] == "Gamma Imports Ltd"
    assert bridge["exposure_score"] == 90 and bridge["exposure_band"] == "Critical"


def test_working_reconstructs(governed, frames):
    out = governed.evaluate_insider_trading(**frames)
    w = json.loads(out.iloc[0]["risk_components"])
    total = sum(c["contribution"] for c in w["components"].values())
    assert abs(total - w["total"]) < 0.01


def test_one_scorer(governed):
    assert SCENARIO.read_text(encoding="utf-8").count("cm001_exposure_score(") == 1


def test_threshold_named_once(governed):
    assert governed.ALERT_THRESHOLD == 80
    assert ">= 80" not in SCENARIO.read_text(encoding="utf-8")

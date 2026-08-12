"""Build CM003_Spoofing.svg from the shared template. Run once; the SVG is
committed as the artefact. python3 diagrams/_build_cm003.py"""
from pathlib import Path
from _diagram_template import DiagramSpec, DataGroup, Component, write

SPEC = DiagramSpec(
    code="CM003", slug="Spoofing", title="Spoofing",
    subtitle="Manipulative Order Book Layering Exposure Pattern",
    description="Detects orders placed with no intention to execute, cancelled before the market can react, "
                 "manufacturing one-sided book depth and closed out by genuine opposite-side execution.",
    pattern_type="Spoofing", exposure_type="Market Manipulation Risk",
    data_groups=[
        DataGroup("ORDER BOOK DATA", ["Order placement &amp; cancellation logs", "Total &amp; spoof order value", "Order-side &amp; instrument reference", "Account order-flow history"]),
        DataGroup("CANCELLATION / AMEND TIMING DATA", ["Placement-to-cancellation timestamps", "Average cancellation speed", "Amend &amp; re-quote sequences", "Order lifecycle events"]),
        DataGroup("DEPTH &amp; IMBALANCE DATA", ["Spoof-side visible depth", "Genuine-side visible depth", "Order book imbalance ratios", "Depth-manufacture timing"]),
        DataGroup("EXECUTION DATA", ["Opposite-side filled value", "Fill rate &amp; execution timing", "Venue execution reports", "Trade confirmations"]),
        DataGroup("BROKER / COUNTERPARTY DATA", ["Broker &amp; clearing relationships", "Venue &amp; jurisdiction", "Relationship type", "Prior-alert history"]),
        DataGroup("TRADER / KYC DATA", ["Trader profile &amp; desk", "Declared trading mandate", "Account tenure", "Prior STOR/alert history"]),
        DataGroup("VENUE DATA", ["Exchange &amp; MTF reference data", "Market microstructure rules", "Trading-hours &amp; session data"]),
        DataGroup("OPEN SOURCE INTELLIGENCE", ["Adverse media", "Investigative reports", "Commercial databases"]),
    ],
    subject_label="TRADING ACCOUNT", subject_name="Viktor Sokolov &#183; ACC019",
    subject_context="Zeta Commodities Ltd Ordinary Shares", bridge_entity="Zeta Commodities Ltd",
    score=90, band="CRITICAL",
    components=[
        Component("Non-Bona-Fide Order Ratio", "$2,181,600 of $2,400,000 total order value (r=0.909)", "Critical", 35),
        Component("Cancellation Speed", "0.6 seconds average placement-to-cancellation", "Critical", 25),
        Component("Order Book Imbalance Created", "7,200 of 8,955 total visible depth manufactured (r=0.804)", "Critical", 20),
        Component("Opposite-Side Execution", "$1,917,630 filled on $2,181,600 spoof value (r=0.879)", "Critical", 20),
    ],
    risk_rationale=[
        "Orders placed with no intention to execute",
        "Cancelled well inside normal market reaction time",
        "One-sided book depth manufactured",
        "Genuine execution taken on the opposite side",
        "Broker relationship already flagged elsewhere",
        "Order flow inconsistent with genuine liquidity provision",
    ],
    investigation_value=[
        "Reconciles non-bona-fide order ratio",
        "Detects cancellation speed &amp; book imbalance",
        "Prioritises opposite-side execution risk",
        "Supports STOR filing decisions",
        "Enables workflow automation",
    ],
    intelligence_produced=[
        "Spoofing alerts",
        "Order-ratio exposure maps",
        "Cancellation-timing assessments",
        "Opposite-side execution profiles",
        "Investigator packages",
    ],
    outputs=[
        "Spoofing alerts", "Order-ratio exposure maps", "Cancellation-timing assessments",
        "Opposite-side execution profiles", "Escalation recommendations", "Investigation cases &amp; packages",
    ],
    key_benefits=[
        "Reconciles non-bona-fide order flow", "Detects cancellation &amp; imbalance patterns",
        "Prioritises opposite-side execution risk", "Supports STOR filing decisions",
        "Enables AI-assisted reviews", "Strengthens controls &amp; governance",
    ],
    downstream_consumers=[
        ("CM001", "Insider Trading"), ("CM006", "Front Running"), ("CM008", "Cross Market Abuse"),
        ("AIC001", "AI Investigator Copilot"), ("IW001", "Investigation Workflows"), ("CASEMGMT", "Case Management"),
    ],
    summary_lines=[
        "CM003 detects orders placed with no intention to",
        "execute. It quantifies the non-bona-fide order ratio,",
        "the cancellation speed, and corroborates the finding",
        "with the order book imbalance manufactured and the",
        "genuine execution taken on the opposite side.",
        "Order flow that would otherwise clear as ordinary",
        "market-making is surfaced and escalated for enhanced",
        "due diligence and STOR filing.",
    ],
    confidence_pct=87,
)

if __name__ == "__main__":
    p = write(SPEC, Path(__file__).resolve().parent)
    print("wrote", p)

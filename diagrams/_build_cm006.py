"""Build CM006_Front_Running.svg from the shared template. Run once; the SVG is
committed as the artefact. python3 diagrams/_build_cm006.py"""
from pathlib import Path
from _diagram_template import DiagramSpec, DataGroup, Component, write

SPEC = DiagramSpec(
    code="CM006", slug="Front_Running", title="Front Running",
    subtitle="Client Order Misuse Trading Exposure Pattern",
    description="Detects a trader dealing ahead of a known client order in the same direction, "
                 "corroborated by a documented knowledge linkage and closed out by disproportionate profit capture.",
    pattern_type="Front Running", exposure_type="Client Order Misuse Risk",
    data_groups=[
        DataGroup("ORDER &amp; POSITION DATA", ["Trading account positions", "Order &amp; execution timestamps", "Trader pre-position direction", "Position-correlation history"]),
        DataGroup("CLIENT ORDER DATA", ["Client order timing &amp; direction", "Order execution records", "Client order management logs", "Desk routing history"]),
        DataGroup("COMMUNICATIONS DATA", ["Contact event logs", "Desk communication records", "Meeting &amp; call logs", "Client-desk relationship data"]),
        DataGroup("MARKET DATA", ["Price &amp; volume history", "Realised P&amp;L", "Instrument reference data", "Venue execution data"]),
        DataGroup("CLIENT / COUNTERPARTY DATA", ["Client firm profile", "Client jurisdiction", "Relationship type", "Prior-alert history"]),
        DataGroup("TRADER / KYC DATA", ["Trader profile &amp; desk", "Declared trading mandate", "Account tenure", "Prior STOR/alert history"]),
        DataGroup("MARKET DATA", ["Order book depth", "Quote &amp; trade sequencing", "Venue latency records"]),
        DataGroup("OPEN SOURCE INTELLIGENCE", ["Adverse media", "Investigative reports", "Commercial databases"]),
    ],
    subject_label="TRADING ACCOUNT", subject_name="Vanessa Thistlethimble &#183; ACC019",
    subject_context="Agency Execution Desk", bridge_entity="Alpha Trading Ltd",
    score=90, band="CRITICAL",
    components=[
        Component("Timing Ahead of Client Order", "Trader's order placed 1 second before the client's order", "Critical", 35),
        Component("Position Correlation", "96% correlation with the client order's direction", "Critical", 25),
        Component("Profit Capture", "$2,184,000 captured on $2,400,000 position (r=0.910)", "Critical", 20),
        Component("Client Order Knowledge Linkage", "13 contact events with the desk handling the Alpha Trading Ltd order", "Critical", 20),
    ],
    risk_rationale=[
        "Own order placed seconds before the client order",
        "Position direction strongly correlated to client flow",
        "Documented linkage to the desk handling the order",
        "Profit captured disproportionate to position value",
        "Client firm already flagged elsewhere",
        "Trading pattern inconsistent with mandate",
    ],
    investigation_value=[
        "Reconciles order-timing sequencing",
        "Detects position correlation &amp; knowledge linkage",
        "Prioritises profit-capture risk",
        "Supports STOR filing decisions",
        "Enables workflow automation",
    ],
    intelligence_produced=[
        "Client order misuse alerts",
        "Order-timing exposure maps",
        "Knowledge-linkage assessments",
        "Profit-capture profiles",
        "Investigator packages",
    ],
    outputs=[
        "Client order misuse alerts", "Order-timing exposure maps", "Knowledge-linkage assessments",
        "Profit-capture profiles", "Escalation recommendations", "Investigation cases &amp; packages",
    ],
    key_benefits=[
        "Reconciles order-timing sequencing", "Detects correlation &amp; knowledge linkage",
        "Prioritises profit-capture risk", "Supports STOR filing decisions",
        "Enables AI-assisted reviews", "Strengthens controls &amp; governance",
    ],
    downstream_consumers=[
        ("CM001", "Insider Trading"), ("CM007", "Pump and Dump"), ("CM008", "Cross Market Abuse"),
        ("AIC001", "AI Investigator Copilot"), ("IW001", "Investigation Workflows"), ("CASEMGMT", "Case Management"),
    ],
    summary_lines=[
        "CM006 detects a trader dealing ahead of a known",
        "client order. It quantifies the timing ahead of the",
        "order, the position correlation to the client's",
        "direction, and corroborates the finding with a",
        "documented knowledge linkage and the profit captured",
        "once the client order lands. Trading that would",
        "otherwise clear as an ordinary directional bet is",
        "surfaced and escalated for enhanced due diligence.",
    ],
    confidence_pct=87,
)

if __name__ == "__main__":
    p = write(SPEC, Path(__file__).resolve().parent)
    print("wrote", p)

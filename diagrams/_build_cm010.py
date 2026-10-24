"""Build CM010_Suspicious_Order_Patterns.svg from the shared template. Run once; the
SVG is committed as the artefact. python3 diagrams/_build_cm010.py"""
from pathlib import Path
from _diagram_template import DiagramSpec, DataGroup, Component, write

SPEC = DiagramSpec(
    code="CM010", slug="Suspicious_Order_Patterns", title="Suspicious Order Patterns",
    subtitle="Order-Flow Manipulation Exposure Pattern",
    description="Detects order-flow manipulation via an abnormal cancel/amend rate, quote-stuffing intensity, "
                 "momentum ignition after an order burst, and an order-size anomaly, with no single tell.",
    pattern_type="Suspicious Order Patterns", exposure_type="Order-Flow Manipulation Risk",
    data_groups=[
        DataGroup("ORDER FLOW DATA", ["Trading account order log", "Order &amp; execution history", "Order-submission timestamps", "Venue routing records"]),
        DataGroup("CANCEL/AMEND DATA", ["Cancelled order counts", "Total order counts", "Cancel/amend timing clusters", "Order-lifetime distribution"]),
        DataGroup("BURST/MOMENTUM DATA", ["Order-submission burst rate", "Price move after burst", "Instrument normal move baseline", "Price &amp; volume history"]),
        DataGroup("ORDER SIZE DATA", ["Average order size", "Account normal order size", "Order-size distribution", "Size-anomaly timing"]),
        DataGroup("VENUE DATA", ["Venue operator identity", "Venue jurisdiction", "Venue relationship type", "Prior-alert history"]),
        DataGroup("TRADER / KYC DATA", ["Trader profile", "Declared trading mandate", "Account tenure", "Prior STOR/alert history"]),
        DataGroup("MARKET DATA", ["Instrument reference data", "Order-book depth history", "Reference price levels"]),
        DataGroup("OPEN SOURCE INTELLIGENCE", ["Adverse media", "Investigative reports", "Commercial databases"]),
    ],
    subject_label="TRADING ACCOUNT", subject_name="Dominic Heronbutton &#183; ACC019",
    subject_context="Order Flow (Alpha Trading Ltd Ordinary Shares)", bridge_entity="Alpha Trading Ltd",
    score=90, band="CRITICAL",
    components=[
        Component("Cancel/Amend Rate", "2,720 of 3,200 orders cancelled (r=0.850)", "Critical", 35),
        Component("Quote Stuffing Intensity", "70 orders per second at peak", "Critical", 25),
        Component("Momentum Ignition Signal", "2.40% move after burst vs. 0.30% normal (r=8.00)", "Critical", 20),
        Component("Order Size Anomaly", "4,000 of 1,000 normal order size (r=4.00)", "Critical", 20),
    ],
    risk_rationale=[
        "Cancel/amend rate far beyond genuine trading",
        "Order-submission burst consistent with quote stuffing",
        "Price move ignited immediately after the burst",
        "Order size sharply beyond the account's normal size",
        "Venue operator already flagged elsewhere",
        "Order flow inconsistent with declared mandate",
    ],
    investigation_value=[
        "Reconciles cancel/amend burst pattern",
        "Detects momentum ignition &amp; size anomaly",
        "Prioritises order-flow manipulation risk",
        "Supports STOR filing decisions",
        "Enables workflow automation",
    ],
    intelligence_produced=[
        "Order-flow manipulation alerts",
        "Cancel/amend exposure maps",
        "Momentum-ignition assessments",
        "Order-size anomaly profiles",
        "Investigator packages",
    ],
    outputs=[
        "Order-flow manipulation alerts", "Cancel/amend exposure maps", "Momentum-ignition assessments",
        "Order-size anomaly profiles", "Escalation recommendations", "Investigation cases &amp; packages",
    ],
    key_benefits=[
        "Reconciles cancel/amend burst pattern", "Detects momentum &amp; size anomaly",
        "Prioritises order-flow manipulation risk", "Supports STOR filing decisions",
        "Enables AI-assisted reviews", "Strengthens controls &amp; governance",
    ],
    downstream_consumers=[
        ("CM003", "Spoofing"), ("CM004", "Layering"), ("CM002", "Market Manipulation"),
        ("AIC001", "AI Investigator Copilot"), ("IW001", "Investigation Workflows"), ("CASEMGMT", "Case Management"),
    ],
    summary_lines=[
        "CM010 detects order-flow manipulation with no",
        "single tell. It quantifies the cancel/amend rate, the",
        "quote-stuffing intensity, and corroborates the finding",
        "with momentum ignition after the order burst and an",
        "order-size anomaly beyond the account's normal size.",
        "Order flow that would otherwise clear as noisy but",
        "ordinary high-frequency activity is surfaced and",
        "escalated for enhanced due diligence and STOR filing.",
    ],
    confidence_pct=87,
)

if __name__ == "__main__":
    p = write(SPEC, Path(__file__).resolve().parent)
    print("wrote", p)

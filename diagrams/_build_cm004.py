"""Build CM004_Layering.svg from the shared template. Run once; the SVG is
committed as the artefact. python3 diagrams/_build_cm004.py"""
from pathlib import Path
from _diagram_template import DiagramSpec, DataGroup, Component, write

SPEC = DiagramSpec(
    code="CM004", slug="Layering", title="Layering",
    subtitle="Order-Book Staggered Price-Level Exposure Pattern",
    description="Detects staggered non-bona-fide orders across multiple price levels, distorting the "
                 "order book, sized well beyond ordinary order-to-trade activity, and reversed within "
                 "seconds once the book has moved.",
    pattern_type="Layering (Order-Book)", exposure_type="Order-Book Distortion Risk",
    data_groups=[
        DataGroup("ORDER BOOK DATA", ["Trading account order flow", "Distinct price levels populated", "Order placement timestamps", "Book depth snapshots"]),
        DataGroup("ORDER-TO-TRADE RATIO DATA", ["Orders placed counts", "Orders executed counts", "Order-to-trade ratio history", "Cancellation patterns"]),
        DataGroup("DEPTH &amp; IMBALANCE DATA", ["Visible book depth by side", "Imbalance ratio history", "Price-level concentration", "Counterparty order flow"]),
        DataGroup("REVERSAL TIMING DATA", ["Seconds-to-reversal history", "Cancellation timestamps", "Book-movement correlation", "Reversal pattern clustering"]),
        DataGroup("VENUE/COUNTERPARTY DATA", ["Venue operator identity", "Venue jurisdiction", "Relationship type", "Prior-alert history"]),
        DataGroup("TRADER/KYC DATA", ["Trader profile", "Declared trading mandate", "Account tenure", "Prior STOR/alert history"]),
        DataGroup("INSTRUMENT REFERENCE DATA", ["Instrument identifiers", "Issuer reference data", "Tick size &amp; venue rules", "Liquidity profile"]),
        DataGroup("OPEN SOURCE INTELLIGENCE", ["Adverse media", "Investigative reports", "Commercial databases"]),
    ],
    subject_label="TRADING ACCOUNT", subject_name="Renata Silva &#183; ACC019",
    subject_context="Order Flow", bridge_entity="Gamma Imports Ltd",
    score=90, band="CRITICAL",
    components=[
        Component("Staggered Order Levels", "10 distinct price levels populated", "Critical", 35),
        Component("Order-to-Trade Ratio", "300 orders placed against 5 executed (r=60.0)", "Critical", 25),
        Component("Book Imbalance Created", "0.75 share of visible book depth on one side", "Critical", 20),
        Component("Reversal Speed", "Staggered orders pulled 3 seconds after the book moved", "Critical", 20),
    ],
    risk_rationale=[
        "Orders staggered across a wide spread of price levels",
        "Order-to-trade ratio far beyond ordinary activity",
        "Material book imbalance created on one side",
        "Staggered orders reversed within seconds",
        "Venue already flagged elsewhere in the estate",
        "Order flow inconsistent with mandate",
    ],
    investigation_value=[
        "Reconciles staggered order-level footprint",
        "Detects order-to-trade &amp; imbalance signals",
        "Prioritises reversal-speed risk",
        "Supports STOR filing decisions",
        "Enables workflow automation",
    ],
    intelligence_produced=[
        "Order-book distortion alerts",
        "Staggered-level exposure maps",
        "Order-to-trade ratio assessments",
        "Reversal-speed profiles",
        "Investigator packages",
    ],
    outputs=[
        "Order-book distortion alerts", "Staggered-level exposure maps", "Order-to-trade ratio assessments",
        "Reversal-speed profiles", "Escalation recommendations", "Investigation cases &amp; packages",
    ],
    key_benefits=[
        "Reconciles staggered order levels", "Detects order-to-trade &amp; imbalance signals",
        "Prioritises reversal-speed risk", "Supports STOR filing decisions",
        "Enables AI-assisted reviews", "Strengthens controls &amp; governance",
    ],
    downstream_consumers=[
        ("CM001", "Insider Trading"), ("CM006", "Front Running"), ("CM007", "Pump and Dump"),
        ("AIC001", "AI Investigator Copilot"), ("IW001", "Investigation Workflows"), ("CASEMGMT", "Case Management"),
    ],
    summary_lines=[
        "CM004 detects staggered non-bona-fide orders across",
        "multiple price levels. It quantifies the staggered order",
        "levels, the order-to-trade ratio, and corroborates the",
        "finding with the book imbalance created and the speed",
        "at which the staggered orders are reversed once the",
        "book has moved. Order flow that would otherwise clear",
        "as unremarkable market-making is surfaced and escalated",
        "for enhanced due diligence and STOR filing.",
    ],
    confidence_pct=87,
)

if __name__ == "__main__":
    p = write(SPEC, Path(__file__).resolve().parent)
    print("wrote", p)

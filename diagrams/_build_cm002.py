"""Build CM002_Market_Manipulation.svg from the shared template. Run once; the SVG is
committed as the artefact. python3 diagrams/_build_cm002.py"""
from pathlib import Path
from _diagram_template import DiagramSpec, DataGroup, Component, write

SPEC = DiagramSpec(
    code="CM002", slug="Market_Manipulation", title="Market Manipulation",
    subtitle="Artificial Price / Volume Distortion Exposure Pattern",
    description="Detects a price move sized well beyond normal volatility, concentrated in an outsized share "
                 "of market volume, coordinated across linked accounts, and largely unwound once the "
                 "manipulative window closes.",
    pattern_type="Market Manipulation", exposure_type="Price/Volume Distortion Risk",
    data_groups=[
        DataGroup("ORDER &amp; TRADE DATA", ["Trading account positions", "Order &amp; execution history", "Trade timestamps &amp; sequencing", "Cancel/amend ratios"]),
        DataGroup("MARKET DATA", ["Price &amp; volume history", "Normal volatility baselines", "Total market volume by window", "Instrument reference data"]),
        DataGroup("COORDINATED-ACCOUNT DATA", ["Linked-account identifiers", "Common ownership &amp; control", "Shared execution timing", "Venue-level clustering"]),
        DataGroup("REVERSAL / POST-WINDOW DATA", ["Post-period price series", "Reversal magnitude &amp; timing", "Window close timestamps", "Exit order records"]),
        DataGroup("COUNTERPARTY DATA", ["Ultimate owner &amp; venue", "Jurisdiction of registration", "Relationship type", "Prior-alert history"]),
        DataGroup("TRADER / KYC DATA", ["Account holder profile &amp; desk", "Declared trading mandate", "Account tenure", "Prior STOR/alert history"]),
        DataGroup("CORPORATE REGISTRY DATA", ["Issuer ownership &amp; control", "Director &amp; officer records", "Beneficial ownership"]),
        DataGroup("OPEN SOURCE INTELLIGENCE", ["Adverse media", "Investigative reports", "Commercial databases"]),
    ],
    subject_label="TRADING ACCOUNT", subject_name="Marcus Kettlebutton &#183; ACC019",
    subject_context="Equities Prop Desk", bridge_entity="Alpha Trading Ltd",
    score=90, band="CRITICAL",
    components=[
        Component("Price Impact Ratio", "30.06% move against 4.0% normal volatility (r=7.515)", "Critical", 35),
        Component("Volume Concentration", "67% of total market volume in the window", "Critical", 25),
        Component("Coordinated Accounts", "8 linked accounts trading in concert", "Critical", 20),
        Component("Reversal After Close", "28.74% reversed once the window closed (r=0.956)", "Critical", 20),
    ],
    risk_rationale=[
        "Price move well beyond normal volatility",
        "Outsized share of total market volume",
        "Coordinated across multiple linked accounts",
        "Move largely unwound once the window closed",
        "Ultimate owner already flagged elsewhere",
        "Trading pattern inconsistent with mandate",
    ],
    investigation_value=[
        "Reconciles price impact against normal volatility",
        "Detects coordinated-account trading &amp; volume concentration",
        "Prioritises reversal-after-close risk",
        "Supports STOR filing decisions",
        "Enables workflow automation",
    ],
    intelligence_produced=[
        "Market manipulation alerts",
        "Price-impact exposure maps",
        "Coordinated-account network assessments",
        "Reversal-after-close profiles",
        "Investigator packages",
    ],
    outputs=[
        "Market manipulation alerts", "Price-impact exposure maps", "Coordinated-account assessments",
        "Reversal-after-close profiles", "Escalation recommendations", "Investigation cases &amp; packages",
    ],
    key_benefits=[
        "Reconciles price impact &amp; volume concentration", "Detects coordinated-account trading",
        "Prioritises reversal-after-close risk", "Supports STOR filing decisions",
        "Enables AI-assisted reviews", "Strengthens controls &amp; governance",
    ],
    downstream_consumers=[
        ("CM001", "Insider Trading"), ("CM006", "Front Running"), ("CM008", "Cross Market Abuse"),
        ("AIC001", "AI Investigator Copilot"), ("IW001", "Investigation Workflows"), ("CASEMGMT", "Case Management"),
    ],
    summary_lines=[
        "CM002 detects a price move artificially distorted",
        "well beyond normal volatility. It quantifies the price",
        "impact ratio, the volume concentration, and corroborates",
        "the finding with coordination across linked accounts",
        "and the reversal once the manipulative window closes.",
        "Trading that would otherwise clear as an ordinary large",
        "directional trade is surfaced and escalated for enhanced",
        "due diligence and STOR filing.",
    ],
    confidence_pct=87,
)

if __name__ == "__main__":
    p = write(SPEC, Path(__file__).resolve().parent)
    print("wrote", p)

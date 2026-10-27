"""Build CM005_Wash_Trading.svg from the shared template. Run once; the SVG is
committed as the artefact. python3 diagrams/_build_cm005.py"""
from pathlib import Path
from _diagram_template import DiagramSpec, DataGroup, Component, write

SPEC = DiagramSpec(
    code="CM005", slug="Wash_Trading", title="Wash Trading",
    subtitle="Matched-Order No-Genuine-Ownership-Change Exposure Pattern",
    description="Detects matched buy and sell orders that produce no genuine change in beneficial ownership, "
                 "corroborated by documented ownership overlap and closed out in a concentrated counterparty ring.",
    pattern_type="Wash Trading", exposure_type="Manufactured Volume Risk",
    data_groups=[
        DataGroup("ORDER &amp; EXECUTION DATA", ["Trading account positions", "Order &amp; execution history", "Self-matched order pairs", "Trade timing &amp; sequencing"]),
        DataGroup("OWNERSHIP DATA", ["Buy-side beneficial ownership", "Sell-side beneficial ownership", "Common control &amp; directorships", "Registered address matches"]),
        DataGroup("VOLUME &amp; REPORTING DATA", ["Reported trade volume", "Genuine economic volume", "Instrument turnover baselines", "Price-window volume profiles"]),
        DataGroup("COUNTERPARTY DATA", ["Distinct counterparty counts", "Counterparty relationship history", "Give-up clearing arrangements", "Prior-alert history"]),
        DataGroup("CLEARING/BROKER DATA", ["Clearing broker identity", "Prime brokerage relationships", "Broker jurisdiction", "Cross-account clearing linkages"]),
        DataGroup("TRADER / KYC DATA", ["Trader profile &amp; account", "Declared trading mandate", "Account tenure", "Prior STOR/alert history"]),
        DataGroup("INSTRUMENT REFERENCE DATA", ["Instrument issuer &amp; class", "Venue execution data", "Price &amp; volume history", "Corporate actions"]),
        DataGroup("OPEN SOURCE INTELLIGENCE", ["Adverse media", "Investigative reports", "Commercial databases"]),
    ],
    subject_label="TRADING ACCOUNT", subject_name="Grigor Puddlequill &#183; ACC019",
    subject_context="Continental Correspondent Bank Pref Shares", bridge_entity="Continental Correspondent Bank",
    score=90, band="CRITICAL",
    components=[
        Component("Self-Match Ratio", "450,000 of 500,000 total volume self-matched (r=0.900)", "Critical", 35),
        Component("Beneficial Ownership Overlap", "Overlap score 95 of 100 between buy-side and sell-side", "Critical", 25),
        Component("Volume Inflation", "480,000 reported vs. 150,000 genuine economic volume (r=3.200)", "Critical", 20),
        Component("Counterparty Concentration", "1 distinct counterparty", "Critical", 20),
    ],
    risk_rationale=[
        "Self-matched volume well beyond ordinary market making",
        "Documented overlap in beneficial ownership",
        "Reported volume materially exceeds genuine activity",
        "Volume concentrated in a single counterparty",
        "Clearing broker already flagged elsewhere",
        "Trading pattern inconsistent with mandate",
    ],
    investigation_value=[
        "Reconciles self-matched order volume",
        "Detects ownership overlap &amp; ring trading",
        "Prioritises volume-inflation risk",
        "Supports STOR filing decisions",
        "Enables workflow automation",
    ],
    intelligence_produced=[
        "Wash trading alerts",
        "Self-match exposure maps",
        "Ownership-overlap assessments",
        "Volume-inflation profiles",
        "Investigator packages",
    ],
    outputs=[
        "Wash trading alerts", "Self-match exposure maps", "Ownership-overlap assessments",
        "Volume-inflation profiles", "Escalation recommendations", "Investigation cases &amp; packages",
    ],
    key_benefits=[
        "Reconciles self-matched order volume", "Detects ownership overlap &amp; ring trading",
        "Prioritises volume-inflation risk", "Supports STOR filing decisions",
        "Enables AI-assisted reviews", "Strengthens controls &amp; governance",
    ],
    downstream_consumers=[
        ("CM001", "Insider Trading"), ("CM006", "Front Running"), ("CM008", "Cross Market Abuse"),
        ("AIC001", "AI Investigator Copilot"), ("IW001", "Investigation Workflows"), ("CASEMGMT", "Case Management"),
    ],
    summary_lines=[
        "CM005 detects matched buy and sell orders that",
        "produce no genuine change in beneficial ownership.",
        "It quantifies the self-match ratio, the documented",
        "ownership overlap, and corroborates the finding with",
        "volume inflation and counterparty concentration.",
        "Trading that would otherwise clear as ordinary",
        "two-sided liquidity provision is surfaced and",
        "escalated for enhanced due diligence and STOR filing.",
    ],
    confidence_pct=87,
)

if __name__ == "__main__":
    p = write(SPEC, Path(__file__).resolve().parent)
    print("wrote", p)

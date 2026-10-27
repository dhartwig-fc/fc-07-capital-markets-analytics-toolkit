"""Build CM008_Cross_Market_Abuse.svg from the shared template. Run once; the SVG is
committed as the artefact. python3 diagrams/_build_cm008.py"""
from pathlib import Path
from _diagram_template import DiagramSpec, DataGroup, Component, write

SPEC = DiagramSpec(
    code="CM008", slug="Cross_Market_Abuse", title="Cross Market Abuse",
    subtitle="Cross-Venue Correlated Position Manipulation Pattern",
    description="Detects manipulation transmitted across correlated venues or instruments, sized by cross-venue "
                 "position correlation, corroborated by price-impact transfer and closed out by tightly synchronised timing.",
    pattern_type="Cross Market Abuse", exposure_type="Cross-Venue Manipulation Risk",
    data_groups=[
        DataGroup("ORDER &amp; POSITION DATA", ["Trading account positions", "Order &amp; execution history", "Cash vs derivative position pairs", "Cross-venue timing"]),
        DataGroup("CORRELATED INSTRUMENT DATA", ["Primary / correlated instrument pairs", "Correlation coefficients", "Instrument reference data", "Product type (CFD, futures, ADR, swap)"]),
        DataGroup("PRICE IMPACT DATA", ["Price &amp; volume history", "Price-impact-transfer ratios", "Market microstructure data", "Venue execution data"]),
        DataGroup("TRADE TIMING DATA", ["Cross-venue trade timestamps", "Synchronisation windows", "Order-routing latency", "Execution sequencing"]),
        DataGroup("VENUE DATA", ["Venue &amp; jurisdiction reference", "Venue liquidity profiles", "Cross-listing records", "OTC venue registrations"]),
        DataGroup("TRADER / KYC DATA", ["Trader profile", "Declared trading mandate", "Account tenure", "Prior STOR/alert history"]),
        DataGroup("INSTRUMENT REFERENCE DATA", ["Issuer identifiers", "Corporate actions", "Listing history", "Product relationship type"]),
        DataGroup("OPEN SOURCE INTELLIGENCE", ["Adverse media", "Investigative reports", "Commercial databases"]),
    ],
    subject_label="TRADING ACCOUNT", subject_name="Natasha Ivybristlea &#183; ACC019",
    subject_context="Cross-Venue Correlated Position", bridge_entity="Zeta Commodities Ltd",
    score=90, band="CRITICAL",
    components=[
        Component("Cross-Venue Position Correlation", "97% correlation between cash &amp; derivative positions", "Critical", 35),
        Component("Venue Count", "Correlated activity spread across 6 distinct venues", "Critical", 25),
        Component("Price Impact Transfer", "0.85 of primary-instrument impact transferred", "Critical", 20),
        Component("Timing Synchronization", "Trades executed 2 seconds apart across venues", "Critical", 20),
    ],
    risk_rationale=[
        "Position correlation tighter than normal trading",
        "Activity spread across a growing venue count",
        "Material price-impact transfer confirmed",
        "Trades tightly synchronised across venues",
        "Correlated instrument already flagged elsewhere",
        "Trading pattern inconsistent with mandate",
    ],
    investigation_value=[
        "Reconciles cross-venue position correlation",
        "Detects venue spread &amp; price-impact transfer",
        "Prioritises timing-synchronization risk",
        "Supports STOR filing decisions",
        "Enables workflow automation",
    ],
    intelligence_produced=[
        "Cross-venue manipulation alerts",
        "Position-correlation exposure maps",
        "Price-impact-transfer assessments",
        "Timing-synchronization profiles",
        "Investigator packages",
    ],
    outputs=[
        "Cross-venue manipulation alerts", "Position-correlation exposure maps", "Price-impact-transfer assessments",
        "Timing-synchronization profiles", "Escalation recommendations", "Investigation cases &amp; packages",
    ],
    key_benefits=[
        "Reconciles cross-venue correlation", "Detects price-impact &amp; timing signals",
        "Prioritises manipulation risk", "Supports STOR filing decisions",
        "Enables AI-assisted reviews", "Strengthens controls &amp; governance",
    ],
    downstream_consumers=[
        ("CM001", "Insider Trading"), ("CM006", "Front Running"), ("CM007", "Pump and Dump"),
        ("AIC001", "AI Investigator Copilot"), ("IW001", "Investigation Workflows"), ("CASEMGMT", "Case Management"),
    ],
    summary_lines=[
        "CM008 detects manipulation transmitted across",
        "correlated venues or instruments. It quantifies the",
        "cross-venue position correlation, the number of venues",
        "the correlated activity spans, and corroborates the",
        "finding with a documented price-impact transfer and",
        "tightly synchronised cross-venue timing. Manipulation",
        "that would otherwise clear as independent trading in",
        "unrelated products is surfaced and escalated for STOR.",
    ],
    confidence_pct=87,
)

if __name__ == "__main__":
    p = write(SPEC, Path(__file__).resolve().parent)
    print("wrote", p)

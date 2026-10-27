"""Build CM007_Pump_and_Dump.svg from the shared template. Run once; the SVG is
committed as the artefact. python3 diagrams/_build_cm007.py"""
from pathlib import Path
from _diagram_template import DiagramSpec, DataGroup, Component, write

SPEC = DiagramSpec(
    code="CM007", slug="Pump_and_Dump", title="Pump and Dump",
    subtitle="Coordinated Promotion &amp; Price Inflation Exposure Pattern",
    description="Detects free-float accumulation ahead of a coordinated promotional campaign, the price "
                 "inflation the campaign produces, and the volume distributed into the retail it creates.",
    pattern_type="Pump and Dump", exposure_type="Market Manipulation Risk",
    data_groups=[
        DataGroup("POSITION &amp; FLOAT DATA", ["Trading account positions", "Free-float accumulation history", "Order &amp; execution history", "Accumulation timing"]),
        DataGroup("PROMOTIONAL/SOCIAL DATA", ["Telegram / Discord / forum posts", "Coordinated-account clustering", "Campaign timing &amp; burst detection", "Content dissemination logs"]),
        DataGroup("PRICE &amp; VOLUME DATA", ["Pre-campaign baseline price", "Peak price &amp; timing", "Volume history", "Venue execution data"]),
        DataGroup("DISTRIBUTION DATA", ["Volume sold to retail", "Total position &amp; distribution timing", "Retail buy-side concentration", "Post-peak volume decay"]),
        DataGroup("PROMOTER DATA", ["Promoter identity &amp; channel", "Promoter jurisdiction", "Prior-alert history", "Cross-campaign linkage"]),
        DataGroup("TRADER / KYC DATA", ["Trader profile", "Account tenure", "Declared trading mandate", "Prior STOR/alert history"]),
        DataGroup("INSTRUMENT REFERENCE DATA", ["Free-float &amp; share structure", "Listing venue &amp; tier", "Issuer disclosures", "Market-cap tier"]),
        DataGroup("OPEN SOURCE INTELLIGENCE", ["Adverse media", "Investigative reports", "Commercial databases"]),
    ],
    subject_label="TRADING ACCOUNT", subject_name="Desmond Vellummote &#183; ACC019",
    subject_context="Corvus Aerospace Inc", bridge_entity="John Cloverspindle (P001)",
    score=90, band="CRITICAL",
    components=[
        Component("Accumulation Concentration", "68% of the free float accumulated pre-promotion", "Critical", 35),
        Component("Promotional Coordination", "14 coordinated promotional posts identified", "Critical", 25),
        Component("Price Inflation", "$3.57 peak on a $0.85 baseline (r=4.200)", "Critical", 20),
        Component("Distribution Into Retail", "315,000 of 350,000 units distributed (r=0.900)", "Critical", 20),
    ],
    risk_rationale=[
        "Free float accumulated well beyond a passive position",
        "Promotional burst coordinated across multiple channels",
        "Price inflated well beyond the pre-campaign baseline",
        "Position distributed once retail buying peaked",
        "Promoter already flagged elsewhere in the network",
        "Trading pattern inconsistent with organic interest",
    ],
    investigation_value=[
        "Reconciles pre-campaign accumulation",
        "Detects promotional coordination &amp; price inflation",
        "Prioritises distribution-into-retail risk",
        "Supports STOR filing decisions",
        "Enables workflow automation",
    ],
    intelligence_produced=[
        "Market manipulation alerts",
        "Accumulation exposure maps",
        "Promotional-coordination assessments",
        "Distribution-into-retail profiles",
        "Investigator packages",
    ],
    outputs=[
        "Market manipulation alerts", "Accumulation exposure maps", "Promotional-coordination assessments",
        "Distribution-into-retail profiles", "Escalation recommendations", "Investigation cases &amp; packages",
    ],
    key_benefits=[
        "Reconciles pre-campaign accumulation", "Detects coordination &amp; price inflation",
        "Prioritises distribution-into-retail risk", "Supports STOR filing decisions",
        "Enables AI-assisted reviews", "Strengthens controls &amp; governance",
    ],
    downstream_consumers=[
        ("CM001", "Insider Trading"), ("CM006", "Front Running"), ("CM008", "Cross Market Abuse"),
        ("AIC001", "AI Investigator Copilot"), ("IW001", "Investigation Workflows"), ("CASEMGMT", "Case Management"),
    ],
    summary_lines=[
        "CM007 detects free-float accumulation ahead of a",
        "coordinated promotional campaign. It quantifies the",
        "accumulation concentration, the promotional burst, and",
        "corroborates the finding with the price inflation the",
        "campaign produces and the volume distributed into the",
        "retail buying it created. Trading that would otherwise",
        "clear as an ordinary momentum trade is surfaced and",
        "escalated for enhanced due diligence and STOR filing.",
    ],
    confidence_pct=87,
)

if __name__ == "__main__":
    p = write(SPEC, Path(__file__).resolve().parent)
    print("wrote", p)

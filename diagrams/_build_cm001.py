"""Build CM001_Insider_Trading.svg from the shared template. Run once; the SVG is
committed as the artefact. python3 diagrams/_build_cm001.py"""
from pathlib import Path
from _diagram_template import DiagramSpec, DataGroup, Component, write

SPEC = DiagramSpec(
    code="CM001", slug="Insider_Trading", title="Insider Trading",
    subtitle="Material Non-Public Information Trading Exposure Pattern",
    description="Detects trading ahead of a material non-public event, sized well beyond normal activity, "
                 "corroborated by a documented information-access linkage and closed out by realised profit.",
    pattern_type="Insider Trading", exposure_type="MNPI Trading Risk",
    data_groups=[
        DataGroup("ORDER &amp; POSITION DATA", ["Trading account positions", "Order &amp; execution history", "Normal average position baselines", "Position-build timing"]),
        DataGroup("MATERIAL EVENT DATA", ["Earnings / M&amp;A / regulatory events", "Public disclosure timestamps", "Event price-impact data", "Issuer corporate actions"]),
        DataGroup("COMMUNICATIONS DATA", ["Contact event logs", "Corporate access records", "Meeting &amp; call logs", "Information-source relationships"]),
        DataGroup("MARKET DATA", ["Price &amp; volume history", "Realised P&amp;L", "Instrument reference data", "Venue execution data"]),
        DataGroup("INFORMATION SOURCE DATA", ["Source role &amp; employer", "Source jurisdiction", "Relationship type", "Prior-alert history"]),
        DataGroup("TRADER / KYC DATA", ["Trader profile &amp; desk", "Declared trading mandate", "Account tenure", "Prior STOR/alert history"]),
        DataGroup("CORPORATE REGISTRY DATA", ["Issuer ownership &amp; control", "Director &amp; officer records", "Beneficial ownership"]),
        DataGroup("OPEN SOURCE INTELLIGENCE", ["Adverse media", "Investigative reports", "Commercial databases"]),
    ],
    subject_label="TRADING ACCOUNT", subject_name="Viktor Flintquill &#183; ACC019",
    subject_context="Special Situations Desk", bridge_entity="Gammavane Imports Ltd",
    score=90, band="CRITICAL",
    components=[
        Component("Pre-Event Position Build", "39,600 of 60,000 normal position (r=0.660)", "Critical", 35),
        Component("Timing Proximity to Event", "Position built 0 days before the event", "Critical", 25),
        Component("Information Access Linkage", "10 contact events with the Gammavane Imports Ltd Head of IR", "Critical", 20),
        Component("Profit Realisation", "$2,090,400 realised on $2,400,000 entry (r=0.871)", "Critical", 20),
    ],
    risk_rationale=[
        "Position built well beyond normal average",
        "Position timed immediately before the event",
        "Documented linkage to a corporate insider",
        "Profit realised once the event's impact landed",
        "Information source already flagged elsewhere",
        "Trading pattern inconsistent with mandate",
    ],
    investigation_value=[
        "Reconciles pre-event position build",
        "Detects timing proximity &amp; information linkage",
        "Prioritises profit-realisation risk",
        "Supports STOR filing decisions",
        "Enables workflow automation",
    ],
    intelligence_produced=[
        "MNPI trading alerts",
        "Position-build exposure maps",
        "Information-linkage assessments",
        "Profit-realisation profiles",
        "Investigator packages",
    ],
    outputs=[
        "MNPI trading alerts", "Position-build exposure maps", "Information-linkage assessments",
        "Profit-realisation profiles", "Escalation recommendations", "Investigation cases &amp; packages",
    ],
    key_benefits=[
        "Reconciles pre-event position build", "Detects timing &amp; information linkage",
        "Prioritises profit-realisation risk", "Supports STOR filing decisions",
        "Enables AI-assisted reviews", "Strengthens controls &amp; governance",
    ],
    downstream_consumers=[
        ("CM006", "Front Running"), ("CM007", "Pump and Dump"), ("CM008", "Cross Market Abuse"),
        ("AIC001", "AI Investigator Copilot"), ("IW001", "Investigation Workflows"), ("CASEMGMT", "Case Management"),
    ],
    summary_lines=[
        "CM001 detects trading ahead of a material non-public",
        "event. It quantifies the pre-event position build, the",
        "timing proximity to the event, and corroborates the",
        "finding with a documented information-access linkage",
        "and the profit realised once the event's impact lands.",
        "Trading that would otherwise clear as an ordinary",
        "directional bet is surfaced and escalated for enhanced",
        "due diligence and STOR filing.",
    ],
    confidence_pct=87,
)

if __name__ == "__main__":
    p = write(SPEC, Path(__file__).resolve().parent)
    print("wrote", p)

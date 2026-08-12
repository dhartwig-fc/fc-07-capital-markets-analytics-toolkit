"""Build CM009_Benchmark_Manipulation.svg from the shared template. Run once; the SVG
is committed as the artefact. python3 diagrams/_build_cm009.py"""
from pathlib import Path
from _diagram_template import DiagramSpec, DataGroup, Component, write

SPEC = DiagramSpec(
    code="CM009", slug="Benchmark_Manipulation", title="Benchmark Manipulation",
    subtitle="Fixing-Window Order Flow Exposure Pattern",
    description="Detects volume concentrated into a regulated fixing window's closing seconds, distorting the "
                 "price far beyond the instrument's normal deviation, with a documented repeat pattern.",
    pattern_type="Benchmark Manipulation", exposure_type="Fixing Distortion Risk",
    data_groups=[
        DataGroup("FIXING WINDOW DATA", ["Fixing-window order flow", "Fixing-window volume", "Total daily volume baselines", "Order execution timestamps"]),
        DataGroup("BENCHMARK REFERENCE DATA", ["Benchmark fixing methodology", "Fixing window open/close times", "Reference-rate publication records", "Prior benchmark alert history"]),
        DataGroup("PRICE DEVIATION DATA", ["Fixing price deviation", "Instrument normal deviation baselines", "Contemporaneous market-wide moves", "Post-fixing price reversion"]),
        DataGroup("ORDER TIMING DATA", ["Seconds before fixing close", "Order-book depth at close", "Execution venue timestamps", "Order cancellation history"]),
        DataGroup("REPEAT-PATTERN DATA", ["Prior fixing-window occurrences", "Cross-window behavioural clustering", "Same-benchmark repeat frequency", "Escalation trend history"]),
        DataGroup("TRADER / KYC DATA", ["Trader profile &amp; mandate", "Account tenure", "Declared trading strategy", "Prior STOR/alert history"]),
        DataGroup("ADMINISTRATOR / BENCHMARK DATA", ["Benchmark administrator", "Benchmark jurisdiction", "BMR compliance status", "Prior administrator alerts"]),
        DataGroup("OPEN SOURCE INTELLIGENCE", ["Adverse media", "Regulatory enforcement actions", "Commercial databases"]),
    ],
    subject_label="TRADING ACCOUNT", subject_name="Sergei Ivanov &#183; ACC019",
    subject_context="USD Reference Rate Fixing", bridge_entity="Gamma Imports Ltd",
    score=90, band="CRITICAL",
    components=[
        Component("Fixing Window Concentration", "22,525,000 of 26,500,000 total volume (r=0.850)", "Critical", 35),
        Component("Price Distortion", "1.44% deviation vs 0.18% normal (r=8.00)", "Critical", 25),
        Component("Order Timing Precision", "Order placed 2 seconds before the fixing close", "Critical", 20),
        Component("Repeat Pattern", "8 prior fixing windows with the same signature", "Critical", 20),
    ],
    risk_rationale=[
        "Volume concentrated well beyond normal daily activity",
        "Order timed in the fixing window's closing seconds",
        "Price distorted far beyond normal deviation",
        "Repeat pattern across prior fixing windows",
        "Issuer of record already flagged elsewhere",
        "Trading pattern inconsistent with mandate",
    ],
    investigation_value=[
        "Reconciles fixing-window concentration",
        "Detects timing precision &amp; price distortion",
        "Prioritises repeat-pattern risk",
        "Supports STOR filing decisions",
        "Enables workflow automation",
    ],
    intelligence_produced=[
        "Fixing distortion alerts",
        "Window-concentration exposure maps",
        "Order-timing precision assessments",
        "Repeat-pattern profiles",
        "Investigator packages",
    ],
    outputs=[
        "Fixing distortion alerts", "Window-concentration exposure maps", "Order-timing precision assessments",
        "Repeat-pattern profiles", "Escalation recommendations", "Investigation cases &amp; packages",
    ],
    key_benefits=[
        "Reconciles fixing-window concentration", "Detects timing precision &amp; distortion",
        "Prioritises repeat-pattern risk", "Supports STOR filing decisions",
        "Enables AI-assisted reviews", "Strengthens controls &amp; governance",
    ],
    downstream_consumers=[
        ("CM006", "Front Running"), ("CM007", "Pump and Dump"), ("CM008", "Cross Market Abuse"),
        ("AIC001", "AI Investigator Copilot"), ("IW001", "Investigation Workflows"), ("CASEMGMT", "Case Management"),
    ],
    summary_lines=[
        "CM009 detects volume concentrated into a regulated",
        "fixing window's closing seconds. It quantifies the",
        "fixing window concentration, the price distortion",
        "relative to the instrument's normal deviation, and",
        "corroborates the finding with order timing precision",
        "and a documented repeat pattern across prior fixing",
        "windows. Trading that would otherwise clear as an",
        "ordinary large fill is surfaced and escalated for",
        "enhanced due diligence and STOR filing.",
    ],
    confidence_pct=87,
)

if __name__ == "__main__":
    p = write(SPEC, Path(__file__).resolve().parent)
    print("wrote", p)

"""Shared SVG diagram generator for the fc-07 CM00N pattern diagrams.

Not part of the runtime -- a build-time helper that renders the same enterprise
diagram scaffold FC-06 hand-authored for BA001 (1900x1104, navy header/footer,
left data-sources rail, centre relationship graph with a four-component strip,
right risk/intelligence rail, bottom outputs/benefits/consumers/summary strip),
parameterised per CM00N typology. Kept beside the SVGs it produces so the
pattern is auditable and reproducible, not a one-off hand trace.

Usage: import `render` and call it with a typology's DiagramSpec; this module is
not itself a test target and ships no CLI beyond the __main__ smoke check.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

PALETTE = {
    "navy": "#0e1b2e", "ink": "#1e2a3d", "sub": "#5b6b82", "blue": "#1c4fa0",
    "red": "#c0202a", "green": "#2f7d4f", "gold": "#f4a920", "purple": "#6a3fa0",
    "accent": "#46b262", "card_border": "#c9d2df", "panel_border": "#dbe2ec",
    "rule": "#e6ebf2", "bg": "#eef1f6",
}


@dataclass
class DataGroup:
    title: str
    bullets: List[str]


@dataclass
class Component:
    name: str
    evidence: str
    band: str
    weight_pct: int


@dataclass
class DiagramSpec:
    code: str                      # "CM001"
    slug: str                      # "Insider_Trading" (for the filename)
    title: str                     # "INSIDER TRADING"
    subtitle: str                  # short pattern label
    description: str               # one-liner under the subtitle
    domain: str = "Capital Markets Analytics"
    pattern_type: str = ""
    exposure_type: str = ""
    data_groups: List[DataGroup] = field(default_factory=list)
    subject_label: str = ""        # e.g. "TRADING ACCOUNT"
    subject_name: str = ""         # e.g. "Viktor Sokolov · ACC019"
    subject_context: str = ""      # e.g. "Special Situations Desk"
    bridge_entity: str = ""        # e.g. "Gamma Imports Ltd"
    score: int = 90
    band: str = "CRITICAL"
    components: List[Component] = field(default_factory=list)
    risk_rationale: List[str] = field(default_factory=list)
    investigation_value: List[str] = field(default_factory=list)
    intelligence_produced: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    key_benefits: List[str] = field(default_factory=list)
    downstream_consumers: List[Tuple[str, str]] = field(default_factory=list)
    summary_lines: List[str] = field(default_factory=list)
    confidence_pct: int = 87


_HEAD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1900 1104" font-family="Helvetica, Arial, sans-serif" text-rendering="geometricPrecision">
  <defs>
    <style>
      .nvy{{fill:#12233b}}.grn{{fill:#2f7d4f}}.red{{fill:#c0202a}}.gold{{fill:#f4a920}}.pur{{fill:#6a3fa0}}
      .wht{{fill:#ffffff}}.ink{{fill:#1e2a3d}}.blu{{fill:#1c4fa0}}.sub{{fill:#5b6b82}}
      .hd{{fill:#ffffff;font-weight:bold;letter-spacing:.4px}}
      .sh{{font-weight:bold;fill:#1c4fa0}}.b{{font-weight:bold}}
      .card{{fill:#ffffff;stroke:#c9d2df;stroke-width:1.5}}
      .elab{{fill:#6b7688;font-weight:bold;letter-spacing:.3px}}
      text{{dominant-baseline:middle}}
    </style>
    <marker id="ar" markerWidth="9" markerHeight="9" refX="6" refY="4" orient="auto"><path d="M0 0l7 4L0 8z" fill="#1c4fa0"/></marker>
    <marker id="arR" markerWidth="9" markerHeight="9" refX="6" refY="4" orient="auto"><path d="M0 0l7 4L0 8z" fill="#c0202a"/></marker>
    <marker id="arO" markerWidth="9" markerHeight="9" refX="6" refY="4" orient="auto"><path d="M0 0l7 4L0 8z" fill="#d98324"/></marker>
    <marker id="arG" markerWidth="9" markerHeight="9" refX="6" refY="4" orient="auto"><path d="M0 0l7 4L0 8z" fill="#5b6b82"/></marker>
    <symbol id="i-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9.5" fill="none" stroke="#1c4fa0" stroke-width="2"/><ellipse cx="12" cy="12" rx="4" ry="9.5" fill="none" stroke="#1c4fa0" stroke-width="1.6"/><line x1="2.5" y1="12" x2="21.5" y2="12" stroke="#1c4fa0" stroke-width="1.6"/></symbol>
    <symbol id="i-doc" viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="1.5" fill="#1c4fa0"/><rect x="8" y="7" width="8" height="1.6" fill="#fff"/><rect x="8" y="11" width="8" height="1.6" fill="#fff"/><rect x="8" y="15" width="5" height="1.6" fill="#fff"/></symbol>
    <symbol id="i-link" viewBox="0 0 24 24"><circle cx="5" cy="12" r="2.6" fill="#1c4fa0"/><circle cx="19" cy="6" r="2.6" fill="#1c4fa0"/><circle cx="19" cy="18" r="2.6" fill="#1c4fa0"/><line x1="7" y1="11" x2="17" y2="7" stroke="#1c4fa0" stroke-width="1.8"/><line x1="7" y1="13" x2="17" y2="17" stroke="#1c4fa0" stroke-width="1.8"/></symbol>
    <symbol id="i-search" viewBox="0 0 24 24"><circle cx="10" cy="10" r="6.2" fill="none" stroke="#1c4fa0" stroke-width="2.2"/><line x1="15" y1="15" x2="21" y2="21" stroke="#1c4fa0" stroke-width="2.6"/></symbol>
    <symbol id="i-shield" viewBox="0 0 24 24"><path d="M12 2 21 5v7c0 5.5-3.8 9-9 10-5.2-1-9-4.5-9-10V5z" fill="#1c4fa0"/><path d="M8 12l3 3 5-6" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <symbol id="i-alert" viewBox="0 0 24 24"><path d="M12 2 23 21H1z" fill="#c0202a"/><rect x="10.8" y="8" width="2.4" height="7" fill="#fff"/><circle cx="12" cy="18" r="1.5" fill="#fff"/></symbol>
    <symbol id="i-db" viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="8" ry="3" fill="#1c4fa0"/><path d="M4 5v14c0 1.6 3.6 3 8 3s8-1.4 8-3V5" fill="none" stroke="#1c4fa0" stroke-width="2"/><path d="M4 12c0 1.6 3.6 3 8 3s8-1.4 8-3" fill="none" stroke="#1c4fa0" stroke-width="2"/></symbol>
    <symbol id="i-fp" viewBox="0 0 24 24"><g fill="none" stroke="#6a3fa0" stroke-width="1.6" stroke-linecap="round"><path d="M12 3a9 9 0 0 1 9 9v3"/><path d="M6 6a9 9 0 0 0-3 6v4"/><path d="M12 7a5 5 0 0 1 5 5v5"/><path d="M8 9a5 5 0 0 0-1 3v6"/><path d="M12 11v8"/></g></symbol>
    <symbol id="i-chart" viewBox="0 0 24 24"><g fill="currentColor"><rect x="3" y="12" width="4" height="9"/><rect x="10" y="6" width="4" height="15"/><rect x="17" y="2" width="4" height="19"/></g></symbol>
    <symbol id="i-bank" viewBox="0 0 24 24"><path d="M12 2 22 8H2z" fill="currentColor"/><rect x="4" y="9" width="2.4" height="10" fill="currentColor"/><rect x="10.8" y="9" width="2.4" height="10" fill="currentColor"/><rect x="17.6" y="9" width="2.4" height="10" fill="currentColor"/><rect x="2" y="20" width="20" height="2" fill="currentColor"/></symbol>
    <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 6v6l4 3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol>
    <symbol id="i-hex" viewBox="0 0 48 48"><g fill="none" stroke="#46b262" stroke-width="1.6"><path d="M24 6 40 15v18L24 42 8 33V15z"/></g><g fill="#46b262"><circle cx="24" cy="6" r="2.4"/><circle cx="40" cy="15" r="2.4"/><circle cx="40" cy="33" r="2.4"/><circle cx="24" cy="42" r="2.4"/><circle cx="8" cy="33" r="2.4"/><circle cx="8" cy="15" r="2.4"/><circle cx="24" cy="24" r="3"/></g><g stroke="#46b262" stroke-width="1.2"><line x1="24" y1="24" x2="24" y2="6"/><line x1="24" y1="24" x2="40" y2="33"/><line x1="24" y1="24" x2="8" y2="33"/></g></symbol>
  </defs>

  <rect width="1900" height="1104" fill="#eef1f6"/>

  <!-- HEADER -->
  <rect x="0" y="0" width="1900" height="132" fill="#0e1b2e"/>
  <use href="#i-hex" x="34" y="34" width="64" height="64"/>
  <text x="122" y="42" class="hd" font-size="34">{code_upper} &#8211; {title_upper}</text>
  <text x="124" y="74" font-size="18" font-weight="bold" fill="#46b262">{subtitle}</text>
  <text x="124" y="100" class="wht" font-size="13.5" opacity=".9">{description}</text>
  <g font-size="12.5">
    <use href="#i-globe" x="1300" y="18" width="14" height="14"/><text x="1320" y="26" class="wht b">DOMAIN:</text><text x="1452" y="26" fill="#cfe6d6">{domain}</text>
    <use href="#i-globe" x="1300" y="42" width="14" height="14"/><text x="1320" y="50" class="wht b">PATTERN TYPE:</text><text x="1452" y="50" fill="#cfe6d6">{pattern_type}</text>
    <use href="#i-globe" x="1300" y="66" width="14" height="14"/><text x="1320" y="74" class="wht b">EXPOSURE TYPE:</text><text x="1452" y="74" fill="#cfe6d6">{exposure_type}</text>
    <use href="#i-globe" x="1300" y="90" width="14" height="14"/><text x="1320" y="98" class="wht b">SCORE TYPE:</text><text x="1452" y="98" fill="#cfe6d6">Exposure Score</text>
  </g>
  <rect x="1742" y="22" width="126" height="88" rx="8" fill="#0e1b2e" stroke="#46b262" stroke-width="2.5"/>
  <text x="1805" y="52" class="hd" font-size="24" text-anchor="middle" fill="#46b262">CM</text>
  <text x="1805" y="84" class="hd" font-size="30" text-anchor="middle" fill="#46b262">{num}</text>

  <!-- LEFT — DATA SOURCES -->
  <rect x="20" y="150" width="236" height="24" class="nvy"/>
  <text x="138" y="163" class="hd" font-size="13" text-anchor="middle">DATA SOURCES</text>
  <g font-size="10.6">
{data_groups_svg}
  </g>

  <!-- CENTRE GRAPH -->
  <rect x="266" y="150" width="1330" height="700" rx="4" fill="#ffffff" stroke="#dbe2ec" stroke-width="1.5"/>
  <g font-size="11.5" class="ink">
    <circle cx="292" cy="170" r="6" fill="none" stroke="#6a3fa0" stroke-width="2"/><text x="304" y="171">Counterparty / Source</text>
    <circle cx="470" cy="170" r="6" fill="none" stroke="#1c4fa0" stroke-width="2"/><text x="482" y="171">Trading Account / Order</text>
    <line x1="656" y1="170" x2="688" y2="170" stroke="#1c4fa0" stroke-width="2.4" marker-end="url(#ar)"/><text x="696" y="171">Order / Trade Flow</text>
    <line x1="850" y1="170" x2="882" y2="170" stroke="#5b6b82" stroke-width="2" stroke-dasharray="5 3"/><text x="890" y="171">Behavioural Linkage</text>
    <use href="#i-alert" x="1060" y="163" width="14" height="14"/><text x="1080" y="171">Risk / Alert</text>
  </g>
  <line x1="286" y1="186" x2="1576" y2="186" stroke="#e6ebf2"/>

  <!-- edges -->
  <g fill="none">
    <path d="M452 352 L790 262" stroke="#1c4fa0" stroke-width="2.2" marker-end="url(#ar)"/>
    <path d="M1030 232 L1130 352" stroke="#5b6b82" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#arG)"/>
    <path d="M900 268 L900 470" stroke="#1c4fa0" stroke-width="2.2" marker-end="url(#ar)"/>
    <path d="M1180 434 L1016 496" stroke="#5b6b82" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#arG)"/>
    <path d="M452 434 L742 512" stroke="#1c4fa0" stroke-width="2.2" marker-end="url(#ar)"/>
    <path d="M1016 528 L1126 566" stroke="#c0202a" stroke-width="2.4" marker-end="url(#arR)"/>
    <path d="M450 772 L800 566" stroke="#d98324" stroke-width="2" marker-end="url(#arO)"/>
    <path d="M778 772 L868 570" stroke="#5b6b82" stroke-width="2" marker-end="url(#arG)"/>
    <path d="M1106 772 L940 566" stroke="#5b6b82" stroke-width="2" marker-end="url(#arG)"/>
    <path d="M1434 772 L1250 648" stroke="#5b6b82" stroke-width="2" marker-end="url(#arG)"/>
  </g>
  <g font-size="10" class="elab" text-anchor="middle">
    <text x="612" y="296">{c1_edge_label}</text>
    <text x="1108" y="288" fill="#6b7688">{c2_edge_label}</text>
    <text x="948" y="372">AGGREGATES TO</text>
    <text x="1130" y="474" fill="#6b7688">{c3_edge_label}</text>
    <text x="566" y="470">{c4_edge_label}</text>
    <text x="1082" y="528" fill="#c0202a">TRIGGERS</text>
    <text x="612" y="682" fill="#d98324">MEASURES</text>
    <text x="806" y="690">CONTEXT</text>
    <text x="1034" y="690">CONTEXT</text>
    <text x="1372" y="716">CONTEXT</text>
  </g>

  <!-- nodes -->
  <g>
    <rect x="326" y="352" width="244" height="82" rx="7" fill="#fdeef0" stroke="#c0202a" stroke-width="2"/>
    <text x="460" y="372" class="red b" font-size="12.5" text-anchor="middle">{comp1_name_upper}</text>
    <text x="460" y="392" class="ink" font-size="11.5" text-anchor="middle">{comp1_evidence}</text>
    <text x="460" y="410" class="sub" font-size="10.8" text-anchor="middle">primary driver</text>
  </g>
  <g>
    <rect x="784" y="192" width="232" height="72" rx="7" fill="#f3eefb" stroke="#6a3fa0" stroke-width="2"/>
    <text x="912" y="214" class="pur b" font-size="12.5" text-anchor="middle">{comp3_name_upper}</text>
    <text x="912" y="234" class="ink" font-size="11.5" text-anchor="middle">{comp3_evidence}</text>
    <text x="912" y="250" class="sub" font-size="10.8" text-anchor="middle">supporting signal</text>
  </g>
  <g>
    <rect x="1128" y="352" width="244" height="82" rx="7" class="card"/>
    <text x="1262" y="372" class="blu b" font-size="12.5" text-anchor="middle">{comp2_name_upper}</text>
    <text x="1262" y="392" class="ink" font-size="11.5" text-anchor="middle">{comp2_evidence}</text>
    <text x="1262" y="410" class="sub" font-size="10.8" text-anchor="middle">timing signal</text>
  </g>
  <g>
    <rect x="742" y="470" width="272" height="96" rx="8" fill="#e9f0fb" stroke="#1c4fa0" stroke-width="2.6"/>
    <text x="892" y="496" class="blu b" font-size="13" text-anchor="middle">{subject_label}</text>
    <text x="892" y="517" class="ink b" font-size="12.5" text-anchor="middle">{subject_name}</text>
    <text x="892" y="536" class="sub" font-size="10.8" text-anchor="middle">{subject_context}</text>
    <text x="892" y="552" class="sub" font-size="10.8" text-anchor="middle">exposure aggregating</text>
  </g>
  <g>
    <rect x="1128" y="540" width="244" height="108" rx="7" fill="#fdeef0" stroke="#c0202a" stroke-width="2.2"/>
    <use href="#i-alert" x="1142" y="560" width="30" height="30"/>
    <text x="1262" y="566" class="red b" font-size="13" text-anchor="middle">RISK ALERT</text>
    <text x="1262" y="588" class="ink" font-size="11.5" text-anchor="middle">{alert_line1}</text>
    <text x="1262" y="606" class="ink" font-size="11.5" text-anchor="middle">{alert_line2}</text>
    <text x="1262" y="628" class="red b" font-size="13" text-anchor="middle">{score} / 100 &#183; {band}</text>
  </g>

  <!-- bottom analysis (4 components) -->
  <g>
{components_strip_svg}
  </g>

  <!-- RIGHT — RISK & INTELLIGENCE -->
  <rect x="1612" y="150" width="268" height="24" class="nvy"/>
  <text x="1746" y="163" class="hd" font-size="12.5" text-anchor="middle">RISK &amp; INTELLIGENCE</text>
  <g font-size="10.3">
    <use href="#i-alert" x="1620" y="184" width="16" height="16"/><text x="1644" y="192" class="red b" font-size="12">RISK RATIONALE</text>
    <g class="ink">
{risk_rationale_svg}
    </g>
    <use href="#i-search" x="1620" y="308" width="16" height="16"/><text x="1644" y="316" class="blu b" font-size="12">INVESTIGATION VALUE</text>
    <g class="ink">
{investigation_value_svg}
    </g>
    <use href="#i-db" x="1620" y="416" width="16" height="16"/><text x="1644" y="424" class="grn b" font-size="12">INTELLIGENCE PRODUCED</text>
    <g class="ink">
{intelligence_produced_svg}
    </g>
  </g>
  <line x1="1612" y1="528" x2="1880" y2="528" stroke="#d7deea"/>
  <path d="M1626 610 A44 44 0 0 1 1714 610" fill="none" stroke="#e2e8f0" stroke-width="11" stroke-linecap="round"/>
  <path d="M1626 610 A44 44 0 0 1 1710 594" fill="none" stroke="#2f7d4f" stroke-width="11" stroke-linecap="round"/>
  <text x="1670" y="602" class="grn b" font-size="22" text-anchor="middle">{confidence_pct}%</text>
  <text x="1734" y="556" class="grn b" font-size="12">RISK CONFIDENCE*</text>
  <g font-size="9.8" class="ink">
{confidence_lines_svg}
  </g>
  <line x1="1612" y1="636" x2="1880" y2="636" stroke="#d7deea"/>
  <path d="M1622 704 A40 40 0 0 1 1702 704" fill="none" stroke="#c0202a" stroke-width="10" stroke-linecap="round"/>
  <text x="1662" y="696" class="ink b" font-size="18" text-anchor="middle">{score}</text>
  <text x="1662" y="713" class="sub" font-size="9.5" text-anchor="middle">/100</text>
  <text x="1720" y="660" class="red b" font-size="12">RISK SCORE &#183; {band}</text>
  <g font-size="9.8" class="ink">
{score_component_lines_svg}
  </g>
  <line x1="1612" y1="744" x2="1880" y2="744" stroke="#d7deea"/>
  <use href="#i-fp" x="1620" y="756" width="22" height="22"/>
  <text x="1650" y="769" class="pur b" font-size="12">PATTERN CLASSIFICATION</text>
  <g font-size="10.8"><text x="1620" y="792" class="sub">Type:</text><text x="1712" y="792" class="ink">{pattern_type}</text>
    <text x="1620" y="810" class="sub">Category:</text><text x="1712" y="810" class="ink">Financial Crime Analytics</text>
    <text x="1620" y="828" class="sub">Exposure:</text><text x="1712" y="828" class="ink">Capital Markets Exposure</text></g>

  <!-- BOTTOM STRIP -->
  <g transform="translate(20,872)">
    <rect x="0" y="0" width="300" height="24" class="nvy"/><text x="150" y="13" class="hd" font-size="12.5" text-anchor="middle">OUTPUTS</text>
    <g font-size="10.8" class="ink">
{outputs_svg}
    </g>
  </g>
  <g transform="translate(338,872)">
    <rect x="0" y="0" width="330" height="24" class="grn"/><text x="165" y="13" class="hd" font-size="12.5" text-anchor="middle">KEY BENEFITS</text>
    <g font-size="10.8" class="ink"><g fill="#2f7d4f" font-weight="bold">
{key_benefits_marks_svg}
    </g>
{key_benefits_svg}
    </g>
  </g>
  <g transform="translate(686,872)">
    <rect x="0" y="0" width="470" height="24" class="nvy"/><text x="235" y="13" class="hd" font-size="12.5" text-anchor="middle">DOWNSTREAM INTELLIGENCE CONSUMERS</text>
    <g font-size="10.8">
{downstream_consumers_svg}
    </g>
  </g>
  <g transform="translate(1174,872)">
    <rect x="0" y="0" width="418" height="24" class="nvy"/><text x="209" y="13" class="hd" font-size="12.5" text-anchor="middle">PATTERN SUMMARY</text>
    <g font-size="10.4" class="ink">
{summary_svg}
    </g>
  </g>
  <text x="1612" y="1042" class="sub" font-size="9.5" font-style="italic">* Confidence figure illustrative.</text>

  <!-- FOOTER -->
  <rect x="0" y="1058" width="1900" height="40" fill="#0e1b2e"/>
  <use href="#i-hex" x="430" y="1062" width="30" height="30"/>
  <text x="950" y="1079" class="hd" font-size="14" text-anchor="middle">BUILDING THE FOUNDATION FOR NETWORK INTELLIGENCE AND GRAPH-BASED FINANCIAL CRIME INVESTIGATIONS</text>
</svg>
"""

_BAND_CLASS = {"Low": "sub", "Medium": "gold", "High": "d98324", "Critical": "red"}


def _data_groups_svg(groups: List[DataGroup]) -> str:
    out = []
    y = 182
    for g in groups:
        lines = [f'    <g transform="translate(0,{y})"><text x="26" y="0" class="sh" font-size="11.2">{g.title}</text>']
        by = 20
        for b in g.bullets:
            lines.append(f'<text x="30" y="{by}" class="ink">&#8226; {b}</text>')
            by += 15
        lines.append("</g>")
        out.append("".join(lines))
        y += 82
    return "\n".join(out)


def _bullets_svg(bullets: List[str], x: int, y0: int, dy: int, cls: str = "") -> str:
    out = []
    y = y0
    for b in bullets:
        out.append(f'      <text x="{x}" y="{y}">&#8226; {b}</text>')
        y += dy
    return "\n".join(out)


def _components_strip_svg(components: List[Component]) -> str:
    xs = [300, 628, 956, 1284]
    out = []
    for x, c in zip(xs, components):
        out.append(f'''    <rect x="{x}" y="772" width="300" height="62" rx="7" class="card"/>
    <text x="{x+44}" y="790" class="ink b" font-size="11.5">{c.name.upper()}</text>
    <text x="{x+44}" y="810" class="sub" font-size="10.5">{c.evidence}</text>
    <text x="{x+44}" y="825" class="red b" font-size="10.5">{c.band} &#183; weight {c.weight_pct}%</text>''')
    return "\n".join(out)


def _downstream_svg(items: List[Tuple[str, str]]) -> str:
    out = []
    col2 = 250
    for i, (code, label) in enumerate(items):
        col = i // 3
        row = i % 3
        x = 10 if col == 0 else col2
        y = 44 + row * 20
        out.append(f'      <text x="{x}" y="{y}" class="sh">{code}</text><text x="{x+82}" y="{y}" class="ink">{label}</text>')
    return "\n".join(out)


def _outputs_svg(items: List[str]) -> str:
    out = []
    y = 44
    for it in items:
        out.append(f'      <text x="8" y="{y}">{it}</text>')
        y += 20
    return "\n".join(out)


def _key_benefits_svg(items: List[str]) -> str:
    out = []
    y = 44
    marks = []
    for it in items:
        out.append(f'      <text x="26" y="{y}">{it}</text>')
        marks.append(f'      <text x="8" y="{y}">&#10003;</text>')
        y += 20
    return "\n".join(marks), "\n".join(out)


def _summary_svg(lines: List[str]) -> str:
    out = []
    y = 42
    for ln in lines:
        out.append(f'      <text x="8" y="{y}">{ln}</text>')
        y += 16
    return "\n".join(out)


def render(spec: DiagramSpec) -> str:
    marks_svg, benefits_svg = _key_benefits_svg(spec.key_benefits)
    return _HEAD.format(
        code_upper=spec.code, title_upper=spec.title.upper(), subtitle=spec.subtitle,
        description=spec.description, domain=spec.domain, pattern_type=spec.pattern_type,
        exposure_type=spec.exposure_type, num=spec.code.replace("CM", ""),
        data_groups_svg=_data_groups_svg(spec.data_groups),
        c1_edge_label="DRIVES", c2_edge_label="SPREAD ACROSS", c3_edge_label="LINKED VIA",
        c4_edge_label="MEASURES",
        comp1_name_upper=spec.components[0].name.upper(), comp1_evidence=spec.components[0].evidence,
        comp3_name_upper=spec.components[2].name.upper(), comp3_evidence=spec.components[2].evidence,
        comp2_name_upper=spec.components[1].name.upper(), comp2_evidence=spec.components[1].evidence,
        subject_label=spec.subject_label, subject_name=spec.subject_name, subject_context=spec.subject_context,
        alert_line1=f"{spec.components[0].name} confirmed &amp;",
        alert_line2=f"linked to {spec.bridge_entity}",
        score=spec.score, band=spec.band,
        components_strip_svg=_components_strip_svg(spec.components),
        risk_rationale_svg=_bullets_svg(spec.risk_rationale, 1620, 212, 16),
        investigation_value_svg=_bullets_svg(spec.investigation_value, 1620, 336, 16),
        intelligence_produced_svg=_bullets_svg(spec.intelligence_produced, 1620, 444, 16),
        confidence_pct=spec.confidence_pct,
        confidence_lines_svg=_bullets_svg(spec.investigation_value[:4], 1734, 576, 15),
        score_component_lines_svg=_bullets_svg([c.name for c in spec.components], 1720, 680, 15),
        outputs_svg=_outputs_svg(spec.outputs),
        key_benefits_marks_svg=marks_svg, key_benefits_svg=benefits_svg,
        downstream_consumers_svg=_downstream_svg(spec.downstream_consumers),
        summary_svg=_summary_svg(spec.summary_lines),
    )


def write(spec: DiagramSpec, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{spec.code}_{spec.slug}.svg"
    path.write_text(render(spec), encoding="utf-8")
    return path

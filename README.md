[← Back to Portfolio](https://dhartwig-fc.github.io/dan-hartwig-portfolio/)

## FC-07 Capital Markets Analytics Toolkit

The Capital Markets Analytics Toolkit is a repository focused on trade- and order-flow
surveillance for capital markets: insider trading, market manipulation, spoofing,
order-book layering, wash trading, front running, pump and dump, cross-market abuse,
benchmark manipulation and suspicious order patterns.

The repository explores how order behaviour, trade timing, position build and
information-access linkage can be combined to identify market-abuse risk that a
single-order rule would miss — trading ahead of a material non-public event,
non-bona-fide orders cancelled before execution, staggered order-book layers, self-
matched volume, and fixing-window concentration, in patterns that only resolve at the
account or network level, never at the single-order level.

The toolkit contains capital markets analytics typologies (CM001–CM010), detection
methodologies, exposure scoring logic and intelligence artefacts covering order-flow
behavioural monitoring, trade-timing analysis, position-build detection and
cross-venue/cross-instrument surveillance.

The objective is to demonstrate how intelligence-led trade surveillance can evolve
beyond static single-order rules and support a more holistic understanding of market-
abuse risk, control effectiveness and typology exposure.

### Key Capability Areas

- Capital Markets Surveillance
- Trade & Order Flow Analytics
- Insider Trading Detection
- Market Manipulation & Spoofing Detection
- Order-Book Layering & Wash Trading Typologies
- Front Running & Information-Linkage Analytics
- Cross Market Abuse Detection
- Benchmark & Fixing-Window Manipulation Analytics
- Behavioural Order-Flow Pattern Detection
- Exposure Scoring Frameworks
- Detection Strategy
- Investigation Workflows

### The CM001–CM010 Family

| ID | Typology | Pattern | Subject |
|------|------|------|------|
| CM001 | Insider Trading | Trading ahead of a material non-public event, sized well beyond normal activity | Trading account |
| CM002 | Market Manipulation | Artificial price/volume influence across accounts to move a market | Trading account |
| CM003 | Spoofing | Non-bona-fide orders placed to create false pressure, cancelled before execution | Trading account |
| CM004 | Layering | Staggered order-book levels fabricating depth/imbalance, then reversed (order-book layering) | Trading account |
| CM005 | Wash Trading | Self-matched trades faking volume and liquidity with no change in beneficial ownership | Trading account |
| CM006 | Front Running | Dealing ahead of a known client order to profit from the anticipated price move | Trading account |
| CM007 | Pump and Dump | Coordinated accumulation and promotion, then distribution into the retail bid | Trading account |
| CM008 | Cross Market Abuse | Manipulation spanning venues/correlated instruments to evade single-market surveillance | Trading account |
| CM009 | Benchmark Manipulation | Concentrated trading in the fixing window to distort a reference rate or closing price | Trading account |
| CM010 | Suspicious Order Patterns | Anomalous order behaviour (quote stuffing, momentum ignition, abnormal cancel/amend rates) | Trading account |

See `typologies/CM_Typology_Register.md` for the full inventory and build waves.

### House Conventions

Every CM analytic follows the estate-wide conventions established by the fc-04/fc-05/
fc-06 toolkits:

- **W2 analytic contract** — each engine emits `exposure_score` (int 0–100) and
  `exposure_band = band(exposure_score)`, `risk_components`, and full narrative
  sections, so the FC-10 runtime can delegate to it without re-implementing scoring.
- **Band-midpoint scoring** — `BAND_SCORE = {Low: 15, Medium: 45, High: 70,
  Critical: 90}`, `RISK_BANDS = ((0,29,Low), (30,59,Medium), (60,79,High),
  (80,100,Critical))`, boundary at 80, `ROUND_HALF_UP` via `Decimal`. Every component
  scorer returns a band name, never a raw number; `RiskModelError` is raised (not
  defaulted to zero) when a required field is missing. Every typology's four
  components are weighted 0.35 / 0.25 / 0.20 / 0.20, the house standard across the
  whole CM family.
- **≥20-row real-named sample data** — every typology's sample-data CSVs ship at
  least 20 data rows per component, using real trader/entity/broker/venue names (no
  bare ids), enforced live by `python/specific/test_sample_data_row_minimum.py` (no
  grandfathering for CM — every typology here is new).

### Repository Structure

```text
fc-07-capital-markets-analytics-toolkit/
├── typologies/                 # CM typology library + CM_Typology_Register.md
├── diagrams/                   # Enterprise typology diagrams + the shared SVG template
├── data-model/                 # Domain data dictionary and entity models
├── python/
│   └── specific/                # Per-analytic engine packages
│       └── CM0NN/               # risk model · scenario callable · schema · sample-data
│                                # · expected_outputs · executable tests
├── intelligence-products/
│   ├── common/                 # Product standards and templates
│   └── specific/                # Per-analytic intelligence products
└── operations/
    ├── common/                 # Alert triage, escalation, investigation standards
    └── specific/                # Per-analytic investigator playbooks
```

### Build Model

Each analytic is built as a **self-contained, independently tested engine** under
`python/specific/<ID>/`, mirroring the fc-04 TBML, fc-05 Sanctions and fc-06
Correspondent Banking toolkits. The engine is proven standalone in this repository —
risk model, scenario callable, schema, generated sample data, expected outputs and its
own test suite — **before** it is put through the FC-10 governed runtime, where a thin
adapter delegates to it. CM001 Insider Trading is the reference implementation every
subsequent CM00N typology mirrors, file-for-file. See `typologies/CM_Typology_Register.md`
for the scenario inventory and build waves.

### Strategic Focus

The repository demonstrates how capital-markets surveillance, order-flow analytics and
trade-timing intelligence can be integrated into a modern market-abuse detection
operating model capable of identifying insider trading, market manipulation, spoofing,
order-book layering, wash trading, front running, pump-and-dump schemes, cross-market
abuse, benchmark manipulation and anomalous order-flow patterns.

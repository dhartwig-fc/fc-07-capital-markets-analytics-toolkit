# Data Dictionary

## Purpose

This data dictionary defines the core data elements required to support the Capital
Markets Analytics suite (CM001–CM010).

The model supports:

- Order and trade behavioural monitoring
- Position-build and timing-proximity analysis (insider trading)
- Price/volume manipulation and reversal detection
- Order-book layering and spoofing detection
- Wash-trading and beneficial-ownership overlap analysis
- Front-running and client-order-knowledge linkage detection
- Coordinated promotion and distribution detection (pump and dump)
- Cross-venue / cross-instrument correlation analysis
- Benchmark/fixing-window manipulation detection
- Behavioural order-flow anomaly detection (quote stuffing, momentum ignition)
- Exposure scoring
- Alert generation
- Intelligence product production

The authoritative field-level model for the Python layer lives beside each analytic
under `python/specific/<ID>/schema.json`; this dictionary is the domain-level summary.
Individual analytics add per-entity model documents to this folder as their data
requirements are specified.

---

## Core Entities

| Entity | Description |
|--------|--------------|
| Trading Account | The account/trader under assessment across all ten typologies |
| Trader | The individual or desk operating the trading account |
| Issuer | The company whose instrument is being traded (CM001, CM008, CM009) |
| Instrument | The security, bond, derivative or benchmark-linked product being traded |
| Venue | Trading venue or market on which orders/trades execute |
| Broker | Executing or clearing broker/counterparty |
| Counterparty | Trade counterparty, information source, promoter or client firm,
  depending on the typology |
| Client Order | The known/pending client order a trader deals ahead of (CM006) |
| Information Source | The person or entity documented as a linkage to material
  non-public information (CM001) |
| Promoter | The person or entity coordinating promotional activity (CM007) |
| Benchmark | The fixing/reference-rate benchmark being manipulated (CM009) |
| Order | An individual order event (placed, amended, cancelled, executed) |
| Alert | Generated capital-markets exposure alert |

---

## Exposure Model

Exposure is assessed as a weighted composite of four component scores per typology,
each weighted **0.35 / 0.25 / 0.20 / 0.20** (the house standard across the whole CM
family — the primary driver carries 35%, the two supporting/corroborating signals
carry 20% each, and the secondary driver carries 25%). Each analytic's typology
write-up (`typologies/`) states its own four components, formulas and band cut-lines.
The suite-wide vocabulary is:

| Component | Meaning |
|-----------|---------|
| Pre-Event Position Build Exposure | Position build materially larger than normal, ahead of a material event (CM001) |
| Price Impact / Manipulation Exposure | Artificial price/volume influence relative to normal activity (CM002) |
| Non-Bona-Fide Order Exposure | Orders placed with no intention to execute, cancelled before fill (CM003) |
| Order-Book Distortion Exposure | Staggered order levels fabricating depth/imbalance (CM004) |
| Self-Match / Wash Exposure | Self-matched volume with no genuine change in beneficial ownership (CM005) |
| Front-Running Timing Exposure | Dealing ahead of a known client order (CM006) |
| Coordinated Promotion Exposure | Accumulation and promotion ahead of distribution (CM007) |
| Cross-Venue Correlation Exposure | Manipulation spanning correlated instruments/venues (CM008) |
| Fixing-Window Concentration Exposure | Order concentration in a benchmark's fixing window (CM009) |
| Behavioural Order-Flow Exposure | Cancel/amend rate, quote-stuffing and momentum-ignition anomalies (CM010) |
| Information Access / Linkage Exposure | Documented contact with an information source, insider or promoter |
| Counterparty / Venue Exposure | Risk carried by brokers, venues, clearing counterparties or issuers |

---

## Exposure Bands

| Score Range | Exposure Band | Priority |
|-------------|---------------|----------|
| 0–29 | Low | Monitor |
| 30–59 | Medium | Review |
| 60–79 | High | Investigate |
| 80–100 | Critical | Immediate Escalation |

---

## Data Model Principle

The data model is intentionally simple and synthetic. It is designed to demonstrate
analytical logic, exposure scoring and investigation outputs rather than replicate a
production capital-markets trade-surveillance data model (order management system,
market data feed, or trade repository).

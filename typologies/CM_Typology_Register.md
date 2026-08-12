# Capital Markets Analytics Typology Register

## Purpose

Master inventory of the Capital Markets Analytics scenarios.

---

## Build Status

- **CM001 Insider Trading — BUILT**. The reference implementation every other
  CM00N typology mirrors: fc-07 analytic (pre-event position build 35%, timing
  proximity to event 25%, information access linkage 20%, profit realisation 20%)
  + 22-row real-named sample data + docs + diagram; fuses onto **Gamma Imports Ltd**
  in the estate network via canonical entity resolution (ACC019, Viktor Sokolov,
  90/Critical, the single highest-scoring account).
- **CM002 Market Manipulation — BUILT**. Mirrors CM001's file set exactly
  (price impact ratio 35%, volume concentration 25%, coordinated accounts 20%,
  reversal after close 20%); fuses onto **Alpha Trading Ltd** in the estate network
  via canonical entity resolution (ACC019, 90/Critical).
- **CM003 Spoofing — BUILT**. Mirrors CM001/CM002's file set exactly (non-bona-fide
  order ratio 35%, cancellation speed 25%, order book imbalance 20%, opposite-side
  execution 20%); fuses onto **Zeta Commodities Ltd** in the estate network via
  canonical entity resolution (ACC019, 90/Critical).
- **CM004 Layering — BUILT**. Order-book layering, distinct from the AML "layering"
  typology. Mirrors CM001-CM003's file set exactly (staggered order levels 35%,
  order-to-trade ratio 25%, book imbalance created 20%, reversal speed 20%); fuses
  onto **Gamma Imports Ltd** in the estate network via canonical entity resolution
  (ACC019, 90/Critical). A second row names **Continental Correspondent Bank** as a
  recurring venue operator, the family's first recurring shared entity after Gamma
  Imports Ltd.
- **CM005 Wash Trading — BUILT**. Mirrors CM001-CM004's file set exactly
  (self-match ratio 35%, beneficial ownership overlap 25%, volume inflation 20%,
  counterparty concentration 20%); fuses onto **Continental Correspondent Bank** in
  the estate network via canonical entity resolution (ACC019, 90/Critical).
- **CM006 Front Running — BUILT**. Mirrors CM001-CM005's file set exactly (timing
  ahead of client order 35%, position correlation 25%, profit capture 20%, client
  order knowledge linkage 20%); fuses onto **Alpha Trading Ltd** in the estate
  network via canonical entity resolution (ACC019, 90/Critical), the second CM
  typology to bridge onto Alpha Trading Ltd after CM002.
- **CM007 Pump and Dump — BUILT**. Mirrors CM001-CM006's file set exactly
  (accumulation concentration 35%, promotional coordination 25%, price inflation
  20%, distribution into retail 20%); fuses onto **John Smith** (the network's PEP,
  local id **P001**) in the estate network via canonical entity resolution
  (ACC019, 90/Critical). CM007 is the family's designated PERSON-bridge typology:
  unlike every other CM00N typology, which bridges onto a connected COMPANY matched
  by exact name, ACC019's promotion is coordinated by John Smith, and because
  persons never name-merge under canonical resolution, the bridge is carried on the
  shared local id (P001) instead of the name — mirroring fc-06's BA009.
- **CM008 Cross Market Abuse — BUILT**. Mirrors CM001-CM007's file set exactly
  (cross-venue position correlation 35%, venue count 25%, price impact transfer 20%,
  timing synchronization 20%); fuses onto **Zeta Commodities Ltd** in the estate
  network via canonical entity resolution (ACC019, 90/Critical), the second CM
  typology to bridge onto Zeta Commodities Ltd after CM003.
- **CM009 Benchmark Manipulation — BUILT**. Mirrors CM001-CM008's file set exactly
  (fixing window concentration 35%, price distortion 25%, order timing precision
  20%, repeat pattern 20%); fuses onto **Gamma Imports Ltd** in the estate network
  via canonical entity resolution (ACC019, 90/Critical), the third CM typology to
  bridge onto Gamma Imports Ltd after CM001 and CM004.
- **CM010 Suspicious Order Patterns — BUILT**. The tenth and final fc-07 typology.
  Mirrors CM001-CM009's file set exactly (cancel/amend rate 35%, quote stuffing
  intensity 25%, momentum ignition signal 20%, order size anomaly 20%); fuses onto
  **Alpha Trading Ltd** in the estate network via canonical entity resolution
  (ACC019, 90/Critical), the third CM typology to bridge onto Alpha Trading Ltd
  after CM002 and CM006. CM010 is the family's purely behavioural, no-single-signal
  capstone — every component is an order-flow behavioural anomaly (cancel/amend
  rate, quote stuffing, momentum ignition, order size) rather than a single
  identifiable rule, proving the template extends cleanly to pure behavioural-
  surveillance shape, mirroring how BA010 closed the fc-06 family as a purely
  statistical, peer-relative capstone.

---

| ID | Name | Category | Pattern | Subject |
|------|------|------|------|------|
| CM001 | Insider Trading | Insider Trading | Trading ahead of a material non-public event, sized well beyond normal activity | Trading account |
| CM002 | Market Manipulation | Market Manipulation | Artificial price/volume influence across accounts to move a market | Trading account |
| CM003 | Spoofing | Spoofing | Non-bona-fide orders placed to create false pressure, cancelled before execution | Trading account |
| CM004 | Layering | Order-Book Layering | Staggered order-book levels fabricating depth/imbalance, then reversed | Trading account |
| CM005 | Wash Trading | Wash Trading | Self-matched trades faking volume/liquidity with no change in beneficial ownership | Trading account |
| CM006 | Front Running | Front Running | Dealing ahead of a known client order to profit from the anticipated price move | Trading account |
| CM007 | Pump and Dump | Pump and Dump | Coordinated accumulation and promotion, then distribution into the retail bid | Trading account |
| CM008 | Cross Market Abuse | Cross Market Abuse | Manipulation spanning venues/correlated instruments to evade single-market surveillance | Trading account |
| CM009 | Benchmark Manipulation | Benchmark Manipulation | Concentrated trading in the fixing window to distort a reference rate or closing price | Trading account |
| CM010 | Suspicious Order Patterns | Behavioural Anomaly | Anomalous order behaviour (quote stuffing, momentum ignition, abnormal cancel/amend rates) | Trading account |

---

## Regulatory Reference Summary

| ID | Primary Reference |
|------|------|
| CM001 | MAR Article 8 (Insider Dealing) / Article 10 (Unlawful Disclosure) |
| CM002 | MAR Article 12 / Article 15 (Market Manipulation) |
| CM003 | MAR Article 12(1)(a)(ii) (non-bona-fide orders) |
| CM004 | MAR Article 12(1)(a) (order-book distortion / layering) |
| CM005 | MAR Article 12(1)(a)(i) (wash trades / matched orders) |
| CM006 | MiFID II Article 16(3) / Article 27 (conflicts of interest, misuse of client order information) |
| CM007 | MAR Article 12(1)(a) and 12(2)(a) (transactions combined with false/misleading information) |
| CM008 | MAR Article 12(1)(c) (cross-venue / cross-instrument manipulation) |
| CM009 | MAR Article 12(1)(d) (benchmark manipulation); EU Benchmarks Regulation (BMR) 2016/1011 |
| CM010 | MAR Article 16 (STOR obligation); MAR Annex II indicators (quote stuffing, momentum ignition) |

---

## Build Waves

### Wave 1 — Information-Advantage & Price-Influence Patterns

- CM001 Insider Trading
- CM002 Market Manipulation
- CM003 Spoofing

### Wave 2 — Order-Book & Ownership Patterns

- CM004 Layering
- CM005 Wash Trading
- CM006 Front Running

### Wave 3 — Coordinated, Cross-Venue & Behavioural Patterns

- CM007 Pump and Dump
- CM008 Cross Market Abuse
- CM009 Benchmark Manipulation
- CM010 Suspicious Order Patterns

---

## Fusion Bridges

Every CM typology deliberately names an entity already in the estate network so
canonical resolution joins it into a fused case:

- CM001 Insider Trading → issuer/information-source linkage to **Gamma Imports Ltd**.
- CM002 Market Manipulation → ultimate owner **Alpha Trading Ltd**.
- CM003 Spoofing → broker **Zeta Commodities Ltd**.
- CM004 Layering → venue operator **Gamma Imports Ltd** (also names **Continental
  Correspondent Bank** as a recurring secondary venue operator).
- CM005 Wash Trading → clearing broker **Continental Correspondent Bank**.
- CM006 Front Running → client firm **Alpha Trading Ltd** (second appearance).
- CM007 Pump and Dump → promoter **John Smith** (the network PEP, local id P001).
- CM008 Cross Market Abuse → issuer **Zeta Commodities Ltd** (second appearance).
- CM009 Benchmark Manipulation → issuer **Gamma Imports Ltd** (third appearance).
- CM010 Suspicious Order Patterns → venue operator **Alpha Trading Ltd** (third
  appearance).

Gamma Imports Ltd (x3), Alpha Trading Ltd (x3), Zeta Commodities Ltd (x2),
Continental Correspondent Bank (x1 primary + x1 recurring secondary) and John Smith
(x1, person bridge) between them cover all ten CM typologies, mirroring the fc-06
family's recurring-entity pattern.

---

## Enterprise Standard Requirements

Every Capital Markets Analytics analytic should include (mirroring the fc-04 TBML001
/ fc-05 SAN003 / fc-06 BA001 pattern):

- Typology definition (`typologies/`)
- Enterprise diagram (`diagrams/`)
- Python engine package (`python/specific/<ID>/`): risk model, scenario callable,
  `schema.json`, generated sample data (>= 20 real-named rows per component),
  `expected_outputs/`, and executable tests
- Investigator playbook (`operations/specific/`, where applicable)
- Intelligence products (`intelligence-products/specific/<ID>/`)
- Data requirements & schema design
- Model governance linkage (see `operations/common/Risk_Scoring_Governance.md`)

Each engine is built and tested **standalone** in this repository before it is put
through the FC-10 governed runtime, where a thin adapter delegates to it.

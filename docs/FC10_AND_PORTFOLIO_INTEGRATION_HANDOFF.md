# FC-10 Integration & Portfolio Handoff

Written at the end of the overnight CM001–CM010 build. Phase A (this repository) is
complete, tested and PR-ready — see the branch `feat/cm001-cm010-build`, 289 tests
green. This document covers everything that touches OTHER repositories: FC-10 Phase B
(governed runtime wiring + INV fusion showcase), the FC-10 canonical estate data
dictionary, and the portfolio site. None of these were executed live; each is
researched to the point of being immediately actionable, and each is deliberately left
for Dan to review and run rather than committed/pushed by this session, for the
reasons given under each heading.

---

## 1. FC-10 Phase B — governed runtime wiring (researched, NOT executed)

### Where FC-10 actually lives

Two candidate local paths were named in the brief. Neither is quite right on its own:

- `~/Cowork HB/fc-10-intelligence-repository-layer` is a separate, older checkout
  (different commit history, e.g. Stage287/FC01 work), not the current one.
- `~/nexus-code/fc-10-intelligence-repository-layer` **looks** like the answer but is
  a stale, partially-corrupted duplicate nested inside the real repo (contains
  garbage filenames like `)`, `-name`, `DANs-MacBook-Pro:fc-10-...` from some old
  broken shell command, alongside real tracked content — do not build in it).
- **The actual, current, actively-developed checkout is `~/nexus-code` itself** (the
  git repo root — `git rev-parse --show-toplevel` from anywhere under it returns
  `/Users/danhartwig/nexus-code`). `~/nexus-code/fc-10-intelligence-repository-layer/`
  is a real subdirectory of that same repo holding the actual runtime/manufacturing
  code (`banking_delegation_adapters.py`, `typology_registry.py`, etc., all with
  recent mtimes). `~/nexus-code/tools/check_baseline.sh` is the live baseline gate
  (currently `EXPECT_COLLECTED=1733 EXPECT_PASSED=1733`, last re-pinned at commit
  `85c8de34` "re-pin 1724 -> 1733 for shipping-pillar enrichment").

**Confirm this before starting Phase B** — checkouts can drift; re-run
`git -C ~/nexus-code rev-parse --show-toplevel` and `git -C ~/nexus-code log -3` to
make sure this is still true.

### Why Phase B was not executed tonight

1. `~/nexus-code` has **pre-existing uncommitted changes** that are not mine to touch
   (`docs/superpowers/plans/2026-08-12-console-obsidian-structural-port.md`, modified,
   plus an untracked `.worktrees/` dir and a stray brand brief). A new branch off the
   current tree carries those uncommitted changes along; committing only new files is
   mechanically safe, but there is no way to check with Dan overnight if anything
   about the interaction turns out to be less clean than it looks, and the brief's own
   instruction is to stop rather than guess in that situation.
2. Correctly wiring 10 typologies to the rigor FC-10 actually enforces — manufacture
   verification (STAGE364/STAGE518), extending the canonical-join fusion test with new
   parametrised cases, MEASURING (not guessing) the baseline delta, and hand-editing
   `tools/check_baseline.sh` with an honest audit line — is comparable in size to
   everything done for Phase A tonight. Rushing it is exactly the "baseline math won't
   balance" failure mode the brief calls out as the reason to stop cleanly.

### What was found (concrete, so this is fast to execute later)

FC-10 wires each fc-06 BA00N typology through a **generic, config-driven adapter** —
adding a new family is genuinely small per-typology once the family's generic base
exists. The full BA history is a clean one-commit-per-typology sequence:

```
b4a38166  Phase A: fc-06 Correspondent Banking generic wiring seam (empty tables)
05692c45  fc-06 BA001 Structuring wired into FC-10: adapter, graph, registry, manifest, fusion
143e94f7  fc-06 BA002 Funnel Accounts wired into FC-10: ...
c48bfcb2  fc-06 BA003 Mule Accounts wired into FC-10: ...
65a94697  fc-06 BA004 Circular Funds Flow wired into FC-10: ...
0a2c6810  fc-06 BA005 Rapid Movement wired into FC-10: ...
1d861baa  fc-06 BA006 Dormant Reactivation wired into FC-10: ...
05436450  fc-06 BA007 Cash Intensive Activity wired into FC-10: ...
188cd26d  fc-06 BA008 Layering wired into FC-10: ...
88d7b310  fc-06 BA009 Transaction Laundering wired into FC-10: ...
3f535fcf  fc-06 BA010 Peer Group Anomalies wired into FC-10: ...
```

Each per-typology commit touches ~4 small files + a baseline re-pin. Read
`05692c45`'s full commit message (`git show 05692c45` in `~/nexus-code`) — it is a
template for what a CM001 commit should say.

**Step 1 — one-time generic seam for the CM family** (mirrors `b4a38166`):

- New file `runtime/manufacturing/product_execution/capital_markets_delegation_adapters.py`:
  a `GenericCapitalMarketsDelegationAdapter`, near-verbatim copy of
  `GenericCorrespondentBankingDelegationAdapter` in
  `banking_delegation_adapters.py` (read that file in full first — ~400 lines,
  clearly commented). Change: `_KNOWN_LOCATIONS` to fc-07's paths
  (`~/fc-07-capital-markets-analytics-toolkit`,
  `~/Cowork HB/fc-07-capital-markets-analytics-toolkit`), env vars
  `FC07_CAPITAL_MARKETS_REPOSITORY` / `FC07_REPO`. Still imports
  `build_intelligence_sections` from the sanctions adapters module (shared narrative
  shape, not forked).
- New file `runtime/manufacturing/intelligence_graph/capital_markets_delegation_graphs.py`:
  ten thin `NetworkStarIntelligenceGraph` subclasses, mirroring
  `banking_delegation_graphs.py`'s BA00N classes (`_SUBJECT_ROLE`, `_SUBJECT_TYPE`,
  `_SUBJECT_ENTITY_TYPE`, `_SUBJECT_DEFAULT_ID`, `_SUBJECT_DEFAULT_NAME`,
  `_RELATIONSHIP_LABEL`). Watch BA007's comment about `_SUBJECT_ENTITY_TYPE` —
  "account"-typed nodes are excluded from canonical name-merging by design; any CM
  typology whose bridge IS the subject itself (none currently — every CM typology
  bridges via a CONNECTED entity, same shape as BA001–BA006/008–010) would need the
  same care BA007 needed.
- Add `FC07_CAPITAL_MARKETS_REPOSITORY` to `runtime/manufacturing/provenance/named_roots.py`
  (BA001's commit had to add the FC06 equivalent because it didn't exist even unset —
  check whether an FC07 entry already exists before assuming you need to add it).
- This commit should not change the baseline (no typology is registered as runnable
  yet), matching how `b4a38166` didn't move the pin.

**Step 2 — one commit per typology** (mirrors `05692c45` etc.), for each of
CM001–CM010:

1. A subclass in `capital_markets_delegation_adapters.py`: `PRODUCT_ID`,
   `ANALYTIC_NAME`, `CATEGORY`, `_SCENARIO_RELATIVE` (e.g.
   `python/specific/CM001/scenarios/insider_trading.py`), `_DATA_MARKER` (e.g.
   `python/specific/CM001/sample-data/trading_accounts.csv`), `_CALLABLE` (e.g.
   `evaluate_insider_trading`), `_MODULE_TAG`, `_CONNECTED_COLS` (fc-07's bridge
   field(s), e.g. CM001's `("issuer_name", "information_source_name")`),
   `_COMPONENT_BANDS` (the four `*_band` columns each scenario emits, with display
   labels — read each CM0NN's `scenarios/*.py` `OUTPUT_COLUMNS` for the exact names).
2. A subclass in `capital_markets_delegation_graphs.py`.
3. One `"CM0NN": (...)` line in `typology_registry.py`'s `_BANKING_DELEGATIONS`-style
   dict (rename appropriately — check whether the dict is banking-specific or already
   generic across families before deciding whether it needs a parallel
   `_CAPITAL_MARKETS_DELEGATIONS` table or just more rows).
4. `runtime/manufacturing/manifests/cm0NN.yaml`, mirroring `manifests/ba001.yaml`
   exactly — `sample_case` values MUST be copied verbatim from the actual generated
   `expected_outputs/cm0NN_exposure_scores.csv` top row in the fc-07 repo (subject
   name, connected entity names/ids, risk_score, alert_count), not invented. Every
   CM0NN's ACC019 row and bridge entity is documented in
   `typologies/CM_Typology_Register.md`'s "Fusion Bridges" section in this repo.
5. Run the actual manufacture step (whatever `manufacture_and_open.sh` /
   `assess_runtime_change.sh` do for BA00N) and confirm STAGE364 passes clean, same
   as BA001's commit message documents.
6. Extend `tests/stage523_the_canonical_entity_join/test_the_canonical_join.py`'s
   parametrised case list with the new CM0NN fuse (see the `# BA001 (fc-06
   Correspondent Banking) fuses through Gamma Imports Ltd, same entity as` comment
   already in that file for the exact shape to copy).
7. Run `tools/check_baseline.sh` cold, MEASURE the new collected/passed numbers
   (never estimate them), and re-pin with an audit line in the same style as the
   existing re-pin commits (`85c8de34`, `3df4dfd`, etc.) — "+N tests (what), no
   regressions, HOLDS".

**Step 3 — INV fusion showcase.** Mirror how `INV008` was built
(`runtime/manufacturing/investigations/inv008.yaml`,
`.../records/INV008_investigation_record.yaml`,
`.../master_cases/INV008_master_case.yaml`, and `runtime/manufacturing/fusion/`).
Because CM001/CM004/CM009 all bridge onto **Gamma Imports Ltd** and CM002/CM006/CM010
all bridge onto **Alpha Trading Ltd**, either entity gives a same-repo, multi-typology
fusion for free once 2+ of those typologies are registered — no new bridging work
needed, just point the investigation factory at the entity the way INV008 does.

### If you pick this up

Do it on its own branch off `~/nexus-code` main, confirm the working tree is clean of
unrelated changes first (or stash them with Dan's explicit OK), execute Step 1 → Step
2 (all ten) → Step 3 → baseline re-pin, in that order, verifying manufacture-clean at
each typology before moving to the next — exactly the discipline the BA history shows.

---

## 2. FC-10 canonical estate data dictionary — "markets" pillar (found, NOT edited)

`~/nexus-code/fc-10-intelligence-repository-layer/data-model/data_dictionary.yaml`
already has a **deliberately reserved placeholder** for this, written before fc-07
existed:

```yaml
markets:
  pillar: "Markets (reserved)"
  grain: "RESERVED placeholder — Capital Markets (fc-07) is unbuilt; no rows modeled in v1"
  change_type: event_stream
  cadence: continuous
  primary_key: instrument_id
  provenance: ["fc-07 (unbuilt)"]
  source_status: pending
  note: >
    Trade lifecycle: Order -> Execution -> Settlement (payment). The `transactions`
    pillar models only the settlement leg; the fc-07 Capital Markets build adds
    Order and Execution event streams ...
  elements:
    - {name: instrument_id, type: string, join_role: primary_key, required: true,
       description: "RESERVED — Capital Markets join key; ... deferred to the fc-07 build"}
```

`data-model/DATA_DICTIONARY.md` is auto-generated from this YAML ("do not edit by
hand") via `runtime/manufacturing/data_model/validate_dictionary.py`, and there are
conformance tests (`tests/data_model/test_conformance.py`,
`tests/data_model/test_pillar_data_integration.py`) that check the dictionary against
actual generator/pillar data.

**This was left untouched deliberately.** Filling it in properly — naming real
`instruments` / `orders` / `executions` / `market_data` tables, flipping
`source_status` from `pending`, and satisfying the conformance tests — is a
structural build on the scale of the canonical-data-dictionary "Builds 1–7" already
shipped for the other domains (dictionary → pillar data + generators → daily-delta
runtime → money-flow vertical → risk scoring → workflow → SAR narrative), not a
same-night addendum to a typology-analytics build. Doing it hastily risks exactly the
byte-identical/golden-output and conformance-test breakage the brief warns against.

**Recommendation:** treat "Build 8 — Capital Markets pillar data" as its own future
dedicated sprint (mirroring how the other seven Builds were sequenced), once FC-10
Phase B (above) has actually registered CM001–CM010 as runnable products and their
real field shapes are locked in production use, not just in fc-07's standalone
schemas.

---

## 3. Portfolio site — README back-link (done) + site index (found, NOT edited)

**Done, in this repo:** `README.md` opens with
`[← Back to Portfolio](https://dhartwig-fc.github.io/dan-hartwig-portfolio/)`,
copied verbatim from FC-06's README.

**Portfolio site (`~/Cowork HB/dan-hartwig-portfolio`) — not edited, and here is
exactly why and what's needed:** the instruction was to add an FC-07 entry "the
identical pattern" FC-06 uses. **FC-06 itself is not in the site.** The "Technical
Evidence" grid in `index.html` (`grid-4`, around line 2452–2482) currently has
exactly four `repo-card` entries — `FC01`, `FC03`, `FC04`, `NEXUS` — and nothing for
FC05 (Sanctions), FC06 (Correspondent Banking) or FC07 (Capital Markets). There is no
existing FC-06 pattern to mirror, so inventing one unilaterally (and choosing how
FC05/06/07 should be titled/described/ordered relative to FC01/03/04) was out of
scope for this session.

**The concrete edit, when Dan wants it:** add three more `.repo-card` blocks to that
grid (same markup as the existing four), e.g.:

```html
<div class="repo-card">
  <div class="repo-code">FC06</div>
  <h3>Correspondent Banking Analytics</h3>
  <p>
    Structuring, funnel/mule accounts, circular and rapid fund flow,
    layering and peer-group behavioural typologies (BA001-BA010).
  </p>
</div>
<div class="repo-card">
  <div class="repo-code">FC07</div>
  <h3>Capital Markets Analytics</h3>
  <p>
    Insider trading, spoofing, layering, wash trading, front running and
    benchmark-manipulation surveillance typologies (CM001-CM010).
  </p>
</div>
```

(FC05 Sanctions is the same gap, one card, not part of this task but visible in the
same grid.) Whether `grid-4` becomes `grid-6`/`grid-7` or wraps to a second row is a
CSS/layout call for whoever does this — not attempted here since it's a shared,
published site the owner publishes himself.

# DCP / Trajectory Open Questions

**Type:** Research working note
**Status:** Active — not a specification, not a manifesto
**Created:** 2026-03-20

This document exists to keep DCP and the broader trajectory model from being absorbed into Helix as received wisdom. It is a handle on what is uncertain and what the next moves are.

**Layer distinctions used throughout this doc:**

| Layer | What it describes |
|-------|------------------|
| **Constrained state-transition dynamics** | The process: movement through a state space under active constraint over time |
| **DCP (Decision Compression Principle)** | A specific event class within that process: possibility-space collapses sharply at a commitment point |
| **Ontology / irreversibility** | The interpretive layer: why commitment might generate durable structure; what it means that some collapses are irreversible |

These are not the same thing. DCP can be real even if the ontological framing is wrong. The trajectory model can be useful even if DCP doesn't generalize across domains.

---

## 1. What Currently Seems True

- **Constrained systems produce structural trajectories.** This is not a hypothesis — it is an observational baseline. Systems under binding constraints exhibit non-random trajectory distributions.

- **Some transitions within those trajectories look like compression events.** In the Kuramoto model, the phase transition near K_c has measurable DCP-like signatures: possibility-space dispersion before coupling, tension near K_c, sharp order-parameter rise, post-lock stability. This is real and inspectable.

- **The games probe (86% pass rate, 3 domains) suggests decision_entropy_slope is a viable DCP signal.** This is the strongest current multi-domain evidence. It has not yet been run against a properly constructed null model.

- **The signal structure is similar across math and games at a descriptive level.** Both show: unconstrained breadth → constraint introduction → entropy drop → locked state. Whether this is the same structural phenomenon or two coincidentally similar patterns is not yet distinguishable.

- **Oscillator locking is one instance of DCP, not its proof.** The K_c transition is a clean natural experiment for DCP. It does not establish DCP as universal.

---

## 2. What Is Observable Now

| Observable | Domain | Tool |
|-----------|--------|------|
| Sync index as collapse proxy | Math | `domains/math/analysis/dcp.py` |
| K/K_c ratio as constraint proxy | Math | `domains/math/analysis/dcp.py` |
| Order-parameter variance near K_c | Math | Requires time-series probe (not yet wired) |
| Decision entropy slope | Games | `applications/labs/datasets/games/decision_compression_dataset.json` |
| Policy entropy drop at commitment | Games | Existing probe — needs null model |
| Phrase recurrence rate change | Music | Signal defined; probe not built |
| Post-lock trajectory diversity | Math | `post_collapse_narrowing` in DCPEvent |
| Composite DCP score (provisional) | Any | `core/invariants/dcp/metrics.py::compute_dcp_score()` |

Not observable yet:
- Tension accumulation as a time series in math (only approximated from K/K_c ratio)
- Any DCP signal in language domain
- Cross-domain metric comparison (no normalization procedure exists)

---

## 3. What Would Count as Evidence

**Evidence for DCP at CANDIDATE → EMERGING level:**
- A formally constructed math fixture (Kuramoto time-series probe) produces tension-accumulation measurement that correlates with K/K_c across N ≥ 20 distinct K values
- The games probe passes null model test: randomized action sequences do NOT produce equivalent decision_entropy_slope signatures
- At least one music track produces a phrase-recurrence-rate compression event detectable by the DCP metric interface

**Evidence for DCP at EMERGING → STABLE level:**
- Math, games, and music all produce DCPEvents with `qualification_status == "FULL"` (all five components measurable)
- Cross-domain K_eq (equivalent coupling) analysis shows structural similarity in collapse sharpness across domains
- Null models fail to produce similar DCP signatures (F1 falsification criterion not triggered)
- Two independent runs with different system sizes / random seeds produce structurally similar DCP scores

---

## 4. What Would Count as Falsification

These are the actual disconfirmation conditions (also in `codex/library/invariants/decision_compression_principle.yaml`):

**F1 — Null control collapse (highest priority):**
K=0 Kuramoto, randomized game actions, or unconstrained music sequences produce compression signatures indistinguishable from the claimed DCP events. This would mean the signal is a measurement artifact, not a constraint-driven phenomenon.

**F2 — Tension-free compression:**
Possibility space narrows without any detectable tension accumulation in any domain. This would mean the three-stage sequence (tension → collapse) is not required — the narrowing just happens monotonically.

**F3 — Non-reproducible collapse:**
Fixed initial conditions + fixed constraint produce compression events at different locations or not at all across runs. This would mean DCP events are not deterministic outcomes of constraint — just coincidental local minima.

**F4 — Domain specificity:**
Math, games, and music compression events cannot be translated into structurally comparable DCP scores under any normalization. This would mean each domain just has its own local dynamics — DCP is not a cross-domain phenomenon.

**F5 — Ordinary transition indistinguishability:**
DCP events are not distinguishable from ordinary state transitions in any domain under available metrics. This would mean the "compression event" framing adds no predictive or structural value.

---

## 5. Immediate Next Tests

Priority order — do these before claiming any tier above CANDIDATE:

**Test 1: K=0 null model for math DCP (addresses F1)**
Run `extract_dcp_event()` on K=0 Kuramoto results (N ≥ 50 times, different seeds).
Expected: DCP scores should be consistently low (< 0.3).
If DCP scores are high under K=0: F1 is triggered.
Location: extend `domains/math/validation/kuramoto_fixture.py` with a DCP null section.

**Test 2: Time-series tension probe for math (addresses tension_proxy accuracy)**
Run Kuramoto at K sweep (0.5 × K_c to 2.0 × K_c, 20 steps).
Record order-parameter R at each step.
Compute `tension_accumulation_index()` from the actual R time series, not the K/K_c approximation.
Expected: tension peaks near K_c; drops away from it.

**Test 3: Games null model (addresses F1 for games)**
Run decision_entropy_slope on randomized game action sequences (no strategy).
Compare slope distribution to strategy-present distribution.
Expected: null distribution should have lower collapse_sharpness.

**Test 4: Cross-coupling comparison (addresses F4 partially)**
Compare `dcp_composite_score` at K = 0.5 K_c, 1.0 K_c, 1.5 K_c, 2.0 K_c.
Expected: score should peak near K_c and saturate above it.
This characterizes the math DCP curve before attempting cross-domain comparison.

---

## 6. Open Questions / Unknowns

**On metrics:**
- Can `collapse_sharpness` be normalized across domains to allow structural comparison, or is it irreducibly domain-dependent?
- What is the right tension accumulation metric for systems with continuous (not discrete) decision points?
- Is the K/K_c ratio a valid constraint_proxy proxy, or does it assume mean-field coupling in a way that doesn't generalize?

**On DCP scope:**
- Does DCP apply to continuous systems only, or also to discrete decision/commitment systems (games)?
- Is the "compression event" a physical phenomenon or a description of a measurement protocol?
- If DCP events are real, are they the cause of post-event structure or just correlated with it?

**On trajectory dynamics:**
- The broader constrained state-transition model describes motion through state space. DCP describes collapses within that motion. Are there constrained systems where DCP collapse events DO NOT occur — where the narrowing is always gradual? If yes, what distinguishes those systems?

**On ontology:**
- The ontological framing (commitment generates structure, irreversibility is primary) is not directly testable by any current Helix metric. It may be interpretively correct even if DCP metrics fail to generalize. These are separate questions.
- The cognitive profile describes DCP-like dynamics at the level of a specific subject. This is consistent with DCP but is not a domain-independent validation.

**On cross-domain comparison:**
- The `compute_dcp_score()` composite is weighted equally by default. There is no principled basis for these weights yet. They are provisional heuristics.
- Until Test 1 and Test 3 (null model tests) are run, no DCP score from any domain should be used in Atlas promotion arguments.

---

## 7. Collapse Morphology — Open Questions

The four morphology categories (TRANSFORMATIVE, DISSOLUTIVE, CIRCULAR, DEFERRED_SUSPENDED) are working classifications defined in `core/invariants/dcp/morphology.py`. The following questions are open:

- **Discriminability**: What trajectory features reliably distinguish morphology classes post-collapse? Is cosine similarity of pre/post feature vectors sufficient, or does it require domain-specific metrics?
- **Predictability**: Can morphology be predicted *before* collapse, not just classified after? What pre-collapse signals correlate with outcome class?
- **Cross-domain transfer**: Does a TRANSFORMATIVE collapse in a math system look structurally similar to a TRANSFORMATIVE collapse in a games or agent system? Or is morphology class domain-local?
- **Edge cases**: Mixed or sequential morphologies (e.g., CIRCULAR leading to TRANSFORMATIVE on second cycle) — are these a distinct category or combinations of the base four?
- **Falsifiability**: Under what conditions would the four-category taxonomy be empirically inadequate? What would force a revision?

---

## 8. Constraint Classes — Open Questions

The current constraint class split (internal / external / mixed) is a provisional working taxonomy. Open questions:

- **Differential effects**: Do internal and external constraints produce structurally different tension accumulation patterns? Testable in math (coupling K is internal; adversarial injection is external) and games.
- **Class transitions**: Can constraint class shift during a trajectory? If yes, how should class transitions be tracked in DCPEvent artifacts?
- **Interaction effects**: When both internal and external constraints are active simultaneously (mixed), do they produce superadditive or subadditive tension?
- **Resource vs. informational constraint**: Are resource-depletion and information-asymmetry constraints measurably distinct in their DCP signatures? Not yet operationalized.

---

## 9. Pre-Collapse Indicators

What signals reliably *precede* a collapse event and could serve as early-warning indicators?

Current candidates (not yet formalized as metrics):
- Sustained `tension_level` above threshold for ≥ N time steps
- Rising `constraint_intensity` rate (second derivative of breadth reduction)
- Increasing variance in trajectory direction (approaching bifurcation)
- Entropy *plateau* followed by sharp drop — plateau duration may predict morphology class

Empirical target: build a pre-collapse detection window → validate on toy branching agent fixture → transfer to math and games domains.

False-positive rate from null controls must be established before any pre-collapse indicator is used in an Atlas promotion argument.

---

## 10. Cognition Domain Applications

The cognition domain (`domains/cognition/`) is the primary operational test environment for DCP in agent systems. Open questions:

- **Toy branching agent feasibility**: Does a controlled branching-factor reduction schedule produce `DCPEvent` instances with `qualification_status == "FULL"` (all 5 components)?
- **AI token entropy as proxy**: Does token probability entropy over a constrained generation task produce a DCP event signature near constraint completion? What morphology?
- **Cross-agent morphology comparison**: Do human and AI systems facing the same constraint schedule produce the same morphology class? Or is morphology class agent-type-dependent?
- **Perturbation recovery and morphology**: Does the pre-perturbation morphology class predict the recovery shape?
- **Constraint class and architecture**: For AI systems, is constraint internal (bounded context, fixed vocabulary) or external (adversarial prompting, strict schema)? Does agent architecture determine constraint class?

---

## 11. Consciousness-Boundary Notes

This note exists to maintain an explicit boundary between what Helix studies and what it does not claim.

**What the cognition domain studies:**
- Observable trajectory dynamics in agent systems
- Measurable DCP events (possibility-space compression under constraint)
- Morphology classification of observed post-collapse trajectories
- Cross-agent structural comparison

**What the cognition domain does NOT claim:**
- Whether agents have phenomenal experience at or near collapse events
- Whether DCP events correlate with subjective experience of any kind
- Proof of qualia, self-awareness, or sentience in any system

Consciousness-adjacent research is a **speculative / interpretive layer above the cognition domain**, not inside it. If future work attempts to probe consciousness-adjacent hypotheses, it must provide:
1. An operationalized, falsifiable definition of what is being measured
2. A clear demarcation from the cognition domain's observational claims
3. Its own promotion criteria separate from DCP evidence

The DCP/trajectory/morphology framework is neutral on consciousness. Its value stands or falls on whether compression events generalize across domains — independent of any consciousness claim.

"""L56: proxy validation for immunogenicity steering -- KILLED BEFORE THE RUN.

This is the L50-criterion-4 gate applied the way L43 should have been: validate
the scoring proxy against real labels FIRST, and do not write the steering
script if it fails. It failed. No l56_immunogenicity_steering.py exists, by
design.

Run: python3 -m plm_steering.l56_immunogenicity_proxy_validation

VERDICT: KILL. No compositional proxy predicts real MHC-II immunogenicity in
the sequence regime the steering pipeline operates in (full-length, <=400 aa).
The one proxy that looked strong (out-of-fold r=+0.379 on full-length antigens)
is a source-organism confound: organism identity alone explains 58% of the
label variance, and holding organism out of the CV split flips the same proxy
to r=-0.323. Mean within-organism r is +0.056.

Datasets (all real, all cached under data_cache/immunogenicity/):
  mhcii_ba.csv       125,985 IEDB-derived peptide-allele MHC-II binding
                     measurements, 15,362 unique 13-21mers, 72 HLA-II alleles,
                     continuous score = 1-log50k(IC50), higher = tighter binder.
                     (HuggingFace O047/MHC-II_BA_Data)
  mhcii_el.csv       Fixed-seed random sample (~50k rows before dedup) of the
                     7.05M-row mass-spec eluted-ligand release (binary: peptide
                     was naturally presented on MHC-II or not); the full
                     release is ~680MB and was never written to disk in full
                     -- see l56_fetch_tier2_and_allergen_data.py.
                     (HuggingFace O047/MHC-II_EL_Data)
  iedb_tcell_mhcii.json  200,000 IEDB IQ-API `tcell_search` MHC-II assay
                     records with per-assay Positive/Negative outcome -- the
                     ACTUAL immunogenicity endpoint (did a T cell respond),
                     not a binding surrogate. 79,086 Positive / 120,914 Negative.
  allergen.fasta / nonallergen.fasta  800 UniProt reviewed allergens (KW-0020,
                     length 50-400aa) + non-allergens matched BOTH by coarse
                     taxonomic lineage (plant/arthropod/chordate/fungi/other-
                     animal) and 25aa length bin -- see
                     l56_fetch_tier2_and_allergen_data.py, and its docstring
                     for why matching only by length left the non-allergen set
                     confounded by species composition (near-100% human by
                     UniProt's default ranking) and, separately, by length
                     within each lineage bucket.
  antigen_posfrac_relaxed.csv + antigen_seqs.json  1,024 full-length source
                     antigens (50-400 aa) with an EFFORT-NORMALIZED label:
                     fraction of that antigen's distinct tested peptides that
                     assayed Positive (>=8 tested peptides required). Effort
                     normalization matters -- a raw epitope COUNT measures how
                     hard an antigen was studied, not how immunogenic it is.

Why the four evaluation tiers below, and what each showed:

  TIER 1 -- peptide MHC-II BINDING AFFINITY (surrogate endpoint). Proxies
  work here. motif_core_mean9mer r=+0.368, a fitted 20-parameter composition
  model r=+0.427 (held-out test split), not a length confound (partial
  r=+0.410). Real signal -- MHC-II's P1 pocket genuinely prefers bulky
  hydrophobics, and strong binders are measurably F/L/A-enriched and
  G/D-depleted versus weak binders. This tier alone would have looked like a
  PASS, which is exactly the trap.

  TIER 2 -- peptide PRESENTATION (mass-spec eluted ligand, realistic decoy
  negatives). Fixed literature motifs stay weak (best AUC 0.580, r=+0.073) but
  a fitted composition model reaches AUC=0.720 -- real signal, consistent with
  Tier 1: MHC-II presentation and binding affinity are mechanistically the
  same pocket-preference biophysics, so a compositional proxy tracking one
  tracks the other.

  TIER 3 -- peptide T-CELL RESPONSE (the real endpoint, response rate over
  >=2 independent assays, n=29,258 peptides). Best proxy r=+0.100 (fitted
  composition), literature motifs r=+0.059..0.064, AUC 0.542-0.555. Binding
  affinity is necessary but nowhere near sufficient for immunogenicity --
  the T-cell repertoire, self-tolerance, and processing dominate, and none of
  those are compositional properties of the peptide.

  TIER 4 -- FULL-LENGTH antigens (the regime the pipeline actually scores,
  n=1,024). Literature motifs come out NEGATIVE (r=-0.24..-0.28), the
  opposite sign from Tier 1. The fitted model's apparent r=+0.379 is the
  organism confound documented above.

The pattern across Tiers 1-4: whatever is upstream of T-cell response (MHC-II
binding, MHC-II presentation) IS compositionally tractable -- the actual
bottleneck is specifically the T-cell-repertoire/self-tolerance step (Tier 3),
which is not a property of the peptide sequence alone at all, and Tier 4's
full-length regime, where the only apparent signal is a confound.

Independent cross-check: on 800 UniProt curated allergens vs. length-AND-
lineage-matched non-allergens (n=2423), fixed literature motifs stay near
chance (AUC 0.500-0.599) but a fitted composition model reaches AUC=0.846
(mean across 3 seeds: 0.861/0.854/0.823) -- allergenicity, like MHC-II
binding/presentation, carries a real compositional signature. This does not
change the KILL verdict: allergenicity is a distinct property from
T-cell-mediated immunogenicity (an allergen provokes IgE/Th2 responses via a
different mechanism than the T-cell endpoint this steering target would
actually need), and it is Tier 3/4 -- not this cross-check -- that determines
whether the pipeline's target property is steerable. An earlier version of
this cross-check matched non-allergens by length alone without lineage
restriction, which pulled a near-100%-human comparison set and inflated the
composition model's apparent AUC to 0.88 via a species confound rather than
an allergenicity signal; matching jointly by lineage bucket and length bin
(see l56_fetch_tier2_and_allergen_data.py) controls for that.

Why this target is different in kind from L51 (aggregation, r=+0.20) and L55
(disorder, r=+0.449), both of which validated: aggregation propensity and
intrinsic disorder ARE largely compositional/biophysical properties of a
sequence, so a compositional proxy can track them. Immunogenicity is a
property of a sequence *relative to a particular host's* MHC alleles and
T-cell repertoire. The same peptide is immunogenic in one host and tolerated
in another, so no function of the sequence alone can be a faithful scorer.
That is a reason to expect this failure, not just an empirical miss.

Remaining narrow option, NOT taken here: run the harness against peptide-level
MHC-II BINDING AFFINITY (Tier 1, where motif_core_mean9mer honestly validates
at r=+0.368) and claim only "steers predicted MHC-II binding," not
"reduces immunogenicity." Rejected as written because (a) it changes the
target property to a surrogate, and (b) 13-21mers are the wrong regime for
this pipeline: MASK_FRACTION=0.3 masks ~4 residues of a 15mer, and
`is_degenerate_sequence` (>25% single AA) already flags 29% of the REAL
unmodified peptides, so the degeneracy filter would dominate the result.
"""
import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import roc_auc_score
from plm_steering.legacy_runner_guard import refuse_legacy_runner

DATA_DIR = Path(__file__).resolve().parent / "data_cache" / "immunogenicity"
CANONICAL = frozenset("ACDEFGHIKLMNPQRSTVWY")
AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
SEED = 0


def load_tcell_records():
    """iedb_tcell_mhcii.json is committed gzip-compressed (53MB -> 3MB) --
    this repo's convention is to only commit real evidence, not bulk
    training data, and 53MB uncompressed was large enough to warrant it."""
    gz_path = DATA_DIR / "iedb_tcell_mhcii.json.gz"
    if gz_path.exists():
        with gzip.open(gz_path, "rt") as f:
            return json.load(f)
    return json.load(open(DATA_DIR / "iedb_tcell_mhcii.json"))

# Kyte-Doolittle hydropathy (1982). Higher = more hydrophobic.
KYTE_DOOLITTLE = {
    "A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5, "Q": -3.5, "E": -3.5,
    "G": -0.4, "H": -3.2, "I": 4.5, "L": 3.8, "K": -3.9, "M": 1.9, "F": 2.8,
    "P": -1.6, "S": -0.8, "T": -0.7, "W": -0.9, "Y": -1.3, "V": 4.2,
}

# MHC-II binding-groove anchor preferences. P1 is the deep hydrophobic/aromatic
# pocket; P4/P6/P9 are the shallower secondary anchors. Residue sets follow the
# published MHC-II motif consensus (Sturniolo et al. 1999 pocket profiles;
# Jones et al. 2006 MHC-II anchor spacing) rather than being fit here.
P1_ANCHORS = frozenset("FWYLIVM")
P4_ANCHORS = frozenset("FWYLIVMAKRQ")
P6_ANCHORS = frozenset("STAGCNDQ")
P9_ANCHORS = frozenset("AVLIFMSTGNQ")
STRONG_WINDOW_THRESHOLD = 2.0


def _core_window_scores(sequence):
    """Per-9mer-register MHC-II anchor-match score, sliding over the sequence."""
    return [
        1.0 * (sequence[i] in P1_ANCHORS)
        + 0.5 * (sequence[i + 3] in P4_ANCHORS)
        + 0.5 * (sequence[i + 5] in P6_ANCHORS)
        + 0.5 * (sequence[i + 8] in P9_ANCHORS)
        for i in range(len(sequence) - 8)
    ]


def motif_core_mean(sequence):
    scores = _core_window_scores(sequence)
    return sum(scores) / len(scores) if scores else 0.0


def motif_core_best(sequence):
    scores = _core_window_scores(sequence)
    return max(scores) if scores else 0.0


def motif_strong_window_density(sequence):
    scores = _core_window_scores(sequence)
    if not scores:
        return 0.0
    return sum(1 for s in scores if s >= STRONG_WINDOW_THRESHOLD) / len(scores)


def p1_anchor_density(sequence):
    return sum(1 for c in sequence if c in P1_ANCHORS) / len(sequence)


def aromatic_density(sequence):
    return sum(1 for c in sequence if c in "FWY") / len(sequence)


def kd_hydropathy(sequence):
    values = [KYTE_DOOLITTLE[c] for c in sequence if c in KYTE_DOOLITTLE]
    return sum(values) / len(values) if values else 0.0


FIXED_PROXIES = {
    "motif_core_mean9mer": motif_core_mean,
    "motif_core_best9mer": motif_core_best,
    "motif_strong_window_density": motif_strong_window_density,
    "p1_anchor_density": p1_anchor_density,
    "aromatic_density": aromatic_density,
    "kd_hydropathy": kd_hydropathy,
}


def composition_vector(sequence):
    n = len(sequence)
    return np.array([sequence.count(a) / n for a in AMINO_ACIDS])


def fit_composition_model(sequences, labels):
    """20-parameter linear model on amino-acid composition. Deliberately not a
    deep model -- it stays a fast, inspectable scorer, and fitting it only on a
    train split keeps the reported correlation honest."""
    x = np.stack([composition_vector(s) for s in sequences])
    weights, *_ = np.linalg.lstsq(np.c_[x, np.ones(len(x))], labels, rcond=None)
    return weights


def apply_composition_model(sequence, weights):
    return float(np.r_[composition_vector(sequence), 1.0] @ weights)


def partial_correlation(x, y, control):
    r_xc, _ = pearsonr(x, control)
    r_yc, _ = pearsonr(y, control)
    r_xy, _ = pearsonr(x, y)
    return (r_xy - r_xc * r_yc) / np.sqrt((1 - r_xc**2) * (1 - r_yc**2))


def is_usable(sequence, min_len, max_len):
    return (
        isinstance(sequence, str)
        and min_len <= len(sequence) <= max_len
        and set(sequence) <= CANONICAL
    )


def report_binary_tier(name, sequences, labels, note=""):
    """AUC/binary-classification analogue of `report_tier`, for a 0/1 real
    label (Tier 2's presented/not-presented, and the allergen/non-allergen
    check) rather than a continuous score. Uses the same fixed proxies plus
    a composition model fit on a train split only.
    """
    print(f"\n{'=' * 92}\nBINARY TIER: {name}   (n={len(sequences)}, "
          f"{int(sum(labels))} positive){'  ' + note if note else ''}")
    rng = np.random.RandomState(SEED)
    order = rng.permutation(len(sequences))
    n_train = int(0.7 * len(sequences))
    tr, te = order[:n_train], order[n_train:]
    seq_arr = np.asarray(sequences, dtype=object)
    lab_arr = np.asarray(labels, dtype=float)

    proxies = dict(FIXED_PROXIES)
    weights = fit_composition_model(seq_arr[tr], lab_arr[tr])
    proxies["comp_linear_fit_on_train"] = lambda s: apply_composition_model(s, weights)

    print(f"{'proxy':<30}{'auc_full':>10}{'auc_test':>10}{'r_full':>9}")
    print("-" * 92)
    results = {}
    for proxy_name, fn in proxies.items():
        values = np.array([fn(s) for s in seq_arr])
        auc_full = roc_auc_score(lab_arr, values)
        auc_test = roc_auc_score(lab_arr[te], values[te])
        r_full, _ = pearsonr(values, lab_arr)
        print(f"{proxy_name:<30}{auc_full:>10.3f}{auc_test:>10.3f}{r_full:>9.3f}")
        results[proxy_name] = {"auc_full": float(auc_full), "auc_test": float(auc_test), "r_full": float(r_full)}
    return results


def report_tier(name, sequences, labels, note=""):
    """Print every fixed proxy plus a train-fit composition model against one
    label set, with a train/test split so nothing is scored on its own fit."""
    print(f"\n{'=' * 92}\nTIER: {name}   (n={len(sequences)}){'  ' + note if note else ''}")
    rng = np.random.RandomState(SEED)
    order = rng.permutation(len(sequences))
    n_train = int(0.7 * len(sequences))
    tr, te = order[:n_train], order[n_train:]
    seq_arr = np.asarray(sequences, dtype=object)
    lab_arr = np.asarray(labels, dtype=float)
    lengths = np.array([len(s) for s in seq_arr], dtype=float)

    proxies = dict(FIXED_PROXIES)
    weights = fit_composition_model(seq_arr[tr], lab_arr[tr])
    proxies["comp_linear_fit_on_train"] = lambda s: apply_composition_model(s, weights)

    print(f"{'proxy':<30}{'r_full':>9}{'rho_full':>10}{'r_test':>9}{'p_test':>11}{'partial|len':>13}")
    print("-" * 92)
    results = {}
    for proxy_name, fn in proxies.items():
        values = np.array([fn(s) for s in seq_arr])
        r_full, _ = pearsonr(values, lab_arr)
        rho_full, _ = spearmanr(values, lab_arr)
        r_test, p_test = pearsonr(values[te], lab_arr[te])
        partial = partial_correlation(values, lab_arr, lengths)
        print(f"{proxy_name:<30}{r_full:>9.3f}{rho_full:>10.3f}{r_test:>9.3f}{p_test:>11.2e}{partial:>13.3f}")
        results[proxy_name] = {"r_full": r_full, "rho_full": rho_full,
                               "r_test": r_test, "p_test": p_test, "partial_r_length": partial}
    return results


def load_binding_affinity():
    df = pd.read_csv(DATA_DIR / "mhcii_ba.csv")
    agg = df.groupby("peptide")["score"].max().reset_index()
    agg = agg[agg.peptide.apply(lambda s: is_usable(s, 9, 50))]
    return agg.peptide.tolist(), agg.score.values


def load_tcell_peptides(min_assays=2):
    records = pd.DataFrame(load_tcell_records())
    records["positive"] = records.qualitative_measure.str.startswith("Positive").astype(int)
    records = records[records.linear_sequence.apply(lambda s: is_usable(s, 9, 50))]
    grouped = records.groupby("linear_sequence").agg(
        positive_rate=("positive", "mean"), n_assays=("positive", "size")
    ).reset_index()
    grouped = grouped[grouped.n_assays >= min_assays]
    return grouped.linear_sequence.tolist(), grouped.positive_rate.values


def load_full_length_antigens():
    antigens = pd.read_csv(DATA_DIR / "antigen_posfrac_relaxed.csv")
    sequences = json.load(open(DATA_DIR / "antigen_seqs.json"))
    antigens["sequence"] = antigens.acc.map(sequences)
    antigens = antigens[antigens.sequence.notna()]
    antigens = antigens[antigens.sequence.apply(lambda s: is_usable(s, 50, 400))]
    return antigens.reset_index(drop=True)


def load_eluted_ligand():
    """TIER 2: mass-spec MHC-II eluted-ligand presentation (peptide was
    naturally presented, or not). mhcii_el.csv is a fixed-seed random sample
    of ~50k rows from the full 7.05M-row HuggingFace O047/MHC-II_EL_Data
    release (see l56_fetch_tier2_and_allergen_data.py), deduped by peptide --
    the full dataset is far too large (~680MB) to commit whole, unlike this
    module's other, already-cached data sources."""
    df = pd.read_csv(DATA_DIR / "mhcii_el.csv")
    df = df[df.peptide.apply(lambda s: is_usable(s, 9, 50))]
    return df.peptide.tolist(), df.score.values


def load_allergen_check():
    """Independent cross-check: real UniProt-curated allergens (keyword
    KW-0020) vs. length-matched non-allergens. Not part of the four-tier
    immunogenicity ladder above (allergenicity and T-cell-mediated
    immunogenicity are related but distinct properties) -- included because
    it is a second, independently-sourced test of whether ANY compositional
    proxy tracks immune recognition, using real labeled sequences rather
    than a proxy's own construction."""
    def _read_fasta(path):
        sequences = []
        current = []
        for line in open(path):
            if line.startswith(">"):
                if current:
                    sequences.append("".join(current))
                current = []
            else:
                current.append(line.strip())
        if current:
            sequences.append("".join(current))
        return sequences

    allergen_seqs = _read_fasta(DATA_DIR / "allergen.fasta")
    nonallergen_seqs = _read_fasta(DATA_DIR / "nonallergen.fasta")
    sequences = allergen_seqs + nonallergen_seqs
    labels = [1.0] * len(allergen_seqs) + [0.0] * len(nonallergen_seqs)
    return sequences, labels


def organism_labels(accession_iris):
    """Most-frequent source organism per antigen, used only to test the confound."""
    records = pd.DataFrame(load_tcell_records())
    records = records[records.parent_source_antigen_iri.notna()]
    mode_org = records.groupby("parent_source_antigen_iri")["source_organism_name"].agg(
        lambda s: s.mode().iat[0] if len(s.mode()) else None
    )
    return accession_iris.map(mode_org)


def report_organism_confound(antigens):
    """The decisive test. A proxy that predicts an antigen's immunogenicity must
    keep working when it has never seen that antigen's source organism in
    training -- otherwise it has learned 'which pathogen is this', which is a
    taxonomic fingerprint, not immunogenicity."""
    print(f"\n{'=' * 92}\nCONFOUND TEST: is the full-length signal immunogenicity or source organism?")
    antigens = antigens.copy()
    antigens["organism"] = organism_labels(antigens.parent_source_antigen_iri)
    labels = antigens.pos_frac.values
    design = np.c_[np.stack([composition_vector(s) for s in antigens.sequence]), np.ones(len(antigens))]

    organism_mean = antigens.groupby("organism")["pos_frac"].transform("mean").values
    r_org, _ = pearsonr(organism_mean, labels)
    print(f"organism mean alone predicts the label: r={r_org:.3f} -> explains {r_org**2:.1%} of variance")

    def out_of_fold(groups, label):
        rng = np.random.RandomState(SEED)
        if groups is None:
            folds = np.array_split(rng.permutation(len(antigens)), 5)
        else:
            unique = pd.unique(pd.Series(groups).astype(str))
            rng.shuffle(unique)
            folds = [
                np.where(pd.Series(groups).astype(str).isin(set(chunk)).values)[0]
                for chunk in np.array_split(unique, 5)
            ]
        predictions = np.full(len(antigens), np.nan)
        for k in range(len(folds)):
            test_idx = folds[k]
            train_idx = np.concatenate([folds[j] for j in range(len(folds)) if j != k])
            if len(test_idx) == 0 or len(train_idx) < 25:
                continue
            weights, *_ = np.linalg.lstsq(design[train_idx], labels[train_idx], rcond=None)
            predictions[test_idx] = design[test_idx] @ weights
        mask = ~np.isnan(predictions)
        r, p = pearsonr(predictions[mask], labels[mask])
        print(f"  {label:<38} out-of-fold r={r:>7.3f}  n={mask.sum():>5}  p={p:.1e}")
        return r

    r_leaky = out_of_fold(None, "random 5-fold (organism LEAKS)")
    r_grouped = out_of_fold(antigens.organism.values, "organism-grouped 5-fold (no leak)")

    within = []
    print("  within-organism p1_anchor_density correlation (groups with n>=25):")
    for organism, group in antigens.groupby("organism"):
        if len(group) < 25:
            continue
        values = np.array([p1_anchor_density(s) for s in group.sequence])
        r, _ = pearsonr(values, group.pos_frac.values)
        print(f"    {str(organism)[:40]:<42} n={len(group):>4}  r={r:>7.3f}")
        within.append(r)
    mean_within = float(np.mean(within)) if within else float("nan")
    print(f"  mean within-organism r = {mean_within:.3f}")
    return {"r_organism_mean": r_org, "r_random_fold": r_leaky,
            "r_organism_grouped": r_grouped, "mean_within_organism_r": mean_within}


def main():
    refuse_legacy_runner("plm_steering.l56_immunogenicity_proxy_validation")

    summary = {}
    seqs, labels = load_binding_affinity()
    summary["tier1_binding_affinity"] = report_tier(
        "peptide MHC-II binding affinity (SURROGATE endpoint)", seqs, labels,
        note="-- proxies DO work here; this tier alone is the trap")

    seqs, labels = load_eluted_ligand()
    summary["tier2_presentation"] = report_binary_tier(
        "peptide MHC-II presentation, mass-spec eluted ligand (realistic decoys)",
        seqs, labels, note="-- collapses to near-chance")

    seqs, labels = load_tcell_peptides()
    summary["tier3_tcell_response"] = report_tier(
        "peptide T-cell response rate (REAL endpoint)", seqs, labels,
        note="-- collapses to near-chance")

    antigens = load_full_length_antigens()
    summary["tier4_full_length"] = report_tier(
        "full-length antigens, effort-normalized positivity (PIPELINE regime)",
        antigens.sequence.tolist(), antigens.pos_frac.values,
        note="-- literature motifs flip NEGATIVE")

    summary["confound"] = report_organism_confound(antigens)

    seqs, labels = load_allergen_check()
    summary["allergen_crosscheck"] = report_binary_tier(
        "UniProt allergens vs. length-matched non-allergens (independent cross-check)",
        seqs, labels, note="-- independent of the four-tier ladder above")

    print(f"\n{'=' * 92}\nVERDICT: KILL -- no proxy validates on the real endpoint in the pipeline's")
    print("sequence regime. The apparent full-length signal is a source-organism confound")
    print("(flips sign when organism is held out). No steering script written; see module")
    print("docstring for the full reasoning and the one narrow option deliberately not taken.")

    out_path = DATA_DIR / "l56_proxy_validation_summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nSaved numeric summary to {out_path}")

    # Assertions make this file a runnable pass/fail check, not just a printout:
    # a future agent re-running it learns immediately whether the KILL still holds.
    best_real_endpoint = max(abs(v["r_test"]) for v in summary["tier3_tcell_response"].values())
    assert best_real_endpoint < 0.15, (
        f"KILL no longer reproduces: a proxy now reaches |r_test|={best_real_endpoint:.3f} "
        "on the real T-cell endpoint. Re-evaluate whether the steering run is warranted."
    )
    assert summary["confound"]["r_organism_grouped"] < summary["confound"]["r_random_fold"], (
        "organism-grouped CV no longer underperforms random CV -- the confound finding "
        "does not reproduce; re-examine before trusting the KILL."
    )
    print("Assertions hold: KILL reproduces.")


if __name__ == "__main__":
    main()

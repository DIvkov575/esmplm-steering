import numpy as np
import pytest

from plm_steering.l53_binding_affinity_steering import (
    binding_affinity_proxy,
    binding_affinity_proxy_excluding,
    mutational_sensitivity_weights,
    parse_mutant_positions,
    unweighted_identity,
    weighted_wildtype_preservation,
)


def test_parse_mutant_positions_single_mutation():
    assert parse_mutant_positions("A11C") == [10]


def test_parse_mutant_positions_double_mutation():
    assert parse_mutant_positions("A11C:D38C") == [10, 37]


def test_parse_mutant_positions_skips_unparseable_tokens():
    assert parse_mutant_positions("A11C:garbage:D38C") == [10, 37]


def test_parse_mutant_positions_empty_string():
    assert parse_mutant_positions("") == []


def test_mutational_sensitivity_weights_flags_position_that_hurts_binding():
    # Position 0 mutations tank binding (score -5, below the median);
    # position 1 mutations are neutral (score 0, at the median).
    mutants = ["A1C", "A1D", "B2C", "B2D"]
    scores = [-5.0, -5.0, 0.0, 0.0]
    weights = mutational_sensitivity_weights(mutants, scores, reference_length=3)
    assert weights[0] == pytest.approx(1.0)
    assert weights[1] == pytest.approx(0.0)
    assert weights[2] == pytest.approx(0.0)


def test_mutational_sensitivity_weights_ignores_neutral_or_helpful_positions():
    # position 1 mutations score ABOVE the median -- should get zero weight,
    # not negative weight.
    mutants = ["A1C", "B2C"]
    scores = [-5.0, 5.0]
    weights = mutational_sensitivity_weights(mutants, scores, reference_length=2)
    assert weights[0] > 0.0
    assert weights[1] == pytest.approx(0.0)


def test_mutational_sensitivity_weights_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        mutational_sensitivity_weights(["A1C", "B2C"], [1.0], reference_length=2)


def test_mutational_sensitivity_weights_rejects_all_zero_weights():
    # every mutation scores at or above the median -> nothing to weight.
    with pytest.raises(ValueError):
        mutational_sensitivity_weights(["A1C"], [5.0], reference_length=1)


def test_weighted_wildtype_preservation_full_score_for_exact_wildtype():
    reference = "ABCDE"
    weights = np.array([0.5, 0.2, 0.1, 0.1, 0.1])
    assert weighted_wildtype_preservation(reference, reference, weights) == pytest.approx(1.0)


def test_weighted_wildtype_preservation_drops_when_sensitive_position_mutated():
    reference = "ABCDE"
    weights = np.array([0.5, 0.2, 0.1, 0.1, 0.1])
    mutant = "XBCDE"  # position 0, the highest-weighted position, mutated
    assert weighted_wildtype_preservation(mutant, reference, weights) == pytest.approx(0.5)


def test_unweighted_identity_full_for_exact_match():
    assert unweighted_identity("ABCDE", "ABCDE") == pytest.approx(1.0)


def test_unweighted_identity_zero_for_no_match():
    assert unweighted_identity("XXXXX", "ABCDE") == pytest.approx(0.0)


def test_binding_affinity_proxy_zero_for_exact_wildtype():
    # weighted preservation == unweighted identity == 1.0 for the wildtype
    # itself, so the proxy (their difference) is exactly zero.
    reference = "ABCDE"
    weights = np.array([0.5, 0.2, 0.1, 0.1, 0.1])
    assert binding_affinity_proxy(reference, reference, weights) == pytest.approx(0.0)


def test_binding_affinity_proxy_rewards_preferential_preservation_at_sensitive_positions():
    reference = "ABCDE"
    weights = np.array([0.8, 0.05, 0.05, 0.05, 0.05])
    # preserves the high-weight position, mutates a low-weight one
    preserve_sensitive = binding_affinity_proxy("AXCDE", reference, weights)
    # mutates the high-weight position, preserves the same number of low-weight ones
    mutate_sensitive = binding_affinity_proxy("XBCDE", reference, weights)
    assert preserve_sensitive > mutate_sensitive


def test_binding_affinity_proxy_excluding_masks_out_excluded_positions_entirely():
    # "AXCDE" mismatches the reference only at position 1 (X). Masking X out
    # removes that position from BOTH the weighted and unweighted terms, so
    # the remaining 4 positions all match -- weighted preservation is the
    # raw weight sum over kept matches (0.5+0.1+0.1+0.1=0.8, NOT renormalized),
    # while identity IS renormalized by len(kept) (4/4=1.0).
    reference = "ABCDE"
    weights = np.array([0.5, 0.2, 0.1, 0.1, 0.1])
    result = binding_affinity_proxy_excluding("AXCDE", reference, weights, frozenset("X"))
    assert result == pytest.approx(0.8 - 1.0)


def test_binding_affinity_proxy_excluding_matches_manual_unexcluded_proxy_when_no_residue_present():
    # if the excluded residue never appears in the sequence, excluding it
    # changes nothing -- masking removes zero positions.
    reference = "ABCDE"
    weights = np.array([0.5, 0.2, 0.1, 0.1, 0.1])
    sequence = "AXCDE"
    result = binding_affinity_proxy_excluding(sequence, reference, weights, frozenset("Z"))
    assert result == pytest.approx(binding_affinity_proxy(sequence, reference, weights))


def test_binding_affinity_proxy_excluding_rejects_all_positions_excluded():
    reference = "ABC"
    weights = np.array([0.5, 0.3, 0.2])
    with pytest.raises(ValueError):
        binding_affinity_proxy_excluding("ABC", reference, weights, frozenset("ABC"))

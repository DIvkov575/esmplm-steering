"""Fast, model-free unit tests for the new validation helpers (L60/L61).

The full L59/L60/L61 runs need ESM2-650M and are self-verifying (each
reproduces a committed result as a built-in correctness check). These tests
gate the pure-math / pure-composition pieces that must be correct for those
runs to mean anything.
"""
import numpy as np
import pytest

from plm_steering.l60_l57_orthogonalized_validation import orthogonalize_residual
from plm_steering.l61_l57_altproxy_validation import gravy, frac
from plm_steering.l63_l57_gravy_endtoend_validation import gravy_soluble


def test_orthogonalize_residual_is_orthogonal_and_renormalized():
    rng = np.random.RandomState(0)
    v57 = rng.normal(size=64)
    v55 = rng.normal(size=64)
    resid, frac_removed = orthogonalize_residual(v57, v55)
    # residual has NO component along v55
    assert abs(float(np.dot(resid, v55))) < 1e-8
    # residual is renormalized back to ||v57||
    assert np.isclose(np.linalg.norm(resid), np.linalg.norm(v57))
    # fraction removed matches the geometric identity 1 - sqrt(1 - cos^2)
    cos = np.dot(v57, v55) / (np.linalg.norm(v57) * np.linalg.norm(v55))
    assert np.isclose(frac_removed, 1.0 - np.sqrt(1.0 - cos ** 2))


def test_orthogonalize_residual_parallel_vectors_removes_everything():
    v = np.array([1.0, 2.0, 3.0, 4.0])
    resid, frac_removed = orthogonalize_residual(v, 2.5 * v)
    assert np.isclose(frac_removed, 1.0)
    assert np.allclose(resid, 0.0)


def test_orthogonalize_residual_orthogonal_inputs_unchanged():
    v57 = np.array([1.0, 0.0, 0.0])
    v55 = np.array([0.0, 5.0, 0.0])  # already orthogonal
    resid, frac_removed = orthogonalize_residual(v57, v55)
    assert np.isclose(frac_removed, 0.0)
    assert np.allclose(resid, v57)


def test_orthogonalize_residual_zero_v55_is_noop():
    v57 = np.array([1.0, -2.0, 3.0])
    resid, frac_removed = orthogonalize_residual(v57, np.zeros(3))
    assert frac_removed == 0.0
    assert np.allclose(resid, v57)


def test_gravy_matches_manual_kyte_doolittle():
    # A=1.8, K=-3.9  ->  mean = -1.05
    assert np.isclose(gravy("AK"), (1.8 - 3.9) / 2)
    # unknown chars ignored; empty -> 0.0
    assert gravy("") == 0.0


def test_frac_counts_only_listed_residues():
    assert np.isclose(frac("NGPSAA", set("NGPS")), 4 / 6)
    assert frac("", set("NGPS")) == 0.0


def test_gravy_soluble_is_negated_gravy_and_honors_exclusion():
    seq = "AKLE"
    # soluble-oriented = -mean(KD); KD: A=1.8,K=-3.9,L=3.8,E=-3.5
    assert np.isclose(gravy_soluble(seq), -np.mean([1.8, -3.9, 3.8, -3.5]))
    # excluding E and L removes those residues before averaging
    assert np.isclose(gravy_soluble(seq, frozenset("EL")), -np.mean([1.8, -3.9]))
    # excluding everything -> defined as 0.0
    assert gravy_soluble(seq, frozenset("AKLE")) == 0.0


def test_gravy_soluble_exclusion_can_flip_sign():
    # A sequence whose soluble-orientation depends entirely on E: with E it reads
    # more soluble, without E the remaining hydrophobic residues flip it negative.
    # This is the exact failure mode L63's crit3 must treat as NOT-robust.
    seq = "LLLE" * 5
    with_e = gravy_soluble(seq)
    without_e = gravy_soluble(seq, frozenset("E"))
    assert with_e > without_e  # removing hydrophilic E lowers soluble-orientation


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

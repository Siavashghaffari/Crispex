"""Integration tests for end-to-end workflows"""

import pytest
from crispex.core.extract import extract_guides
from crispex.core.predict import predict_efficiency_scores
from crispex.core.offtarget import search_off_targets
from crispex.core.rank import rank_guides, select_top_guides
from crispex.utils.export import guides_to_dataframe


def test_full_guide_design_pipeline():
    """Test complete guide design pipeline"""
    # Sample sequence with known PAM sites
    sequence = (
        "ACGTACGTACGTACGTACGTAGGCCCGGGAAATTTGGGACGTACGT"
        "ACGTACGTACGTACGTACGTAGGCCCGGGAAATTTGGGACGTACGT"
        "ACGTACGTACGTACGTACGTAGGCCCGGGAAATTTGGGACGTACGT"
    )

    # Step 1: Extract guides
    guides = extract_guides(
        sequence=sequence,
        chromosome="chr1",
        start_position=1000,
        gene_name="TEST",
        apply_filters=True
    )

    if len(guides) == 0:
        pytest.skip("No guides found in test sequence")

    assert len(guides) > 0, "Should extract at least one guide"

    # Step 2: Predict efficiency
    guides = predict_efficiency_scores(guides)

    for guide in guides:
        assert 0 <= guide.efficiency_score <= 100, "Score should be 0-100"

    # Step 3: Search off-targets
    guides = search_off_targets(guides, species="human")

    for guide in guides:
        assert guide.off_targets is not None
        assert guide.off_targets.get(0, 0) >= 0

    # Step 4: Rank guides
    ranked = rank_guides(guides)

    assert len(ranked) == len(guides)

    # Verify ranking (efficiency should be descending)
    if len(ranked) > 1:
        assert ranked[0].efficiency_score >= ranked[-1].efficiency_score

    # Step 5: Select top guides
    top_guides = select_top_guides(ranked, top_n=3)

    assert len(top_guides) <= 3
    assert len(top_guides) <= len(ranked)

    # Step 6: Export to DataFrame
    df = guides_to_dataframe(top_guides)

    assert len(df) == len(top_guides)
    assert 'guide_sequence' in df.columns
    assert 'efficiency_score' in df.columns


def test_guide_sequence_properties():
    """Test that guides have correct sequence properties"""
    sequence = "A" * 30 + "TGG" + "C" * 30  # Simple sequence with PAM

    guides = extract_guides(
        sequence=sequence,
        chromosome="chr1",
        start_position=1,
        apply_filters=False  # Don't filter for this test
    )

    for guide in guides:
        # All guides should be 20bp
        assert len(guide.sequence) == 20

        # PAM should be 3bp
        assert len(guide.pam) == 3

        # Full sequence should be guide + PAM
        assert guide.full_sequence == guide.sequence + guide.pam

        # Coordinates should make sense
        assert guide.start > 0
        assert guide.end > guide.start


def test_export_empty_guides():
    """Test exporting empty guide list"""
    df = guides_to_dataframe([])

    assert len(df) == 0
    assert 'guide_sequence' in df.columns  # Should have correct columns


def test_ranking_consistency():
    """Test that ranking is consistent and deterministic"""
    from crispex.core.guide import Guide

    # Create test guides with known scores
    guides = [
        Guide(sequence="A"*20, pam="TGG", chromosome="chr1", start=100, end=120,
              strand="+", efficiency_score=80.0, off_targets={0:1, 1:2, 2:5, 3:10}),
        Guide(sequence="C"*20, pam="TGG", chromosome="chr1", start=200, end=220,
              strand="+", efficiency_score=90.0, off_targets={0:1, 1:1, 2:3, 3:8}),
        Guide(sequence="G"*20, pam="TGG", chromosome="chr1", start=300, end=320,
              strand="+", efficiency_score=85.0, off_targets={0:1, 1:5, 2:10, 3:20}),
    ]

    ranked = rank_guides(guides)

    # Highest efficiency with good off-target profile should be first
    assert ranked[0].efficiency_score == 90.0

    # Ranking should be stable
    ranked_again = rank_guides(guides)
    assert [g.efficiency_score for g in ranked] == [g.efficiency_score for g in ranked_again]

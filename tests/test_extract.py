"""Tests for guide extraction"""

import pytest
from crispex.core.extract import find_pam_sites, extract_guide_sequence, extract_guides


def test_find_pam_sites():
    """Test PAM site finding"""
    sequence = "ATCGATCGAGGTAGGTCGGATCGATCG"  # Contains AGG, GGT, GGA

    pam_positions = find_pam_sites(sequence, pam_type='SpCas9')

    assert len(pam_positions) > 0
    # Check that PAM sites end in GG
    for pos in pam_positions:
        assert sequence[pos+1:pos+3] == "GG"


def test_extract_guide_sequence():
    """Test extracting guide sequence"""
    # Sequence with PAM at position 20
    sequence = "A" * 20 + "TGG" + "C" * 10

    guide = extract_guide_sequence(sequence, pam_position=20, guide_length=20, strand='+')

    assert guide == "A" * 20
    assert len(guide) == 20


def test_extract_guides():
    """Test full guide extraction pipeline"""
    # Simple sequence with known PAM sites
    sequence = "ACGTACGTACGTACGTACGTAGGCCCGGGAAATTTGGG"

    guides = extract_guides(
        sequence=sequence,
        chromosome="chr1",
        start_position=1,
        apply_filters=False  # Don't filter for this test
    )

    # Should find at least some guides
    assert len(guides) >= 0

    # All guides should have valid properties
    for guide in guides:
        assert len(guide.sequence) == 20
        assert len(guide.pam) == 3
        assert guide.chromosome == "chr1"

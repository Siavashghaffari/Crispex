"""Tests for Guide dataclass and operations"""

import pytest
from crispex.core.guide import Guide


def test_guide_creation():
    """Test creating a Guide object"""
    guide = Guide(
        sequence="GGAAGACTCCAGTGGTAATC",
        pam="TGG",
        chromosome="chr17",
        start=7675088,
        end=7675110,
        strand="+"
    )

    assert guide.sequence == "GGAAGACTCCAGTGGTAATC"
    assert guide.pam == "TGG"
    assert guide.full_sequence == "GGAAGACTCCAGTGGTAATCTGG"


def test_gc_content_calculation():
    """Test GC content calculation"""
    guide = Guide(
        sequence="GGGGCCCCAAAATTTT",  # 50% GC
        pam="NGG",
        chromosome="chr1",
        start=100,
        end=120,
        strand="+"
    )

    gc = guide.calculate_gc_content()
    assert gc == 50.0


def test_quality_filters():
    """Test quality filter checks"""
    # Good guide
    good_guide = Guide(
        sequence="GGAAGACTCCAGTGGTAATC",  # 50% GC, no homopolymers
        pam="TGG",
        chromosome="chr17",
        start=100,
        end=120,
        strand="+"
    )
    good_guide.calculate_gc_content()
    assert good_guide.passes_quality_filters() == True

    # Guide with polyT (should fail)
    poly_t_guide = Guide(
        sequence="GGAAGACTTTTTTGGTAATC",  # Has TTTTTT
        pam="TGG",
        chromosome="chr17",
        start=100,
        end=120,
        strand="+"
    )
    poly_t_guide.calculate_gc_content()
    assert poly_t_guide.passes_quality_filters() == False


def test_guide_to_dict():
    """Test converting guide to dictionary"""
    guide = Guide(
        sequence="GGAAGACTCCAGTGGTAATC",
        pam="TGG",
        chromosome="chr17",
        start=7675088,
        end=7675110,
        strand="+",
        efficiency_score=81.2,
        off_targets={0: 1, 1: 2, 2: 8, 3: 34},
        gc_content=50.0,
        gene_name="TP53"
    )

    guide_dict = guide.to_dict()

    assert guide_dict['guide_sequence'] == "GGAAGACTCCAGTGGTAATC"
    assert guide_dict['efficiency_score'] == 81.2
    assert guide_dict['off_targets_1mm'] == 2
    assert guide_dict['gene_name'] == "TP53"

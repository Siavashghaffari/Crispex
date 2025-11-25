"""Tests for input validation"""

import pytest
from crispex.utils.validate import (
    validate_species,
    validate_gene_symbol,
    parse_genomic_coordinates,
    validate_top_n
)
from crispex.utils.errors import InvalidSpeciesError, InvalidInputError, InvalidCoordinatesError


def test_validate_species():
    """Test species validation"""
    # Valid species
    result = validate_species("human")
    assert result['name'] == 'Homo sapiens'

    result = validate_species("mouse")
    assert result['name'] == 'Mus musculus'

    # Invalid species
    with pytest.raises(InvalidSpeciesError):
        validate_species("elephant")


def test_validate_gene_symbol():
    """Test gene symbol validation"""
    assert validate_gene_symbol("TP53") == "TP53"
    assert validate_gene_symbol("brca1") == "BRCA1"  # Should uppercase

    with pytest.raises(InvalidInputError):
        validate_gene_symbol("")


def test_parse_genomic_coordinates():
    """Test genomic coordinate parsing"""
    # Valid coordinates
    chr, start, end = parse_genomic_coordinates("chr17:7661779-7687550")
    assert chr == "chr17"
    assert start == 7661779
    assert end == 7687550

    # Without chr prefix
    chr, start, end = parse_genomic_coordinates("17:1000-2000")
    assert chr == "chr17"

    # Invalid format
    with pytest.raises(InvalidCoordinatesError):
        parse_genomic_coordinates("invalid")

    # End before start
    with pytest.raises(InvalidCoordinatesError):
        parse_genomic_coordinates("chr17:1000-500")


def test_validate_top_n():
    """Test top_n validation"""
    assert validate_top_n(5) == 5
    assert validate_top_n(1) == 1
    assert validate_top_n(100) == 100

    with pytest.raises(InvalidInputError):
        validate_top_n(0)

    with pytest.raises(InvalidInputError):
        validate_top_n(101)

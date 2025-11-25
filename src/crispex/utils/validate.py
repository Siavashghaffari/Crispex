"""Input validation utilities"""

import re
from typing import Tuple, Optional
from crispex.utils.errors import InvalidCoordinatesError, InvalidSpeciesError, InvalidInputError


SUPPORTED_SPECIES = {
    'human': {
        'name': 'Homo sapiens',
        'genome_assembly': 'GRCh38',
        'ensembl_name': 'homo_sapiens'
    },
    'mouse': {
        'name': 'Mus musculus',
        'genome_assembly': 'GRCm39',
        'ensembl_name': 'mus_musculus'
    }
}


def validate_species(species: str) -> dict:
    """Validate and normalize species name

    Args:
        species: Species identifier (e.g., 'human', 'mouse')

    Returns:
        Dictionary with species information

    Raises:
        InvalidSpeciesError: If species is not supported
    """
    species_lower = species.lower().strip()

    if species_lower not in SUPPORTED_SPECIES:
        supported = ', '.join(SUPPORTED_SPECIES.keys())
        raise InvalidSpeciesError(
            f"Species '{species}' is not supported. "
            f"Supported species: {supported}"
        )

    return SUPPORTED_SPECIES[species_lower]


def validate_gene_symbol(gene: str) -> str:
    """Validate gene symbol format

    Args:
        gene: Gene symbol (e.g., 'TP53', 'BRCA1')

    Returns:
        Normalized gene symbol (uppercase)

    Raises:
        InvalidInputError: If gene symbol is invalid
    """
    if not gene or not isinstance(gene, str):
        raise InvalidInputError("Gene symbol must be a non-empty string")

    gene = gene.strip().upper()

    # Basic validation - gene symbols should be alphanumeric with possible hyphens
    if not re.match(r'^[A-Z0-9][-A-Z0-9]*$', gene):
        raise InvalidInputError(
            f"Invalid gene symbol format: '{gene}'. "
            "Gene symbols should contain only letters, numbers, and hyphens."
        )

    return gene


def parse_genomic_coordinates(region: str) -> Tuple[str, int, int]:
    """Parse genomic coordinate string

    Args:
        region: Genomic coordinates (e.g., 'chr17:7661779-7687550')

    Returns:
        Tuple of (chromosome, start, end)

    Raises:
        InvalidCoordinatesError: If coordinates are malformed or invalid
    """
    if not region or not isinstance(region, str):
        raise InvalidCoordinatesError("Genomic region must be a non-empty string")

    # Expected format: chr:start-end or chr:start..end
    pattern = r'^([a-zA-Z0-9]+):(\d+)[-\.]\.?(\d+)$'
    match = re.match(pattern, region.strip())

    if not match:
        raise InvalidCoordinatesError(
            f"Invalid coordinate format: '{region}'. "
            "Expected format: 'chr:start-end' (e.g., 'chr17:7661779-7687550')"
        )

    chromosome, start_str, end_str = match.groups()

    # Add 'chr' prefix if not present
    if not chromosome.lower().startswith('chr'):
        chromosome = f'chr{chromosome}'

    start = int(start_str)
    end = int(end_str)

    # Validate coordinates
    if start < 1:
        raise InvalidCoordinatesError(
            f"Start coordinate must be >= 1, got {start}"
        )

    if end < start:
        raise InvalidCoordinatesError(
            f"End coordinate ({end}) must be >= start coordinate ({start})"
        )

    if end - start > 10_000_000:  # 10 Mb limit
        raise InvalidCoordinatesError(
            f"Region too large: {end - start:,} bp. "
            "Maximum region size is 10 Mb for guide design."
        )

    return chromosome, start, end


def validate_top_n(top_n: int) -> int:
    """Validate top_n parameter

    Args:
        top_n: Number of top guides to return

    Returns:
        Validated top_n value

    Raises:
        InvalidInputError: If top_n is invalid
    """
    if not isinstance(top_n, int):
        raise InvalidInputError(f"top_n must be an integer, got {type(top_n)}")

    if top_n < 1:
        raise InvalidInputError(f"top_n must be >= 1, got {top_n}")

    if top_n > 100:
        raise InvalidInputError(
            f"top_n must be <= 100, got {top_n}. "
            "For more guides, consider multiple design runs."
        )

    return top_n


def validate_design_inputs(
    gene: Optional[str] = None,
    region: Optional[str] = None,
    species: str = "human",
    top_n: int = 5
) -> dict:
    """Validate all inputs for guide design

    Args:
        gene: Gene symbol
        region: Genomic coordinates
        species: Species name
        top_n: Number of guides to return

    Returns:
        Dictionary with validated inputs

    Raises:
        InvalidInputError: If inputs are invalid
    """
    # Must specify either gene or region, but not both
    if gene is None and region is None:
        raise InvalidInputError(
            "Must specify either --gene or --region"
        )

    if gene is not None and region is not None:
        raise InvalidInputError(
            "Cannot specify both --gene and --region. Choose one."
        )

    # Validate species
    species_info = validate_species(species)

    # Validate top_n
    top_n = validate_top_n(top_n)

    # Validate gene or region
    if gene:
        gene = validate_gene_symbol(gene)
        return {
            'mode': 'gene',
            'gene': gene,
            'species': species.lower(),
            'species_info': species_info,
            'top_n': top_n
        }
    else:
        chromosome, start, end = parse_genomic_coordinates(region)
        return {
            'mode': 'region',
            'chromosome': chromosome,
            'start': start,
            'end': end,
            'species': species.lower(),
            'species_info': species_info,
            'top_n': top_n
        }

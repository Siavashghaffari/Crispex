"""Guide extraction and filtering logic"""

import re
from typing import List, Optional
from Bio.Seq import Seq
from crispex.core.guide import Guide


# PAM sequences for different Cas variants
PAM_SEQUENCES = {
    'SpCas9': 'GG',  # NGG pattern (N = any nucleotide)
    'SaCas9': 'GRRT',  # NNGRRT pattern
}


def find_pam_sites(sequence: str, pam_type: str = 'SpCas9') -> List[int]:
    """Find all PAM sites in a sequence

    Args:
        sequence: DNA sequence to search
        pam_type: Cas9 variant (SpCas9, SaCas9)

    Returns:
        List of PAM positions (0-based, position of first PAM nucleotide)
    """
    sequence = sequence.upper()
    pam_pattern = PAM_SEQUENCES.get(pam_type, 'GG')

    pam_positions = []

    # For SpCas9: find NGG (N = any nucleotide)
    if pam_type == 'SpCas9':
        # Pattern: any nucleotide followed by GG
        pattern = r'[ATCG]GG'
        for match in re.finditer(pattern, sequence):
            pam_positions.append(match.start())

    return pam_positions


def extract_guide_sequence(
    sequence: str,
    pam_position: int,
    guide_length: int = 20,
    strand: str = '+'
) -> Optional[str]:
    """Extract guide sequence upstream of PAM

    Args:
        sequence: Full DNA sequence
        pam_position: Position of PAM (0-based)
        guide_length: Length of guide sequence (default: 20bp)
        strand: '+' or '-' strand

    Returns:
        Guide sequence (20bp) or None if extraction fails
    """
    sequence = sequence.upper()

    if strand == '+':
        # Guide is upstream (5') of PAM
        guide_start = pam_position - guide_length
        guide_end = pam_position

        if guide_start < 0:
            return None  # Not enough sequence upstream

        guide_seq = sequence[guide_start:guide_end]

    else:  # strand == '-'
        # For minus strand, take downstream and reverse complement
        guide_start = pam_position + 3  # After PAM (NGG = 3bp)
        guide_end = guide_start + guide_length

        if guide_end > len(sequence):
            return None  # Not enough sequence downstream

        guide_seq = sequence[guide_start:guide_end]
        # Reverse complement
        guide_seq = str(Seq(guide_seq).reverse_complement())

    if len(guide_seq) != guide_length:
        return None

    # Check for valid nucleotides only
    if not all(base in 'ATCG' for base in guide_seq):
        return None

    return guide_seq


def extract_guides(
    sequence: str,
    chromosome: str = "chr1",
    start_position: int = 1,
    gene_name: Optional[str] = None,
    pam_type: str = 'SpCas9',
    guide_length: int = 20,
    apply_filters: bool = True
) -> List[Guide]:
    """Extract all possible guide RNAs from a sequence

    Args:
        sequence: DNA sequence to extract guides from
        chromosome: Chromosome name
        start_position: Genomic start coordinate of sequence (1-based)
        gene_name: Gene symbol (optional)
        pam_type: Cas9 variant
        guide_length: Guide length in bp
        apply_filters: Whether to apply quality filters

    Returns:
        List of Guide objects
    """
    guides = []
    sequence = sequence.upper()

    # Find PAM sites on both strands
    # Plus strand
    pam_positions = find_pam_sites(sequence, pam_type)

    for pam_pos in pam_positions:
        # Extract guide sequence
        guide_seq = extract_guide_sequence(
            sequence, pam_pos, guide_length, strand='+'
        )

        if guide_seq is None:
            continue

        # Get PAM sequence
        pam_seq = sequence[pam_pos:pam_pos+3]  # NGG

        # Calculate genomic coordinates
        guide_start = start_position + pam_pos - guide_length
        guide_end = start_position + pam_pos - 1

        # Create Guide object
        guide = Guide(
            sequence=guide_seq,
            pam=pam_seq,
            chromosome=chromosome,
            start=guide_start,
            end=guide_end,
            strand='+'
        )

        # Calculate GC content
        guide.calculate_gc_content()

        # Add gene name if provided
        if gene_name:
            guide.gene_name = gene_name

        # Apply quality filters
        if apply_filters:
            if guide.passes_quality_filters():
                guides.append(guide)
        else:
            guides.append(guide)

    # Minus strand - search reverse complement
    rev_comp_seq = str(Seq(sequence).reverse_complement())
    pam_positions_rev = find_pam_sites(rev_comp_seq, pam_type)

    for pam_pos in pam_positions_rev:
        # Position in original sequence
        original_pam_pos = len(sequence) - pam_pos - 3

        # Extract guide sequence (from reverse complement perspective)
        guide_seq = extract_guide_sequence(
            rev_comp_seq, pam_pos, guide_length, strand='+'
        )

        if guide_seq is None:
            continue

        # PAM sequence from reverse complement
        pam_seq = rev_comp_seq[pam_pos:pam_pos+3]

        # Calculate genomic coordinates (on minus strand)
        guide_start = start_position + original_pam_pos + 4  # After PAM
        guide_end = start_position + original_pam_pos + 3 + guide_length

        # Create Guide object
        guide = Guide(
            sequence=guide_seq,
            pam=pam_seq,
            chromosome=chromosome,
            start=guide_start,
            end=guide_end,
            strand='-'
        )

        # Calculate GC content
        guide.calculate_gc_content()

        # Add gene name
        if gene_name:
            guide.gene_name = gene_name

        # Apply quality filters
        if apply_filters:
            if guide.passes_quality_filters():
                guides.append(guide)
        else:
            guides.append(guide)

    return guides


def filter_guides_by_quality(
    guides: List[Guide],
    min_gc: float = 40.0,
    max_gc: float = 60.0,
    max_homopolymer: int = 4
) -> List[Guide]:
    """Filter guides by quality criteria

    Args:
        guides: List of Guide objects
        min_gc: Minimum GC content percentage
        max_gc: Maximum GC content percentage
        max_homopolymer: Maximum homopolymer run length

    Returns:
        Filtered list of guides
    """
    return [
        guide for guide in guides
        if guide.passes_quality_filters(min_gc, max_gc, max_homopolymer)
    ]

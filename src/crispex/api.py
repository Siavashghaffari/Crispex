"""Main API for Crispex guide design"""

import pandas as pd
from typing import Optional
from crispex.utils.validate import validate_design_inputs
from crispex.utils.export import guides_to_dataframe, save_to_csv, format_output_filename
from crispex.core.fetch import fetch_gene_sequence
from crispex.core.extract import extract_guides
from crispex.core.predict import predict_efficiency_scores
from crispex.core.offtarget import search_off_targets
from crispex.core.rank import rank_guides, select_top_guides


def design_guides(
    gene: Optional[str] = None,
    region: Optional[str] = None,
    species: str = "human",
    top_n: int = 5,
    output: Optional[str] = None,
) -> pd.DataFrame:
    """Design sgRNA guides for a gene or genomic region

    This is the main API function that coordinates the entire guide design workflow:
    1. Validate inputs
    2. Fetch gene/region sequence
    3. Extract candidate guides
    4. Predict on-target efficiency
    5. Search for off-targets
    6. Rank and select top guides
    7. Export results

    Args:
        gene: Gene symbol (e.g., "TP53", "BRCA1")
        region: Genomic coordinates (e.g., "chr17:7661779-7687550")
        species: Species name ("human" or "mouse")
        top_n: Number of top guides to return (1-100)
        output: Output CSV file path (optional, auto-generated if not provided)

    Returns:
        pandas DataFrame with ranked guides

    Raises:
        InvalidInputError: If inputs are invalid
        GeneNotFoundError: If gene not found
        APIError: If Ensembl API fails
        GenomeNotInstalledError: If genome not available

    Examples:
        >>> # Design guides for a gene
        >>> guides = design_guides(gene="TP53", species="human", top_n=5)
        >>> print(guides.head())

        >>> # Design guides for a genomic region
        >>> guides = design_guides(
        ...     region="chr17:7675000-7676000",
        ...     species="human",
        ...     top_n=10,
        ...     output="my_guides.csv"
        ... )
    """
    # Step 1: Validate inputs
    validated = validate_design_inputs(
        gene=gene,
        region=region,
        species=species,
        top_n=top_n
    )

    mode = validated['mode']
    species = validated['species']
    top_n = validated['top_n']

    # Step 2: Fetch sequence
    if mode == 'gene':
        gene_symbol = validated['gene']

        # Fetch gene information and sequence from Ensembl
        gene_data = fetch_gene_sequence(gene_symbol, species)

        sequence = gene_data['sequence']
        chromosome = gene_data['chromosome']
        start_position = gene_data['start']
        gene_name = gene_data['gene_symbol']

    else:  # mode == 'region'
        chromosome = validated['chromosome']
        start_coord = validated['start']
        end_coord = validated['end']

        # For region mode, we'd need to fetch sequence from genome or Ensembl
        # For MVP, we'll use Ensembl sequence API
        from crispex.core.fetch import EnsemblFetcher

        fetcher = EnsemblFetcher(species=species)
        # Convert to Ensembl format (no 'chr' prefix)
        chr_name = chromosome.replace('chr', '')
        region_str = f"{chr_name}:{start_coord}..{end_coord}"

        sequence = fetcher.get_sequence(region_str)
        start_position = start_coord
        gene_name = None

    # Step 3: Extract candidate guides
    guides = extract_guides(
        sequence=sequence,
        chromosome=chromosome,
        start_position=start_position,
        gene_name=gene_name,
        pam_type='SpCas9',
        guide_length=20,
        apply_filters=True
    )

    if not guides:
        # Return empty DataFrame if no guides found
        return guides_to_dataframe([])

    # Step 4: Predict on-target efficiency
    guides = predict_efficiency_scores(guides)

    # Step 5: Search for off-targets
    guides = search_off_targets(guides, species=species)

    # Step 6: Rank guides
    guides = rank_guides(guides)

    # Step 7: Select top N
    top_guides = select_top_guides(guides, top_n=top_n)

    # Step 8: Convert to DataFrame
    df = guides_to_dataframe(top_guides)

    # Step 9: Save to CSV if output path specified
    if output:
        save_to_csv(top_guides, output)
    elif mode == 'gene':
        # Auto-generate filename for gene mode
        auto_filename = format_output_filename(gene_name=gene_name)
        save_to_csv(top_guides, auto_filename)

    return df

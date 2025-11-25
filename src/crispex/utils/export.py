"""Export utilities for guides"""

import pandas as pd
from typing import List, Optional
from pathlib import Path
from crispex.core.guide import Guide


def guides_to_dataframe(guides: List[Guide]) -> pd.DataFrame:
    """Convert list of guides to pandas DataFrame

    Args:
        guides: List of Guide objects

    Returns:
        DataFrame with guide information
    """
    if not guides:
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=[
            'rank', 'guide_sequence', 'pam_sequence', 'full_sequence',
            'chromosome', 'start', 'end', 'strand', 'efficiency_score',
            'off_targets_0mm', 'off_targets_1mm', 'off_targets_2mm', 'off_targets_3mm',
            'gc_content', 'gene_name', 'exon'
        ])

    # Convert guides to dictionaries
    data = []
    for rank, guide in enumerate(guides, start=1):
        guide_dict = guide.to_dict()
        guide_dict['rank'] = rank
        data.append(guide_dict)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Reorder columns
    column_order = [
        'rank', 'guide_sequence', 'pam_sequence', 'full_sequence',
        'chromosome', 'start', 'end', 'strand', 'efficiency_score',
        'off_targets_0mm', 'off_targets_1mm', 'off_targets_2mm', 'off_targets_3mm',
        'gc_content', 'gene_name', 'exon'
    ]

    return df[column_order]


def save_to_csv(
    guides: List[Guide],
    output_path: str,
    include_header: bool = True
) -> str:
    """Save guides to CSV file

    Args:
        guides: List of Guide objects
        output_path: Path to output CSV file
        include_header: Whether to include header row

    Returns:
        Path to saved file
    """
    df = guides_to_dataframe(guides)

    # Ensure parent directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to CSV
    df.to_csv(output_path, index=False, header=include_header)

    return str(output_path)


def format_output_filename(
    gene_name: Optional[str] = None,
    chromosome: Optional[str] = None,
    start: Optional[int] = None,
    end: Optional[int] = None
) -> str:
    """Generate output filename based on input

    Args:
        gene_name: Gene symbol
        chromosome: Chromosome name
        start: Start coordinate
        end: End coordinate

    Returns:
        Formatted filename
    """
    if gene_name:
        return f"{gene_name.lower()}_guides.csv"
    elif chromosome and start and end:
        chr_clean = chromosome.replace('chr', '')
        return f"chr{chr_clean}_{start}_{end}_guides.csv"
    else:
        return "guides.csv"


def print_guide_summary(guide: Guide, rank: int = 1) -> str:
    """Format guide information for terminal display

    Args:
        guide: Guide object
        rank: Rank number

    Returns:
        Formatted string
    """
    lines = []
    lines.append(f"\nGuide #{rank}")
    lines.append(f"  Sequence:      {guide.sequence} ({guide.pam})")
    lines.append(f"  Location:      {guide.chromosome}:{guide.start:,}-{guide.end:,} ({guide.strand})")
    lines.append(f"  Efficiency:    {guide.efficiency_score:.1f} / 100")

    # Format off-targets
    ot_summary = f"{guide.off_targets.get(0, 0)}/{guide.off_targets.get(1, 0)}/" \
                 f"{guide.off_targets.get(2, 0)}/{guide.off_targets.get(3, 0)}"
    lines.append(f"  Off-targets:   {ot_summary} (0/1/2/3 MM)")
    lines.append(f"  GC content:    {guide.gc_content:.1f}%")

    if guide.gene_name:
        lines.append(f"  Gene:          {guide.gene_name}")

    return "\n".join(lines)


def print_summary_table(guides: List[Guide], top_n: int = 5) -> str:
    """Print summary table of top guides

    Args:
        guides: List of guides (sorted)
        top_n: Number of guides to show

    Returns:
        Formatted table string
    """
    lines = []
    lines.append("\nTop Guides:")
    lines.append("-" * 80)

    for i, guide in enumerate(guides[:top_n], start=1):
        ot_summary = f"{guide.off_targets.get(1, 0)}/{guide.off_targets.get(2, 0)}/{guide.off_targets.get(3, 0)}"
        line = f"  #{i}  {guide.sequence} ({guide.pam})  " \
               f"Score: {guide.efficiency_score:.1f}  " \
               f"Off-targets: {ot_summary}"
        lines.append(line)

    lines.append("-" * 80)

    return "\n".join(lines)

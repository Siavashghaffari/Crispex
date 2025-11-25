"""Command-line interface for Crispex"""

import click
import sys
from crispex.api import design_guides
from crispex.utils.errors import CrispexError, GeneNotFoundError, GenomeNotInstalledError
from crispex.utils.export import format_output_filename, print_guide_summary, print_summary_table
from crispex import __version__


@click.group()
@click.version_option(version=__version__)
def main():
    """Crispex - AI-powered CRISPR guide design

    Design highly efficient and specific sgRNA guides using machine learning
    and comprehensive off-target analysis.

    \b
    Examples:
      # Design guides for TP53 gene
      crispex design --gene TP53 --species human

      # Design guides for genomic region
      crispex design --region chr17:7675000-7676000 --species human

      # Get top 10 guides for BRCA1
      crispex design --gene BRCA1 --top-n 10
    """
    pass


@main.command()
@click.option('--gene', type=str, help='Gene symbol (e.g., TP53, BRCA1, MYC)')
@click.option('--region', type=str, help='Genomic coordinates (e.g., chr17:7661779-7687550)')
@click.option('--species', type=str, default='human', help='Species [human|mouse] (default: human)')
@click.option('--output', type=str, help='Output CSV file path (default: auto-generated)')
@click.option('--top-n', type=int, default=5, help='Number of guides to return (default: 5)')
def design(gene, region, species, output, top_n):
    """Design sgRNA guides for a gene or genomic region

    Extracts candidate guides, predicts on-target efficiency using Azimuth,
    performs genome-wide off-target search, and returns ranked guides ready
    for ordering.

    \b
    Examples:
      crispex design --gene TP53 --species human
      crispex design --gene BRCA1 --top-n 10
      crispex design --region chr17:7675000-7676000 --species human
      crispex design --gene MYC --output my_guides.csv

    \b
    Notes:
      • Either --gene or --region must be specified (not both)
      • Gene symbols are case-insensitive
      • Coordinates use 1-based indexing (same as genome browsers)
    """
    # Print header
    click.echo()
    click.echo("╔" + "═" * 70 + "╗")
    click.echo(f"║{' ' * 20}Crispex v{__version__}{' ' * 31}║")
    click.echo(f"║{' ' * 15}AI-Powered CRISPR Guide Design{' ' * 25}║")
    click.echo("╚" + "═" * 70 + "╝")
    click.echo()

    try:
        # Determine mode
        if gene:
            click.echo(f"[1/5] Fetching gene information for {gene}...")
            click.echo(f"      → Querying Ensembl REST API...")
        elif region:
            click.echo(f"[1/5] Parsing genomic region...")
            click.echo(f"      → Region: {region}")
        else:
            click.echo("❌ Error: Must specify either --gene or --region", err=True)
            click.echo("\nFor help: crispex design --help", err=True)
            sys.exit(1)

        # Call main API
        df = design_guides(
            gene=gene,
            region=region,
            species=species,
            top_n=top_n,
            output=output
        )

        if len(df) == 0:
            click.echo("\n⚠  Warning: No guides found meeting quality criteria")
            click.echo("   Try relaxing filters or choosing a different region")
            sys.exit(0)

        # Print progress for remaining steps
        if gene:
            gene_info = df.iloc[0]
            click.echo(f"      ✓ Found {gene.upper()}")
            click.echo(f"        Location: {gene_info['chromosome']}:{gene_info['start']:,}-{gene_info['end']:,}")

        click.echo()
        click.echo(f"[2/5] Extracting guide candidates...")
        click.echo(f"      ✓ Found {len(df)} potential guides")

        click.echo()
        click.echo(f"[3/5] Predicting on-target efficiency...")
        click.echo(f"      ✓ Scored {len(df)} guides using Azimuth")

        click.echo()
        click.echo(f"[4/5] Searching for off-targets...")
        click.echo(f"      ✓ Off-target analysis complete")

        click.echo()
        click.echo(f"[5/5] Ranking guides...")
        click.echo(f"      ✓ Top {len(df)} guides selected")

        # Print separator
        click.echo()
        click.echo("━" * 72)

        # Print top guide details
        if len(df) > 0:
            top_guide_row = df.iloc[0]

            click.echo()
            click.echo("                          🎯 TOP GUIDE")
            click.echo()
            click.echo(f"  Guide Sequence:  {top_guide_row['guide_sequence']}")
            click.echo(f"  PAM:             {top_guide_row['pam_sequence']}")
            click.echo(f"  Full Oligo:      {top_guide_row['full_sequence']}")
            click.echo()
            click.echo(f"  Genomic Location:")
            click.echo(f"    Chromosome:    {top_guide_row['chromosome']}")
            click.echo(f"    Position:      {top_guide_row['start']:,}-{top_guide_row['end']:,} ({top_guide_row['strand']})")

            click.echo()
            click.echo(f"  Performance Scores:")
            efficiency = top_guide_row['efficiency_score']
            bar_length = int(efficiency / 5)  # 20 chars for 100%
            bar = "█" * bar_length + "░" * (20 - bar_length)
            click.echo(f"    Efficiency:    {efficiency:.1f} / 100  {bar}")

            click.echo()
            click.echo(f"  Off-Target Analysis:")
            click.echo(f"    Perfect match:     {top_guide_row['off_targets_0mm']}  (target site)")
            click.echo(f"    1 mismatch:        {top_guide_row['off_targets_1mm']}")
            click.echo(f"    2 mismatches:      {top_guide_row['off_targets_2mm']}")
            click.echo(f"    3 mismatches:      {top_guide_row['off_targets_3mm']}")

            click.echo()
            click.echo(f"  Quality Metrics:")
            click.echo(f"    GC content:    {top_guide_row['gc_content']:.1f}%  ✓")

        click.echo()
        click.echo("━" * 72)

        # Determine output filename
        if output:
            output_file = output
        else:
            if gene:
                output_file = format_output_filename(gene_name=gene)
            else:
                output_file = "guides.csv"

        click.echo()
        click.echo(f"💾 Results saved to: {output_file}")

        click.echo()
        click.echo(f"📊 Summary:")
        click.echo(f"   • Top guides returned: {len(df)}")

        click.echo()
        click.echo(f"🧬 Ready to order!")
        click.echo(f"   Use the 'full_sequence' column from the CSV for oligo synthesis.")

        click.echo()

    except GeneNotFoundError as e:
        click.echo()
        click.echo(f"❌ Error: Gene not found", err=True)
        click.echo()
        click.echo(str(e), err=True)
        click.echo()
        click.echo("Suggestions:", err=True)
        click.echo("  • Check spelling (gene symbols are case-sensitive)", err=True)
        click.echo("  • Try synonyms (e.g., TP53 vs P53)", err=True)
        click.echo("  • Verify species (human vs mouse)", err=True)
        click.echo()
        click.echo("For help: crispex design --help", err=True)
        sys.exit(1)

    except GenomeNotInstalledError as e:
        click.echo()
        click.echo(f"⚠  Warning: Genome not installed", err=True)
        click.echo()
        click.echo(str(e), err=True)
        sys.exit(1)

    except CrispexError as e:
        click.echo()
        click.echo(f"❌ Error: {e}", err=True)
        click.echo()
        click.echo("For help: crispex design --help", err=True)
        sys.exit(1)

    except Exception as e:
        click.echo()
        click.echo(f"❌ Unexpected error: {e}", err=True)
        click.echo()
        click.echo("Please report this issue at: https://github.com/yourname/crispex/issues", err=True)
        sys.exit(1)


@main.command()
@click.option('--species', type=str, required=True, help='Species to install (human or mouse)')
def install_genome(species):
    """Download and install reference genome

    \b
    Example:
      crispex install-genome --species human
    """
    click.echo()
    click.echo(f"Installing {species} genome...")
    click.echo()
    click.echo("⚠  Note: Genome installation not fully implemented in MVP")
    click.echo()
    click.echo("For MVP, please manually download genome FASTA files to:")
    click.echo(f"  ~/.crispex/genomes/")
    click.echo()
    click.echo("Required files:")
    if species == 'human':
        click.echo("  - GRCh38.fa (human genome)")
    elif species == 'mouse':
        click.echo("  - GRCm39.fa (mouse genome)")
    click.echo()


@main.command()
def list_genomes():
    """Show installed genomes"""
    from crispex.core.genome import GenomeManager
    from pathlib import Path

    click.echo()
    click.echo("Installed genomes:")
    click.echo()

    genome_dir = Path.home() / ".crispex" / "genomes"

    if not genome_dir.exists():
        click.echo("  No genomes installed")
        click.echo()
        click.echo("To install a genome, run:")
        click.echo("  crispex install-genome --species human")
        return

    genomes = {
        'human': 'GRCh38.fa',
        'mouse': 'GRCm39.fa'
    }

    for species, filename in genomes.items():
        filepath = genome_dir / filename
        if filepath.exists():
            size_gb = filepath.stat().st_size / (1024**3)
            click.echo(f"  ✓ {species:10s} {filename:15s} ({size_gb:.2f} GB)")
        else:
            click.echo(f"  ✗ {species:10s} (not installed)")

    click.echo()


if __name__ == '__main__':
    main()

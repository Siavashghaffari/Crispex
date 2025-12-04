# Crispex

**AI-Powered CRISPR sgRNA Design**

Crispex is a Python package for designing highly efficient and specific CRISPR single guide RNAs (sgRNAs) using machine learning and comprehensive off-target analysis.

## Features

- **Simple Interface**: Single command from gene name to ranked guides
- **ML-Powered Predictions**: On-target efficiency scoring using Azimuth algorithm
- **Off-Target Analysis**: Genome-wide off-target detection with mismatch tolerance
- **Quality Filters**: Automatic filtering by GC content, homopolymers, and sequence complexity
- **Multiple Input Modes**: Gene symbols or genomic coordinates
- **Ready-to-Order Output**: CSV export with sequences formatted for oligo synthesis

## Installation

### From Source (MVP)

```bash
cd Crispex
pip install -e .
```

### Dependencies

Crispex requires Python 3.9 or later and the following packages:
- biopython
- pandas
- numpy
- scikit-learn
- requests
- click
- pyfaidx
- tqdm

These will be automatically installed when you install Crispex.

## Quick Start

### Command Line Interface

Design guides for a gene:

```bash
crispex design --gene TP53 --species human
```

Design guides for a genomic region:

```bash
crispex design --region chr17:7675000-7676000 --species human
```

Get top 10 guides:

```bash
crispex design --gene BRCA1 --top-n 10
```

### Python API

```python
from crispex import design_guides

# Design guides for a gene
guides = design_guides(gene="TP53", species="human", top_n=5)

# View results
print(guides.head())

# Access specific guide information
top_guide = guides.iloc[0]
print(f"Best guide: {top_guide['guide_sequence']}")
print(f"Efficiency: {top_guide['efficiency_score']:.1f}")
print(f"Off-targets (1MM): {top_guide['off_targets_1mm']}")
```

## Usage Examples

### Example 1: Basic Gene Targeting

```bash
$ crispex design --gene TP53 --species human

╔══════════════════════════════════════════════════════════════════════╗
║                    Crispex v0.1.0                                    ║
║              AI-Powered CRISPR Guide Design                          ║
╚══════════════════════════════════════════════════════════════════════╝

[1/5] Fetching gene information for TP53...
      → Querying Ensembl REST API...
      ✓ Found TP53
        Location: chr17:7,661,779-7,687,550

[2/5] Extracting guide candidates...
      ✓ Found 247 potential guides

[3/5] Predicting on-target efficiency...
      ✓ Scored 247 guides using Azimuth

[4/5] Searching for off-targets...
      ✓ Off-target analysis complete

[5/5] Ranking guides...
      ✓ Top 5 guides selected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                          🎯 TOP GUIDE

  Guide Sequence:  GGAAGACTCCAGTGGTAATC
  PAM:             TGG
  Full Oligo:      GGAAGACTCCAGTGGTAATCTGG

  Genomic Location:
    Chromosome:    chr17
    Position:      7,675,088-7,675,110 (+)

  Performance Scores:
    Efficiency:    81.2 / 100  ████████████████░░░░

  Off-Target Analysis:
    Perfect match:     1  (target site)
    1 mismatch:        2
    2 mismatches:      8
    3 mismatches:      34

💾 Results saved to: tp53_guides.csv

🧬 Ready to order!
   Use the 'full_sequence' column from the CSV for oligo synthesis.
```

### Example 2: Programmatic Filtering

```python
from crispex import design_guides

# Design guides
guides = design_guides(gene="MYC", species="human", top_n=20)

# Filter for high-efficiency guides with few off-targets
high_quality = guides[
    (guides['efficiency_score'] > 70) &
    (guides['off_targets_1mm'] <= 2) &
    (guides['off_targets_2mm'] <= 5)
]

print(f"Found {len(high_quality)} high-quality guides")

# Export filtered results
high_quality.to_csv('myc_high_quality_guides.csv', index=False)
```

### Example 3: Genomic Region Targeting

```python
from crispex import design_guides

# Target specific region
guides = design_guides(
    region="chr17:7675000-7676000",
    species="human",
    top_n=5,
    output="region_guides.csv"
)

# Iterate through guides
for idx, guide in guides.iterrows():
    print(f"Guide {guide['rank']}: {guide['guide_sequence']} "
          f"(Efficiency: {guide['efficiency_score']:.1f})")
```

## Output Format

Crispex generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `rank` | Guide ranking (1 = best) |
| `guide_sequence` | 20bp guide sequence (5'→3', without PAM) |
| `pam_sequence` | PAM sequence (e.g., NGG for SpCas9) |
| `full_sequence` | Guide + PAM for ordering |
| `chromosome` | Chromosome name |
| `start` | Genomic start coordinate (1-based) |
| `end` | Genomic end coordinate (1-based, inclusive) |
| `strand` | + or - strand |
| `efficiency_score` | On-target efficiency (0-100, Azimuth) |
| `off_targets_0mm` | Perfect match count (should be 1) |
| `off_targets_1mm` | Sites with 1 mismatch |
| `off_targets_2mm` | Sites with 2 mismatches |
| `off_targets_3mm` | Sites with 3 mismatches |
| `gc_content` | GC percentage (0-100) |
| `gene_name` | Gene symbol (if applicable) |
| `exon` | Exon number (if applicable) |

## CLI Commands

### `crispex design`

Design sgRNA guides for a gene or genomic region.

**Options:**
- `--gene TEXT`: Gene symbol (e.g., TP53, BRCA1)
- `--region TEXT`: Genomic coordinates (e.g., chr17:7661779-7687550)
- `--species TEXT`: Species [human|mouse] (default: human)
- `--output PATH`: Output CSV file path (auto-generated if not specified)
- `--top-n INTEGER`: Number of guides to return (default: 5, max: 100)

**Examples:**
```bash
crispex design --gene TP53 --species human
crispex design --gene BRCA1 --top-n 10
crispex design --region chr17:7675000-7676000 --species human
crispex design --gene MYC --output my_guides.csv
```

### `crispex install-genome`

Download and install reference genome (placeholder in MVP).

```bash
crispex install-genome --species human
```

### `crispex list-genomes`

Show installed genomes.

```bash
crispex list-genomes
```

## How It Works

Crispex follows a 5-step workflow:

1. **Gene/Region Lookup**: Fetches sequence from Ensembl REST API
2. **Guide Extraction**: Scans for PAM sites (NGG for SpCas9) and extracts 20bp guides
3. **Quality Filtering**: Filters by GC content (40-60%), homopolymers, polyT runs
4. **Efficiency Prediction**: Scores guides using Azimuth algorithm (0-100)
5. **Off-Target Search**: Identifies potential off-targets with 0-3 mismatches
6. **Ranking**: Sorts by efficiency and specificity, returns top N guides

## Supported Species

- **Human**: GRCh38 assembly
- **Mouse**: GRCm39 assembly

## Quality Filters

Guides are automatically filtered by:

- **GC Content**: 40-60% (optimal for SpCas9)
- **Homopolymer Runs**: No runs of ≥4 identical bases
- **PolyT Stretches**: No TTTT sequences (causes pol III termination)

## Limitations (MVP)

This is a Minimum Viable Product with the following limitations:

- **Off-target search**: Uses heuristic estimation (production version will use FM-index/Bowtie2)
- **Efficiency model**: Simplified Azimuth implementation (production will use full gradient boosting model)
- **Genome download**: Manual genome installation required (auto-download coming soon)
- **Cas variants**: SpCas9 only (SaCas9, Cas12a support planned)
- **No SNP checking**: Variant-aware design not yet implemented
- **No chromatin analysis**: Accessibility scoring planned for future release

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

```bash
black crispex/
flake8 crispex/
```

## Troubleshooting

### Gene Not Found

If you receive a "Gene not found" error:
- Check spelling (gene symbols are case-sensitive in some databases)
- Try synonyms (e.g., TP53 vs P53)
- Use Ensembl gene ID (e.g., ENSG00000141510)
- Verify species (human vs mouse)

### No Guides Found

If no guides pass quality filters:
- Region may be too GC-rich or GC-poor
- Try a different exon or region
- Check sequence composition

### API Timeout

If Ensembl API times out:
- Check internet connection
- Try again (automatic retry logic included)
- Ensembl may be experiencing high load


## Authors

This work was developed by Siavash Ghaffari. For any questions, feedback, or additional information, please feel free to reach out. Your input is highly valued and will help improve and refine this pipeline further.



## Acknowledgments

Crispex builds upon:
- Azimuth algorithm (Doench et al. 2016)
- Ensembl genome database
- BioPython library

## Roadmap

Future features planned:
- Full Azimuth gradient boosting model integration
- Genome-wide off-target search using FM-index
- SNP-aware design with dbSNP integration
- Chromatin accessibility scoring
- SaCas9 and Cas12a support
- Batch processing for multiple genes
- Base editor and prime editor support

---

**Version**: 0.1.0 (MVP)

**Status**: Alpha - Suitable for research use, not validated for therapeutic applications

**Last Updated**: 2025-01-24

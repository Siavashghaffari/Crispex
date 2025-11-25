# Crispex - Interface Design Document

## CLI Command Structure

```
crispex
├── design                    # Main guide design command
│   ├── --gene SYMBOL        # Gene symbol (e.g., TP53, BRCA1)
│   ├── --region COORDS      # Genomic coordinates (chr:start-end)
│   ├── --species SPECIES    # human | mouse
│   ├── --output PATH        # Output CSV file path
│   └── --top-n N           # Number of guides to return (default: 5)
│
├── install-genome           # One-time genome setup
│   └── --species SPECIES    # human | mouse
│
├── list-genomes            # Show installed genomes
│
├── version                 # Show version info
│
└── --help                  # Show help message
```

---

## User Experience Flow

### Flow Diagram: Gene Name → Ranked Guides

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INPUT                                   │
│                                                                      │
│  $ crispex design --gene TP53 --species human                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STEP 1: GENE LOOKUP                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Query Ensembl REST API for TP53                            │  │
│  │ • Retrieve gene coordinates & canonical transcript           │  │
│  │ • Download exon sequences                                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  Output: chr17:7,661,779-7,687,550 (25.8 kb)                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  STEP 2: GUIDE EXTRACTION                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Scan sequence for NGG PAM sites                            │  │
│  │ • Extract 20bp upstream of each PAM                          │  │
│  │ • Apply quality filters:                                     │  │
│  │   - GC content 40-60%                                        │  │
│  │   - No homopolymer runs ≥4bp                                 │  │
│  │   - No polyT stretches (TTTT)                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  Output: 247 candidate guides                                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 3: EFFICIENCY PREDICTION                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Load Azimuth model (pre-trained)                           │  │
│  │ • Extract sequence features (30bp context)                   │  │
│  │ • Batch predict efficiency scores (0-100)                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  Output: 247 guides with scores                                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│               STEP 4: OFF-TARGET SEARCH                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Index genome (FM-index or suffix array)                    │  │
│  │ • Search for matches with 0-3 mismatches                     │  │
│  │ • Count off-targets per mismatch category                    │  │
│  │ • Flag guides with >5 high-risk off-targets                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  Output: Off-target counts per guide                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  STEP 5: RANKING & EXPORT                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Sort by efficiency score (descending)                      │  │
│  │ • Filter by off-target count (ascending)                     │  │
│  │ • Select top N guides                                        │  │
│  │ • Format as CSV with all metadata                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  Output: tp53_guides.csv                                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FINAL OUTPUT                                    │
│                                                                      │
│  • CSV file with 5 ranked guides                                    │
│  • Terminal summary with top guide preview                          │
│  • Total runtime: ~25 seconds                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Terminal Output Examples

### Example 1: Successful Guide Design

```
$ crispex design --gene TP53 --species human

╔══════════════════════════════════════════════════════════════════════╗
║                    Crispex v0.1.0                                    ║
║              AI-Powered CRISPR Guide Design                          ║
╚══════════════════════════════════════════════════════════════════════╝

[1/5] Fetching gene information for TP53...
      → Querying Ensembl REST API...
      ✓ Found TP53 (ENSG00000141510)

        Gene:       TP53 (Tumor protein p53)
        Location:   chr17:7,661,779-7,687,550
        Length:     25,771 bp
        Transcript: ENST00000269305 (canonical)
        Exons:      11

[2/5] Extracting guide candidates...
      → Scanning for NGG PAM sites...
      → Applying quality filters...
      ✓ Found 247 potential guides

[3/5] Predicting on-target efficiency...
      → Loading Azimuth model...
      → Running predictions...
      ✓ Scored 247 guides

[4/5] Searching for off-targets...
      → Indexing genome (GRCh38)...
      → Searching with up to 3 mismatches...
      ⏳ Progress: ████████████████████ 100% (247/247)
      ✓ Off-target analysis complete

[5/5] Ranking guides...
      → Sorting by efficiency and specificity...
      ✓ Top 5 guides selected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                          🎯 TOP GUIDE

  Guide Sequence:  GGAAGACTCCAGTGGTAATC
  PAM:             TGG
  Full Oligo:      GGAAGACTCCAGTGGTAATCTGG

  Genomic Location:
    Chromosome:    chr17
    Position:      7,675,088-7,675,110 (+)
    Exon:          5

  Performance Scores:
    Efficiency:    81.2 / 100  ████████████████░░░░  (Azimuth)
    Specificity:   ★★★★★ Excellent

  Off-Target Analysis:
    Perfect match:     1  (target site)
    1 mismatch:        2
    2 mismatches:      8
    3 mismatches:      34

  Quality Metrics:
    GC content:    50.0%  ✓
    Homopolymers:  None   ✓
    PolyT runs:    None   ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 Results saved to: tp53_guides.csv

📊 Summary:
   • Total candidates evaluated: 247
   • Top guides returned: 5
   • Runtime: 24.3 seconds

🧬 Ready to order!
   Use the 'full_sequence' column from the CSV for oligo synthesis.
   Remember to add cloning adapters based on your vector.

Next steps:
  1. Review full results: cat tp53_guides.csv
  2. Order top guide from IDT/Synthego
  3. Clone into your CRISPR vector (e.g., pSpCas9)
```

---

### Example 2: Using Genomic Coordinates

```
$ crispex design --region chr17:7675000-7676000 --species human --top-n 3

╔══════════════════════════════════════════════════════════════════════╗
║                    Crispex v0.1.0                                    ║
╚══════════════════════════════════════════════════════════════════════╝

[1/5] Parsing genomic region...
      ✓ Region: chr17:7,675,000-7,676,000 (1,000 bp)

[2/5] Extracting guide candidates...
      ✓ Found 18 potential guides

[3/5] Predicting on-target efficiency...
      ✓ Scored 18 guides

[4/5] Searching for off-targets...
      ✓ Off-target analysis complete

[5/5] Ranking guides...
      ✓ Top 3 guides selected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Top 3 Guides:

  #1  GGAAGACTCCAGTGGTAATC (TGG)  Score: 81.2  Off-targets: 2/8/34
  #2  TCAACAAGATGTTTTGCCAA (CTG)  Score: 76.8  Off-targets: 0/4/22
  #3  AGGGCCTCATTCAGCTCTCG (GGG)  Score: 74.1  Off-targets: 1/6/28

💾 Results saved to: chr17_7675000_7676000_guides.csv
⏱  Runtime: 8.7 seconds
```

---

### Example 3: First-Time Genome Installation

```
$ crispex design --gene BRCA1 --species human

╔══════════════════════════════════════════════════════════════════════╗
║                    Crispex v0.1.0                                    ║
╚══════════════════════════════════════════════════════════════════════╝

⚠  Human genome (GRCh38) not found locally.

Would you like to download and install it now? (3.2 GB) [Y/n]: y

[Installing GRCh38 Genome]
  → Downloading from Ensembl...
    ⏳ Progress: ████████████████░░░░ 80% (2.6 GB / 3.2 GB)

    Estimated time remaining: 2m 15s
    Download speed: 12.4 MB/s
```

---

### Example 4: Error Handling

```
$ crispex design --gene FAKEGENE --species human

╔══════════════════════════════════════════════════════════════════════╗
║                    Crispex v0.1.0                                    ║
╚══════════════════════════════════════════════════════════════════════╝

[1/5] Fetching gene information for FAKEGENE...
      → Querying Ensembl REST API...

❌ Error: Gene not found

Gene 'FAKEGENE' could not be found in the Ensembl database (human, GRCh38).

Suggestions:
  • Check spelling (gene symbols are case-sensitive)
  • Try synonyms (e.g., TP53 vs P53)
  • Use Ensembl gene ID (e.g., ENSG00000141510)
  • Verify species (human vs mouse)

Example valid genes: TP53, BRCA1, KRAS, MYC, EGFR

For help: crispex --help
```

---

## CSV Output Format

### File: `tp53_guides.csv`

```
rank,guide_sequence,pam_sequence,full_sequence,chromosome,start,end,strand,efficiency_score,off_targets_0mm,off_targets_1mm,off_targets_2mm,off_targets_3mm,gc_content,gene_name,exon
1,GGAAGACTCCAGTGGTAATC,TGG,GGAAGACTCCAGTGGTAATCTGG,chr17,7675088,7675110,+,81.2,1,2,8,34,50.0,TP53,5
2,TCAACAAGATGTTTTGCCAA,CTG,TCAACAAGATGTTTTGCCAACTG,chr17,7675234,7675256,-,76.8,1,0,4,22,40.0,TP53,5
3,AGGGCCTCATTCAGCTCTCG,GGG,AGGGCCTCATTCAGCTCTCGGGG,chr17,7676154,7676176,+,74.1,1,1,6,28,60.0,TP53,5
4,CTGCCCCCAGGGAGCACTAA,GGG,CTGCCCCCAGGGAGCACTAAGGG,chr17,7674230,7674252,-,72.5,1,3,11,41,60.0,TP53,5
5,GAGGCCTCATCTTGGGCCTG,TGG,GAGGCCTCATCTTGGGCCTGTGG,chr17,7673890,7673912,+,69.3,1,2,9,38,65.0,TP53,4
```

### Column Descriptions

```
┌─────────────────────┬──────────┬────────────────────────────────────────┐
│ Column              │ Type     │ Description                            │
├─────────────────────┼──────────┼────────────────────────────────────────┤
│ rank                │ int      │ Guide ranking (1 = best)               │
│ guide_sequence      │ string   │ 20bp guide sequence (5'→3')            │
│ pam_sequence        │ string   │ PAM sequence (NGG)                     │
│ full_sequence       │ string   │ Guide + PAM for ordering               │
│ chromosome          │ string   │ Chromosome (e.g., chr17)               │
│ start               │ int      │ Genomic start coordinate               │
│ end                 │ int      │ Genomic end coordinate                 │
│ strand              │ char     │ + or - strand                          │
│ efficiency_score    │ float    │ Azimuth score (0-100)                  │
│ off_targets_0mm     │ int      │ Perfect matches (should be 1)          │
│ off_targets_1mm     │ int      │ Sites with 1 mismatch                  │
│ off_targets_2mm     │ int      │ Sites with 2 mismatches                │
│ off_targets_3mm     │ int      │ Sites with 3 mismatches                │
│ gc_content          │ float    │ GC percentage (0-100)                  │
│ gene_name           │ string   │ Gene symbol                            │
│ exon                │ int      │ Exon number                            │
└─────────────────────┴──────────┴────────────────────────────────────────┘
```

---

## Python API Interface

### Basic Usage

```python
from crispex import design_guides

# Simple gene-based design
guides = design_guides(gene="TP53", species="human")

# guides is a pandas DataFrame
print(guides.head())
```

**Output:**
```
   rank          guide_sequence pam_sequence           full_sequence chromosome  ...
0     1  GGAAGACTCCAGTGGTAATC          TGG  GGAAGACTCCAGTGGTAATCTGG      chr17  ...
1     2  TCAACAAGATGTTTTGCCAA          CTG  TCAACAAGATGTTTTGCCAACTG      chr17  ...
2     3  AGGGCCTCATTCAGCTCTCG          GGG  AGGGCCTCATTCAGCTCTCGGGG      chr17  ...
```

---

### Advanced API Examples

#### Example 1: Custom Output Path

```python
from crispex import design_guides

guides = design_guides(
    gene="BRCA1",
    species="human",
    top_n=10,
    output="my_brca1_guides.csv"
)

# Access top guide
top_guide = guides.iloc[0]
print(f"Best guide: {top_guide['guide_sequence']}")
print(f"Efficiency: {top_guide['efficiency_score']:.1f}")
```

**Output:**
```
Best guide: GGAATCCCGGTACTGCTCAG
Efficiency: 84.3
```

---

#### Example 2: Programmatic Analysis

```python
from crispex import design_guides
import pandas as pd

# Design guides
guides = design_guides(gene="MYC", species="human", top_n=20)

# Filter high-efficiency guides with few off-targets
high_quality = guides[
    (guides['efficiency_score'] > 70) &
    (guides['off_targets_1mm'] <= 2) &
    (guides['off_targets_2mm'] <= 5)
]

print(f"Found {len(high_quality)} high-quality guides")

# Sort by efficiency
best = high_quality.sort_values('efficiency_score', ascending=False)
print(best[['guide_sequence', 'efficiency_score', 'off_targets_1mm']])
```

---

#### Example 3: Batch Processing (Future)

```python
# Note: Not in MVP, but future API design
from crispex import design_guides_batch

genes = ["TP53", "BRCA1", "KRAS", "MYC"]
results = design_guides_batch(genes=genes, species="human", top_n=5)

# results is a dict: {gene: DataFrame}
for gene, guides in results.items():
    print(f"\n{gene}: Top guide score = {guides.iloc[0]['efficiency_score']}")
```

---

#### Example 4: Genomic Coordinates

```python
from crispex import design_guides

# Target specific region
guides = design_guides(
    region="chr17:7675000-7676000",
    species="human",
    top_n=5
)

# Iterate over guides
for idx, guide in guides.iterrows():
    print(f"Guide {guide['rank']}: {guide['guide_sequence']} "
          f"(Score: {guide['efficiency_score']:.1f})")
```

**Output:**
```
Guide 1: GGAAGACTCCAGTGGTAATC (Score: 81.2)
Guide 2: TCAACAAGATGTTTTGCCAA (Score: 76.8)
Guide 3: AGGGCCTCATTCAGCTCTCG (Score: 74.1)
Guide 4: CTGCCCCCAGGGAGCACTAA (Score: 72.5)
Guide 5: GAGGCCTCATCTTGGGCCTG (Score: 69.3)
```

---

#### Example 5: Error Handling

```python
from crispex import design_guides, CrispexError

try:
    guides = design_guides(gene="INVALID_GENE", species="human")
except CrispexError as e:
    print(f"Error: {e}")
    # Handle error gracefully
```

---

## Package Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                              │
├──────────────────────────────┬───────────────────────────────────────┤
│                              │                                       │
│     CLI (Click)              │       Python API                      │
│                              │                                       │
│  $ crispex design \          │   from crispex import design_guides   │
│      --gene TP53             │   guides = design_guides(...)         │
│                              │                                       │
└──────────────┬───────────────┴──────────────┬────────────────────────┘
               │                              │
               └──────────────┬───────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────────┐
│                        CORE ENGINE                                   │
│                                                                      │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│  │  Input Parser  │  │ Guide Extractor│  │   ML Predictor │        │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘        │
│           │                   │                   │                 │
│           ▼                   ▼                   ▼                 │
│  ┌────────────────────────────────────────────────────────┐        │
│  │              Genome Manager & Indexer                  │        │
│  └────────────────────────┬───────────────────────────────┘        │
│                           │                                         │
│  ┌────────────────┐  ┌────▼───────────┐  ┌────────────────┐        │
│  │ Off-Target     │  │    Ranker      │  │    Exporter    │        │
│  │ Searcher       │  │                │  │                │        │
│  └────────────────┘  └────────────────┘  └────────────────┘        │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                       DATA LAYER                                     │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Reference   │  │  ML Models   │  │  API Cache   │              │
│  │  Genomes     │  │              │  │              │              │
│  │  (FASTA)     │  │ azimuth.pkl  │  │ (Ensembl)    │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                      │
│  Storage: ~/.crispex/                                                │
│  ├── genomes/                                                        │
│  │   ├── human_grch38.fa                                            │
│  │   └── mouse_grcm39.fa                                            │
│  ├── models/                                                         │
│  │   └── azimuth_v2.pkl                                             │
│  └── cache/                                                          │
│      └── ensembl_cache.db                                           │
└──────────────────────────────────────────────────────────────────────┘
```

---

### Module Structure

```
crispex/
│
├── __init__.py                 # Package entry point
│   └── Exports: design_guides(), __version__
│
├── cli.py                      # Click CLI implementation
│   ├── design()                # Main design command
│   ├── install_genome()        # Genome installation
│   └── list_genomes()          # List available genomes
│
├── core/
│   ├── __init__.py
│   ├── extract.py              # Guide extraction logic
│   │   ├── find_pam_sites()
│   │   ├── extract_guides()
│   │   └── filter_quality()
│   │
│   ├── predict.py              # ML prediction
│   │   ├── load_azimuth_model()
│   │   ├── extract_features()
│   │   └── predict_efficiency()
│   │
│   ├── offtarget.py            # Off-target search
│   │   ├── index_genome()
│   │   ├── search_mismatches()
│   │   └── count_offtargets()
│   │
│   ├── rank.py                 # Ranking algorithm
│   │   ├── score_guides()
│   │   └── select_top_n()
│   │
│   ├── genome.py               # Genome management
│   │   ├── download_genome()
│   │   ├── index_fasta()
│   │   └── get_sequence()
│   │
│   └── fetch.py                # External API calls
│       ├── fetch_gene_info()   # Ensembl REST API
│       ├── get_transcript()
│       └── cache_response()
│
├── utils/
│   ├── __init__.py
│   ├── export.py               # CSV/JSON export
│   │   ├── to_csv()
│   │   └── to_dataframe()
│   │
│   ├── validate.py             # Input validation
│   │   ├── validate_gene()
│   │   ├── validate_coords()
│   │   └── validate_species()
│   │
│   └── errors.py               # Custom exceptions
│       ├── CrispexError
│       ├── GeneNotFoundError
│       └── GenomeNotInstalledError
│
├── data/
│   └── models/
│       └── azimuth_v2.pkl      # Pre-trained model
│
└── tests/
    ├── test_extract.py
    ├── test_predict.py
    ├── test_offtarget.py
    └── test_integration.py
```

---

### Data Flow Diagram

```
┌─────────┐
│  User   │
└────┬────┘
     │
     │  Input: gene="TP53", species="human"
     ▼
┌──────────────────┐
│  design_guides() │  ◄── Main API function
└────┬─────────────┘
     │
     │  1. Validate input
     ▼
┌──────────────────┐
│  fetch.py        │  ◄── Query Ensembl for gene info
│  fetch_gene_info │
└────┬─────────────┘
     │
     │  Returns: chr17:7661779-7687550
     ▼
┌──────────────────┐
│  genome.py       │  ◄── Load genome sequence
│  get_sequence()  │
└────┬─────────────┘
     │
     │  Returns: ATCG...GCTA (gene sequence)
     ▼
┌──────────────────┐
│  extract.py      │  ◄── Find PAMs & extract guides
│  extract_guides()│
└────┬─────────────┘
     │
     │  Returns: List[Guide] (247 candidates)
     ▼
┌──────────────────┐
│  predict.py      │  ◄── Run Azimuth model
│  predict_eff()   │
└────┬─────────────┘
     │
     │  Returns: List[Guide + scores]
     ▼
┌──────────────────┐
│  offtarget.py    │  ◄── Search genome for off-targets
│  search_mism()   │
└────┬─────────────┘
     │
     │  Returns: List[Guide + OT counts]
     ▼
┌──────────────────┐
│  rank.py         │  ◄── Sort and select top N
│  select_top_n()  │
└────┬─────────────┘
     │
     │  Returns: Top 5 guides
     ▼
┌──────────────────┐
│  export.py       │  ◄── Format as DataFrame/CSV
│  to_dataframe()  │
└────┬─────────────┘
     │
     │  Returns: pandas DataFrame
     ▼
┌──────────────────┐
│  User receives   │
│  ranked guides   │
└──────────────────┘
```

---

### Class/Object Design (Simplified)

```python
# Core data structure
@dataclass
class Guide:
    """Represents a single sgRNA candidate"""
    sequence: str              # 20bp guide sequence
    pam: str                   # PAM sequence (NGG)
    chromosome: str            # e.g., "chr17"
    start: int                 # Genomic start
    end: int                   # Genomic end
    strand: str                # "+" or "-"
    efficiency_score: float    # 0-100 (Azimuth)
    off_targets: Dict[int, int]  # {0: 1, 1: 2, 2: 8, 3: 34}
    gc_content: float          # 0-100
    gene_name: str             # e.g., "TP53"
    exon: int                  # Exon number

# Main API function signature
def design_guides(
    gene: Optional[str] = None,
    region: Optional[str] = None,
    species: str = "human",
    top_n: int = 5,
    output: Optional[str] = None
) -> pd.DataFrame:
    """
    Design sgRNA guides for a gene or genomic region.

    Args:
        gene: Gene symbol (e.g., "TP53", "BRCA1")
        region: Genomic coordinates (e.g., "chr17:1000-2000")
        species: "human" or "mouse"
        top_n: Number of top guides to return
        output: Output CSV file path (optional)

    Returns:
        pandas DataFrame with ranked guides

    Raises:
        CrispexError: If input validation fails
        GeneNotFoundError: If gene not found in database
        GenomeNotInstalledError: If reference genome not downloaded
    """
    pass
```

---

## Help System

### Main Help Screen

```
$ crispex --help

Usage: crispex [OPTIONS] COMMAND [ARGS]...

  Crispex - AI-powered CRISPR guide design

  Design highly efficient and specific sgRNA guides using machine learning
  and comprehensive off-target analysis.

Options:
  --version   Show version and exit
  --help      Show this message and exit

Commands:
  design          Design sgRNA guides for a gene or region
  install-genome  Download and install reference genome
  list-genomes    Show installed genomes

Examples:
  # Design guides for TP53 gene
  crispex design --gene TP53 --species human

  # Design guides for genomic region
  crispex design --region chr17:7675000-7676000 --species human

  # Install human genome (one-time setup)
  crispex install-genome --species human

Documentation: https://github.com/yourname/crispex
Report issues: https://github.com/yourname/crispex/issues
```

---

### Design Command Help

```
$ crispex design --help

Usage: crispex design [OPTIONS]

  Design sgRNA guides for a gene or genomic region.

  Extracts candidate guides, predicts on-target efficiency using Azimuth,
  performs genome-wide off-target search, and returns ranked guides ready
  for ordering.

Options:
  --gene TEXT      Gene symbol (e.g., TP53, BRCA1, MYC)
  --region TEXT    Genomic coordinates (format: chr:start-end)
  --species TEXT   Species [human|mouse] [default: human]
  --output PATH    Output CSV file path [default: {gene}_guides.csv]
  --top-n INTEGER  Number of guides to return [default: 5]
  --help           Show this message and exit

Examples:
  # Design guides for TP53
  crispex design --gene TP53 --species human

  # Get top 10 guides for BRCA1
  crispex design --gene BRCA1 --top-n 10

  # Target specific region
  crispex design --region chr17:7675000-7676000 --species human

  # Custom output file
  crispex design --gene MYC --output my_guides.csv

Notes:
  • Either --gene or --region must be specified (not both)
  • Gene symbols are case-insensitive
  • Coordinates use 1-based indexing (same as genome browsers)
  • First run requires genome installation (see: install-genome)
```

---

## Visual Design Elements

### Progress Indicators

```
# Spinner (for quick operations)
⏳ Loading model...

# Progress bar (for longer operations)
Searching genome: ████████████████████ 100% (247/247) [00:18<00:00, 13.2 guides/s]

# Checkmarks for completed steps
✓ Gene fetch complete
✓ Guides extracted
✓ Predictions complete
```

### Status Symbols

```
✓  Success / Complete
⚠  Warning
❌ Error
⏳ In progress
💾 File saved
📊 Data/results
🎯 Top result
🧬 Biological data
```

### Score Visualizations

```
Efficiency Score: 81.2 / 100
████████████████░░░░  (81%)

Specificity: ★★★★★ Excellent
             ★★★★☆ Good
             ★★★☆☆ Moderate
             ★★☆☆☆ Low
             ★☆☆☆☆ Poor
```

---

## Configuration (Future)

### Config File: `~/.crispex/config.yaml`

```yaml
# Crispex configuration

# Default species for design
default_species: human

# Number of top guides to return
default_top_n: 5

# Output directory for results
output_dir: ./crispex_results/

# Genome data location
genome_dir: ~/.crispex/genomes/

# Off-target search parameters
offtarget:
  max_mismatches: 3
  skip_high_mismatch: false  # Skip 3MM search for speed

# Ensembl API settings
ensembl:
  cache_enabled: true
  cache_ttl: 604800  # 1 week in seconds
  timeout: 30  # seconds
```

*Note: Configuration file is not part of MVP but shows extensibility.*

---

## Summary: What Makes This Design "Magical"

1. **One command**: `crispex design --gene TP53 --species human`
2. **Fast**: Results in <30 seconds
3. **Beautiful output**: Clean, informative terminal display
4. **Ready to use**: CSV with sequences ready for ordering
5. **Trustworthy**: ML scores + off-target analysis
6. **Simple**: No complex configuration or multi-step workflows

The design prioritizes **developer experience** (clear API) and **user experience** (informative, beautiful CLI) while maintaining scientific rigor.

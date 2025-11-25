# Crispex Tutorial 3: Command-Line Interface

Step-by-step guide to using Crispex from the command line.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Commands](#basic-commands)
3. [Gene-Based Design](#gene-based-design)
4. [Region-Based Design](#region-based-design)
5. [Advanced Options](#advanced-options)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Check Installation

First, verify that Crispex is installed and accessible:

```bash
crispex --version
```

Expected output:
```
crispex, version 0.1.0
```

### Get Help

View all available commands:

```bash
crispex --help
```

Get help for a specific command:

```bash
crispex design --help
```

---

## Basic Commands

### 1. Design Guides for a Gene

The simplest command - design guides for a gene:

```bash
crispex design --gene TP53 --species human
```

**What this does:**
- Fetches the TP53 gene sequence from Ensembl
- Extracts all possible guide sequences
- Scores them for efficiency
- Analyzes off-targets
- Returns top 5 guides
- Saves to `tp53_guides.csv`

**Output:**
```
Crispex - CRISPR Guide Design
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Target: TP53 (Homo sapiens)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pipeline:
  ✓ Validated inputs
  ✓ Fetched sequence (1,182 bp)
  ✓ Extracted 127 candidate guides
  ✓ Predicted efficiency scores
  ✓ Searched off-targets
  ✓ Ranked guides

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Top Guide:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🧬 Guide:      ACACTCATTGCAGACTCAGG
  🎯 Full:       ACACTCATTGCAGACTCAGGTGG
  📍 Location:   chr17:7676146-7676165 (-)
  ⚡ Efficiency: 71.0 / 100
  🎲 GC%:        50.0%

  Off-targets:
    0MM: 1    1MM: 0    2MM: 1    3MM: 3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Saved 5 guides to: tp53_guides.csv
```

---

## Gene-Based Design

### 2. Design More Guides

Get top 10 instead of default 5:

```bash
crispex design --gene BRCA1 --species human --top-n 10
```

### 3. Mouse Genes

Design guides for mouse genes:

```bash
crispex design --gene Trp53 --species mouse --top-n 5
```

**Note:** Mouse gene symbols typically start with uppercase, rest lowercase (Trp53, Brca1, etc.)

### 4. Custom Output File

Specify where to save results:

```bash
crispex design --gene MYC --species human --output my_myc_guides.csv
```

### 5. More Comprehensive Analysis

Get more guides for detailed analysis:

```bash
crispex design --gene KRAS --species human --top-n 50
```

---

## Region-Based Design

### 6. Target Genomic Coordinates

Design guides for a specific region instead of a whole gene:

```bash
crispex design --region chr17:7675000-7676000 --species human
```

**When to use this:**
- Target a specific exon
- Target a regulatory region
- Target a non-coding region
- Target a custom sequence

### 7. Smaller Regions

Target a 200bp region:

```bash
crispex design --region chr17:7676000-7676200 --species human --top-n 3
```

### 8. Multiple Regions (Using Shell)

Design for multiple regions using a bash loop:

```bash
for region in "chr17:7675000-7676000" "chr17:7680000-7681000" "chr17:7685000-7686000"
do
  echo "Designing for $region..."
  crispex design --region "$region" --species human --output "region_${region//[:-]/_}_guides.csv"
done
```

---

## Advanced Options

### 9. Batch Gene Processing

Process multiple genes with a script:

```bash
# Create a file called genes.txt with one gene per line:
# TP53
# BRCA1
# BRCA2
# KRAS

while read gene; do
  echo "Processing $gene..."
  crispex design --gene "$gene" --species human --top-n 10
done < genes.txt
```

### 10. Organized Output Directory

Keep outputs organized:

```bash
mkdir -p output/guides

crispex design --gene TP53 --species human --output output/guides/tp53_guides.csv
crispex design --gene BRCA1 --species human --output output/guides/brca1_guides.csv
crispex design --gene KRAS --species human --output output/guides/kras_guides.csv
```

### 11. Quick Lookup (No Save)

If you don't specify `--output`, it auto-saves to `{gene}_guides.csv`. To just view results without saving (not currently supported, but you can delete after):

```bash
crispex design --gene EGFR --species human --top-n 5
rm egfr_guides.csv  # Delete if you don't need it
```

---

## Common Workflows

### Workflow 1: Cancer Gene Panel

Design guides for a panel of cancer genes:

```bash
#!/bin/bash
# cancer_panel.sh

GENES=("TP53" "BRCA1" "BRCA2" "KRAS" "EGFR" "MYC" "PTEN")
OUTPUT_DIR="output/cancer_panel"

mkdir -p "$OUTPUT_DIR"

for gene in "${GENES[@]}"; do
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Designing guides for $gene"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  crispex design \
    --gene "$gene" \
    --species human \
    --top-n 10 \
    --output "$OUTPUT_DIR/${gene}_guides.csv"

  echo ""
done

echo "✓ Complete! All results in $OUTPUT_DIR/"
```

Run it:
```bash
chmod +x cancer_panel.sh
./cancer_panel.sh
```

### Workflow 2: Exon-by-Exon Design

Target specific exons of TP53:

```bash
#!/bin/bash
# tp53_exons.sh

# TP53 exon coordinates (example)
declare -A EXONS=(
  [exon5]="chr17:7676000-7676300"
  [exon6]="chr17:7675000-7675200"
  [exon7]="chr17:7674200-7674400"
)

for exon in "${!EXONS[@]}"; do
  echo "Designing guides for TP53 $exon..."
  crispex design \
    --region "${EXONS[$exon]}" \
    --species human \
    --top-n 5 \
    --output "output/tp53_${exon}_guides.csv"
done
```

### Workflow 3: Quality Control Pipeline

Design and filter for high-quality guides:

```bash
#!/bin/bash
# high_quality_design.sh

GENE="$1"

if [ -z "$GENE" ]; then
  echo "Usage: ./high_quality_design.sh GENE_NAME"
  exit 1
fi

echo "Designing 50 guides for $GENE..."
crispex design --gene "$GENE" --species human --top-n 50 --output "temp_${GENE}.csv"

echo "Filtering for high-quality guides..."
# Use Python or awk to filter the CSV
python3 << EOF
import pandas as pd

df = pd.read_csv('temp_${GENE}.csv')

# Filter for high quality
high_quality = df[
    (df['efficiency_score'] >= 70) &
    (df['off_targets_1mm'] <= 2) &
    (df['gc_content'] >= 40) &
    (df['gc_content'] <= 60)
].head(10)

high_quality.to_csv('${GENE}_high_quality_guides.csv', index=False)
print(f"✓ Found {len(high_quality)} high-quality guides")
print(f"✓ Saved to: ${GENE}_high_quality_guides.csv")
EOF

rm "temp_${GENE}.csv"
```

---

## Troubleshooting

### Error: "Gene not found"

```bash
crispex design --gene XYZ123 --species human
# Error: Gene 'XYZ123' not found in Ensembl database
```

**Solutions:**
- Check gene symbol spelling (TP53, not Tp53 for human)
- Try alternative gene names (gene aliases)
- Use Ensembl gene ID instead
- Check the correct species

### Error: "No guides found"

```bash
crispex design --region chr1:100-150 --species human
# Warning: No guides found in this region
```

**Solutions:**
- Region might be too small (need >23bp for guide+PAM)
- Region might not have any NGG PAM sites
- Try a larger region

### Error: Network/API Issues

```bash
# Error: Failed to connect to Ensembl API
```

**Solutions:**
- Check internet connection
- Ensembl might be down - try again later
- Use `--timeout` option (if available) for slow connections

### Slow Performance

If design is taking too long:

1. **Smaller regions:** Instead of whole gene, target specific exons
2. **Fewer guides:** Use smaller `--top-n` value
3. **Check region size:** Very large regions (>100kb) take longer

---

## Tips & Best Practices

### 1. Always Specify Output

Be explicit about where files go:

```bash
# Good
crispex design --gene TP53 --output output/tp53_guides.csv

# Less organized
crispex design --gene TP53  # Saves to ./tp53_guides.csv
```

### 2. Use Consistent Naming

Develop a naming convention:

```bash
# Date-based
crispex design --gene TP53 --output "$(date +%Y%m%d)_tp53_guides.csv"

# Project-based
crispex design --gene TP53 --output "project_alpha/tp53_v1_guides.csv"
```

### 3. Keep a Log

Log your commands:

```bash
{
  echo "$(date): Designed guides for TP53"
  crispex design --gene TP53 --species human --top-n 10
} | tee -a design_log.txt
```

### 4. Verify Before Ordering

Always review the CSV before ordering guides:

```bash
crispex design --gene TP53 --species human
cat tp53_guides.csv | column -t -s,  # Pretty print CSV
```

---

## Next Steps

- ✓ **Completed:** CLI basics
- **Next:** Try the Python API for more flexibility (see `tutorial_01_beginner.py`)
- **Advanced:** Integrate into your own pipelines and scripts

---

**Questions?** Check the main README.md or open an issue on GitHub.

# Crispex Examples & Tutorials

Complete collection of examples and step-by-step tutorials for Crispex.

## Quick Start

**New to Crispex?** Start with the tutorials in order:

1. **Tutorial 1:** Beginner's Guide → `tutorial_01_beginner.py`
2. **Tutorial 2:** Advanced Features → `tutorial_02_advanced.py`
3. **Tutorial 3:** CLI Usage → `tutorial_03_cli.md`

**Need a quick reference?** Check the standalone examples:
- Basic API usage → `basic_usage.py`
- Custom filtering → `filtering_guides.py`
- Region targeting → `region_targeting.py`

---

## 📚 Tutorials (Step-by-Step Learning)

### Tutorial 1: Beginner's Guide
**File:** `tutorial_01_beginner.py`
**Level:** Beginner
**Duration:** ~10 minutes

Complete introduction to Crispex for newcomers.

**You'll learn:**
- ✓ How to design your first guide
- ✓ Understanding guide quality metrics
- ✓ Comparing multiple guides
- ✓ Saving and exporting results
- ✓ Complete workflow from gene to ordered guides

**Run it:**
```bash
python examples/tutorial_01_beginner.py
```

**Interactive:** Yes - press Enter to advance through steps

---

### Tutorial 2: Advanced Features
**File:** `tutorial_02_advanced.py`
**Level:** Intermediate/Advanced
**Duration:** ~15 minutes

Deep dive into advanced guide design techniques.

**You'll learn:**
- ✓ Region-based targeting (coordinates instead of genes)
- ✓ Custom filtering strategies
- ✓ Batch analysis across multiple genes
- ✓ Quality control and validation
- ✓ Experiment-specific design (knockout, clinical, multiplexing)
- ✓ Multiple export formats

**Run it:**
```bash
python examples/tutorial_02_advanced.py
```

**Prerequisites:** Complete Tutorial 1 first

---

### Tutorial 3: Command-Line Interface
**File:** `tutorial_03_cli.md`
**Level:** Beginner to Advanced
**Format:** Markdown guide (read in your editor)

Comprehensive guide to using Crispex from the command line.

**Covers:**
- ✓ Basic CLI commands
- ✓ Gene-based vs region-based design
- ✓ Batch processing workflows
- ✓ Shell scripting integration
- ✓ Common workflows (cancer panels, exon-by-exon)
- ✓ Troubleshooting and best practices

**Read it:**
```bash
cat examples/tutorial_03_cli.md
# Or open in your favorite editor
```

---

## 📝 Standalone Examples

These are quick, focused examples for specific use cases.

### 1. Basic Usage
**File:** `basic_usage.py`

Minimal example showing the simplest way to design guides.

```bash
python examples/basic_usage.py
```

**Code snippet:**
```python
from crispex import design_guides

guides = design_guides(
    gene="TP53",
    species="human",
    top_n=5
)
print(guides.head())
```

**Good for:**
- Quick start
- Testing installation
- Copy-paste into your scripts

---

### 2. Filtering Guides
**File:** `filtering_guides.py`

Advanced filtering based on custom criteria.

```bash
python examples/filtering_guides.py
```

**Demonstrates:**
- Getting more guides (top_n=20)
- Filtering by efficiency score
- Filtering by off-target counts
- Combined filtering criteria
- Statistical analysis

**Output:** `output/brca1_optimal_guides.csv`

---

### 3. Region Targeting
**File:** `region_targeting.py`

Target specific genomic coordinates instead of gene names.

```bash
python examples/region_targeting.py
```

**Demonstrates:**
- Genomic coordinate input (chr:start-end)
- Region-based guide design
- Strand distribution analysis
- Position analysis across region

**Output:** `output/region_guides.csv`

---

## 🎯 Use Case Guide

**What should I run?**

| You want to... | Run this |
|----------------|----------|
| Learn Crispex from scratch | `tutorial_01_beginner.py` |
| Design guides for a gene | `basic_usage.py` |
| Design guides for specific coordinates | `region_targeting.py` |
| Filter guides by quality metrics | `filtering_guides.py` |
| Advanced techniques | `tutorial_02_advanced.py` |
| Use the command line | Read `tutorial_03_cli.md` |
| Process multiple genes | `tutorial_02_advanced.py` (Example 3) |
| Experiment-specific design | `tutorial_02_advanced.py` (Example 5) |

---

## 📂 Output Files

All examples now save results to the `output/` directory to keep the repository clean.

**Generated files:**
- `output/tutorial_tp53_guides.csv` - From Tutorial 1
- `output/brca1_guides.csv` - From Tutorial 1
- `output/pten_guides_*.csv` - From Tutorial 2
- `output/brca1_optimal_guides.csv` - From filtering example
- `output/region_guides.csv` - From region example

The `output/` directory is gitignored, so these files won't be committed.

---

## 🚀 Running All Examples

### Run All Tutorials
```bash
# Tutorial 1
python examples/tutorial_01_beginner.py

# Tutorial 2
python examples/tutorial_02_advanced.py

# Tutorial 3 (just read it)
cat examples/tutorial_03_cli.md
```

### Run All Standalone Examples
```bash
for script in examples/basic_usage.py examples/filtering_guides.py examples/region_targeting.py; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Running $(basename $script)..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python "$script"
    echo ""
done
```

---

## ⚙️ Requirements

All examples require:

**Software:**
- Python 3.9+
- Crispex installed: `pip install -e .` (from repo root)

**System:**
- Internet connection (to fetch sequences from Ensembl API)
- ~50MB RAM
- Takes 5-30 seconds per gene

**Optional:**
- `pandas` for CSV manipulation
- Text editor for viewing .md files

---

## 🔧 Modifying Examples

All examples are designed to be modified and adapted to your needs.

### Change the Target Gene
```python
# Change this:
guides = design_guides(gene="TP53", species="human")

# To this:
guides = design_guides(gene="BRCA1", species="human")
```

### Get More Guides
```python
guides = design_guides(gene="TP53", top_n=50)  # Get 50 instead of 5
```

### Change Species
```python
guides = design_guides(gene="Trp53", species="mouse")
```

### Custom Filtering
```python
# Add your own filters
optimal = guides[
    (guides['efficiency_score'] >= 80) &
    (guides['off_targets_1mm'] == 0) &
    (guides['gc_content'].between(45, 55))
]
```

---

## 🐛 Troubleshooting

### Error: "Gene not found"
```
GeneNotFoundError: Gene 'XYZ' not found
```

**Solutions:**
- Check gene symbol spelling (human: TP53, mouse: Trp53)
- Try alternative names or Ensembl IDs
- Verify species is correct

### Error: "No guides found"
```
Warning: No suitable guides found
```

**Solutions:**
- Region might be too small (need ≥23bp)
- Sequence might lack PAM sites (NGG)
- Try relaxing quality filters
- Try a different region

### Error: Network/API timeout
```
APIError: Failed to connect to Ensembl
```

**Solutions:**
- Check internet connection
- Ensembl servers might be down - try later
- Try a smaller gene/region first

### Slow performance
**If examples take too long:**
- Use smaller `top_n` values
- Target specific exons instead of whole genes
- Check internet speed
- Large genes (>100kb) naturally take longer

---

## 📊 Expected Outputs

### Typical Results
For most genes, you should expect:
- **Runtime:** 10-30 seconds
- **Guides found:** 5-200 candidates
- **Efficiency scores:** 50-85 range
- **Off-targets:** 0-10 at 1 mismatch

### Good vs Great Guides

| Metric | Good | Great |
|--------|------|-------|
| Efficiency | ≥60 | ≥75 |
| GC% | 40-60% | 45-55% |
| Off-targets (1MM) | ≤5 | 0-2 |
| Off-targets (2MM) | ≤20 | ≤10 |

---

## 💡 Tips & Best Practices

### 1. Start with Tutorials
Don't skip the tutorials - they teach important concepts that the standalone examples assume you know.

### 2. Always Review Before Ordering
```python
# Print top guide details
print(guides.iloc[0])

# Check off-targets
print(guides[['guide_sequence', 'off_targets_1mm', 'off_targets_2mm']].head())
```

### 3. Save Everything
```python
# Always specify output
guides = design_guides(
    gene="TP53",
    output="output/tp53_experiment1_guides.csv"
)
```

### 4. Keep Notes
Add comments to your scripts:
```python
# Designing for knockout experiment - prioritize efficiency
# Date: 2024-01-15
# Project: cancer-screen-v2
guides = design_guides(gene="TP53", top_n=10)
```

---

## 🤝 Contributing Examples

Have a useful workflow or example? Share it!

**Good examples to contribute:**
- Novel filtering strategies
- Integration with other tools
- Specific experimental designs
- Performance optimizations

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## 📖 Additional Resources

- **Main Documentation:** [../README.md](../README.md)
- **API Reference:** See docstrings in source code
- **Issues & Questions:** [GitHub Issues](https://github.com/yourusername/crispex/issues)

---

## 🎓 Learning Path

**Recommended progression:**

```
1. Install Crispex
   ↓
2. Run tutorial_01_beginner.py
   ↓
3. Try basic_usage.py with your gene
   ↓
4. Read tutorial_03_cli.md
   ↓
5. Run tutorial_02_advanced.py
   ↓
6. Adapt examples for your research
   ↓
7. Share your workflows!
```

---

**Ready to start?** Run your first tutorial:

```bash
python examples/tutorial_01_beginner.py
```

Happy guide designing! 🧬✨

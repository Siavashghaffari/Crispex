# Crispex MVP - Minimum Viable Product

## The Magic Moment

**Input**: A gene name (e.g., "TP53")
**Output**: 5 ready-to-order sgRNA sequences with AI-predicted efficiency scores
**Time**: Under 30 seconds

That's it. No complex configuration, no multi-step workflows, no manual BLAST searches. Just the fastest path from "I need guides for this gene" to "Here are your top 5 guides, scored and validated."

---

## MVP Goal

Build the **simplest possible package** that delivers real value to researchers:
- Eliminates manual guide design and BLAST searches
- Provides ML-predicted efficiency scores (not just random sequences)
- Validates guides against genome-wide off-targets
- Outputs sequences ready for oligonucleotide ordering

**Success metric**: A grad student can design high-quality guides during their coffee break.

---

## Core Features (MVP Only)

### 1. Input Options (Simple)

**Option A - Gene Symbol**:
```bash
crispex design --gene TP53 --species human
```
- Auto-fetch gene sequence from Ensembl REST API
- Use canonical transcript (longest coding sequence)
- Target all exons by default

**Option B - Genomic Coordinates**:
```bash
crispex design --region chr17:7661779-7687550 --species human
```
- Direct genomic region targeting
- No gene annotation required

**Species Support (MVP)**:
- Human (GRCh38) - priority
- Mouse (GRCm39) - if time permits
- That's it. No custom genomes, no other organisms.

### 2. Guide Extraction

**PAM Search**:
- SpCas9 PAM only: **NGG**
- No SaCas9, no xCas9, no other variants

**Guide Length**:
- Fixed 20bp upstream of PAM
- No configurability (keep it simple)

**Basic Quality Filters**:
- GC content: 40-60%
- No homopolymer runs (≥4 identical bases)
- No polyT stretches (≥4 T's - causes pol III termination)

**That's all.** No complexity filters, no self-complementarity checks, no advanced sequence analysis.

### 3. On-Target Efficiency Prediction

**Single Model**: Azimuth (Doench 2016)
- Well-validated, widely cited model
- Good balance of accuracy and speed
- Pre-trained weights included in package

**Why Azimuth for MVP**:
- Published, peer-reviewed algorithm
- Moderate file size (~10MB)
- Fast inference (batch of 100 guides in <1 second)
- No ensemble complexity

**Scoring**:
- Output: 0-100 efficiency score per guide
- Higher = more likely to cut efficiently

**No ensemble, no other models.** Keep it simple and ship fast.

### 4. Off-Target Detection (Basic)

**Genome-Wide Search**:
- Find all genomic sites with 0-3 mismatches to guide sequence + PAM
- Use exact string matching with mismatch tolerance (not full alignment)
- Count off-targets by mismatch category:
  - 0MM: Perfect matches (should only be 1 - the target)
  - 1MM: Single mismatch
  - 2MM: Two mismatches
  - 3MM: Three mismatches

**Scoring**:
- Simple count: fewer off-targets = better specificity
- Flag guides with >5 off-targets at 0-2 mismatches

**What's NOT included**:
- No chromatin accessibility scoring
- No bulges or gaps in alignment
- No off-target cutting probability (CFD scores)
- No annotation of off-target locations (intron/exon/etc.)

**Implementation**: Use simple indexed search (suffix array or FM-index) for speed.

### 5. Ranking Algorithm

**Simple multi-criteria sort**:

1. **Efficiency score** (primary): Higher is better
2. **Off-target count** (0-2MM): Lower is better
3. **Position in gene**: Earlier exons preferred (for knockouts)

**Output**: Top 5 guides only

No complex weighting, no quality tiers, no confidence intervals. Just rank and return the best 5.

### 6. Output Format

**CSV File**: `{gene_name}_guides.csv`

Columns:
- `rank`: 1-5
- `guide_sequence`: 20bp guide (without PAM)
- `pam_sequence`: NGG
- `full_sequence`: guide + PAM for easy ordering
- `chromosome`: e.g., chr17
- `start`: Genomic start coordinate
- `end`: Genomic end coordinate
- `strand`: + or -
- `efficiency_score`: 0-100 (Azimuth)
- `off_targets_0mm`: Count (should be 1)
- `off_targets_1mm`: Count
- `off_targets_2mm`: Count
- `off_targets_3mm`: Count
- `gc_content`: Percentage

**That's it.** No JSON, no GenBank, no visualizations, no BED files.

**Ready to order**: The `full_sequence` column contains the exact oligo to order (add adapters based on cloning protocol).

---

## Interface Design

### CLI (Click-based)

**Main command**:
```bash
crispex design --gene BRCA1 --species human
```

**Optional flags**:
```bash
--gene GENE            Gene symbol (e.g., TP53, BRCA1)
--region REGION        Genomic coordinates (e.g., chr17:1000-2000)
--species SPECIES      Species name (human or mouse)
--output PATH          Output CSV file path (default: {gene}_guides.csv)
--top-n N             Number of guides to return (default: 5)
```

**Output behavior**:
- Print summary to stdout (gene info, number of candidates found)
- Write CSV to file
- Show top guide info in terminal for quick view

**Example output**:
```
Designing guides for TP53 (human)
Gene location: chr17:7661779-7687550
Found 247 candidate guides
Running efficiency predictions...
Searching for off-targets...
Ranking guides...

Top guide:
  Sequence: GGGGCCCATCCTCACCATCA (NGG)
  Efficiency: 78.4
  Off-targets: 0/1/3/12 (0/1/2/3 MM)

Results saved to: tp53_guides.csv
```

### Python API

**Simple function-based API**:

```python
from crispex import design_guides

# Basic usage
guides = design_guides(gene="BRCA1", species="human")
print(guides)  # pandas DataFrame

# With options
guides = design_guides(
    gene="TP53",
    species="human",
    top_n=10,
    output="my_guides.csv"
)

# Access specific columns
for idx, guide in guides.iterrows():
    print(f"{guide['guide_sequence']} - Efficiency: {guide['efficiency_score']}")
```

**Return type**: pandas DataFrame (same columns as CSV)

**No class-based API for MVP.** Keep it functional and simple.

---

## Technical Implementation (MVP)

### Core Components (Minimal)

```
crispex/
├── __init__.py           # Expose design_guides() function
├── cli.py                # Click CLI commands
├── extract.py            # Guide extraction and filtering
├── predict.py            # Azimuth model wrapper
├── offtarget.py          # Genome search for mismatches
├── rank.py               # Sorting and ranking logic
├── fetch.py              # Ensembl API wrapper
├── genome.py             # Genome download and indexing
└── data/
    └── azimuth_model.pkl # Pre-trained Azimuth weights
```

**Total code estimate**: ~1500-2000 lines

### Dependencies (Minimal)

**Required**:
- `biopython` - Sequence handling, FASTA parsing
- `pandas` - DataFrames for results
- `numpy` - Numerical operations
- `scikit-learn` - For Azimuth model (uses gradient boosting)
- `requests` - Ensembl API calls
- `click` - CLI framework
- `pyfaidx` - Fast FASTA indexing

**Optional**:
- `tqdm` - Progress bars (nice-to-have)

**No PyTorch, no TensorFlow** for MVP. Azimuth uses sklearn.

### Data Requirements

**Reference Genomes**:
- Human GRCh38: ~3GB (download on first use, cache locally)
- Mouse GRCm39: ~2.5GB (optional for MVP)
- Store in `~/.crispex/genomes/`

**Model Files**:
- Azimuth model: ~10MB (bundled with package)

**Total install size**: ~15MB (without genomes)
**With human genome cached**: ~3GB

### Performance Targets

**Speed goals** (for typical gene ~50kb, ~200 candidate guides):
- Gene fetch from Ensembl: <2 seconds
- Guide extraction: <1 second
- Azimuth predictions: <1 second
- Off-target search: <20 seconds (genome-wide)
- Total runtime: **<30 seconds**

**Memory**: Should run on 8GB RAM laptop

### Genome Indexing

**First-run setup**:
```bash
crispex install-genome --species human
```
- Downloads GRCh38 FASTA
- Creates FASTA index (.fai)
- Creates suffix array for off-target search
- One-time operation (~5 minutes)

**Auto-install**: If genome not found, prompt user to install

---

## What's NOT in MVP

### Features Explicitly Excluded

- ❌ Batch processing (multiple genes at once)
- ❌ Ensemble ML models (DeepSpCas9, DeepCRISPR)
- ❌ Chromatin accessibility analysis
- ❌ SNP/variant checking (dbSNP integration)
- ❌ Other Cas variants (SaCas9, Cas12a, base editors)
- ❌ Custom genome support (FASTA upload)
- ❌ Visualizations (plots, genome browser tracks)
- ❌ JSON/GenBank export (CSV only)
- ❌ Quality tier assignments (Excellent/Good/Acceptable)
- ❌ HDR template design
- ❌ Guide library design for screens
- ❌ Configuration files
- ❌ Interactive mode
- ❌ Web interface
- ❌ Docker images (just pip install)

### Advanced Filters Excluded

- ❌ Secondary structure prediction
- ❌ Seed region specificity
- ❌ Distance to start codon
- ❌ Exon/intron preferences
- ❌ Alternative transcript checking
- ❌ Conservation scores
- ❌ Epigenetic marks

**Philosophy**: Ship the core loop first. Add complexity based on user feedback.

---

## MVP User Journey

### Scenario: PhD student needs guides for TP53 knockout

**Step 1**: Install package
```bash
pip install crispex
```

**Step 2**: Install human genome (first time only)
```bash
crispex install-genome --species human
# Downloads ~3GB, takes 5 minutes
```

**Step 3**: Design guides
```bash
crispex design --gene TP53 --species human
# Takes 25 seconds
```

**Step 4**: Review results
```bash
cat tp53_guides.csv
```

**Step 5**: Order top guide from IDT/Synthego
- Copy `full_sequence` from CSV
- Add cloning adapters
- Submit order

**Total time**: 30 seconds (after initial setup)
**Previous workflow**: 2-3 hours of manual work (primer design, BLAST, manual scoring)

**That's the magic.**

---

## Development Milestones

### Milestone 1: Core Engine (Week 1-2)
- [ ] Guide extraction with PAM search
- [ ] GC and homopolymer filters
- [ ] Ensembl gene sequence fetcher
- [ ] Genomic coordinate parser

### Milestone 2: ML Prediction (Week 2-3)
- [ ] Implement Azimuth algorithm
- [ ] Bundle pre-trained model
- [ ] Batch prediction pipeline
- [ ] Score validation against test set

### Milestone 3: Off-Target Search (Week 3-4)
- [ ] Genome indexing (suffix array or FM-index)
- [ ] Mismatch search algorithm
- [ ] Off-target counting
- [ ] Performance optimization (<30s total)

### Milestone 4: Ranking & Export (Week 4)
- [ ] Multi-criteria ranking
- [ ] CSV export formatting
- [ ] Guide sequence formatting

### Milestone 5: CLI & API (Week 5)
- [ ] Click CLI implementation
- [ ] Python API wrapper
- [ ] Error handling and validation
- [ ] Help documentation

### Milestone 6: Polish & Release (Week 6)
- [ ] Unit tests (core functions)
- [ ] Integration tests (end-to-end)
- [ ] README with examples
- [ ] PyPI packaging
- [ ] First release: v0.1.0

**Total development time**: ~6 weeks for one developer

---

## Success Criteria (MVP)

### Functional Requirements
- ✅ Accepts gene symbol, returns 5 ranked guides
- ✅ Completes in <30 seconds for typical gene
- ✅ Efficiency scores correlate with literature values
- ✅ Finds all off-targets with ≤3 mismatches
- ✅ CSV output ready for oligo ordering

### User Experience
- ✅ One-line installation: `pip install crispex`
- ✅ One-line execution: `crispex design --gene TP53 --species human`
- ✅ Clear error messages for invalid inputs
- ✅ Works on Linux and macOS (Windows nice-to-have)

### Quality
- ✅ 20+ unit tests covering core functions
- ✅ Example-driven documentation
- ✅ MIT license, open source
- ✅ No crashes on valid inputs

---

## Post-MVP Roadmap (Future Versions)

Once MVP is validated by users, add features in order of impact:

**v0.2.0 - Enhanced Scoring**:
- Add ensemble ML (DeepSpCas9 + Azimuth)
- CFD scores for off-targets
- Batch processing (multiple genes)

**v0.3.0 - Variants**:
- SNP checking (dbSNP)
- Flag guides disrupted by common variants

**v0.4.0 - Specificity**:
- Chromatin accessibility integration
- Cell-type specific off-target scoring

**v0.5.0 - Flexibility**:
- SaCas9 support
- Custom genome upload
- Cas12a support

**v1.0.0 - Production Ready**:
- Comprehensive testing
- Full documentation
- Performance benchmarks
- Published validation study

---

## Risk Mitigation (MVP)

### Technical Risks

**Risk**: Off-target search too slow (>30s)
- **Mitigation**: Use FM-index or pre-built suffix array, test early

**Risk**: Azimuth model accuracy poor on our sequences
- **Mitigation**: Validate against published benchmarks, have DeepSpCas9 ready as backup

**Risk**: Ensembl API unreliable/rate-limited
- **Mitigation**: Implement caching, retry logic, fallback to local annotation files

**Risk**: Package size too large (with genome bundles)
- **Mitigation**: Genomes downloaded separately, not bundled in pip package

### Scope Risks

**Risk**: Feature creep during development
- **Mitigation**: This document. Ruthlessly cut features not on this list.

**Risk**: Users request features before MVP complete
- **Mitigation**: "Great idea! We'll add it post-MVP based on demand."

---

## Definition of Done (MVP)

**Code complete when**:
1. Can design guides for any human gene symbol in <30s
2. Returns 5 ranked guides with efficiency scores
3. CSV export with all required columns
4. Both CLI and Python API work
5. Basic tests pass
6. README has installation + usage example

**Ready to share when**:
1. Installable via `pip install crispex`
2. Tested on ≥3 different genes (small, medium, large)
3. Off-target counts match manual BLAST (spot check)
4. Documentation covers happy path
5. No known crash bugs

**MVP = Minimum VIABLE Product**
It should work reliably for the core use case, even if it's missing bells and whistles.

---

## Example Output (What Users See)

```bash
$ crispex design --gene TP53 --species human

Crispex v0.1.0 - AI-powered CRISPR guide design

Fetching gene information for TP53...
✓ Found TP53 (ENSG00000141510)
  Location: chr17:7,661,779-7,687,550 (25.8 kb)
  Transcript: ENST00000269305 (canonical)

Extracting guide candidates...
✓ Found 247 potential guides

Predicting on-target efficiency...
✓ Scored 247 guides using Azimuth

Searching for off-targets...
✓ Genome-wide search complete

Ranking guides...
✓ Top 5 guides selected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Top Guide:
  Sequence: GGAAGACTCCAGTGGTAATC (TGG)
  Location: chr17:7,675,088 (+)
  Efficiency: 81.2 / 100
  Off-targets: 0 / 2 / 8 / 34 (0/1/2/3 MM)
  GC content: 50.0%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Results saved to: tp53_guides.csv

Ready to order! Use the 'full_sequence' column for oligo synthesis.

$ head -3 tp53_guides.csv
rank,guide_sequence,pam_sequence,full_sequence,chromosome,start,end,strand,efficiency_score,off_targets_0mm,off_targets_1mm,off_targets_2mm,off_targets_3mm,gc_content
1,GGAAGACTCCAGTGGTAATC,TGG,GGAAGACTCCAGTGGTAATCTGG,chr17,7675088,7675110,+,81.2,1,2,8,34,50.0
2,TCAACAAGATGTTTTGCCAA,CTG,TCAACAAGATGTTTTGCCAACTG,chr17,7675234,7675256,-,76.8,1,0,4,22,40.0
```

**This is what "magical" looks like**: Gene name in, ranked guides out, ready to order.

---

## Final Notes

**MVP Philosophy**:
- Do one thing extremely well: turn gene names into validated sgRNA sequences
- Ship fast, learn from users, iterate based on real needs
- Resist feature creep until core workflow is bulletproof

**Success = Usage**:
- If researchers use Crispex instead of manual design, we win
- If guides work in the lab, we win
- If it saves time, we win

**Everything else is secondary.**

Build this first. Ship it. Get feedback. Then add the fancy stuff.

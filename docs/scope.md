# Crispex - Scope Definition

## Project Overview

**Crispex** is a Python package for AI-powered CRISPR single guide RNA (sgRNA) design that combines ensemble machine learning for on-target efficiency prediction with chromatin-aware off-target detection. The package enables researchers to design highly specific and efficient CRISPR guides for gene editing experiments and therapeutic development.

**Distribution**: Installable via `pip install crispex`

**Target Python Version**: 3.9+

---

## Target Users

- Molecular biologists conducting CRISPR experiments
- Researchers in therapeutic development
- Bioinformaticians designing genome editing workflows
- Academic labs and biotech companies performing gene editing

---

## Core Objectives

1. **Simplify sgRNA design**: Transform complex multi-step guide design into a single command/function call
2. **Maximize editing success**: Use state-of-the-art ML models to predict guide efficiency
3. **Minimize off-target effects**: Perform comprehensive genome-wide off-target analysis with chromatin context
4. **Support production workflows**: Enable reliable, reproducible guide design for both research and therapeutic applications
5. **Species flexibility**: Support multiple model organisms and custom genomes

---

## Primary Use Case

**Input**: Gene name/ID (e.g., "BRCA1", "ENSG00000012048") OR genomic coordinates (e.g., "chr17:43044295-43125483")

**Output**: Ranked list of sgRNA candidates with:
- On-target efficiency scores (0-100)
- Comprehensive off-target analysis
- Chromatin accessibility at target site
- SNP disruption warnings
- Editing recommendations and quality flags
- Genomic coordinates and sequences

**Workflow**: User → Query → Guide Extraction → ML Scoring → Off-target Search → Ranking → Results Export

---

## Core Features (MVP)

### 1. Interface Options
- **Command-Line Interface (CLI)**: Interactive tool using Click framework
  - Simple commands like `crispex design --gene BRCA1 --species human`
  - Batch processing from input files
  - Progress indicators for long-running analyses

- **Python API**: Programmatic access for integration into pipelines
  ```python
  from crispex import GuideDesigner
  designer = GuideDesigner(species='human')
  guides = designer.design_guides(gene='BRCA1', top_n=10)
  ```

### 2. Species and Genome Support
- **Built-in genomes**: Human (GRCh38), Mouse (GRCm39), Rat (mRatBN7.2)
- **Custom genome support**: Allow users to provide FASTA files for any organism
- **Automatic genome indexing**: Download and index reference genomes on first use

### 3. On-Target Efficiency Prediction (Ensemble ML)
- **Ensemble approach**: Combine predictions from multiple models to improve accuracy
  - DeepSpCas9 (CNN-based, considers sequence features)
  - Azimaru (rule-based + ML hybrid)
  - DeepCRISPR (deep learning with sequence context)

- **Scoring methodology**:
  - Generate individual scores from each model
  - Weighted ensemble to produce final efficiency score (0-100)
  - Confidence intervals based on model agreement

- **Pre-trained models included**: Ship with package to avoid user training requirements

### 4. Off-Target Detection
- **Genome-wide search**: Identify all potential off-target sites with up to 3-4 mismatches
- **Chromatin accessibility integration**:
  - Use DNase-seq/ATAC-seq data to score off-target sites
  - Prioritize off-targets in open chromatin (higher risk)
  - Flag guides with accessible off-targets

- **Off-target scoring**:
  - Calculate cutting probability at each site
  - Distance from target (same chromosome vs. different)
  - Aggregate risk score combining frequency and accessibility

### 5. SNP-Aware Design
- **Variant integration**: Query dbSNP for common variants (MAF > 1%)
- **Guide disruption detection**: Flag guides where SNPs disrupt:
  - PAM sequence
  - Seed region (positions 1-12)
  - Full guide sequence

- **Population-specific variants**: Support different variant databases for populations

### 6. Cas9 Variant Support
- **SpCas9** (Streptococcus pyogenes): NGG PAM (default)
- **SaCas9** (Staphylococcus aureus): NNGRRT PAM
- **Extensible architecture**: Easy addition of new Cas variants and PAM sequences

### 7. Guide Extraction and Filtering
- **PAM identification**: Search for appropriate PAM sequences in target region
- **Guide length**: Standard 20bp guides (configurable 17-24bp)
- **Quality filters**:
  - GC content (40-60% recommended)
  - Homopolymer runs (exclude guides with 4+ identical bases)
  - Self-complementarity (avoid secondary structures)
  - Complexity filters (exclude low-complexity sequences)

### 8. Database Integration
- **Gene sequence retrieval**:
  - Ensembl REST API for gene coordinates and sequences
  - NCBI E-utilities as fallback
  - Support for gene symbols, Ensembl IDs, Entrez IDs

- **Variant data**:
  - dbSNP for human variants
  - MGI for mouse variants
  - Local variant files (VCF) for custom datasets

### 9. Results Export and Visualization
- **Export formats**:
  - CSV: Tabular results with all scores and annotations
  - JSON: Structured data for programmatic use
  - GenBank/BED: Genomic coordinate files for genome browsers

- **Visualizations** (basic):
  - Guide location plot showing positions along gene
  - On-target score distribution
  - Off-target summary charts
  - Export as PNG/SVG files

### 10. Ranking and Recommendations
- **Multi-criteria ranking**:
  - On-target efficiency (primary)
  - Off-target specificity (critical filter)
  - Chromatin accessibility at target
  - Position within gene (prefer early exons for knockouts)
  - SNP disruption (penalize affected guides)

- **Quality tiers**:
  - Tier 1 (Excellent): High efficiency, no significant off-targets
  - Tier 2 (Good): Good efficiency, minimal off-target risk
  - Tier 3 (Acceptable): Moderate efficiency or minor off-target concerns
  - Flagged: Quality issues requiring expert review

---

## Technical Architecture

### Core Components

1. **Input Handler**: Parse gene names, coordinates, FASTA sequences
2. **Genome Manager**: Download, index, and cache reference genomes
3. **Guide Extractor**: Identify PAM sites and extract candidate guides
4. **ML Ensemble Predictor**: Load models and generate on-target scores
5. **Off-Target Searcher**: Genome-wide alignment and scoring
6. **Chromatin Analyzer**: Integrate accessibility data
7. **SNP Checker**: Query variant databases
8. **Ranker**: Multi-criteria sorting and quality assignment
9. **Export Engine**: Generate output files and visualizations

### Key Dependencies

- **BioPython**: Sequence manipulation, file I/O, alignment
- **PyTorch/TensorFlow**: ML model inference
- **pandas**: Data processing and tabular operations
- **NumPy**: Numerical computations
- **Click**: CLI framework
- **requests**: API calls to Ensembl/NCBI
- **matplotlib/seaborn**: Visualization (basic plots)
- **pyfaidx**: Fast FASTA indexing and retrieval
- **pysam**: BAM/CRAM handling for chromatin data (if needed)

### Data Requirements

- **Reference genomes**: Downloaded on-demand, cached locally (~3GB per genome)
- **ML models**: Bundled with package (~50-200MB)
- **Chromatin accessibility data**: Optional, user-provided or default datasets
- **Variant databases**: Downloaded/indexed as needed

### Performance Considerations

- **Guide extraction**: Should handle genes up to 2.5Mb (e.g., DMD) in seconds
- **ML inference**: Batch prediction for hundreds of guides in < 30 seconds
- **Off-target search**: Optimized indexing for genome-wide search in < 5 minutes
- **Memory footprint**: Should run on standard laptops (8GB RAM)

---

## Out of Scope (Not in MVP)

### Explicitly Excluded from Initial Release

- **Web interface or GUI**: Command-line and Python API only
- **Cloud deployment**: Local execution only (no hosted service)
- **Base editors or Prime editing**: Focus on traditional SpCas9/SaCas9
- **Multi-gene multiplexing**: Design for one gene/region at a time
- **HDR template design**: Off-target scoring only, no repair template generation
- **Experimental validation prediction**: No cell-type specific efficiency models
- **Real-time database updates**: Use static releases of variant databases
- **Interactive genome browser**: Export BED files for external browsers

### Future Considerations (Post-MVP)

- Additional Cas variants (Cas12a, Cas13)
- Multiplexed guide design for CRISPR screens
- Cell-type specific models
- HDR template design
- Integration with ordering platforms (e.g., Synthego, IDT)
- Web dashboard for visualization
- Cloud-based large-scale screening

---

## Success Criteria

### Technical Metrics
- Successful installation via pip on Linux/macOS/Windows
- Complete guide design for a typical gene in < 3 minutes
- On-target predictions correlate with experimental data (R² > 0.5)
- Off-target detection sensitivity > 95% for sites with ≤ 3 mismatches

### User Experience
- Single command to go from gene name to ranked guides
- Clear documentation with examples for common use cases
- Informative error messages for invalid inputs
- Reproducible results across runs

### Quality
- Comprehensive test coverage (>80%)
- Type hints throughout codebase
- CI/CD pipeline for automated testing
- Clear contribution guidelines

---

## Development Phases

### Phase 1: Core Guide Design (MVP)
- Input parsing and genome handling
- Guide extraction with quality filters
- On-target ML ensemble
- Basic ranking and CSV export
- CLI interface for single genes

### Phase 2: Off-Target Analysis
- Genome-wide off-target search
- Chromatin accessibility integration
- Enhanced ranking with specificity

### Phase 3: Variant Awareness
- dbSNP integration
- SNP disruption detection
- Population-specific filtering

### Phase 4: Polish and Release
- Visualization exports
- Complete documentation
- Performance optimization
- Published package on PyPI

---

## Key Design Principles

1. **Sensible defaults**: Work out-of-the-box for common use cases
2. **Progressive disclosure**: Simple interface for beginners, advanced options for experts
3. **Reproducibility**: Same inputs always produce same outputs
4. **Transparency**: Explain scoring decisions and quality flags
5. **Extensibility**: Easy to add new models, Cas variants, species
6. **Performance**: Optimize for interactive use (results in minutes, not hours)

---

## Package Structure (Logical)

```
crispex/
├── cli/              # Click-based command-line interface
├── api/              # Python API for programmatic use
├── core/
│   ├── guide.py      # Guide extraction and filtering
│   ├── genome.py     # Genome management and indexing
│   ├── models.py     # ML ensemble predictor
│   ├── offtarget.py  # Off-target search engine
│   ├── chromatin.py  # Accessibility scoring
│   └── snp.py        # Variant checking
├── data/
│   ├── models/       # Pre-trained ML models
│   └── configs/      # Species configurations, PAM sequences
├── utils/
│   ├── database.py   # Ensembl/NCBI API wrappers
│   ├── export.py     # Output formatters
│   └── viz.py        # Visualization functions
└── tests/            # Comprehensive test suite
```

---

## Example Workflow

```
User input: "Design guides for human BRCA1 gene"

Step 1: Fetch BRCA1 sequence from Ensembl
Step 2: Scan for NGG PAM sites
Step 3: Extract 20bp guides upstream of PAMs
Step 4: Filter by GC%, homopolymers, complexity
Step 5: Run ensemble ML models (DeepSpCas9, Azimaru, DeepCRISPR)
Step 6: Search genome for off-targets (≤3 mismatches)
Step 7: Score off-targets with chromatin accessibility
Step 8: Check guides against dbSNP variants
Step 9: Rank by efficiency + specificity + SNP status
Step 10: Export top 20 guides to CSV with visualization

Output: brca1_guides.csv, brca1_guides.json, brca1_plot.png
```

---

## Risk Mitigation

### Technical Risks
- **Large genome downloads**: Implement resumable downloads, compression
- **ML model size**: Use quantized models, lazy loading
- **Off-target search speed**: Pre-index genomes, use fast alignment tools (Bowtie2)
- **Database API limits**: Implement caching, retry logic, rate limiting

### Data Quality Risks
- **Genome version mismatches**: Clearly document and validate genome versions
- **Model generalization**: Ensemble approach mitigates single-model failures
- **Variant database staleness**: Document release versions, provide update mechanism

### User Adoption Risks
- **Installation complexity**: Minimize dependencies, provide Docker image
- **Learning curve**: Comprehensive docs with tutorials
- **Trust in predictions**: Transparent scoring, cite validation studies

---

## Compliance and Licensing

- **Open source license**: MIT (permissive, research-friendly)
- **Model licenses**: Ensure compatibility with open-source distribution
- **Database usage**: Comply with Ensembl/NCBI terms of service
- **Export controls**: Document any therapeutic design considerations

---

## Documentation Plan

1. **README**: Quick start, installation, basic example
2. **User Guide**: Comprehensive CLI and API documentation
3. **Tutorials**: Common workflows (knockout, knockin, screening)
4. **API Reference**: Auto-generated from docstrings
5. **Model Guide**: Explanation of scoring algorithms
6. **FAQ**: Troubleshooting, best practices
7. **Contributing**: Developer guidelines for extensions

---

## Initial Non-Goals

To maintain focus on core guide design functionality, the following are explicitly **not** goals for the initial release:

- Supporting base editors (ABE, CBE) or prime editors
- Wet-lab protocol generation
- Oligonucleotide ordering integration
- Real-time collaboration features
- Mobile/tablet interfaces
- Integration with LIMS systems
- Cost estimation for synthesis

These may be considered for future releases based on user feedback.

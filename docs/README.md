# Crispex Documentation

Project documentation and design specifications.

## Contents

### 📋 Project Planning Documents

**[scope.md](scope.md)** - Complete Project Vision
- Full feature specification
- Long-term goals and roadmap
- Ensemble ML models, chromatin analysis, SNP integration
- All planned capabilities for production version

**[mvp.md](mvp.md)** - Minimum Viable Product
- Simplified feature set for initial release
- Core workflow (gene → guides in <30 seconds)
- Single Azimuth model, basic off-target search
- What was actually built for v0.1.0

**[design.md](design.md)** - Technical Design Specification
- CLI and API interface design
- Architecture diagrams
- Data structures and workflows
- Implementation details

---

## Document Purpose

These documents guided the development of Crispex v0.1.0:

1. **scope.md** - Defined the complete vision
2. **mvp.md** - Narrowed to achievable first version
3. **design.md** - Specified exact implementation

**Current Status:** MVP (v0.1.0) complete and functional

---

## User Documentation

For **usage documentation**, see:
- **[../README.md](../README.md)** - Main package documentation
- **[../examples/README.md](../examples/README.md)** - Tutorials and examples
- **[../CONTRIBUTING.md](../CONTRIBUTING.md)** - Development guide

---

## Development Roadmap

See [scope.md](scope.md) for planned future features:
- Ensemble ML models (DeepSpCas9, DeepCRISPR)
- Full Azimuth gradient boosting model
- Chromatin accessibility analysis
- SNP-aware design
- Additional Cas variants (SaCas9, Cas12a)
- Web interface

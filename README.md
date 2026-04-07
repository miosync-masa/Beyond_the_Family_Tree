#Language as Genome — Analysis Code

**Paper:** *Language as Genome: Beyond the Family Tree: Historical Corridors Organize Lexical Borrowing Networks*

**Alternative Title:** *Language as Civilization Fossil: Climate, Food, and Faith as the Three Drivers of Linguistic Evolution*

---

## Overview

This repository contains the complete analysis pipeline for the SEED paper.
The code demonstrates that lexical borrowing patterns are better predicted by
historical contact corridors (trade routes, religious networks, colonial paths)
than by genealogical family-tree proximity, and that different corridors carry
distinct "nutrient bundles" (religion, food, material culture) through the
mycorrhizal network beneath the family tree.

### Core Findings

1. **Corridor > Genealogy**: Language pairs sharing a historical contact corridor
   exhibit 1.79× greater donor-overlap than pairs sharing only genealogical
   affiliation (Cliff's δ = 0.346, p = .002; permutation p < .0001).

2. **Genealogical control**: Tree distance explains R² = 0.0001 of borrowing
   overlap variance. 80% of corridor pairs fall in the top residual quartile
   (expected: 25%; enrichment = 3.2×; permutation p < .0001).

3. **Semantic domain specificity**: Corridors carry different nutrient bundles
   (all χ² p < .001):
   - Islamic Law corridor: Religion enriched 1.27× (χ² contribution = 55.8)
   - Mesoamerican corridor: Food enriched 1.33× (χ² contribution = 35.2)
   - Climate depleted in all corridors → climate sculpts locally, not transported

4. **Convergent borrowing**: 190 Arabic meanings independently settled in 3+
   Islamic corridor languages; 20 meanings in 6+ languages (including all days
   of the week, "the world," "the mosque," "the demon").

## Data Sources

| Database | Languages | Content | Source |
|----------|-----------|---------|--------|
| WOLD | 41 | ~1,460 meanings, borrowing status, donor languages | https://github.com/lexibank/wold |
| Glottolog | 8,000+ | Language classification paths (family → genus → language) | https://github.com/glottolog/glottolog-cldf |

### Data Setup

```bash
# Clone WOLD (World Loanword Database, CLDF format)
git clone https://github.com/lexibank/wold.git

# Clone Glottolog (classification data)
git clone https://github.com/glottolog/glottolog-cldf.git
```

All scripts assume these repositories are cloned as siblings in the working directory.

## Scripts (Execution Order)

### Phase 1: DNA Fragment Extraction

| # | Script | Section | What it does |
|---|--------|---------|-------------|
| 01 | `01_arabic_dna_extraction.py` | §3–5 | Extracts all Arabic-origin borrowings from WOLD (1,670 fragments across 17 languages). Maps al- prefix DNA distribution. Builds complete 41-language mycorrhizal network. Detects Stealth (immune-evasion) pathways where Arabic DNA enters through intermediary language capsules. |

### Phase 2: Corridor vs Genealogy

| # | Script | Section | What it does |
|---|--------|---------|-------------|
| 02 | `02_corridor_vs_family.py` | §4–5 | Tests core hypothesis: corridor topology > family tree for predicting borrowing overlap. Three-layer statistical design: descriptive stats → Mann-Whitney U + Cliff's delta → 10,000-iteration corridor-label permutation test. |
| 03 | `03_genealogical_control.py` | §5 | Computes pairwise Glottolog tree distances, fits baseline regression (overlap ~ tree_distance), extracts residuals. Tests corridor enrichment in positive residuals. Demonstrates R² = 0.0001 for genealogy, 80% corridor enrichment in top quartile. |

### Phase 3: Semantic Domain Analysis

| # | Script | Section | What it does |
|---|--------|---------|-------------|
| 04 | `04_semantic_domains.py` | §3, §6 | Classifies WOLD semantic fields into 6 domains (Food, Religion, Climate, Body, Social, Material). Tests domain enrichment per corridor via chi-square. Identifies convergent borrowing patterns (same meaning → multiple languages from same donor). |

## Key Results Summary

### Corridor vs Family Tree
- Same corridor (diff family): mean overlap = 124.9
- Same family: mean overlap = 69.9
- Neither: mean overlap = 18.5
- Corridor/Family ratio: 1.79×
- Mann-Whitney U: p = .002, Cliff's δ = 0.346 (medium)
- Permutation test: p < .0001 (10,000 iterations; max permuted diff = −14.4 vs observed +55.0)

### Genealogical Control
- Tree distance R² = 0.0001 (explains 0.01% of variance)
- Corridor pairs mean residual: +97.6
- Non-corridor pairs mean residual: −8.5
- Top quartile enrichment: 80% (expected 25%), 3.2× enrichment
- Residual permutation: p < .0001

### Semantic Domain Specificity
- Islamic Law corridor: Religion ↑ (1.27×), χ² = 82.9***
- Mesoamerican corridor: Food ↑ (1.33×), χ² = 74.4***
- Saharan Trade corridor: Religion ↑ (1.27×), χ² = 48.5***
- Sinosphere: Religion ↑ (1.20×), Social ↑ (1.25×), χ² = 38.3***
- Climate: depleted or neutral in all corridors (max 1.18×)

### Arabic Convergent Borrowing
- 7-language convergence: "the world" (dunia), "the time," all days of the week, "the demon," "the mosque"
- 190 meanings in 3+ languages, 108 in 4+, 51 in 5+, 20 in 6+

## Historical Contact Corridors

| Corridor | Languages | Historical basis |
|----------|-----------|-----------------|
| Indian Ocean | Swahili, Malagasy, Indonesian, Seychelles Creole | Maritime trade network |
| Saharan Trade | Hausa, Kanuri, Tarifiyt Berber, Swahili | Trans-Saharan caravan routes |
| Islamic Law Sphere | Swahili, Hausa, Kanuri, Berber, Indonesian, Bezhta, Archi, Malagasy | Islamic legal/religious network |
| Mesoamerican Colonial | Yaqui, Otomi, Tzotzil, Q'eqchi', Imbabura Quechua | Spanish colonial administration |
| Sinosphere | Japanese, Vietnamese, White Hmong, Mandarin, Thai | Chinese cultural/writing sphere |
| European Core | English, Dutch, Romanian, Lower Sorbian, Selice Romani | European linguistic contact zone |
| Caucasus Local | Bezhta, Archi | Dagestanian lingua franca area |
| Port City Chain (SE Asia) | Indonesian, Ceq Wong, Thai, Vietnamese | Southeast Asian maritime trade |

## Three Settlement Pathways

| Pathway | Mechanism | Biological analogy | Key example |
|---------|-----------|-------------------|-------------|
| **Force** | Conquest/colonization | Viral genome insertion | Spanish → 6 Mesoamerican languages |
| **Contagion** | Voluntary imitation via R₀ | Horizontal gene transfer | Chinese → Japanese (647 fragments) |
| **Stealth** | Intermediary language capsule | Immune evasion | Arabic sukkar → Italian → German → Czech → Romani "cukro" |

## Connection to IMT Architecture

| Paper | A=B premise | Hidden M |
|-------|-------------|----------|
| RBS | Signs are arbitrary | Body (articulatory constraints) |
| MBL | Meaning is in the sign | Cognitive lens |
| CPG | Official lexicon = all vocabulary | Covert meaning pathways |
| SSI | Sign sharing = experience sharing | Experience variance |
| **SEED** | **Languages diverge from proto-language** | **Contact-mixing via corridor topology** |

## Dependencies

```
Python 3.8+
Standard library only (csv, math, collections, random)
No external packages required.
```

## Citation

[To be added upon publication]

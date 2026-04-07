#!/usr/bin/env python3
"""
SEED: Language as Genome
Script 01: Arabic DNA Fragment Extraction & Mycorrhizal Network Mapping

Extracts all Arabic-origin borrowings from WOLD (World Loanword Database),
identifies al- prefix DNA fragments, maps the Arabic mycorrhizal network
across recipient languages, and builds the complete donor-recipient
network for all 41 WOLD languages.

Data: WOLD (lexibank/wold) - 41 languages, ~1,460 meanings
Output: Arabic DNA distribution, al- prefix tracking, top mycorrhizal channels,
        DNA source diversity per recipient language

Section: §3 (Three-Layer Separation), §4 (Against Stammbaum), §5 (Methodology)
"""

import csv
from collections import Counter, defaultdict

# =============================================================================
# DATA LOADING
# =============================================================================

def load_languages(path='wold/cldf/languages.csv'):
    langs = {}
    with open(path, 'r') as f:
        for row in csv.DictReader(f):
            langs[row['ID']] = {
                'name': row['Name'],
                'lat': row.get('Latitude', ''),
                'lon': row.get('Longitude', ''),
                'family': row.get('Family', ''),
                'macroarea': row.get('Macroarea', ''),
            }
    return langs


def load_borrowings(path='wold/cldf/borrowings.csv'):
    borrowings = {}
    with open(path, 'r') as f:
        for row in csv.DictReader(f):
            borrowings[row['Target_Form_ID']] = row
    return borrowings


def load_forms(path='wold/cldf/forms.csv'):
    forms = {}
    with open(path, 'r') as f:
        for row in csv.DictReader(f):
            forms[row['ID']] = row
    return forms


def load_parameters(path='wold/cldf/parameters.csv'):
    params = {}
    with open(path, 'r') as f:
        for row in csv.DictReader(f):
            params[row['ID']] = row.get('Name', '')
    return params


# =============================================================================
# ANALYSIS 1: ARABIC DNA FRAGMENT EXTRACTION
# =============================================================================

def extract_arabic_dna(forms, borrowings):
    """Extract all Arabic-origin borrowings across WOLD languages."""
    arabic_forms = []
    for fid, form in forms.items():
        if fid not in borrowings:
            continue
        b = borrowings[fid]
        src = (b.get('Source_languoid', '') + ' ' +
               b.get('Source_languoid_glottocode', '')).lower()
        if 'arab' in src:
            arabic_forms.append({
                'id': fid,
                'language': form['Language_ID'],
                'form': form['Form'],
                'param_id': form['Parameter_ID'],
                'borrowed_score': float(form['Borrowed_score'])
                    if form.get('Borrowed_score') else 0,
                'source_word': b.get('Source_word', ''),
                'source_lang': b.get('Source_languoid', ''),
            })
    return arabic_forms


def extract_al_prefix(arabic_forms):
    """Extract al- definite article DNA fragments."""
    return [f for f in arabic_forms
            if f['source_word'].lower().startswith('al')
            or f['form'].lower().startswith('al')]


# =============================================================================
# ANALYSIS 2: COMPLETE MYCORRHIZAL NETWORK
# =============================================================================

def build_network(forms, borrowings):
    """Build donor → recipient borrowing network."""
    network = defaultdict(lambda: defaultdict(int))
    for fid, form in forms.items():
        if fid not in borrowings:
            continue
        b = borrowings[fid]
        donor = b.get('Source_languoid', '')
        recipient = form['Language_ID']
        if donor:
            network[donor][recipient] += 1
    return network


def compute_diversity(network):
    """Compute DNA source diversity per recipient language."""
    diversity = defaultdict(set)
    totals = defaultdict(int)
    for donor, recipients in network.items():
        for recip, cnt in recipients.items():
            diversity[recip].add(donor)
            totals[recip] += cnt
    return diversity, totals


# =============================================================================
# ANALYSIS 3: STEALTH PATHWAY DETECTION
# =============================================================================

def detect_stealth(forms, borrowings):
    """Detect Stealth (immune-evasion) pathways:
    Words with Arabic origin in loan_history but non-Arabic immediate donor."""
    stealth = []
    for fid, form in forms.items():
        hist = ((form.get('loan_history', '') or '') + ' ' +
                (form.get('etymological_note', '') or ''))
        if 'arab' not in hist.lower() and 'Arabic' not in hist:
            continue
        if fid not in borrowings:
            continue
        b = borrowings[fid]
        donor = b.get('Source_languoid', '')
        if donor and 'arab' not in donor.lower():
            stealth.append({
                'language': form['Language_ID'],
                'form': form['Form'],
                'immediate_donor': donor,
                'history': hist.strip()[:200],
            })
    return stealth


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("Loading WOLD data...")
    langs = load_languages()
    borrowings = load_borrowings()
    forms = load_forms()
    params = load_parameters()

    # --- TOP DONOR LANGUAGES ---
    print("\n" + "=" * 70)
    print("TOP 20 DONOR LANGUAGES (by borrowing count)")
    print("=" * 70)
    donor_counts = Counter()
    for fid, form in forms.items():
        if fid in borrowings:
            donor = borrowings[fid].get('Source_languoid', '')
            if donor:
                donor_counts[donor] += 1
    for lang, cnt in donor_counts.most_common(20):
        print(f"  {lang:30s} {cnt:5d}")

    # --- ARABIC DNA ---
    arabic_forms = extract_arabic_dna(forms, borrowings)
    print(f"\n{'=' * 70}")
    print(f"ARABIC-ORIGIN DNA FRAGMENTS: {len(arabic_forms)} total")
    print("=" * 70)
    lang_counts = Counter(f['language'] for f in arabic_forms)
    print(f"\nBy recipient language:")
    for lang, cnt in lang_counts.most_common():
        l = langs.get(lang, {})
        print(f"  {lang:25s} [{l.get('macroarea',''):10s} | "
              f"{l.get('family',''):20s}] : {cnt:4d}")

    # --- AL- PREFIX ---
    al_forms = extract_al_prefix(arabic_forms)
    print(f"\n{'=' * 70}")
    print(f"AL- PREFIX DNA FRAGMENTS: {len(al_forms)} total")
    print("=" * 70)
    al_lang = Counter(f['language'] for f in al_forms)
    for lang, cnt in al_lang.most_common():
        print(f"  {lang:25s} {cnt:5d}")

    # --- SEMANTIC DOMAINS ---
    print(f"\n{'=' * 70}")
    print("SEMANTIC DOMAINS OF ARABIC DNA (top 30)")
    print("=" * 70)
    meanings = Counter()
    for f in arabic_forms:
        m = params.get(f['param_id'], f['param_id'])
        meanings[m] += 1
    for m, cnt in meanings.most_common(30):
        print(f"  {m:40s} {cnt:3d}")

    # --- MYCORRHIZAL NETWORK ---
    network = build_network(forms, borrowings)
    print(f"\n{'=' * 70}")
    print("ARABIC MYCORRHIZAL NETWORK")
    print("=" * 70)
    for donor in ['Arabic', 'Classical Arabic']:
        if donor in network:
            print(f"\n[{donor}] →")
            for recip, cnt in sorted(network[donor].items(),
                                     key=lambda x: -x[1]):
                l = langs.get(recip, {})
                print(f"  → {recip:25s} [{l.get('macroarea',''):10s} | "
                      f"{l.get('family',''):20s}] : {cnt:4d}")

    # --- TOP FLOWS ---
    print(f"\n{'=' * 70}")
    print("TOP 30 MYCORRHIZAL CHANNELS")
    print("=" * 70)
    flows = []
    for donor, recipients in network.items():
        for recip, cnt in recipients.items():
            flows.append((donor, recip, cnt))
    flows.sort(key=lambda x: -x[2])
    for donor, recip, cnt in flows[:30]:
        print(f"  {donor:25s} → {recip:25s} : {cnt:4d}")

    # --- DIVERSITY ---
    diversity, totals = compute_diversity(network)
    print(f"\n{'=' * 70}")
    print("DNA SOURCE DIVERSITY (donors per recipient)")
    print("=" * 70)
    for recip in sorted(diversity, key=lambda x: -len(diversity[x])):
        l = langs.get(recip, {})
        print(f"  {recip:25s} [{l.get('macroarea',''):10s}] : "
              f"{len(diversity[recip]):3d} donors, "
              f"{totals[recip]:5d} fragments")

    # --- STEALTH ---
    stealth = detect_stealth(forms, borrowings)
    print(f"\n{'=' * 70}")
    print(f"STEALTH PATHWAY DETECTION: {len(stealth)} cases")
    print("=" * 70)
    for s in stealth:
        print(f"  {s['language']:20s} | {s['form']:20s} | "
              f"donor: {s['immediate_donor']:15s}")
        print(f"    {s['history'][:100]}")


if __name__ == '__main__':
    main()

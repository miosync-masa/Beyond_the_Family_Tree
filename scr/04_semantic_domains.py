#!/usr/bin/env python3
"""
SEED: Language as Genome
Script 04: Semantic Domain Analysis

Classifies WOLD borrowings into semantic domains (Food, Religion, Climate,
Body, Social, Material) and tests whether corridors carry different
"nutrient bundles" through the mycorrhizal network.

Key findings:
  - Islamic Law corridor: Religion enriched 1.27x (χ²=82.9, p<.001)
  - Mesoamerican corridor: Food enriched 1.33x (χ²=74.4, p<.001)
  - Climate depleted in all corridors → climate is not transported,
    it sculpts locally (supports two-layer model)
  - 190 Arabic meanings converge in 3+ Islamic corridor languages
  - Days of the week: 7-language convergent borrowing from Arabic

Data: WOLD borrowings × WOLD semantic fields (24 fields → 6 domains)
Output: Domain enrichment by corridor, chi-square tests,
        convergent borrowing analysis

Section: §3 (Civilization Triangle), §6 (Contagion Model), Results 3
"""

import csv
from collections import defaultdict, Counter

# =============================================================================
# SEMANTIC DOMAIN CLASSIFICATION
# =============================================================================

DOMAIN_MAP = {
    # FOOD & TRADE (what you eat = who you traded with)
    '5': 'FOOD',      # Food and drink
    '8': 'FOOD',      # Agriculture and vegetation
    '3': 'FOOD',      # Animals (livestock, hunting)
    # RELIGION & GOVERNANCE (what you believe = how you speak)
    '22': 'RELIGION',  # Religion and belief
    '21': 'RELIGION',  # Law and jurisprudence
    '16': 'RELIGION',  # Emotions and values (soul, spirit)
    '14': 'RELIGION',  # Time and calendar (days of week)
    # CLIMATE & ENVIRONMENT (where you live = how you sound)
    '1': 'CLIMATE',    # Physical world (land, water, sky, weather)
    # BODY (control domain - universal, less borrowable)
    '4': 'BODY',       # Body
    '15': 'BODY',      # Sense perception
    # SOCIAL/MATERIAL CULTURE
    '19': 'SOCIAL',    # Social and political relations
    '20': 'SOCIAL',    # Warfare and hunting
    '6': 'MATERIAL',   # Clothing and grooming
    '7': 'MATERIAL',   # House and dwelling
    '9': 'MATERIAL',   # Basic actions and technology
    '23': 'MATERIAL',  # Modern world
}

CORRIDORS = {
    'Indian Ocean': [
        'Swahili', 'Malagasy', 'Indonesian', 'SeychellesCreole'],
    'Saharan Trade': [
        'Hausa', 'Kanuri', 'TarifiytBerber', 'Swahili'],
    'Islamic Law': [
        'Swahili', 'Hausa', 'Kanuri', 'TarifiytBerber',
        'Indonesian', 'Bezhta', 'Archi', 'Malagasy'],
    'Mesoamerican': [
        'Yaqui', 'Otomi', 'ZinacantanTzotzil',
        'Qeqchi', 'ImbaburaQuechua'],
    'Sinosphere': [
        'Japanese', 'Vietnamese', 'WhiteHmong',
        'MandarinChinese', 'Thai'],
    'European Core': [
        'English', 'Dutch', 'Romanian',
        'LowerSorbian', 'SeliceRomani'],
}

CORE_DOMAINS = ['FOOD', 'RELIGION', 'CLIMATE', 'BODY', 'SOCIAL', 'MATERIAL']


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    # Load data
    borrowings = {}
    with open('wold/cldf/borrowings.csv', 'r') as f:
        for row in csv.DictReader(f):
            borrowings[row['Target_Form_ID']] = row

    params = {}
    with open('wold/cldf/parameters.csv', 'r') as f:
        for row in csv.DictReader(f):
            params[row['ID']] = row.get('Name', '')

    # Build domain counts per corridor
    corridor_domains = defaultdict(lambda: defaultdict(int))
    corridor_total = defaultdict(int)
    global_domains = defaultdict(int)
    global_total = 0

    with open('wold/cldf/forms.csv', 'r') as f:
        for row in csv.DictReader(f):
            if row['ID'] not in borrowings:
                continue
            field = row['Parameter_ID'].split('-')[0]
            domain = DOMAIN_MAP.get(field)
            if domain is None:
                continue

            global_domains[domain] += 1
            global_total += 1

            lang = row['Language_ID']
            for cname, members in CORRIDORS.items():
                if lang in members:
                    corridor_domains[cname][domain] += 1
                    corridor_total[cname] += 1

    # =========================================================================
    # DOMAIN DISTRIBUTION TABLE
    # =========================================================================
    print("=" * 90)
    print("SEMANTIC DOMAIN ANALYSIS OF BORROWING BY CORRIDOR")
    print("=" * 90)
    print(f"\n{'Corridor':20s}", end='')
    for d in CORE_DOMAINS:
        print(f" {d:>10s}", end='')
    print(f" {'TOTAL':>8s}")
    print("-" * 90)

    for cname in sorted(CORRIDORS.keys()):
        total = corridor_total[cname]
        print(f"{cname:20s}", end='')
        for d in CORE_DOMAINS:
            cnt = corridor_domains[cname][d]
            pct = cnt / total * 100 if total else 0
            print(f" {cnt:4d}({pct:4.1f}%)", end='')
        print(f" {total:8d}")

    print(f"\n{'GLOBAL':20s}", end='')
    for d in CORE_DOMAINS:
        cnt = global_domains[d]
        pct = cnt / global_total * 100 if global_total else 0
        print(f" {cnt:4d}({pct:4.1f}%)", end='')
    print(f" {global_total:8d}")

    # =========================================================================
    # ENRICHMENT TABLE
    # =========================================================================
    print(f"\n\n{'=' * 90}")
    print("DOMAIN ENRICHMENT BY CORRIDOR (ratio vs global baseline)")
    print("=" * 90)
    print(f"\n{'Corridor':20s}", end='')
    for d in CORE_DOMAINS:
        print(f" {d:>10s}", end='')
    print()
    print("-" * 90)

    for cname in sorted(CORRIDORS.keys()):
        total = corridor_total[cname]
        print(f"{cname:20s}", end='')
        for d in CORE_DOMAINS:
            local_pct = (corridor_domains[cname][d] / total * 100
                         if total else 0)
            global_pct = (global_domains[d] / global_total * 100
                          if global_total else 0)
            ratio = local_pct / global_pct if global_pct else 0
            marker = " **" if ratio > 1.3 else (
                " --" if ratio < 0.7 else "   ")
            print(f" {ratio:6.2f}x{marker}", end='')
        print()

    print("\n  ** = enriched (>1.3x), -- = depleted (<0.7x)")

    # =========================================================================
    # CHI-SQUARE TESTS
    # =========================================================================
    test_domains = ['FOOD', 'RELIGION', 'CLIMATE', 'BODY']

    print(f"\n\n{'=' * 90}")
    print("CHI-SQUARE GOODNESS-OF-FIT TESTS")
    print("=" * 90)

    for cname in sorted(CORRIDORS.keys()):
        total = corridor_total[cname]
        chi2 = 0
        print(f"\n  {cname}:")
        for d in test_domains:
            o = corridor_domains[cname][d]
            global_pct = global_domains[d] / global_total if global_total else 0
            e = global_pct * total
            contrib = (o - e) ** 2 / e if e > 0 else 0
            chi2 += contrib
            direction = "+" if o > e else "-"
            print(f"    {d:12s}: obs={o:4d}, exp={e:6.1f}, "
                  f"{direction} chi2_contrib={contrib:.1f}")

        df = len(test_domains) - 1
        if chi2 > 16.27:
            sig = "p < .001 ***"
        elif chi2 > 11.34:
            sig = "p < .01 **"
        elif chi2 > 7.81:
            sig = "p < .05 *"
        else:
            sig = "n.s."
        print(f"    chi2 = {chi2:.1f}, df = {df}, {sig}")

    # =========================================================================
    # CONVERGENT BORROWING ANALYSIS (Islamic corridor)
    # =========================================================================
    print(f"\n\n{'=' * 90}")
    print("CONVERGENT BORROWING: Arabic → Islamic corridor")
    print("=" * 90)

    islamic_langs = set(CORRIDORS['Islamic Law'])
    meaning_lang = defaultdict(lambda: defaultdict(list))

    with open('wold/cldf/forms.csv', 'r') as f:
        for row in csv.DictReader(f):
            if row['ID'] not in borrowings:
                continue
            b = borrowings[row['ID']]
            lang = row['Language_ID']
            if lang not in islamic_langs:
                continue
            src = b.get('Source_languoid', '')
            if 'arab' not in src.lower():
                continue
            meaning = params.get(row['Parameter_ID'],
                                 row['Parameter_ID'])
            meaning_lang[meaning][lang].append(row['Form'])

    convergent = []
    for meaning, langs_dict in sorted(meaning_lang.items(),
                                      key=lambda x: -len(x[1])):
        n = len(langs_dict)
        if n >= 3:
            lang_forms = [f"{l}:{','.join(fs)}"
                          for l, fs in sorted(langs_dict.items())]
            convergent.append((meaning, n, lang_forms))

    print(f"\nMeanings with 3+ language convergence: {len(convergent)}")
    print(f"Meanings with 4+: "
          f"{sum(1 for _, n, _ in convergent if n >= 4)}")
    print(f"Meanings with 5+: "
          f"{sum(1 for _, n, _ in convergent if n >= 5)}")
    print(f"Meanings with 6+: "
          f"{sum(1 for _, n, _ in convergent if n >= 6)}")
    print(f"Meanings with 7:  "
          f"{sum(1 for _, n, _ in convergent if n >= 7)}")

    print(f"\n--- 7-language convergent borrowings ---")
    for meaning, n, lang_forms in convergent:
        if n >= 7:
            print(f"\n  {meaning} ({n} languages):")
            for lf in lang_forms:
                print(f"    {lf}")


if __name__ == '__main__':
    main()

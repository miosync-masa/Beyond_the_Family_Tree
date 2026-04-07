#!/usr/bin/env python3
"""
SEED: Language as Genome
Script 02: Corridor vs Family Tree Hypothesis Test

Tests the core hypothesis: lexical borrowing overlap is better predicted
by historical contact corridor membership than by genealogical affiliation.

Three-layer statistical design (following Muni's recommendation):
  Layer 1: Descriptive statistics (mean, median, IQR, N)
  Layer 2: Mann-Whitney U + Cliff's delta (effect size)
  Layer 3: Corridor-label permutation test (10,000 iterations)

Data: WOLD borrowings × WOLD language families
Output: Corridor/Family/Neither overlap comparison, significance tests

Section: §4 (Against Stammbaum), §5 (Methodology STEP 1-2)
"""

import csv
import math
import random
from collections import defaultdict
from itertools import combinations

# =============================================================================
# DATA LOADING
# =============================================================================

def load_data():
    langs = {}
    with open('wold/cldf/languages.csv', 'r') as f:
        for row in csv.DictReader(f):
            langs[row['ID']] = {
                'family': row.get('Family', ''),
                'macroarea': row.get('Macroarea', ''),
            }

    borrowings = {}
    with open('wold/cldf/borrowings.csv', 'r') as f:
        for row in csv.DictReader(f):
            borrowings[row['Target_Form_ID']] = row

    lang_borrowing = defaultdict(lambda: defaultdict(int))
    with open('wold/cldf/forms.csv', 'r') as f:
        for row in csv.DictReader(f):
            if row['ID'] in borrowings:
                b = borrowings[row['ID']]
                donor = b.get('Source_languoid', '')
                recip = row['Language_ID']
                if donor:
                    lang_borrowing[recip][donor] += 1

    return langs, lang_borrowing


# =============================================================================
# CORRIDOR DEFINITIONS
# =============================================================================

CORRIDORS = {
    'Indian Ocean': [
        'Swahili', 'Malagasy', 'Indonesian', 'SeychellesCreole'],
    'Saharan Trade': [
        'Hausa', 'Kanuri', 'TarifiytBerber', 'Swahili'],
    'Islamic Law Sphere': [
        'Swahili', 'Hausa', 'Kanuri', 'TarifiytBerber',
        'Indonesian', 'Bezhta', 'Archi', 'Malagasy'],
    'Mesoamerican Colonial': [
        'Yaqui', 'Otomi', 'ZinacantanTzotzil',
        'Qeqchi', 'ImbaburaQuechua'],
    'Sinosphere': [
        'Japanese', 'Vietnamese', 'WhiteHmong',
        'MandarinChinese', 'Thai'],
    'European Core': [
        'English', 'Dutch', 'Romanian',
        'LowerSorbian', 'SeliceRomani'],
    'Caucasus Local': [
        'Bezhta', 'Archi'],
    'Port City Chain SE Asia': [
        'Indonesian', 'CeqWong', 'Thai', 'Vietnamese'],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def donor_overlap(lang_borrowing, l1, l2):
    """Compute weighted minimum donor overlap between two languages."""
    d1 = set(lang_borrowing[l1].keys())
    d2 = set(lang_borrowing[l2].keys())
    shared = d1 & d2
    return sum(min(lang_borrowing[l1][d], lang_borrowing[l2][d])
               for d in shared)


def shared_corridors(l1, l2):
    """Return list of corridors shared by two languages."""
    return [n for n, m in CORRIDORS.items() if l1 in m and l2 in m]


def descriptive_stats(arr, name):
    """Compute and print descriptive statistics."""
    arr_s = sorted(arr)
    n = len(arr_s)
    mean = sum(arr_s) / n
    median = (arr_s[n // 2] if n % 2
              else (arr_s[n // 2 - 1] + arr_s[n // 2]) / 2)
    q1 = arr_s[n // 4]
    q3 = arr_s[3 * n // 4]
    iqr = q3 - q1
    print(f"  {name:45s} | N={n:4d} | mean={mean:7.1f} | "
          f"median={median:6.1f} | IQR=[{q1}, {q3}] ({iqr})")
    return mean, median


# =============================================================================
# STATISTICAL TESTS
# =============================================================================

def mann_whitney_u(x, y):
    """Manual Mann-Whitney U test (one-tailed: x > y)."""
    nx, ny = len(x), len(y)
    u = 0
    for xi in x:
        for yj in y:
            if xi > yj:
                u += 1
            elif xi == yj:
                u += 0.5
    mu = nx * ny / 2
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12)
    z_directed = (u - mu) / sigma if sigma > 0 else 0
    p_directed = 0.5 * math.erfc(z_directed / math.sqrt(2))
    return min(u, nx * ny - u), z_directed, p_directed


def cliffs_delta(x, y):
    """Cliff's delta effect size."""
    nx, ny = len(x), len(y)
    more = sum(1 for xi in x for yj in y if xi > yj)
    less = sum(1 for xi in x for yj in y if xi < yj)
    return (more - less) / (nx * ny)


def interpret_cliffs(d):
    ad = abs(d)
    if ad < 0.147:
        return "negligible"
    elif ad < 0.33:
        return "small"
    elif ad < 0.474:
        return "medium"
    else:
        return "large"


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    print("Loading data...")
    langs, lang_borrowing = load_data()
    wold_langs = list(langs.keys())

    # --- CLASSIFY ALL PAIRS ---
    group_corridor = []
    group_family = []
    group_neither = []

    for l1, l2 in combinations(wold_langs, 2):
        f1, f2 = langs[l1]['family'], langs[l2]['family']
        corrs = shared_corridors(l1, l2)
        ov = donor_overlap(lang_borrowing, l1, l2)
        same_fam = (f1 and f2 and f1 == f2)
        has_corr = len(corrs) > 0

        if has_corr and not same_fam:
            group_corridor.append(ov)
        elif same_fam:
            group_family.append(ov)
        else:
            group_neither.append(ov)

    # =========================================================================
    # LAYER 1: DESCRIPTIVE STATISTICS
    # =========================================================================
    print("\n" + "=" * 90)
    print("LAYER 1: DESCRIPTIVE STATISTICS")
    print("=" * 90)
    m_c, md_c = descriptive_stats(
        group_corridor, "Same corridor, different family")
    m_f, md_f = descriptive_stats(
        group_family, "Same family")
    m_n, md_n = descriptive_stats(
        group_neither, "Neither")

    print(f"\n  Corridor / Family ratio: {m_c / max(m_f, 0.01):.2f}x")
    print(f"  Corridor / Neither ratio: {m_c / max(m_n, 0.01):.2f}x")
    print(f"  Family / Neither ratio: {m_f / max(m_n, 0.01):.2f}x")

    # =========================================================================
    # LAYER 2: MANN-WHITNEY U + CLIFF'S DELTA
    # =========================================================================
    print("\n" + "=" * 90)
    print("LAYER 2: MANN-WHITNEY U + CLIFF'S DELTA")
    print("=" * 90)

    comparisons = [
        ("Corridor vs Family", group_corridor, group_family),
        ("Corridor vs Neither", group_corridor, group_neither),
        ("Family vs Neither", group_family, group_neither),
    ]
    for name, g1, g2 in comparisons:
        u, z, p = mann_whitney_u(g1, g2)
        cd = cliffs_delta(g1, g2)
        interp = interpret_cliffs(cd)
        print(f"\n  {name}")
        print(f"    U = {u:.0f}, z = {z:.3f}, p = {p:.2e}")
        print(f"    Cliff's delta = {cd:.3f} ({interp})")

    # =========================================================================
    # LAYER 3: CORRIDOR-LABEL PERMUTATION TEST
    # =========================================================================
    print("\n" + "=" * 90)
    print("LAYER 3: CORRIDOR-LABEL PERMUTATION TEST (10,000 iterations)")
    print("=" * 90)

    obs_diff_cf = m_c - m_f
    obs_diff_cn = m_c - m_n

    random.seed(42)
    N_PERM = 10000
    perm_diffs_cf = []
    perm_diffs_cn = []

    all_pairs = list(combinations(wold_langs, 2))

    # Pre-compute overlaps
    overlap_cache = {}
    for l1, l2 in all_pairs:
        ov = donor_overlap(lang_borrowing, l1, l2)
        overlap_cache[(l1, l2)] = ov
        overlap_cache[(l2, l1)] = ov

    for i in range(N_PERM):
        # Shuffle corridor membership
        shuffled = list(wold_langs)
        random.shuffle(shuffled)
        perm_corridor_langs = defaultdict(set)
        idx = 0
        for cname, members in CORRIDORS.items():
            for _ in range(len(members)):
                if idx < len(shuffled):
                    perm_corridor_langs[shuffled[idx]].add(cname)
                    idx += 1

        perm_corr, perm_fam, perm_neither = [], [], []
        for l1, l2 in all_pairs:
            f1, f2 = langs[l1]['family'], langs[l2]['family']
            same_fam = (f1 and f2 and f1 == f2)
            shared_perm = (perm_corridor_langs[l1] &
                           perm_corridor_langs[l2])
            has_corr = len(shared_perm) > 0
            ov = overlap_cache.get((l1, l2), 0)

            if has_corr and not same_fam:
                perm_corr.append(ov)
            elif same_fam:
                perm_fam.append(ov)
            else:
                perm_neither.append(ov)

        pm_c = sum(perm_corr) / max(len(perm_corr), 1)
        pm_f = sum(perm_fam) / max(len(perm_fam), 1)
        pm_n = sum(perm_neither) / max(len(perm_neither), 1)
        perm_diffs_cf.append(pm_c - pm_f)
        perm_diffs_cn.append(pm_c - pm_n)

    p_cf = sum(1 for d in perm_diffs_cf if d >= obs_diff_cf) / N_PERM
    p_cn = sum(1 for d in perm_diffs_cn if d >= obs_diff_cn) / N_PERM

    print(f"\n  Corridor vs Family:")
    print(f"    Observed diff: {obs_diff_cf:.1f}")
    print(f"    Permutation p-value: {p_cf:.4f}")
    print(f"    Permuted max: {max(perm_diffs_cf):.1f}")

    print(f"\n  Corridor vs Neither:")
    print(f"    Observed diff: {obs_diff_cn:.1f}")
    print(f"    Permutation p-value: {p_cn:.4f}")
    print(f"    Permuted max: {max(perm_diffs_cn):.1f}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 90)
    print("FINAL SUMMARY")
    print("=" * 90)
    print(f"""
  DESCRIPTIVE:
    Same corridor (diff family):  mean={m_c:.1f}, median={md_c:.1f}, N={len(group_corridor)}
    Same family:                  mean={m_f:.1f}, median={md_f:.1f}, N={len(group_family)}
    Neither:                      mean={m_n:.1f}, median={md_n:.1f}, N={len(group_neither)}
    Corridor / Family ratio:      {m_c / max(m_f, 0.01):.2f}x

  MANN-WHITNEY U + CLIFF'S DELTA:
    Corridor > Family:  delta = {cliffs_delta(group_corridor, group_family):.3f}
    Corridor > Neither: delta = {cliffs_delta(group_corridor, group_neither):.3f}

  PERMUTATION TEST ({N_PERM} iterations):
    Corridor vs Family:  p = {p_cf:.4f}
    Corridor vs Neither: p = {p_cn:.4f}
""")


if __name__ == '__main__':
    main()

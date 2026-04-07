#!/usr/bin/env python3
"""
SEED: Language as Genome
Script 03: Genealogical Control & Residual Analysis

Tests whether corridor effects survive genealogical control.
Computes pairwise tree distance from Glottolog classification paths,
fits baseline regression (overlap ~ tree_distance), extracts residuals,
and tests whether corridor pairs are enriched in positive residuals.

Key finding: R² = 0.0001 — tree distance explains virtually nothing.
80% of corridor pairs fall in the top residual quartile (expected: 25%).
Permutation p < 0.0001.

Data: WOLD borrowings × Glottolog classification
Output: Regression statistics, residual ranking, corridor enrichment

Section: §5 (Methodology STEP 1-3), Results 2
"""

import csv
import math
import random
from collections import defaultdict
from itertools import combinations

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
# DATA LOADING
# =============================================================================

def load_wold_glottocodes():
    wold_gc = {}
    with open('wold/cldf/languages.csv', 'r') as f:
        for row in csv.DictReader(f):
            wold_gc[row['ID']] = row.get('Glottocode', '')
    return wold_gc


def load_glottolog_classification():
    classification = {}
    with open('glottolog-cldf/cldf/values.csv', 'r') as f:
        for row in csv.DictReader(f):
            if row['Parameter_ID'] == 'classification':
                gc = row['Language_ID']
                path = row['Value']
                classification[gc] = path.split('/') if path else []
    return classification


def load_borrowing_data():
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
    return lang_borrowing


# =============================================================================
# TREE DISTANCE COMPUTATION
# =============================================================================

def tree_distance(path1, path2):
    """Compute tree distance as sum of steps from each node to LCA."""
    lca_depth = 0
    for a, b in zip(path1, path2):
        if a == b:
            lca_depth += 1
        else:
            break
    d1 = len(path1) - lca_depth
    d2 = len(path2) - lca_depth
    return d1 + d2, lca_depth


def donor_overlap(lang_borrowing, l1, l2):
    d1 = set(lang_borrowing[l1].keys())
    d2 = set(lang_borrowing[l2].keys())
    shared = d1 & d2
    return sum(min(lang_borrowing[l1][d], lang_borrowing[l2][d])
               for d in shared)


def shared_corridors(l1, l2):
    return [n for n, m in CORRIDORS.items() if l1 in m and l2 in m]


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    print("Loading data...")
    wold_gc = load_wold_glottocodes()
    classification = load_glottolog_classification()
    lang_borrowing = load_borrowing_data()

    # Build classification paths for WOLD languages
    wold_paths = {}
    for wid, gc in wold_gc.items():
        path = classification.get(gc, [])
        wold_paths[wid] = path + [gc]

    print(f"\nClassification paths for {len(wold_paths)} WOLD languages:")
    for wid, path in sorted(wold_paths.items()):
        print(f"  {wid:25s} ({wold_gc[wid]}) depth={len(path):2d}")

    # =========================================================================
    # BUILD PAIR DATA
    # =========================================================================
    wold_list = list(wold_paths.keys())
    pairs = []
    for l1, l2 in combinations(wold_list, 2):
        td, lca = tree_distance(wold_paths[l1], wold_paths[l2])
        ov = donor_overlap(lang_borrowing, l1, l2)
        corrs = shared_corridors(l1, l2)
        pairs.append({
            'l1': l1, 'l2': l2,
            'tree_dist': td, 'lca_depth': lca,
            'overlap': ov,
            'has_corridor': len(corrs) > 0,
            'corridors': corrs,
        })

    # =========================================================================
    # BASELINE REGRESSION: overlap ~ tree_distance
    # =========================================================================
    n = len(pairs)
    x = [p['tree_dist'] for p in pairs]
    y = [p['overlap'] for p in pairs]

    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((xi - mx) ** 2 for xi in x)
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    slope = sxy / sxx if sxx else 0
    intercept = my - slope * mx

    ss_res = sum((yi - (intercept + slope * xi)) ** 2
                 for xi, yi in zip(x, y))
    ss_tot = sum((yi - my) ** 2 for yi in y)
    r_sq = 1 - ss_res / ss_tot if ss_tot else 0

    print(f"\n{'=' * 80}")
    print("BASELINE REGRESSION: overlap ~ tree_distance")
    print("=" * 80)
    print(f"  slope     = {slope:.3f}")
    print(f"  intercept = {intercept:.3f}")
    print(f"  R²        = {r_sq:.4f}")
    print(f"  N pairs   = {n}")

    # =========================================================================
    # COMPUTE RESIDUALS
    # =========================================================================
    for p in pairs:
        predicted = intercept + slope * p['tree_dist']
        p['residual'] = p['overlap'] - predicted

    # =========================================================================
    # TOP 20 POSITIVE RESIDUALS (mycorrhizal signal)
    # =========================================================================
    pairs_sorted = sorted(pairs, key=lambda p: -p['residual'])
    print(f"\n{'=' * 80}")
    print("TOP 20 POSITIVE RESIDUALS (= mycorrhizal signal)")
    print("=" * 80)
    header = (f"  {'L1':20s} {'L2':20s} {'dist':>5s} {'overlap':>8s} "
              f"{'predicted':>10s} {'residual':>9s} {'corridor':>8s} corridors")
    print(header)
    for p in pairs_sorted[:20]:
        corr_str = ','.join(p['corridors']) if p['corridors'] else '-'
        pred = intercept + slope * p['tree_dist']
        print(f"  {p['l1']:20s} {p['l2']:20s} {p['tree_dist']:5d} "
              f"{p['overlap']:8d} {pred:10.1f} {p['residual']:9.1f} "
              f"{'YES' if p['has_corridor'] else 'NO':>8s} {corr_str}")

    # =========================================================================
    # RESIDUAL ANALYSIS: Corridor vs Non-corridor
    # =========================================================================
    corridor_resid = [p['residual'] for p in pairs if p['has_corridor']]
    no_corridor_resid = [p['residual'] for p in pairs
                         if not p['has_corridor']]

    mean_c = sum(corridor_resid) / len(corridor_resid)
    mean_nc = sum(no_corridor_resid) / len(no_corridor_resid)

    resid_sorted = sorted([p['residual'] for p in pairs], reverse=True)
    q75_threshold = resid_sorted[len(resid_sorted) // 4]
    top_q_corridor = sum(1 for p in pairs
                         if p['has_corridor']
                         and p['residual'] >= q75_threshold)
    corridor_total = sum(1 for p in pairs if p['has_corridor'])

    print(f"\n{'=' * 80}")
    print("RESIDUAL ANALYSIS: Corridor vs Non-corridor")
    print("=" * 80)
    print(f"  Corridor pairs mean residual:     {mean_c:+.1f}")
    print(f"  Non-corridor pairs mean residual: {mean_nc:+.1f}")
    print(f"  Ratio: {mean_c / abs(mean_nc) if mean_nc != 0 else 'inf':.1f}x")
    print(f"\n  Top quartile of residuals:")
    print(f"    Corridor pairs in top Q:  {top_q_corridor} / "
          f"{corridor_total} = "
          f"{top_q_corridor / max(corridor_total, 1) * 100:.0f}%")
    print(f"    Expected by chance:       "
          f"{corridor_total * 0.25:.1f} (25%)")
    enrichment = top_q_corridor / max(corridor_total * 0.25, 0.01)
    print(f"    Enrichment:               {enrichment:.1f}x")

    # =========================================================================
    # PERMUTATION TEST ON RESIDUALS
    # =========================================================================
    random.seed(42)
    N_PERM = 10000
    obs_mean_diff = mean_c - mean_nc
    perm_count = 0
    all_resid = [p['residual'] for p in pairs]
    n_corr = len(corridor_resid)

    for _ in range(N_PERM):
        random.shuffle(all_resid)
        perm_c = sum(all_resid[:n_corr]) / n_corr
        perm_nc = sum(all_resid[n_corr:]) / (len(all_resid) - n_corr)
        if perm_c - perm_nc >= obs_mean_diff:
            perm_count += 1

    p_perm = perm_count / N_PERM

    print(f"\n  Permutation test ({N_PERM} iterations):")
    print(f"    Observed mean diff: {obs_mean_diff:.1f}")
    print(f"    p-value: {p_perm:.4f}")

    # =========================================================================
    # CONCLUSION
    # =========================================================================
    print(f"\n{'=' * 80}")
    print("CONCLUSION")
    print("=" * 80)
    print(f"""
  Tree distance alone explains R² = {r_sq:.4f} of donor-overlap variance.
  After controlling for tree distance:
    - Corridor pairs have mean residual = {mean_c:+.1f}
    - Non-corridor pairs have mean residual = {mean_nc:+.1f}
    - {top_q_corridor}/{corridor_total} ({top_q_corridor / max(corridor_total, 1) * 100:.0f}%) corridor pairs
      are in the top quartile of residuals (expected: 25%)
    - Permutation p = {p_perm:.4f}

  CORRIDOR EFFECT SURVIVES GENEALOGICAL CONTROL.
""")


if __name__ == '__main__':
    main()

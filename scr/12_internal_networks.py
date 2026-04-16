#!/usr/bin/env python3
"""
SEED v2 - Phase 1 Expansion
=============================
Internal corridor network analysis.
Uses SEABOR/SABOR to reveal WHO borrowed FROM WHOM within each corridor.

WOLD = external view (which corridors exist)
SEABOR/SABOR = internal view (flow structure within corridors)
"""

import csv
import os
from collections import defaultdict, Counter

BASE = os.path.dirname(os.path.abspath(__file__))
SEABOR = os.path.join(BASE, '..', 'seabor', 'cldf')
SABOR = os.path.join(BASE, '..', 'sabor', 'cldf')


# ============================================================
# SEABOR internal flow analysis
# ============================================================
# SEABOR identifies borrowings via Xenolog_Cluster_ID.
# A cluster = a set of forms in different languages linked by borrowing.
# For each cluster, languages sharing it have borrowing-related forms.
# We build pairwise co-occurrence counts.

print("=" * 70)
print("SEABOR INTERNAL CORRIDOR STRUCTURE")
print("=" * 70)

# Load language metadata
sea_langs = {}
with open(os.path.join(SEABOR, 'languages.csv')) as f:
    for row in csv.DictReader(f):
        sea_langs[row['ID']] = {
            'name': row['Name'],
            'family': row.get('Family', ''),
            'subgroup': row.get('SubGroup', ''),
            'lat': float(row['Latitude']) if row.get('Latitude') else None,
            'lon': float(row['Longitude']) if row.get('Longitude') else None,
        }

print(f"\nSEABOR languages: {len(sea_langs)}")
fam = Counter(l['family'] for l in sea_langs.values())
for f, c in fam.most_common():
    print(f"  {f}: {c}")

# Map form -> language
form_to_lang = {}
with open(os.path.join(SEABOR, 'forms.csv')) as f:
    for row in csv.DictReader(f):
        form_to_lang[row['ID']] = row['Language_ID']

# Build clusters
clusters = defaultdict(set)  # cluster_id -> set of language_ids
with open(os.path.join(SEABOR, 'borrowings.csv')) as f:
    for row in csv.DictReader(f):
        target = row.get('Target_Form_ID')
        cluster = row.get('Xenolog_Cluster_ID')
        if target and cluster:
            lang = form_to_lang.get(target)
            if lang:
                clusters[cluster].add(lang)

print(f"\nTotal xenolog clusters: {len(clusters)}")

# Analyze cluster size distribution
size_dist = Counter(len(langs) for langs in clusters.values())
print(f"Cluster size distribution (how many langs share each cluster):")
for size in sorted(size_dist.keys())[:10]:
    print(f"  {size} lang(s): {size_dist[size]} clusters")

# Pairwise co-occurrence: for each pair of languages, how many clusters they share
pair_share = defaultdict(int)
for cluster, langs_set in clusters.items():
    langs_list = sorted(langs_set)
    for i in range(len(langs_list)):
        for j in range(i + 1, len(langs_list)):
            pair = (langs_list[i], langs_list[j])
            pair_share[pair] += 1

print(f"\nTop 20 internal borrowing pairs (shared xenolog clusters):")
print(f"{'Rank':<5} {'Lang1':<20} {'Fam1':<15} {'Lang2':<20} {'Fam2':<15} {'Shared':>6}")
print('-' * 95)

ranked = sorted(pair_share.items(), key=lambda x: -x[1])[:20]
for i, ((l1, l2), c) in enumerate(ranked, 1):
    n1 = sea_langs[l1]['name']
    n2 = sea_langs[l2]['name']
    f1 = sea_langs[l1]['family'][:13]
    f2 = sea_langs[l2]['family'][:13]
    print(f"{i:<5} {n1:<20} {f1:<15} {n2:<20} {f2:<15} {c:>6}")


# ============================================================
# Identify HUB languages (highest total sharing)
# ============================================================
print()
print("=" * 70)
print("SINOSPHERE HUB LANGUAGES (by total shared clusters)")
print("=" * 70)

lang_hub_score = defaultdict(int)
for (l1, l2), c in pair_share.items():
    lang_hub_score[l1] += c
    lang_hub_score[l2] += c

print(f"\n{'Rank':<5} {'Language':<25} {'Family':<18} {'Hub score':>10}")
print('-' * 65)
for i, (lang, score) in enumerate(sorted(lang_hub_score.items(), key=lambda x: -x[1])[:15], 1):
    info = sea_langs[lang]
    print(f"{i:<5} {info['name']:<25} {info['family']:<18} {score:>10}")


# ============================================================
# Cross-family borrowing detection
# ============================================================
print()
print("=" * 70)
print("CROSS-FAMILY BORROWING CLUSTERS (potential corridor evidence)")
print("=" * 70)

# Clusters where 2+ languages from DIFFERENT families appear
cross_family_clusters = 0
cross_family_pairs = Counter()
for cluster, langs_set in clusters.items():
    families_in_cluster = set(sea_langs[l]['family'] for l in langs_set if sea_langs[l]['family'])
    if len(families_in_cluster) >= 2:
        cross_family_clusters += 1
        # Record all cross-family pairs
        langs_list = sorted(langs_set)
        for i in range(len(langs_list)):
            for j in range(i + 1, len(langs_list)):
                l1, l2 = langs_list[i], langs_list[j]
                f1 = sea_langs[l1]['family']
                f2 = sea_langs[l2]['family']
                if f1 != f2 and f1 and f2:
                    families = tuple(sorted([f1, f2]))
                    cross_family_pairs[families] += 1

print(f"\nClusters with 2+ different families: {cross_family_clusters} / {len(clusters)}")
print(f"\nCross-family borrowing flows (family pairs):")
print(f"{'Family 1':<20} {'Family 2':<20} {'Count':>6}")
print('-' * 50)
for (f1, f2), c in cross_family_pairs.most_common(10):
    print(f"{f1:<20} {f2:<20} {c:>6}")


# ============================================================
# SABOR INTERNAL ANALYSIS - Spanish colonial flow details
# ============================================================
print()
print("=" * 70)
print("SABOR INTERNAL CORRIDOR STRUCTURE")
print("=" * 70)

sabor_langs = {}
with open(os.path.join(SABOR, 'languages.csv')) as f:
    for row in csv.DictReader(f):
        sabor_langs[row['ID']] = {
            'name': row['Name'],
            'family': row.get('Family', ''),
            'lat': float(row['Latitude']) if row.get('Latitude') else None,
            'lon': float(row['Longitude']) if row.get('Longitude') else None,
        }

# For each recipient language, count donors (not just Spanish - secondary donors reveal internal flow)
recipient_donor = defaultdict(Counter)
with open(os.path.join(SABOR, 'forms.csv')) as f:
    for row in csv.DictReader(f):
        if row.get('Borrowed') != 'True':
            continue
        recipient = row['Language_ID']
        donor = row.get('Donor_Language', '').strip()
        if donor:
            recipient_donor[recipient][donor] += 1

print(f"\nDonor breakdown per recipient (top 5 per language):")
for lang_id, donors in sorted(recipient_donor.items()):
    name = sabor_langs[lang_id]['name']
    family = sabor_langs[lang_id]['family']
    total = sum(donors.values())
    print(f"\n  {name} ({family}) - {total} borrowings total:")
    for d, c in donors.most_common(5):
        pct = 100 * c / total
        print(f"    {d:<25} {c:>4} ({pct:>5.1f}%)")


# ============================================================
# Save outputs
# ============================================================

# Save pairwise internal sharing for SEABOR
with open('seabor_internal_pairs.tsv', 'w') as f:
    w = csv.writer(f, delimiter='\t')
    w.writerow(['lang1_id', 'lang1_name', 'lang1_family',
                'lang2_id', 'lang2_name', 'lang2_family',
                'shared_clusters', 'is_cross_family'])
    for (l1, l2), c in sorted(pair_share.items(), key=lambda x: -x[1]):
        f1 = sea_langs[l1]['family']
        f2 = sea_langs[l2]['family']
        cross = 1 if (f1 != f2 and f1 and f2) else 0
        w.writerow([l1, sea_langs[l1]['name'], f1,
                    l2, sea_langs[l2]['name'], f2,
                    c, cross])

# Save hub scores
with open('sinosphere_hubs.tsv', 'w') as f:
    w = csv.writer(f, delimiter='\t')
    w.writerow(['lang_id', 'name', 'family', 'subgroup', 'lat', 'lon', 'hub_score'])
    for lang, score in sorted(lang_hub_score.items(), key=lambda x: -x[1]):
        info = sea_langs[lang]
        w.writerow([lang, info['name'], info['family'], info['subgroup'],
                    info['lat'], info['lon'], score])

print(f"\n✓ Saved: seabor_internal_pairs.tsv, sinosphere_hubs.tsv")

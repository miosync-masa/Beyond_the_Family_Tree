#!/usr/bin/env python3
"""
SEED v2 - Phase 1 Expansion
=============================
Spanish colonial penetration gradient across Americas.
Visualizes percentage of Spanish-origin borrowings in each language's total
borrowing inventory. Reveals corridor boundaries.
"""

import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np
from collections import defaultdict

# ============================================================
# Load data
# ============================================================

langs = {}
with open('unified_languages.tsv') as f:
    for row in csv.DictReader(f, delimiter='\t'):
        langs[row['unified_id']] = row

spanish_counts = defaultdict(int)
total_counts = defaultdict(int)
with open('unified_borrowings.tsv') as f:
    for row in csv.DictReader(f, delimiter='\t'):
        c = int(row['count'])
        total_counts[row['recipient_id']] += c
        d = row['donor_name'].lower()
        if 'spanish' in d or 'castilian' in d:
            spanish_counts[row['recipient_id']] += c

# Americas only
americas = []
for lid, info in langs.items():
    try:
        lon = float(info['lon'])
        lat = float(info['lat'])
    except:
        continue
    if not (-120 < lon < -30):
        continue
    tot = total_counts.get(lid, 0)
    if tot == 0:
        continue
    sp = spanish_counts.get(lid, 0)
    pct = 100 * sp / tot
    americas.append({
        'id': lid, 'name': info['name'], 'lat': lat, 'lon': lon,
        'spanish': sp, 'total': tot, 'pct': pct
    })

# Sort by pct for label ordering
americas.sort(key=lambda x: -x['pct'])

# ============================================================
# Figure
# ============================================================

fig = plt.figure(figsize=(15, 10))
gs = fig.add_gridspec(2, 2, width_ratios=[1.6, 1.0], height_ratios=[1, 1],
                     hspace=0.35, wspace=0.25)

# ------------------------------------------------------------
# Panel A: Geographic penetration map
# ------------------------------------------------------------
ax1 = fig.add_subplot(gs[:, 0])

# Use a red-to-white gradient (heat map style)
cmap = plt.cm.get_cmap('Reds')

# Simple Americas outline hint (continental bounds)
ax1.set_xlim(-125, -30)
ax1.set_ylim(-45, 35)
ax1.set_facecolor('#F0F4F8')

# Draw a very rough continental hint (rectangles for N/S America)
# Mexico-Central America bounds
ax1.add_patch(FancyBboxPatch((-118, 14), 25, 20, boxstyle='round,pad=0.5',
                              facecolor='#E8ECF1', edgecolor='#C8D0DA', alpha=0.5, zorder=0))
# South America bounds (rough)
ax1.add_patch(FancyBboxPatch((-82, -40), 50, 48, boxstyle='round,pad=0.5',
                              facecolor='#E8ECF1', edgecolor='#C8D0DA', alpha=0.5, zorder=0))

# Draw penetration gradient
max_abs = max(a['pct'] for a in americas)
for a in americas:
    # Color intensity by pct
    color = cmap(a['pct'] / 100 * 0.85 + 0.1)  # avoid pure white
    # Size by absolute Spanish count (so we don't exaggerate low-N points)
    size = 80 + np.sqrt(a['spanish'] + 5) * 15
    ax1.scatter(a['lon'], a['lat'], s=size, c=[color],
                edgecolors='#333', linewidths=0.8, zorder=3, alpha=0.92)

# Label all languages
for a in americas:
    offset_x, offset_y = 8, 8
    # manual offsets to avoid overlap
    if a['name'] == 'Yaqui':
        offset_x, offset_y = -45, 8
    elif a['name'] == 'Otomi':
        offset_x, offset_y = 8, -14
    elif a['name'] == 'Hup':
        offset_x, offset_y = 8, 8
    elif a['name'] == 'Kali\'na':
        offset_x, offset_y = 8, -12
    elif a['name'] == 'Saramaccan':
        offset_x, offset_y = -55, -10
    label = f"{a['name']}\n{a['pct']:.0f}%"
    ax1.annotate(label,
                 xy=(a['lon'], a['lat']),
                 xytext=(offset_x, offset_y),
                 textcoords='offset points',
                 fontsize=8.5, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3',
                           facecolor='white', edgecolor='#999', alpha=0.9, linewidth=0.5),
                 zorder=5)

ax1.set_xlabel('Longitude', fontsize=10)
ax1.set_ylabel('Latitude', fontsize=10)
ax1.set_title('A  Spanish Colonial Penetration Across the Americas\n'
              '(% of each language\'s borrowings from Spanish)',
              fontsize=13, fontweight='bold', loc='left', pad=10)
ax1.grid(True, linestyle=':', alpha=0.3, zorder=1)

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=100))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax1, fraction=0.025, pad=0.02)
cbar.set_label('% Spanish', fontsize=10)

# Annotation: corridor edge
ax1.annotate('Corridor boundary:\nSpanish empire did not\nreach these languages',
             xy=(-67, 2), xytext=(-58, -22),
             fontsize=9, ha='left', va='center',
             bbox=dict(boxstyle='round,pad=0.5',
                       facecolor='#FFF9E6', edgecolor='#E0A800', linewidth=1),
             arrowprops=dict(arrowstyle='->', color='#E0A800', lw=1.2))

# ------------------------------------------------------------
# Panel B: Penetration gradient bar chart
# ------------------------------------------------------------
ax2 = fig.add_subplot(gs[0, 1])

names = [a['name'] for a in americas]
pcts = [a['pct'] for a in americas]
colors = [cmap(p / 100 * 0.85 + 0.1) for p in pcts]

y_pos = np.arange(len(names))
bars = ax2.barh(y_pos, pcts, color=colors, edgecolor='#444', linewidth=0.6)
ax2.set_yticks(y_pos)
ax2.set_yticklabels(names, fontsize=9)
ax2.invert_yaxis()
ax2.set_xlabel('% Spanish-origin borrowings', fontsize=10)
ax2.set_xlim(0, 105)
ax2.set_title('B  Penetration Ranking', fontsize=13, fontweight='bold', loc='left', pad=10)
ax2.grid(axis='x', linestyle=':', alpha=0.35, zorder=0)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

for bar, pct in zip(bars, pcts):
    ax2.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2,
             f'{pct:.1f}%', va='center', fontsize=8)

# ------------------------------------------------------------
# Panel C: Latitude gradient scatter
# ------------------------------------------------------------
ax3 = fig.add_subplot(gs[1, 1])

lats_arr = np.array([a['lat'] for a in americas])
pcts_arr = np.array([a['pct'] for a in americas])

# Scatter with size = total borrowings
sizes = [60 + np.sqrt(a['total']) * 3 for a in americas]
ax3.scatter(lats_arr, pcts_arr, s=sizes, c=pcts_arr, cmap='Reds',
            edgecolors='#333', linewidths=0.7, alpha=0.88, vmin=0, vmax=100)

for a in americas:
    ax3.annotate(a['name'], (a['lat'], a['pct']),
                 xytext=(4, 4), textcoords='offset points',
                 fontsize=7, alpha=0.75)

ax3.set_xlabel('Latitude (° N)', fontsize=10)
ax3.set_ylabel('% Spanish-origin', fontsize=10)
ax3.set_title('C  Penetration vs Latitude', fontsize=13, fontweight='bold', loc='left', pad=10)
ax3.grid(True, linestyle=':', alpha=0.35)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.set_ylim(-5, 105)

# Overall title
fig.suptitle('Figure: Spanish Colonial Corridor Boundaries '
             '(%-of-borrowings gradient across 10 American languages)',
             fontsize=14, fontweight='bold', y=0.995)

plt.savefig('spanish_penetration.png', dpi=300, bbox_inches='tight',
            facecolor='white')
print("✓ Saved: spanish_penetration.png")

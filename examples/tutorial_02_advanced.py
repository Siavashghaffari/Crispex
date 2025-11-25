#!/usr/bin/env python
"""
Crispex Tutorial 2: Advanced Features
======================================

Learn advanced guide design techniques and data analysis.

This tutorial covers:
1. Genomic region targeting (coordinates instead of genes)
2. Custom filtering and selection criteria
3. Batch analysis and comparison
4. Data visualization and quality control
5. Optimizing for specific experimental needs

Prerequisites:
- Completed tutorial_01_beginner.py
- Understanding of basic genomics concepts
"""

import os
from crispex import design_guides
import pandas as pd


def example1_region_targeting():
    """Example 1: Target specific genomic regions"""
    print("=" * 70)
    print("EXAMPLE 1: Genomic Region Targeting")
    print("=" * 70)
    print()

    print("Sometimes you want to target a specific region, not a whole gene.")
    print("For example:")
    print("  - A specific exon")
    print("  - A regulatory region")
    print("  - A non-coding region")
    print()

    # Target a 500bp region in TP53
    region = "chr17:7676000-7676500"

    print(f"Targeting region: {region}")
    print("(500bp in the TP53 locus)")
    print()

    guides = design_guides(
        region=region,
        species="human",
        top_n=10
    )

    print(f"✓ Found {len(guides)} guides in this 500bp region")
    print()

    # Analyze guide distribution
    print("Guide distribution across region:")
    print(f"  First guide position: {guides['start'].min():,}")
    print(f"  Last guide position:  {guides['end'].max():,}")
    print(f"  Span: {guides['end'].max() - guides['start'].min()}bp")
    print()

    # Strand distribution
    plus_guides = (guides['strand'] == '+').sum()
    minus_guides = (guides['strand'] == '-').sum()
    print("Strand distribution:")
    print(f"  Plus strand (+):  {plus_guides} guides")
    print(f"  Minus strand (-): {minus_guides} guides")
    print()

    return guides


def example2_custom_filtering():
    """Example 2: Advanced filtering strategies"""
    print("=" * 70)
    print("EXAMPLE 2: Custom Filtering Strategies")
    print("=" * 70)
    print()

    print("Design 20 guides, then apply custom filters to find the best ones.")
    print()

    # Get more guides than we need
    guides = design_guides(
        gene="KRAS",
        species="human",
        top_n=20
    )

    print(f"Starting with {len(guides)} guides for KRAS")
    print()

    # Strategy 1: Ultra-high specificity
    print("Filter 1: Ultra-high specificity (minimal off-targets)")
    specific_guides = guides[
        (guides['off_targets_1mm'] == 0) &
        (guides['off_targets_2mm'] <= 3)
    ]
    print(f"  Found {len(specific_guides)} ultra-specific guides")
    if len(specific_guides) > 0:
        print(f"  Top candidate: {specific_guides.iloc[0]['guide_sequence']}")
    print()

    # Strategy 2: Balanced efficiency and specificity
    print("Filter 2: Balanced approach (good efficiency + low off-targets)")
    balanced_guides = guides[
        (guides['efficiency_score'] >= 70) &
        (guides['off_targets_1mm'] <= 2) &
        (guides['gc_content'] >= 40) &
        (guides['gc_content'] <= 60)
    ]
    print(f"  Found {len(balanced_guides)} balanced guides")
    if len(balanced_guides) > 0:
        print(f"  Mean efficiency: {balanced_guides['efficiency_score'].mean():.1f}")
    print()

    # Strategy 3: Maximum efficiency (for difficult-to-edit genes)
    print("Filter 3: Maximum efficiency (for hard targets)")
    high_efficiency = guides.nlargest(5, 'efficiency_score')
    print(f"  Top 5 by efficiency:")
    for idx, guide in high_efficiency.iterrows():
        print(f"    {guide['guide_sequence']}: {guide['efficiency_score']:.1f}")
    print()


def example3_batch_comparison():
    """Example 3: Compare guides across multiple genes"""
    print("=" * 70)
    print("EXAMPLE 3: Batch Gene Analysis")
    print("=" * 70)
    print()

    print("Compare guide quality across multiple genes in a pathway.")
    print()

    genes = ["TP53", "BRCA1", "BRCA2"]
    results = {}

    for gene in genes:
        print(f"Designing guides for {gene}...", end=" ")
        guides = design_guides(gene=gene, species="human", top_n=5)
        results[gene] = guides
        print(f"✓ {len(guides)} guides")

    print()
    print("Comparison across genes:")
    print()

    # Create comparison table
    comparison_data = []
    for gene, guides in results.items():
        comparison_data.append({
            'Gene': gene,
            'Num Guides': len(guides),
            'Mean Efficiency': guides['efficiency_score'].mean(),
            'Max Efficiency': guides['efficiency_score'].max(),
            'Mean Off-targets': guides['off_targets_1mm'].mean(),
            'Best GC%': guides.iloc[0]['gc_content']
        })

    comparison_df = pd.DataFrame(comparison_data)
    print(comparison_df.to_string(index=False))
    print()

    # Find easiest gene to target
    best_gene = comparison_df.loc[comparison_df['Mean Efficiency'].idxmax(), 'Gene']
    print(f"Easiest to target (highest mean efficiency): {best_gene}")
    print()


def example4_quality_control():
    """Example 4: Quality control and validation"""
    print("=" * 70)
    print("EXAMPLE 4: Quality Control Checks")
    print("=" * 70)
    print()

    guides = design_guides(gene="MYC", species="human", top_n=15)

    print(f"Performing QC on {len(guides)} MYC guides...")
    print()

    # Check 1: GC content distribution
    print("Check 1: GC Content Distribution")
    optimal_gc = guides[
        (guides['gc_content'] >= 40) &
        (guides['gc_content'] <= 60)
    ]
    print(f"  Optimal GC% (40-60%): {len(optimal_gc)}/{len(guides)} guides")
    print(f"  Mean GC%: {guides['gc_content'].mean():.1f}%")
    print(f"  Range: {guides['gc_content'].min():.1f}% - {guides['gc_content'].max():.1f}%")
    print()

    # Check 2: Efficiency distribution
    print("Check 2: Efficiency Distribution")
    high_eff = (guides['efficiency_score'] >= 70).sum()
    medium_eff = ((guides['efficiency_score'] >= 60) &
                  (guides['efficiency_score'] < 70)).sum()
    low_eff = (guides['efficiency_score'] < 60).sum()
    print(f"  High (≥70):   {high_eff} guides")
    print(f"  Medium (60-69): {medium_eff} guides")
    print(f"  Low (<60):    {low_eff} guides")
    print()

    # Check 3: Off-target burden
    print("Check 3: Off-Target Analysis")
    no_offtargets = (guides['off_targets_1mm'] == 0).sum()
    low_offtargets = (guides['off_targets_1mm'] <= 2).sum()
    print(f"  Zero off-targets (1MM): {no_offtargets} guides")
    print(f"  Low off-targets (≤2):   {low_offtargets} guides")
    print(f"  Mean off-targets:       {guides['off_targets_1mm'].mean():.1f}")
    print()

    # Check 4: Identify potential issues
    print("Check 4: Flag Potential Issues")
    issues = []
    for idx, guide in guides.iterrows():
        if guide['gc_content'] < 30 or guide['gc_content'] > 70:
            issues.append(f"  Guide #{guide['rank']}: Extreme GC% ({guide['gc_content']:.0f}%)")
        if guide['off_targets_1mm'] > 5:
            issues.append(f"  Guide #{guide['rank']}: High off-targets ({guide['off_targets_1mm']})")

    if issues:
        print(f"  Found {len(issues)} potential issues:")
        for issue in issues[:3]:  # Show first 3
            print(issue)
    else:
        print("  ✓ No major issues detected")
    print()


def example5_experimental_design():
    """Example 5: Designing for specific experiments"""
    print("=" * 70)
    print("EXAMPLE 5: Experiment-Specific Design")
    print("=" * 70)
    print()

    guides = design_guides(gene="EGFR", species="human", top_n=20)

    print("Scenario 1: Knockout experiment (need high efficiency)")
    print("-" * 70)
    knockout_guides = guides.nlargest(3, 'efficiency_score')
    print("Top 3 guides for knockout:")
    for i, (idx, guide) in enumerate(knockout_guides.iterrows(), 1):
        print(f"  {i}. {guide['guide_sequence']}")
        print(f"     Efficiency: {guide['efficiency_score']:.1f}, "
              f"Off-targets: {guide['off_targets_1mm']}")
    print()

    print("Scenario 2: Clinical application (need ultra-specificity)")
    print("-" * 70)
    clinical_guides = guides[guides['off_targets_1mm'] == 0].head(3)
    print(f"Top {len(clinical_guides)} ultra-specific guides:")
    for i, (idx, guide) in enumerate(clinical_guides.iterrows(), 1):
        print(f"  {i}. {guide['guide_sequence']}")
        print(f"     Efficiency: {guide['efficiency_score']:.1f}, "
              f"1MM off-targets: {guide['off_targets_1mm']}")
    print()

    print("Scenario 3: Multiplexing (need diverse positions)")
    print("-" * 70)
    # Select guides spread across the gene
    sorted_by_position = guides.sort_values('start')
    multiplex_guides = [
        sorted_by_position.iloc[0],
        sorted_by_position.iloc[len(sorted_by_position)//2],
        sorted_by_position.iloc[-1]
    ]
    print("3 guides spanning the gene:")
    for i, guide in enumerate(multiplex_guides, 1):
        print(f"  {i}. Position {guide['start']:,}: {guide['guide_sequence']}")
    print()


def example6_export_formats():
    """Example 6: Export in different formats"""
    print("=" * 70)
    print("EXAMPLE 6: Data Export Options")
    print("=" * 70)
    print()

    guides = design_guides(gene="PTEN", species="human", top_n=5)

    # Create output directory
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # Export 1: Full CSV with all columns
    full_csv = os.path.join(output_dir, 'pten_guides_full.csv')
    guides.to_csv(full_csv, index=False)
    print(f"✓ Full data: {full_csv}")

    # Export 2: Minimal CSV for ordering
    minimal_csv = os.path.join(output_dir, 'pten_guides_order.csv')
    guides[['rank', 'guide_sequence', 'full_sequence']].to_csv(
        minimal_csv, index=False
    )
    print(f"✓ Ordering sheet: {minimal_csv}")

    # Export 3: Summary report
    report_file = os.path.join(output_dir, 'pten_guides_report.txt')
    with open(report_file, 'w') as f:
        f.write("CRISPEX GUIDE DESIGN REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Gene: PTEN\n")
        f.write(f"Species: Human\n")
        f.write(f"Number of guides: {len(guides)}\n\n")
        f.write("TOP GUIDE:\n")
        top = guides.iloc[0]
        f.write(f"  Sequence: {top['guide_sequence']}\n")
        f.write(f"  Efficiency: {top['efficiency_score']:.1f}\n")
        f.write(f"  Off-targets: {top['off_targets_1mm']} (1MM)\n")
    print(f"✓ Summary report: {report_file}")
    print()


def main():
    """Run the advanced tutorial"""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "CRISPEX ADVANCED TUTORIAL" + " " * 28 + "║")
    print("║" + " " * 12 + "Advanced Features & Techniques" + " " * 26 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    try:
        example1_region_targeting()
        input("Press Enter for next example...")
        print()

        example2_custom_filtering()
        input("Press Enter for next example...")
        print()

        example3_batch_comparison()
        input("Press Enter for next example...")
        print()

        example4_quality_control()
        input("Press Enter for next example...")
        print()

        example5_experimental_design()
        input("Press Enter for next example...")
        print()

        example6_export_formats()

        print()
        print("=" * 70)
        print("ADVANCED TUTORIAL COMPLETE!")
        print("=" * 70)
        print()
        print("You've learned:")
        print("  ✓ Region-based targeting")
        print("  ✓ Custom filtering strategies")
        print("  ✓ Batch analysis")
        print("  ✓ Quality control")
        print("  ✓ Experiment-specific design")
        print("  ✓ Data export options")
        print()
        print("Next: See tutorial_03_cli.md for command-line usage")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Some examples require internet connection.")
        print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Crispex Tutorial 1: Beginner's Guide
=====================================

Step-by-step introduction to designing CRISPR guides with Crispex.

This tutorial will teach you:
1. How to import and use Crispex
2. How to design guides for a gene
3. How to understand the results
4. How to export and save guides
5. How to interpret quality scores

Prerequisites:
- Python 3.9+
- Internet connection (for Ensembl API)
- Crispex installed: pip install crispex
"""

import os
from crispex import design_guides
import pandas as pd


def step1_simple_design():
    """Step 1: Design your first guide"""
    print("=" * 70)
    print("STEP 1: Design Your First Guide")
    print("=" * 70)
    print()
    print("Let's design guides for the TP53 gene (tumor suppressor gene).")
    print()

    # Design guides - this is the simplest way to use Crispex
    guides = design_guides(
        gene="TP53",           # Gene symbol
        species="human",       # Species (human or mouse)
        top_n=5               # Number of top guides to return
    )

    print(f"✓ Found {len(guides)} guides for TP53")
    print()

    # Let's look at what we got
    print("Here's what the results look like:")
    print()
    print(guides[['rank', 'guide_sequence', 'efficiency_score']].head())
    print()

    print("Each guide has:")
    print("  - rank: Position in the ranked list (1 = best)")
    print("  - guide_sequence: The 20bp sequence to synthesize")
    print("  - efficiency_score: Predicted cutting efficiency (0-100)")
    print()

    return guides


def step2_understand_results(guides):
    """Step 2: Understanding the guide results"""
    print("=" * 70)
    print("STEP 2: Understanding Guide Quality")
    print("=" * 70)
    print()

    # Get the top guide
    top_guide = guides.iloc[0]

    print("Let's examine the top guide in detail:")
    print()
    print(f"  Guide sequence:    {top_guide['guide_sequence']}")
    print(f"  PAM sequence:      {top_guide['pam_sequence']}")
    print(f"  Full sequence:     {top_guide['full_sequence']}")
    print()

    print("Quality metrics:")
    print(f"  Efficiency score:  {top_guide['efficiency_score']:.1f}/100")
    print(f"  GC content:        {top_guide['gc_content']:.1f}%")
    print()

    print("Off-target analysis:")
    print(f"  0 mismatches:      {top_guide['off_targets_0mm']} (should be 1 - the target site)")
    print(f"  1 mismatch:        {top_guide['off_targets_1mm']}")
    print(f"  2 mismatches:      {top_guide['off_targets_2mm']}")
    print(f"  3 mismatches:      {top_guide['off_targets_3mm']}")
    print()

    print("Genomic location:")
    print(f"  Chromosome:        {top_guide['chromosome']}")
    print(f"  Start position:    {top_guide['start']:,}")
    print(f"  End position:      {top_guide['end']:,}")
    print(f"  Strand:            {top_guide['strand']}")
    print()


def step3_compare_guides(guides):
    """Step 3: Comparing multiple guides"""
    print("=" * 70)
    print("STEP 3: Comparing Multiple Guides")
    print("=" * 70)
    print()

    print("Let's compare the top 3 guides:")
    print()

    # Show key columns for comparison
    comparison = guides.head(3)[
        ['rank', 'guide_sequence', 'efficiency_score', 'gc_content',
         'off_targets_1mm', 'off_targets_2mm']
    ]
    print(comparison.to_string(index=False))
    print()

    print("How to choose:")
    print("  1. Higher efficiency_score is better (more likely to cut)")
    print("  2. GC content 40-60% is ideal (too high/low = poor performance)")
    print("  3. Fewer off-targets is better (more specific)")
    print()

    # Find guide with best specificity
    best_specific = guides.loc[guides['off_targets_1mm'].idxmin()]
    print(f"Most specific guide (fewest 1MM off-targets):")
    print(f"  Rank #{best_specific['rank']}: {best_specific['guide_sequence']}")
    print(f"  Off-targets (1MM): {best_specific['off_targets_1mm']}")
    print()


def step4_save_results(guides):
    """Step 4: Saving your results"""
    print("=" * 70)
    print("STEP 4: Saving Results")
    print("=" * 70)
    print()

    # Create output directory
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # Save to CSV
    output_file = os.path.join(output_dir, 'tutorial_tp53_guides.csv')
    guides.to_csv(output_file, index=False)

    print(f"✓ Saved {len(guides)} guides to: {output_file}")
    print()

    print("You can now:")
    print("  - Open this file in Excel or Google Sheets")
    print("  - Share it with your lab")
    print("  - Order the guide sequences from a vendor")
    print()


def step5_design_workflow():
    """Step 5: Complete design workflow"""
    print("=" * 70)
    print("STEP 5: Complete Workflow Example")
    print("=" * 70)
    print()

    print("Let's design guides for BRCA1 (breast cancer gene) with")
    print("automatic file saving:")
    print()

    # Create output directory
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'brca1_guides.csv')

    # Design with output parameter
    guides = design_guides(
        gene="BRCA1",
        species="human",
        top_n=10,
        output=output_file    # Automatically saves to this file
    )

    print(f"✓ Designed {len(guides)} guides for BRCA1")
    print(f"✓ Saved to: {output_file}")
    print()

    # Show summary statistics
    print("Summary statistics:")
    print(f"  Mean efficiency:   {guides['efficiency_score'].mean():.1f}")
    print(f"  Mean GC content:   {guides['gc_content'].mean():.1f}%")
    print(f"  Total off-targets: {guides['off_targets_1mm'].sum()} (1MM)")
    print()


def main():
    """Run the complete beginner tutorial"""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "CRISPEX BEGINNER TUTORIAL" + " " * 28 + "║")
    print("║" + " " * 16 + "Step-by-Step Guide Design" + " " * 27 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    try:
        # Step 1: Simple design
        guides = step1_simple_design()
        input("Press Enter to continue to Step 2...")
        print()

        # Step 2: Understand results
        step2_understand_results(guides)
        input("Press Enter to continue to Step 3...")
        print()

        # Step 3: Compare guides
        step3_compare_guides(guides)
        input("Press Enter to continue to Step 4...")
        print()

        # Step 4: Save results
        step4_save_results(guides)
        input("Press Enter to continue to Step 5...")
        print()

        # Step 5: Complete workflow
        step5_design_workflow()

        print()
        print("=" * 70)
        print("TUTORIAL COMPLETE!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Try designing guides for your own gene of interest")
        print("  2. Check out tutorial_02_advanced.py for advanced features")
        print("  3. See tutorial_03_cli.md for command-line usage")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("  - Check your internet connection (needed for Ensembl API)")
        print("  - Verify Crispex is installed: pip install crispex")
        print("  - Make sure you're using Python 3.9+")
        print()


if __name__ == "__main__":
    main()

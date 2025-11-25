#!/usr/bin/env python
"""
Basic usage example for Crispex

This script demonstrates the simplest way to design sgRNA guides
using Crispex.
"""

from crispex import design_guides

def main():
    print("Crispex - Basic Usage Example")
    print("=" * 50)
    print()

    # Example 1: Design guides for a gene
    print("Example 1: Designing guides for TP53 gene")
    print("-" * 50)

    try:
        guides = design_guides(
            gene="TP53",
            species="human",
            top_n=5
        )

        print(f"\nFound {len(guides)} guides:")
        print(guides[['rank', 'guide_sequence', 'efficiency_score', 'off_targets_1mm']].to_string())

        # Access top guide
        if len(guides) > 0:
            top_guide = guides.iloc[0]
            print(f"\nTop guide:")
            print(f"  Sequence: {top_guide['guide_sequence']}")
            print(f"  Full oligo: {top_guide['full_sequence']}")
            print(f"  Efficiency: {top_guide['efficiency_score']:.1f}")
            print(f"  Off-targets (1MM): {top_guide['off_targets_1mm']}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This example requires internet connection to fetch gene data from Ensembl")

    print()
    print("=" * 50)
    print("Example complete!")


if __name__ == "__main__":
    main()

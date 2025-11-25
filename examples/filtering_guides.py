#!/usr/bin/env python
"""
Advanced filtering example for Crispex

This script demonstrates how to filter and analyze guides
based on custom criteria.
"""

from crispex import design_guides
import pandas as pd

def main():
    print("Crispex - Guide Filtering Example")
    print("=" * 50)
    print()

    try:
        # Design guides with more results than default
        print("Designing 20 guides for BRCA1...")
        guides = design_guides(
            gene="BRCA1",
            species="human",
            top_n=20
        )

        print(f"Total guides: {len(guides)}")
        print()

        # Filter 1: High efficiency guides
        print("Filter 1: High efficiency guides (>75)")
        high_efficiency = guides[guides['efficiency_score'] > 75]
        print(f"  Found: {len(high_efficiency)} guides")
        print()

        # Filter 2: Low off-target guides
        print("Filter 2: Low off-target guides (≤2 at 1MM)")
        low_offtarget = guides[guides['off_targets_1mm'] <= 2]
        print(f"  Found: {len(low_offtarget)} guides")
        print()

        # Filter 3: Combined criteria
        print("Filter 3: High efficiency + Low off-targets")
        optimal = guides[
            (guides['efficiency_score'] > 75) &
            (guides['off_targets_1mm'] <= 2) &
            (guides['off_targets_2mm'] <= 5)
        ]
        print(f"  Found: {len(optimal)} optimal guides")

        if len(optimal) > 0:
            print("\nOptimal guides:")
            print(optimal[['rank', 'guide_sequence', 'efficiency_score',
                         'off_targets_1mm', 'off_targets_2mm']].to_string())

            # Save filtered results
            import os
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, 'brca1_optimal_guides.csv')
            optimal.to_csv(output_file, index=False)
            print(f"\n  Saved to: {output_file}")

        # Statistics
        print("\nStatistics:")
        print(f"  Mean efficiency: {guides['efficiency_score'].mean():.1f}")
        print(f"  Median efficiency: {guides['efficiency_score'].median():.1f}")
        print(f"  Mean GC content: {guides['gc_content'].mean():.1f}%")
        print(f"  Mean off-targets (1MM): {guides['off_targets_1mm'].mean():.1f}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This example requires internet connection")

    print()
    print("=" * 50)


if __name__ == "__main__":
    main()

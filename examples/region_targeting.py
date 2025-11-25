#!/usr/bin/env python
"""
Genomic region targeting example for Crispex

This script demonstrates how to design guides for specific
genomic coordinates rather than gene names.
"""

import os
from crispex import design_guides

def main():
    print("Crispex - Region Targeting Example")
    print("=" * 50)
    print()

    try:
        # Example: Target a specific region in chromosome 17
        region = "chr17:7675000-7676000"

        print(f"Designing guides for region: {region}")
        print(f"Region size: 1,000 bp")
        print()

        # Create output directory
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'region_guides.csv')

        guides = design_guides(
            region=region,
            species="human",
            top_n=10,
            output=output_file
        )

        print(f"\nFound {len(guides)} guides in region")

        if len(guides) > 0:
            print("\nTop 5 guides:")
            print(guides.head()[['guide_sequence', 'start', 'end', 'strand',
                                'efficiency_score']].to_string())

            # Analyze strand distribution
            plus_strand = (guides['strand'] == '+').sum()
            minus_strand = (guides['strand'] == '-').sum()

            print(f"\nStrand distribution:")
            print(f"  Plus strand (+): {plus_strand}")
            print(f"  Minus strand (-): {minus_strand}")

            # Analyze position distribution
            print(f"\nPosition range:")
            print(f"  First guide: {guides['start'].min():,}")
            print(f"  Last guide: {guides['end'].max():,}")

            print(f"\n  Results saved to: {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This example requires internet connection")

    print()
    print("=" * 50)


if __name__ == "__main__":
    main()

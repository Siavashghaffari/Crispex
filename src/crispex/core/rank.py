"""Ranking and selection of guides"""

from typing import List
from crispex.core.guide import Guide


def calculate_specificity_score(guide: Guide) -> float:
    """Calculate specificity score based on off-targets

    Args:
        guide: Guide object with off_targets populated

    Returns:
        Specificity score (0-100, higher is better)
    """
    # Start with perfect score
    score = 100.0

    # Penalize off-targets by mismatch level
    # Weight: 0MM (should be 1) > 1MM > 2MM > 3MM
    penalties = {
        0: 100.0,  # Perfect match at target (if >1, major penalty)
        1: 20.0,   # 1 mismatch off-targets are concerning
        2: 5.0,    # 2 mismatches less concerning
        3: 1.0     # 3 mismatches least concerning
    }

    for mismatch_count, off_target_count in guide.off_targets.items():
        if mismatch_count == 0:
            # Should only be 1 (the target site)
            if off_target_count > 1:
                score -= (off_target_count - 1) * penalties[0]
        else:
            penalty = off_target_count * penalties.get(mismatch_count, 0)
            score -= penalty

    # Clamp to 0-100
    return max(0.0, min(100.0, score))


def calculate_composite_score(guide: Guide, weights: dict = None) -> float:
    """Calculate composite score combining efficiency and specificity

    Args:
        guide: Guide object
        weights: Dictionary of scoring weights

    Returns:
        Composite score (0-100)
    """
    if weights is None:
        weights = {
            'efficiency': 0.6,      # 60% weight on efficiency
            'specificity': 0.4,     # 40% weight on specificity
        }

    # Calculate specificity score
    specificity = calculate_specificity_score(guide)

    # Composite score
    composite = (
        guide.efficiency_score * weights['efficiency'] +
        specificity * weights['specificity']
    )

    return round(composite, 2)


def rank_guides(guides: List[Guide]) -> List[Guide]:
    """Rank guides by multiple criteria

    Ranking priority:
    1. Efficiency score (primary)
    2. Off-target count (0-2 mismatches)
    3. Position in gene (earlier is better for knockouts)

    Args:
        guides: List of Guide objects

    Returns:
        Sorted list of guides (best first)
    """
    def sort_key(guide: Guide):
        # Primary: Efficiency score (descending)
        efficiency = -guide.efficiency_score

        # Secondary: Total off-targets at 0-2 mismatches (ascending)
        critical_offtargets = (
            guide.off_targets.get(0, 0) +
            guide.off_targets.get(1, 0) +
            guide.off_targets.get(2, 0)
        )

        # Tertiary: Position (earlier in gene is better)
        position = guide.start

        return (efficiency, critical_offtargets, position)

    # Sort guides
    sorted_guides = sorted(guides, key=sort_key)

    return sorted_guides


def select_top_guides(guides: List[Guide], top_n: int = 5) -> List[Guide]:
    """Select top N guides

    Args:
        guides: List of Guide objects (should be sorted)
        top_n: Number of top guides to return

    Returns:
        List of top N guides
    """
    return guides[:top_n]


def add_rank_numbers(guides: List[Guide]) -> List[Guide]:
    """Add rank numbers to guides

    Args:
        guides: List of Guide objects (should be sorted)

    Returns:
        Same list (modified in place)
    """
    # We'll add rank as a property or store it separately
    # For simplicity, we can add it to the dict when exporting
    return guides


def filter_by_specificity(
    guides: List[Guide],
    max_off_targets_1mm: int = 5,
    max_off_targets_2mm: int = 10
) -> List[Guide]:
    """Filter guides by off-target thresholds

    Args:
        guides: List of Guide objects
        max_off_targets_1mm: Maximum allowed 1MM off-targets
        max_off_targets_2mm: Maximum allowed 2MM off-targets

    Returns:
        Filtered list of guides
    """
    filtered = []

    for guide in guides:
        if guide.off_targets.get(1, 0) <= max_off_targets_1mm and \
           guide.off_targets.get(2, 0) <= max_off_targets_2mm:
            filtered.append(guide)

    return filtered

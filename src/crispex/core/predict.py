"""On-target efficiency prediction using Azimuth model

For MVP, this implements a simplified heuristic-based scorer.
Future versions will integrate the full Azimuth gradient boosting model.
"""

import numpy as np
from typing import List
from crispex.core.guide import Guide


class AzimuthPredictor:
    """Predicts on-target efficiency scores for sgRNAs

    For MVP: Uses heuristic rules based on known CRISPR design principles
    Future: Will use actual Azimuth gradient boosting model
    """

    def __init__(self):
        """Initialize predictor"""
        self.model_loaded = False

    def predict_efficiency(self, guide: Guide, context_sequence: str = None) -> float:
        """Predict efficiency score for a single guide

        Args:
            guide: Guide object
            context_sequence: 30bp context sequence (guide + PAM + flanking)

        Returns:
            Efficiency score (0-100)
        """
        score = 50.0  # Base score

        sequence = guide.sequence

        # Feature 1: GC content (optimal around 50%)
        gc_score = self._score_gc_content(guide.gc_content)
        score += gc_score

        # Feature 2: Position-specific preferences
        position_score = self._score_position_preferences(sequence)
        score += position_score

        # Feature 3: Seed region (positions 1-12)
        seed_score = self._score_seed_region(sequence[:12])
        score += seed_score

        # Feature 4: PAM-proximal region
        pam_proximal_score = self._score_pam_proximal(sequence[-8:])
        score += pam_proximal_score

        # Feature 5: Penalize homopolymers
        homopolymer_penalty = self._penalize_homopolymers(sequence)
        score += homopolymer_penalty

        # Feature 6: Terminal G preference
        if sequence[19] == 'G':  # Position 20 (last position)
            score += 2.0

        # Clamp score to 0-100 range
        score = max(0.0, min(100.0, score))

        return round(score, 1)

    def predict_batch(self, guides: List[Guide]) -> List[Guide]:
        """Predict efficiency scores for multiple guides

        Args:
            guides: List of Guide objects

        Returns:
            Same list with efficiency_score field updated
        """
        for guide in guides:
            guide.efficiency_score = self.predict_efficiency(guide)

        return guides

    def _score_gc_content(self, gc_content: float) -> float:
        """Score based on GC content (optimal ~50%)

        Args:
            gc_content: GC percentage (0-100)

        Returns:
            Score contribution (-10 to +10)
        """
        # Optimal GC is around 50%
        optimal_gc = 50.0
        deviation = abs(gc_content - optimal_gc)

        if deviation <= 10:
            return 10.0 - deviation
        else:
            return -(deviation - 10) * 0.5

    def _score_position_preferences(self, sequence: str) -> float:
        """Score position-specific nucleotide preferences

        Args:
            sequence: Guide sequence

        Returns:
            Score contribution (-5 to +5)
        """
        score = 0.0

        # Position-specific preferences from Doench et al. 2016
        # Prefer G at positions 19-20
        if len(sequence) >= 20:
            if sequence[18] == 'G':  # Position 19
                score += 2.0
            if sequence[19] == 'G':  # Position 20
                score += 2.0

        # Prefer C at position 1
        if sequence[0] == 'C':
            score += 1.0

        return score

    def _score_seed_region(self, seed_sequence: str) -> float:
        """Score seed region (positions 1-12)

        Args:
            seed_sequence: First 12 nucleotides

        Returns:
            Score contribution (-5 to +5)
        """
        score = 0.0

        # Prefer balanced composition in seed region
        gc_count = seed_sequence.count('G') + seed_sequence.count('C')
        gc_ratio = gc_count / len(seed_sequence)

        if 0.4 <= gc_ratio <= 0.6:
            score += 3.0
        else:
            score -= 2.0

        # Penalize poly-T in seed (causes termination)
        if 'TTT' in seed_sequence:
            score -= 5.0

        return score

    def _score_pam_proximal(self, pam_proximal: str) -> float:
        """Score PAM-proximal region (last 8 nucleotides)

        Args:
            pam_proximal: Last 8 nucleotides of guide

        Returns:
            Score contribution (-3 to +3)
        """
        score = 0.0

        # Prefer higher GC in PAM-proximal region
        gc_count = pam_proximal.count('G') + pam_proximal.count('C')
        gc_ratio = gc_count / len(pam_proximal)

        if gc_ratio >= 0.5:
            score += 2.0
        else:
            score -= 1.0

        return score

    def _penalize_homopolymers(self, sequence: str) -> float:
        """Penalize long homopolymer runs

        Args:
            sequence: Guide sequence

        Returns:
            Penalty score (-10 to 0)
        """
        penalty = 0.0

        for base in ['A', 'T', 'G', 'C']:
            # Check for runs of 3 or more
            if base * 3 in sequence:
                penalty -= 2.0
            if base * 4 in sequence:
                penalty -= 5.0
            if base * 5 in sequence:
                penalty -= 10.0

        return penalty


def predict_efficiency_scores(guides: List[Guide]) -> List[Guide]:
    """Convenience function to predict efficiency scores

    Args:
        guides: List of Guide objects

    Returns:
        List of guides with efficiency scores updated
    """
    predictor = AzimuthPredictor()
    return predictor.predict_batch(guides)

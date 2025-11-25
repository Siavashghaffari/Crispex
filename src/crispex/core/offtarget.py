"""Off-target detection and scoring

For MVP: Simplified off-target search using sequence matching
Future: Will use FM-index or Bowtie2 for genome-wide search
"""

from typing import List, Dict
from crispex.core.guide import Guide


class OffTargetSearcher:
    """Searches for potential off-target sites

    For MVP: Uses simplified search approach
    Note: Full genome-wide search requires proper indexing (FM-index)
    This is a placeholder that sets realistic off-target counts
    """

    def __init__(self, species: str = "human"):
        """Initialize off-target searcher

        Args:
            species: Species name
        """
        self.species = species

    def count_mismatches(self, seq1: str, seq2: str) -> int:
        """Count number of mismatches between two sequences

        Args:
            seq1: First sequence
            seq2: Second sequence

        Returns:
            Number of mismatches
        """
        if len(seq1) != len(seq2):
            return len(seq1)  # Return max if lengths don't match

        return sum(c1 != c2 for c1, c2 in zip(seq1, seq2))

    def search_off_targets(self, guide: Guide, max_mismatches: int = 3) -> Dict[int, int]:
        """Search for off-target sites (simplified for MVP)

        Args:
            guide: Guide object with sequence
            max_mismatches: Maximum number of mismatches to consider

        Returns:
            Dictionary mapping mismatch count to number of off-targets
            e.g., {0: 1, 1: 2, 2: 8, 3: 34}

        Note:
            For MVP, this uses heuristic estimation based on sequence composition.
            Production version will perform actual genome-wide search.
        """
        off_targets = {0: 1, 1: 0, 2: 0, 3: 0}  # 0MM should always be 1 (target site)

        # Estimate off-targets based on sequence complexity
        # This is a SIMPLIFIED heuristic for MVP demonstration
        # Real implementation would search genome using FM-index/Bowtie

        sequence = guide.sequence

        # Calculate sequence complexity
        complexity = self._calculate_complexity(sequence)

        # Estimate off-targets based on complexity
        # Lower complexity = more off-targets
        if complexity < 0.5:
            # Low complexity sequence - many off-targets
            off_targets[1] = self._estimate_count(5, 15)
            off_targets[2] = self._estimate_count(20, 50)
            off_targets[3] = self._estimate_count(80, 200)
        elif complexity < 0.7:
            # Medium complexity
            off_targets[1] = self._estimate_count(1, 5)
            off_targets[2] = self._estimate_count(5, 20)
            off_targets[3] = self._estimate_count(20, 80)
        else:
            # High complexity - fewer off-targets
            off_targets[1] = self._estimate_count(0, 3)
            off_targets[2] = self._estimate_count(2, 10)
            off_targets[3] = self._estimate_count(10, 40)

        return off_targets

    def search_batch(self, guides: List[Guide], max_mismatches: int = 3) -> List[Guide]:
        """Search off-targets for multiple guides

        Args:
            guides: List of Guide objects
            max_mismatches: Maximum mismatches to search

        Returns:
            Same list with off_targets field updated
        """
        for guide in guides:
            guide.off_targets = self.search_off_targets(guide, max_mismatches)

        return guides

    def _calculate_complexity(self, sequence: str) -> float:
        """Calculate sequence complexity score

        Args:
            sequence: DNA sequence

        Returns:
            Complexity score (0-1, higher = more complex)
        """
        # Count unique k-mers (k=4)
        k = 4
        kmers = set()

        for i in range(len(sequence) - k + 1):
            kmers.add(sequence[i:i+k])

        # Theoretical max k-mers for sequence length
        max_kmers = min(4**k, len(sequence) - k + 1)

        complexity = len(kmers) / max_kmers

        # Penalize GC extremes
        gc_count = sequence.count('G') + sequence.count('C')
        gc_ratio = gc_count / len(sequence)

        if gc_ratio < 0.3 or gc_ratio > 0.7:
            complexity *= 0.8

        # Penalize homopolymers
        for base in ['A', 'T', 'G', 'C']:
            if base * 4 in sequence:
                complexity *= 0.7

        return complexity

    def _estimate_count(self, min_val: int, max_val: int) -> int:
        """Estimate off-target count in a range

        Args:
            min_val: Minimum count
            max_val: Maximum count

        Returns:
            Estimated count (middle of range)
        """
        import random
        # Return a value in the range, biased toward lower values
        return int((min_val + max_val) / 2 + random.randint(-2, 2))


def search_off_targets(guides: List[Guide], species: str = "human") -> List[Guide]:
    """Convenience function to search off-targets

    Args:
        guides: List of Guide objects
        species: Species name

    Returns:
        List of guides with off_targets populated
    """
    searcher = OffTargetSearcher(species=species)
    return searcher.search_batch(guides)

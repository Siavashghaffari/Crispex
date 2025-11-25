"""Guide data structure and basic operations"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Guide:
    """Represents a single sgRNA candidate

    Attributes:
        sequence: 20bp guide sequence (5' to 3', without PAM)
        pam: PAM sequence (e.g., 'NGG' for SpCas9)
        chromosome: Chromosome name (e.g., 'chr17')
        start: Genomic start coordinate (1-based)
        end: Genomic end coordinate (1-based, inclusive)
        strand: '+' or '-'
        efficiency_score: On-target efficiency score (0-100)
        off_targets: Dictionary mapping mismatch count to number of off-targets
                    e.g., {0: 1, 1: 2, 2: 8, 3: 34}
        gc_content: GC percentage (0-100)
        gene_name: Gene symbol (optional)
        exon: Exon number (optional)
    """
    sequence: str
    pam: str
    chromosome: str
    start: int
    end: int
    strand: str
    efficiency_score: float = 0.0
    off_targets: Dict[int, int] = field(default_factory=lambda: {0: 0, 1: 0, 2: 0, 3: 0})
    gc_content: float = 0.0
    gene_name: Optional[str] = None
    exon: Optional[int] = None

    @property
    def full_sequence(self) -> str:
        """Returns guide sequence + PAM for ordering"""
        return self.sequence + self.pam

    def calculate_gc_content(self) -> float:
        """Calculate GC content percentage of the guide sequence"""
        if not self.sequence:
            return 0.0
        gc_count = self.sequence.count('G') + self.sequence.count('C')
        self.gc_content = (gc_count / len(self.sequence)) * 100
        return self.gc_content

    def passes_quality_filters(
        self,
        min_gc: float = 40.0,
        max_gc: float = 60.0,
        max_homopolymer: int = 4
    ) -> bool:
        """Check if guide passes basic quality filters

        Args:
            min_gc: Minimum GC content percentage
            max_gc: Maximum GC content percentage
            max_homopolymer: Maximum allowed homopolymer run length

        Returns:
            True if guide passes all filters
        """
        # Check GC content
        if self.gc_content < min_gc or self.gc_content > max_gc:
            return False

        # Check for homopolymer runs
        for base in ['A', 'T', 'G', 'C']:
            if base * max_homopolymer in self.sequence:
                return False

        # Check for polyT runs (causes pol III termination)
        if 'TTTT' in self.sequence:
            return False

        return True

    def to_dict(self) -> Dict:
        """Convert Guide to dictionary for export"""
        return {
            'guide_sequence': self.sequence,
            'pam_sequence': self.pam,
            'full_sequence': self.full_sequence,
            'chromosome': self.chromosome,
            'start': self.start,
            'end': self.end,
            'strand': self.strand,
            'efficiency_score': round(self.efficiency_score, 1),
            'off_targets_0mm': self.off_targets.get(0, 0),
            'off_targets_1mm': self.off_targets.get(1, 0),
            'off_targets_2mm': self.off_targets.get(2, 0),
            'off_targets_3mm': self.off_targets.get(3, 0),
            'gc_content': round(self.gc_content, 1),
            'gene_name': self.gene_name or '',
            'exon': self.exon or '',
        }

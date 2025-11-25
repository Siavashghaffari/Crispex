"""Genome management and FASTA handling

For MVP, this module provides basic genome file handling.
Future versions will include automatic genome downloading and indexing.
"""

import os
from pathlib import Path
from typing import Optional
from pyfaidx import Fasta
from crispex.utils.errors import GenomeNotInstalledError


class GenomeManager:
    """Manages reference genome files and indexing"""

    def __init__(self, species: str = "human"):
        """Initialize genome manager

        Args:
            species: Species name (human or mouse)
        """
        self.species = species
        self.genome_dir = Path.home() / ".crispex" / "genomes"
        self.genome_file = None
        self.fasta = None

    def get_genome_path(self) -> Path:
        """Get path to genome FASTA file

        Returns:
            Path to genome file

        Raises:
            GenomeNotInstalledError: If genome file not found
        """
        # Genome file naming convention
        genome_files = {
            'human': 'GRCh38.fa',
            'mouse': 'GRCm39.fa'
        }

        genome_filename = genome_files.get(self.species)
        if not genome_filename:
            raise GenomeNotInstalledError(
                f"No genome configuration for species: {self.species}"
            )

        genome_path = self.genome_dir / genome_filename

        if not genome_path.exists():
            raise GenomeNotInstalledError(
                f"Genome file not found: {genome_path}\n\n"
                f"To install the {self.species} genome, run:\n"
                f"  crispex install-genome --species {self.species}\n\n"
                f"Note: For MVP, please manually download and place genome FASTA file at:\n"
                f"  {genome_path}"
            )

        return genome_path

    def load_genome(self) -> Fasta:
        """Load genome FASTA file

        Returns:
            Fasta object for genome access

        Raises:
            GenomeNotInstalledError: If genome cannot be loaded
        """
        if self.fasta is not None:
            return self.fasta

        genome_path = self.get_genome_path()

        try:
            self.fasta = Fasta(str(genome_path))
            return self.fasta

        except Exception as e:
            raise GenomeNotInstalledError(
                f"Failed to load genome file: {e}"
            )

    def get_sequence(self, chromosome: str, start: int, end: int) -> str:
        """Get genomic sequence for a region

        Args:
            chromosome: Chromosome name (e.g., 'chr17')
            start: Start coordinate (1-based)
            end: End coordinate (1-based, inclusive)

        Returns:
            DNA sequence string (uppercase)

        Raises:
            GenomeNotInstalledError: If genome not available
        """
        if self.fasta is None:
            self.load_genome()

        try:
            # pyfaidx uses 0-based indexing, convert from 1-based
            sequence = self.fasta[chromosome][start-1:end].seq
            return sequence.upper()

        except KeyError:
            raise GenomeNotInstalledError(
                f"Chromosome '{chromosome}' not found in genome file. "
                f"Available chromosomes: {list(self.fasta.keys())[:5]}..."
            )

    def is_genome_installed(self) -> bool:
        """Check if genome is installed

        Returns:
            True if genome file exists
        """
        try:
            self.get_genome_path()
            return True
        except GenomeNotInstalledError:
            return False

    def get_chromosome_list(self) -> list:
        """Get list of available chromosomes

        Returns:
            List of chromosome names
        """
        if self.fasta is None:
            self.load_genome()

        return list(self.fasta.keys())


def ensure_genome_dir() -> Path:
    """Ensure genome directory exists

    Returns:
        Path to genome directory
    """
    genome_dir = Path.home() / ".crispex" / "genomes"
    genome_dir.mkdir(parents=True, exist_ok=True)
    return genome_dir

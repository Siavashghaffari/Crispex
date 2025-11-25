"""Ensembl API integration for fetching gene information and sequences"""

import requests
import time
from typing import Dict, Optional, List
from crispex.utils.errors import GeneNotFoundError, APIError


class EnsemblFetcher:
    """Fetches gene information from Ensembl REST API"""

    BASE_URL = "https://rest.ensembl.org"

    def __init__(self, species: str = "human"):
        """Initialize Ensembl fetcher

        Args:
            species: Species name (human, mouse, etc.)
        """
        self.species = species
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Crispex/0.1.0'
        })

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        max_retries: int = 3
    ) -> Dict:
        """Make HTTP request to Ensembl API with retry logic

        Args:
            endpoint: API endpoint path
            params: Query parameters
            max_retries: Maximum number of retry attempts

        Returns:
            JSON response as dictionary

        Raises:
            APIError: If request fails after retries
        """
        url = f"{self.BASE_URL}{endpoint}"

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=30)

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    if attempt < max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    raise APIError(f"Rate limited by Ensembl API. Retry after {retry_after}s")

                # Check for errors
                if response.status_code == 404:
                    return None  # Not found

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise APIError("Ensembl API request timed out after multiple retries")

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise APIError(f"Ensembl API request failed: {e}")

        raise APIError("Maximum retries exceeded")

    def lookup_gene(self, gene_symbol: str) -> Dict:
        """Look up gene information by symbol

        Args:
            gene_symbol: Gene symbol (e.g., 'TP53', 'BRCA1')

        Returns:
            Dictionary with gene information including:
                - id: Ensembl gene ID
                - display_name: Gene symbol
                - description: Gene description
                - seq_region_name: Chromosome
                - start: Genomic start
                - end: Genomic end
                - strand: +1 or -1

        Raises:
            GeneNotFoundError: If gene cannot be found
        """
        endpoint = f"/lookup/symbol/{self.species}/{gene_symbol}"
        params = {'expand': 1}  # Expand to include transcripts

        result = self._make_request(endpoint, params)

        if result is None:
            raise GeneNotFoundError(
                f"Gene '{gene_symbol}' not found in Ensembl database "
                f"({self.species}, assembly: GRCh38 or GRCm39). "
                f"Check spelling or try using Ensembl gene ID."
            )

        return result

    def get_sequence(self, region: str) -> str:
        """Get genomic sequence for a region

        Args:
            region: Genomic region (e.g., 'chr17:7661779..7687550')

        Returns:
            DNA sequence string

        Raises:
            APIError: If sequence cannot be retrieved
        """
        endpoint = f"/sequence/region/{self.species}/{region}"
        params = {'content-type': 'text/plain'}

        try:
            response = self.session.get(
                f"{self.BASE_URL}{endpoint}",
                params=params,
                timeout=60
            )
            response.raise_for_status()
            return response.text.upper()

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to fetch sequence from Ensembl: {e}")

    def get_canonical_transcript(self, gene_id: str) -> Optional[Dict]:
        """Get canonical transcript for a gene

        Args:
            gene_id: Ensembl gene ID

        Returns:
            Transcript information dictionary or None

        Raises:
            APIError: If request fails
        """
        endpoint = f"/lookup/id/{gene_id}"
        params = {'expand': 1}

        result = self._make_request(endpoint, params)

        if not result or 'Transcript' not in result:
            return None

        # Find canonical transcript
        transcripts = result.get('Transcript', [])
        canonical = None

        for transcript in transcripts:
            if transcript.get('is_canonical', 0) == 1:
                canonical = transcript
                break

        # Fallback to longest transcript if no canonical marked
        if not canonical and transcripts:
            canonical = max(transcripts, key=lambda t: t.get('length', 0))

        return canonical

    def get_gene_sequence(self, gene_symbol: str) -> Dict:
        """Get complete gene information and sequence

        Args:
            gene_symbol: Gene symbol

        Returns:
            Dictionary with:
                - gene_info: Gene metadata
                - sequence: Full gene sequence
                - chromosome: Chromosome name
                - start: Start coordinate
                - end: End coordinate
                - strand: Strand (+1 or -1)

        Raises:
            GeneNotFoundError: If gene not found
            APIError: If sequence retrieval fails
        """
        # Lookup gene
        gene_info = self.lookup_gene(gene_symbol)

        # Extract coordinates
        chromosome = gene_info['seq_region_name']
        if not chromosome.startswith('chr'):
            chromosome = f"chr{chromosome}"

        start = gene_info['start']
        end = gene_info['end']
        strand = '+' if gene_info['strand'] > 0 else '-'

        # Fetch sequence
        region = f"{gene_info['seq_region_name']}:{start}..{end}"
        sequence = self.get_sequence(region)

        return {
            'gene_info': gene_info,
            'sequence': sequence,
            'chromosome': chromosome,
            'start': start,
            'end': end,
            'strand': strand,
            'gene_id': gene_info['id'],
            'gene_symbol': gene_info['display_name'],
            'description': gene_info.get('description', ''),
            'length': end - start + 1
        }


def fetch_gene_sequence(gene_symbol: str, species: str = "human") -> Dict:
    """Convenience function to fetch gene sequence

    Args:
        gene_symbol: Gene symbol (e.g., 'TP53')
        species: Species name

    Returns:
        Dictionary with gene information and sequence

    Raises:
        GeneNotFoundError: If gene not found
        APIError: If retrieval fails
    """
    fetcher = EnsemblFetcher(species=species)
    return fetcher.get_gene_sequence(gene_symbol)

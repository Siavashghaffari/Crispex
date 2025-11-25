"""Custom exceptions for Crispex"""


class CrispexError(Exception):
    """Base exception for all Crispex errors"""
    pass


class GeneNotFoundError(CrispexError):
    """Raised when a gene cannot be found in the database"""
    pass


class GenomeNotInstalledError(CrispexError):
    """Raised when required reference genome is not installed locally"""
    pass


class InvalidInputError(CrispexError):
    """Raised when user input is invalid"""
    pass


class InvalidCoordinatesError(InvalidInputError):
    """Raised when genomic coordinates are malformed"""
    pass


class InvalidSpeciesError(InvalidInputError):
    """Raised when species is not supported"""
    pass


class APIError(CrispexError):
    """Raised when external API calls fail"""
    pass


class ModelLoadError(CrispexError):
    """Raised when ML model cannot be loaded"""
    pass

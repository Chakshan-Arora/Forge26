"""
Configuration settings for Policy Intel Regulatory Intelligence Engine.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field


class MatcherConfig(BaseModel):
    """Configuration for clause matching and text similarity."""
    exact_match_threshold: float = Field(0.99, description="Threshold for exact textual match")
    high_similarity_threshold: float = Field(0.85, description="High similarity threshold for modified clauses")
    medium_similarity_threshold: float = Field(0.60, description="Medium similarity threshold for candidate pairing")
    renumbering_similarity_threshold: float = Field(0.78, description="Minimum similarity to detect renumbering")
    
    # Weights for hybrid matching
    structural_weight: float = Field(0.35, description="Weight for clause number/section hierarchy")
    lexical_weight: float = Field(0.45, description="Weight for n-gram / token overlap")
    semantic_weight: float = Field(0.20, description="Weight for semantic/vector similarity")


class IntelligenceSettings(BaseModel):
    """Global configuration settings for intelligence components."""
    matcher: MatcherConfig = Field(default_factory=MatcherConfig)
    
    # Financial thresholds parsing defaults
    default_currency: str = "INR"
    
    # Confidence scoring
    default_direct_confidence: float = 0.95
    default_inferred_confidence: float = 0.75
    minimum_actionable_confidence: float = 0.50
    
    # Graph settings
    graph_backend: str = "networkx" # 'networkx' or 'neo4j'
    strict_evidence_enforcement: bool = True


DEFAULT_SETTINGS = IntelligenceSettings()

"""
Policy Intel - Regulatory Intelligence & Impact Analysis Engine.

Core engine for clause-level policy comparison, temporal knowledge graph modeling,
point-in-time applicability resolution, evidence-backed impact analysis,
and conflict detection across Indian Central Government education policies and scholarships.
"""

from intelligence.config import (
    MatcherConfig,
    IntelligenceSettings,
    DEFAULT_SETTINGS,
)
from intelligence.normalizer import RegulatoryNormalizer
from intelligence.semantic_comparator import SemanticComparator
from intelligence.clause_matcher import ClauseMatcher, ClauseMatchResult
from intelligence.change_classifier import ChangeClassifier
from intelligence.change_detector import ChangeDetector, ChangeDetectionSummary
from intelligence.knowledge_graph import BaseRegulatoryGraph, NetworkXRegulatoryGraph

# Convenient alias
KnowledgeGraph = NetworkXRegulatoryGraph
from intelligence.temporal_resolver import TemporalResolver
from intelligence.impact_analyzer import ImpactAnalyzer
from intelligence.conflict_detector import ConflictDetector
from intelligence.evidence_engine import EvidenceEngine, EvidenceMissingError
from intelligence.engine import PolicyIntelEngine

__all__ = [
    "MatcherConfig",
    "IntelligenceSettings",
    "DEFAULT_SETTINGS",
    "RegulatoryNormalizer",
    "SemanticComparator",
    "ClauseMatcher",
    "ClauseMatchResult",
    "ChangeClassifier",
    "ChangeDetector",
    "ChangeDetectionSummary",
    "BaseRegulatoryGraph",
    "NetworkXRegulatoryGraph",
    "KnowledgeGraph",
    "TemporalResolver",
    "ImpactAnalyzer",
    "ConflictDetector",
    "EvidenceEngine",
    "EvidenceMissingError",
    "PolicyIntelEngine",
]

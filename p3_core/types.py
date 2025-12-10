from dataclasses import dataclass, field
from typing import List, Optional, Dict


# -----------------------------------------
# Wikidata Material (Real-world physics data)
# -----------------------------------------
@dataclass
class WikidataMaterial:
    qid: str
    label: str
    description: Optional[str] = None

    density: Optional[float] = None
    melting_point: Optional[float] = None
    tensile_strength: Optional[float] = None
    thermal_conductivity: Optional[float] = None

    aliases: List[str] = field(default_factory=list)

    embedding: Optional[List[float]] = None  # Filled on Day 2


# -----------------------------------------
# CDDA Item (Game-world item)
# -----------------------------------------
@dataclass
class CddaItem:
    id: str
    name: str

    weight: Optional[float] = None
    volume: Optional[float] = None
    price: Optional[float] = None

    materials: List[str] = field(default_factory=list)

    recipes: List[dict] = field(default_factory=list)

    embedding: Optional[List[float]] = None  # Filled on Day 2

    constituents: Optional[Dict[str, float]] = None  # Day 3
    physics: Optional[Dict[str, float]] = None       # Day 3


# -----------------------------------------
# Match Result (Rosetta-Stone resolution)
# -----------------------------------------
@dataclass
class MatchResult:
    cdda_id: str
    wikidata_id: Optional[str]
    confidence_score: float
    review_needed: bool


# -----------------------------------------
# Physics Properties (used by inheritance engine)
# -----------------------------------------
@dataclass
class PhysicsProperties:
    density: Optional[float] = None
    melting_point: Optional[float] = None
    tensile_strength: Optional[float] = None
    thermal_conductivity: Optional[float] = None

import numpy as np
from p3_core.types import WikidataMaterial, CddaItem
from p3_matcher.material_matcher import MaterialMatcher


def test_basic_material_match():
    # Fake embeddings (384-d like MiniLM)
    steel_emb = np.ones(384)
    sword_emb = np.ones(384)
    wood_emb = np.zeros(384)

    wikidata_materials = [
        WikidataMaterial(
            qid="Q11427",
            label="steel",
            description="alloy of iron",
            density=None,
            melting_point=None,
            tensile_strength=None,
            thermal_conductivity=None,
            aliases=[],
            embedding=steel_emb,
        )
    ]

    cdda_items = [
        CddaItem(
            id="steel_sword",
            name="steel sword",
            weight=None,
            volume=None,
            price=None,
            materials=["steel"],
            recipes=[],
            embedding=sword_emb,
            constituents=None,
            physics=None,
        ),
        CddaItem(
            id="wood_plank",
            name="wood plank",
            weight=None,
            volume=None,
            price=None,
            materials=["wood"],
            recipes=[],
            embedding=wood_emb,
            constituents=None,
            physics=None,
        ),
    ]

    matcher = MaterialMatcher(threshold=0.85)
    results = matcher.match(wikidata_materials, cdda_items)

    assert len(results) == 1
    result = results[0]

    assert result.wikidata_id == "Q11427"
    assert result.cdda_id == "steel_sword"
    assert result.confidence_score > 0.85
    assert result.review_needed is False

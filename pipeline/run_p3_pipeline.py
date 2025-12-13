from p3_wikidata.wikidata_materials_client import WikidataMaterialsClient
from p3_cdda.cdda_loader import CddaLoader

from p3_embeddings.embedder import MiniLMEmbedder
from p3_matcher.material_matcher import MaterialMatcher
from p3_physics.physics_inheritance import PhysicsInheritanceEngine
from p3_pricing.pricing_formula_builder import (
    price_raw_material,
    price_composite_material,
)
from p3_export.ledger_exporter import LedgerExporter


def run_pipeline():
    print("=== Project P3 — Pipeline Running ===")

    # ----------------------------------------------------
    # Step 1: Load real-world physics (Wikidata)
    # ----------------------------------------------------
    print("\n[1] Fetching materials from Wikidata...")
    wiki_client = WikidataMaterialsClient()
    wikidata_materials = wiki_client.fetch_all_materials()
    print(f"  → Loaded {len(wikidata_materials)} Wikidata materials")

    # ----------------------------------------------------
    # Step 2: Load CDDA game items
    # ----------------------------------------------------
    print("\n[2] Loading CDDA items...")
    cdda_loader = CddaLoader("CDDA_JSON")
    cdda_items = cdda_loader.load_all_items()
    print(f"  → Loaded {len(cdda_items)} CDDA items")

    # ----------------------------------------------------
    # Step 3: Embeddings + Matching (Day 2)
    # ----------------------------------------------------
    print("\n[3] Computing embeddings & running matcher...")
    embedder = MiniLMEmbedder()

    wiki_client.embed_materials(wikidata_materials, embedder)
    cdda_loader.embed_items(cdda_items, embedder)

    matcher = MaterialMatcher(threshold=0.85)
    match_results = matcher.match(wikidata_materials, cdda_items)

    print(f"  → Generated {len(match_results)} material matches")

    # ----------------------------------------------------
    # Step 4: Recipe Decomposition + Physics (Day 3)
    # ----------------------------------------------------
    print("\n[4] Applying physics inheritance...")
    physics_engine = PhysicsInheritanceEngine()
    physics_engine.apply(wikidata_materials, match_results)
    print("  → Physics propagation complete")

    # ----------------------------------------------------
    # Step 5: Pricing (Day 4 — Step 2)
    # ----------------------------------------------------
    print("\n[5] Applying pricing formulas...")

    # Price raw Wikidata materials
    for mat in wikidata_materials:
        try:
            mat.price = price_raw_material(mat)
        except Exception:
            mat.price = None

    # Price CDDA items via match results
    for result in match_results:
        try:
            wd_mat = result.wikidata_material
            cdda_item = result.cdda_item

            if cdda_item.constituents:
                prices = [
                    c.price for c in cdda_item.constituents
                    if getattr(c, "price", None) is not None
                ]
                cdda_item.price = price_composite_material(
                    constituent_prices=prices,
                    recipe_depth=len(cdda_item.constituents),
                )
            else:
                cdda_item.price = wd_mat.price

        except Exception:
            cdda_item.price = None

    print("  → Pricing complete")

    # ----------------------------------------------------
    # Step 6: Ledger Export (Day 4 — Step 3)
    # ----------------------------------------------------
    print("\n[6] Exporting final ledger...")
    exporter = LedgerExporter(output_path="ledger_materials.json")
    exporter.export(wikidata_materials, match_results)

    print("\n=== Project P3 — Pipeline COMPLETE ===")


if __name__ == "__main__":
    run_pipeline()

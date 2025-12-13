import json
from typing import List


class LedgerExporter:
    """
    Builds the final ledger_materials.json file
    combining Wikidata, CDDA, physics, and pricing.
    """

    def __init__(self, output_path: str = "ledger_materials.json"):
        self.output_path = output_path

    def export(
        self,
        wikidata_materials: list,
        match_results: List,
    ) -> None:
        """
        Writes final unified ledger to disk.
        """

        ledger = []

        for match in match_results:
            wd = match.wikidata_material
            cdda = match.cdda_item

            entry = {
                "wikidata": {
                    "qid": wd.qid,
                    "label": wd.label,
                    "description": wd.description,
                },
                "cdda": {
                    "id": cdda.id,
                    "name": cdda.name,
                },
                "physics": cdda.physics or wd.__dict__.get("physics"),
                "price": cdda.price,
                "confidence_score": match.confidence_score,
                "review_needed": match.review_needed,
            }

            ledger.append(entry)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=2)

        print(f"✔ Ledger exported → {self.output_path}")

import os
import json
from typing import Dict, List, Any

from p3_core.types import CddaItem


class CddaLoader:
    """
    Loads all CDDA JSON item files from a directory.
    Extracts: id, name, weight, volume, price, materials, recipes.
    """

    def __init__(self, root_dir: str):
        """
        root_dir = path to CDDA data/json folder
        Example: "cdda-repo/data/json"
        """
        self.root_dir = root_dir

    # ---------------------------------------------------------
    # Load ALL JSON files recursively
    # ---------------------------------------------------------
    def _load_json_files(self) -> List[Dict[str, Any]]:
        items = []

        for root, dirs, files in os.walk(self.root_dir):
            for f in files:
                if not f.endswith(".json"):
                    continue

                full_path = os.path.join(root, f)
                try:
                    with open(full_path, "r", encoding="utf-8") as infile:
                        data = json.load(infile)
                        if isinstance(data, dict):
                            # Sometimes CDDA JSON is { "items": [...] }
                            data = data.get("items", [])
                        if isinstance(data, list):
                            items.extend(data)
                except Exception:
                    pass  # Ignore bad files for now

        return items

    # ---------------------------------------------------------
    # Normalize raw CDDA dict → CddaItem dataclass
    # ---------------------------------------------------------
    def _dict_to_cdda_item(self, raw: Dict[str, Any]) -> CddaItem:
        item_id = raw.get("id") or raw.get("abstract")
        name = raw.get("name") if isinstance(raw.get("name"), str) else raw.get("name", {}).get("str", "")

        weight = raw.get("weight")
        volume = raw.get("volume")
        price = raw.get("price")

        materials = []
        if "material" in raw:
            if isinstance(raw["material"], list):
                materials = raw["material"]
            elif isinstance(raw["material"], str):
                materials = [raw["material"]]

        recipes = raw.get("recipes", [])

        return CddaItem(
            id=item_id,
            name=name,
            weight=weight,
            volume=volume,
            price=price,
            materials=materials,
            recipes=recipes,
        )

    # ---------------------------------------------------------
    # Public: Load all CDDA items and convert to dataclasses
    # ---------------------------------------------------------
    def load_all_items(self) -> List[CddaItem]:
        raw_items = self._load_json_files()

        final_items = []
        for raw in raw_items:
            try:
                if "id" not in raw:
                    continue
                item = self._dict_to_cdda_item(raw)
                final_items.append(item)
            except Exception:
                continue

        return final_items

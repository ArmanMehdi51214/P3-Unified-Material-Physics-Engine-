import os
import json
from typing import Dict, List, Any, Optional

import commentjson  # pip install commentjson

from p3_core.types import CddaItem
from p3_embeddings.embedder import MiniLMEmbedder


class CddaLoader:
    """
    Loads CDDA JSON files (CDDA JSON often contains // comments and trailing commas).
    Extracts: id/abstract, name, weight, volume, price, materials, recipes.
    """

    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def _parse_cdda_json(self, text: str) -> Any:
        """
        CDDA JSON isn't always strict JSON. Try strict json first, then commentjson.
        """
        try:
            return json.loads(text)
        except Exception:
            return commentjson.loads(text)

    def _load_json_files(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []

        for root, _, files in os.walk(self.root_dir):
            for f in files:
                if not f.endswith(".json"):
                    continue

                full_path = os.path.join(root, f)

                try:
                    with open(full_path, "r", encoding="utf-8") as infile:
                        text = infile.read()
                    data = self._parse_cdda_json(text)
                except Exception:
                    continue

                # CDDA can be list or dict; dict may have "items"
                if isinstance(data, dict):
                    data = data.get("items", [])

                if isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict):
                            items.append(entry)

        return items

    def _dict_to_cdda_item(self, raw: Dict[str, Any]) -> Optional[CddaItem]:
        item_id = raw.get("id") or raw.get("abstract")
        if not item_id:
            return None

        name = raw.get("name")
        if isinstance(name, dict):
            name = name.get("str") or name.get("str_sp") or name.get("str_pl")

        materials: List[str] = []
        mat_val = raw.get("material")
        if isinstance(mat_val, list):
            materials = [str(x) for x in mat_val]
        elif isinstance(mat_val, str):
            materials = [mat_val]

        return CddaItem(
            id=str(item_id),
            name=(name or str(item_id)),
            weight=raw.get("weight"),
            volume=raw.get("volume"),
            price=raw.get("price"),
            materials=materials,
            recipes=raw.get("recipes", []),
            embedding=None,
            constituents=None,
            physics=None,
        )

    def load_all_items(self) -> List[CddaItem]:
        raw_items = self._load_json_files()
        final_items: List[CddaItem] = []

        for raw in raw_items:
            try:
                item = self._dict_to_cdda_item(raw)
                if item:
                    final_items.append(item)
            except Exception:
                continue

        return final_items

    def embed_items(self, items: List[CddaItem], embedder: MiniLMEmbedder) -> None:
        if not items:
            return

        texts: List[str] = []
        for item in items:
            parts: List[str] = []
            if item.name:
                parts.append(item.name)
            if item.materials:
                parts.extend(item.materials)
            texts.append(" ".join(parts))

        embeddings = embedder.embed(texts)
        for item, emb in zip(items, embeddings):
            item.embedding = emb

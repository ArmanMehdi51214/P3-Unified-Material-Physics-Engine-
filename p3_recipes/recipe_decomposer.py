from typing import Dict, Set
from collections import defaultdict

from p3_core.types import CddaItem


class RecipeDecomposer:
    """
    Decomposes a crafted CDDA item into base material counts
    by recursively following its recipes.
    """

    def __init__(self, item_index: Dict[str, CddaItem]):
        """
        item_index: mapping of item_id -> CddaItem
        """
        self.item_index = item_index
        self._cache: Dict[str, Dict[str, float]] = {}

    def decompose(
        self,
        item: CddaItem,
        _visited: Set[str] | None = None,
    ) -> Dict[str, float]:
        """
        Returns a dict of base_material -> quantity
        """

        if item.id in self._cache:
            return self._cache[item.id]

        if _visited is None:
            _visited = set()

        # cycle protection
        if item.id in _visited:
            return {}

        _visited.add(item.id)

        materials: Dict[str, float] = defaultdict(float)

        # Case 1: item has explicit materials → base case
        if item.materials:
            for mat in item.materials:
                materials[mat] += 1.0

            self._cache[item.id] = dict(materials)
            return dict(materials)

        # Case 2: item has recipes → recurse
        for recipe in item.recipes or []:
            for component_id, qty in recipe.items():
                component = self.item_index.get(component_id)
                if not component:
                    continue

                sub_materials = self.decompose(component, _visited)
                for mat, amount in sub_materials.items():
                    materials[mat] += amount * float(qty)

        self._cache[item.id] = dict(materials)
        return dict(materials)

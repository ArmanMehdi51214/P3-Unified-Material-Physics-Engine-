from typing import Dict
from collections import defaultdict

from p3_core.types import CddaItem, WikidataMaterial


class PhysicsPropagator:
    """
    Propagates real-world physics from base materials
    to CDDA items using weighted averages.
    """

    def __init__(self, wikidata_index: Dict[str, WikidataMaterial]):
        """
        wikidata_index: material_name -> WikidataMaterial
        """
        self.wikidata_index = wikidata_index

    def propagate(
        self,
        item: CddaItem,
        material_breakdown: Dict[str, float],
    ) -> Dict[str, float]:
        """
        material_breakdown: { material_name -> quantity }

        Returns physics dict:
        {
            "density": ...,
            "melting_point": ...,
            "thermal_conductivity": ...
        }
        """

        totals = defaultdict(float)
        total_weight = 0.0

        for mat_name, qty in material_breakdown.items():
            mat = self.wikidata_index.get(mat_name)
            if not mat:
                continue

            weight = float(qty)
            total_weight += weight

            if mat.density is not None:
                totals["density"] += mat.density * weight

            if mat.melting_point is not None:
                totals["melting_point"] += mat.melting_point * weight

            if mat.thermal_conductivity is not None:
                totals["thermal_conductivity"] += mat.thermal_conductivity * weight

        if total_weight == 0:
            return {}

        # normalize
        physics = {
            key: value / total_weight
            for key, value in totals.items()
        }

        item.physics = physics
        return physics

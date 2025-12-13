import os
import requests
from typing import List, Dict, Any, Optional
from p3_embeddings.embedder import MiniLMEmbedder
from p3_core.types import WikidataMaterial


WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

DEFAULT_HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "ProjectP3-MaterialEngine/1.0 (contact: developer@example.com)"
}


class WikidataMaterialsClient:
    """
    Fetches real-world materials and physics properties from Wikidata.
    Handles SPARQL execution + result parsing.
    """

    def __init__(self, queries_dir: str = None):
        # Path to SPARQL query files
        self.queries_dir = queries_dir or os.path.join(
            os.path.dirname(__file__), "queries"
        )

    # ------------------------------------------------------------
    # Load SPARQL file contents
    # ------------------------------------------------------------
    def _load_query(self, filename: str) -> str:
        path = os.path.join(self.queries_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # ------------------------------------------------------------
    # Execute SPARQL query
    # ------------------------------------------------------------
    def _run_query(self, query: str) -> Dict[str, Any]:
        resp = requests.get(
            WIKIDATA_SPARQL_ENDPOINT,
            params={"query": query},
            headers=DEFAULT_HEADERS,
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------
    # Helpers to convert Wikidata bindings to Python numbers
    # ------------------------------------------------------------
    def _parse_float(self, value: Optional[Dict[str, Any]]) -> Optional[float]:
        if not value:
            return None
        try:
            return float(value["value"])
        except Exception:
            return None

    # ------------------------------------------------------------
    # Convert row into WikidataMaterial dataclass
    # ------------------------------------------------------------
    def _binding_to_material(self, row: Dict[str, Any]) -> WikidataMaterial:
        qid = row["material"]["value"].split("/")[-1]
        label = row.get("materialLabel", {}).get("value", "")
        description = row.get("materialDescription", {}).get("value", "")

        density = self._parse_float(row.get("density"))
        melting_point = self._parse_float(row.get("melting_point"))
        tensile_strength = self._parse_float(row.get("tensile_strength"))
        thermal_conductivity = self._parse_float(row.get("thermal_conductivity"))

        return WikidataMaterial(
            qid=qid,
            label=label,
            description=description,
            density=density,
            melting_point=melting_point,
            tensile_strength=tensile_strength,
            thermal_conductivity=thermal_conductivity,
            aliases=[],
            embedding=None,
        )

    # ------------------------------------------------------------
    # Public: Fetch chemical elements
    # ------------------------------------------------------------
    def fetch_elements(self) -> List[WikidataMaterial]:
        query = self._load_query("chemical_elements.sparql")
        data = self._run_query(query)
        results = data["results"]["bindings"]
        return [self._binding_to_material(row) for row in results]

    # ------------------------------------------------------------
    # Public: Fetch common industrial materials
    # ------------------------------------------------------------
    def fetch_common_materials(self) -> List[WikidataMaterial]:
        query = self._load_query("common_materials.sparql")
        data = self._run_query(query)
        results = data["results"]["bindings"]
        return [self._binding_to_material(row) for row in results]

    # ------------------------------------------------------------
    # Public: Fetch alloys (steel, bronze, brass, etc.)
    # ------------------------------------------------------------
    def fetch_alloys(self) -> List[WikidataMaterial]:
        query = self._load_query("alloys.sparql")
        data = self._run_query(query)
        results = data["results"]["bindings"]
        return [self._binding_to_material(row) for row in results]

    # ------------------------------------------------------------
    # Public: Combine all sources into one master list
    # ------------------------------------------------------------
    def fetch_all_materials(self) -> List[WikidataMaterial]:
        materials = []
        materials.extend(self.fetch_elements())
        materials.extend(self.fetch_common_materials())
        materials.extend(self.fetch_alloys())

        # Remove duplicates (same QID)
        unique = {}
        for m in materials:
            unique[m.qid] = m

        return list(unique.values())
    def embed_materials(
        self,
        materials: List[WikidataMaterial],
        embedder: MiniLMEmbedder,
    ) -> None:
        """
        Generate embeddings for WikidataMaterial objects in-place.
        """

        texts = []
        for mat in materials:
            parts = [mat.label]

            if mat.description:
                parts.append(mat.description)

            if mat.aliases:
                parts.extend(mat.aliases)

            texts.append(" ".join(parts))

        embeddings = embedder.embed(texts)

        for mat, emb in zip(materials, embeddings):
            mat.embedding = emb


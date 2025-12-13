from typing import Optional


# -----------------------------
# Helper normalization functions
# -----------------------------

def _safe(v: Optional[float], default: float = 0.0) -> float:
    return float(v) if v is not None else default


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(v, hi))


# -----------------------------
# Core pricing formulas
# -----------------------------

def base_material_price(
    density: Optional[float],
    melting_point: Optional[float],
    tensile_strength: Optional[float] = None,
    rarity_factor: float = 1.0,
) -> float:
    """
    Base price for raw / elemental materials.
    """

    density = _safe(density)
    melting_point = _safe(melting_point)
    tensile_strength = _safe(tensile_strength)

    price = (
        density * 0.4 +
        melting_point * 0.002 +
        tensile_strength * 0.3
    )

    price *= rarity_factor
    return round(_clamp(price, 0.1, 10_000.0), 2)


def composite_material_price(
    constituent_price_sum: float,
    processing_complexity: int,
    loss_factor: float = 0.15,
) -> float:
    """
    Price for alloys / crafted materials.
    """

    processing_multiplier = 1.0 + (processing_complexity * 0.25)
    waste_penalty = 1.0 + loss_factor

    price = constituent_price_sum * processing_multiplier * waste_penalty
    return round(_clamp(price, 0.1, 50_000.0), 2)


def recipe_depth_modifier(depth: int) -> float:
    """
    Deeper crafting chains cost more.
    """

    return 1.0 + min(depth * 0.1, 1.0)


# -----------------------------
# High-level pricing entrypoints
# -----------------------------

def price_raw_material(material) -> float:
    """
    Accepts a WikidataMaterial-like object.
    """

    return base_material_price(
        density=material.density,
        melting_point=material.melting_point,
        tensile_strength=material.tensile_strength,
        rarity_factor=1.2 if material.aliases else 1.0,
    )


def price_composite_material(
    constituent_prices: list[float],
    recipe_depth: int,
) -> float:
    """
    Accepts resolved constituents.
    """

    base = sum(constituent_prices)
    depth_mult = recipe_depth_modifier(recipe_depth)

    return composite_material_price(
        constituent_price_sum=base * depth_mult,
        processing_complexity=recipe_depth,
    )

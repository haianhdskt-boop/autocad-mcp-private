"""Geometry Module: Provides spatial validation and collision detection using Shapely."""

from typing import List, Tuple
from shapely.geometry import Polygon

def create_rectangle(x_min: float, y_min: float, x_max: float, y_max: float) -> Polygon:
    """Create a Shapely Polygon representing a rectangle."""
    return Polygon([
        (x_min, y_min),
        (x_max, y_min),
        (x_max, y_max),
        (x_min, y_max)
    ])

def check_overlap(poly1: Polygon, poly2: Polygon) -> bool:
    """Check if two polygons overlap (intersection area > 0)."""
    return poly1.intersection(poly2).area > 0.0

def validate_furniture_clearance(
    furniture_poly: Polygon, 
    wall_polys: List[Polygon],
    min_clearance_mm: float = 0.0
) -> bool:
    """
    Validate that furniture does not overlap with walls, 
    and maintains a minimum clearance if specified.
    """
    if min_clearance_mm > 0:
        # Buffer creates an expanded polygon to check for clearance
        furniture_poly = furniture_poly.buffer(min_clearance_mm)
        
    for wall in wall_polys:
        if check_overlap(furniture_poly, wall):
            return False
    return True

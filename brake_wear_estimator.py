"""
Brake Pad Wear Estimator

This module provides functions to estimate brake pad wear based on various factors
including miles ridden and weather conditions.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import math


class WeatherCondition(Enum):
    """Enumeration of weather conditions that affect brake pad wear."""
    DRY = "dry"
    WET = "wet"
    RAINY = "rainy"
    SNOWY = "snowy"
    MUDDY = "muddy"
    SANDY = "sandy"


class TerrainType(Enum):
    """Enumeration of terrain types that affect brake pad wear."""
    FLAT = "flat"
    HILLY = "hilly"
    MOUNTAINOUS = "mountainous"
    URBAN = "urban"
    OFF_ROAD = "off_road"


@dataclass
class BrakePadSpecs:
    """Specifications for brake pad material and type."""
    material: str  # "organic", "semi-metallic", "ceramic", "sintered"
    compound_hardness: float  # 1-10 scale, higher = harder
    initial_thickness_mm: float
    minimum_thickness_mm: float


@dataclass
class RidingConditions:
    """Conditions that affect brake pad wear."""
    weather: WeatherCondition
    terrain: TerrainType
    rider_weight_kg: float
    bike_weight_kg: float
    average_speed_kmh: float
    braking_frequency: float  # 1-10 scale, higher = more frequent braking


class BrakeWearEstimator:
    """Estimates brake pad wear based on riding conditions and distance."""
    
    # Weather wear multipliers (higher = more wear)
    WEATHER_MULTIPLIERS = {
        WeatherCondition.DRY: 1.0,
        WeatherCondition.WET: 1.3,
        WeatherCondition.RAINY: 1.5,
        WeatherCondition.SNOWY: 1.8,
        WeatherCondition.MUDDY: 2.2,
        WeatherCondition.SANDY: 2.5,
    }
    
    # Terrain wear multipliers
    TERRAIN_MULTIPLIERS = {
        TerrainType.FLAT: 0.8,
        TerrainType.HILLY: 1.2,
        TerrainType.MOUNTAINOUS: 1.6,
        TerrainType.URBAN: 1.1,
        TerrainType.OFF_ROAD: 1.4,
    }
    
    # Material wear rates (mm per 1000 km under standard conditions)
    MATERIAL_WEAR_RATES = {
        "organic": 0.15,
        "semi-metallic": 0.12,
        "ceramic": 0.08,
        "sintered": 0.10,
    }
    
    def __init__(self, brake_pad_specs: BrakePadSpecs):
        """Initialize the estimator with brake pad specifications."""
        self.brake_pad_specs = brake_pad_specs
        
    def estimate_wear(
        self,
        miles_ridden: float,
        conditions: RidingConditions,
        temperature_celsius: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Estimate brake pad wear based on miles ridden and conditions.
        
        Args:
            miles_ridden: Distance ridden in miles
            conditions: Riding conditions object
            temperature_celsius: Ambient temperature (optional, affects wear in extreme conditions)
            
        Returns:
            Dictionary containing wear estimates and remaining life
        """
        # Convert miles to kilometers
        km_ridden = miles_ridden * 1.60934
        
        # Base wear rate for the material
        base_wear_rate = self.MATERIAL_WEAR_RATES.get(
            self.brake_pad_specs.material, 0.12
        )
        
        # Calculate wear multipliers
        weather_multiplier = self.WEATHER_MULTIPLIERS.get(conditions.weather, 1.0)
        terrain_multiplier = self.TERRAIN_MULTIPLIERS.get(conditions.terrain, 1.0)
        
        # Speed factor (higher speeds = more wear due to increased braking force needed)
        speed_factor = min(1.5, max(0.5, conditions.average_speed_kmh / 30.0))
        
        # Braking frequency factor
        braking_factor = conditions.braking_frequency / 5.0  # Normalize to 1.0
        
        # Weight factor (heavier loads = more wear)
        total_weight = conditions.rider_weight_kg + conditions.bike_weight_kg
        weight_factor = min(1.5, max(0.8, total_weight / 100.0))
        
        # Temperature factor (extreme temperatures can affect wear)
        temp_factor = 1.0
        if temperature_celsius is not None:
            if temperature_celsius < -10 or temperature_celsius > 40:
                temp_factor = 1.2  # 20% more wear in extreme temperatures
        
        # Calculate total wear
        total_wear_mm = (
            base_wear_rate *
            (km_ridden / 1000.0) *  # Convert to per-1000km rate
            weather_multiplier *
            terrain_multiplier *
            speed_factor *
            braking_factor *
            weight_factor *
            temp_factor
        )
        
        # Calculate remaining thickness
        remaining_thickness = self.brake_pad_specs.initial_thickness_mm - total_wear_mm
        
        # Calculate wear percentage
        usable_thickness = self.brake_pad_specs.initial_thickness_mm - self.brake_pad_specs.minimum_thickness_mm
        wear_percentage = min(100.0, max(0.0, (total_wear_mm / usable_thickness) * 100))
        
        # Estimate remaining miles
        remaining_miles = 0.0
        if total_wear_mm > 0:
            wear_per_mile = total_wear_mm / miles_ridden
            remaining_thickness_usable = remaining_thickness - self.brake_pad_specs.minimum_thickness_mm
            if wear_per_mile > 0:
                remaining_miles = remaining_thickness_usable / wear_per_mile
        
        return {
            "wear_mm": round(total_wear_mm, 3),
            "remaining_thickness_mm": round(remaining_thickness, 3),
            "wear_percentage": round(wear_percentage, 1),
            "remaining_miles": round(remaining_miles, 0),
            "needs_replacement": remaining_thickness <= self.brake_pad_specs.minimum_thickness_mm,
            "weather_multiplier": weather_multiplier,
            "terrain_multiplier": terrain_multiplier,
            "speed_factor": round(speed_factor, 2),
            "braking_factor": round(braking_factor, 2),
            "weight_factor": round(weight_factor, 2),
            "temp_factor": temp_factor
        }
    
    def estimate_replacement_miles(
        self,
        conditions: RidingConditions,
        temperature_celsius: Optional[float] = None
    ) -> float:
        """
        Estimate how many miles the brake pads will last under given conditions.
        
        Args:
            conditions: Riding conditions object
            temperature_celsius: Ambient temperature (optional)
            
        Returns:
            Estimated miles until replacement needed
        """
        # Use a small test distance to calculate wear rate
        test_miles = 1000.0
        test_result = self.estimate_wear(test_miles, conditions, temperature_celsius)
        
        # Calculate wear per mile
        wear_per_mile = test_result["wear_mm"] / test_miles
        
        # Calculate usable thickness
        usable_thickness = self.brake_pad_specs.initial_thickness_mm - self.brake_pad_specs.minimum_thickness_mm
        
        # Calculate miles until replacement
        if wear_per_mile > 0:
            return usable_thickness / wear_per_mile
        else:
            return float('inf')  # No wear detected


def estimate_brake_pad_wear(
    miles_ridden: float,
    weather: str,
    terrain: str = "flat",
    brake_material: str = "organic",
    rider_weight_kg: float = 70.0,
    bike_weight_kg: float = 15.0,
    average_speed_kmh: float = 25.0,
    braking_frequency: float = 5.0,
    temperature_celsius: Optional[float] = None
) -> Dict[str, float]:
    """
    Convenience function to estimate brake pad wear with simplified parameters.
    
    Args:
        miles_ridden: Distance ridden in miles
        weather: Weather condition ("dry", "wet", "rainy", "snowy", "muddy", "sandy")
        terrain: Terrain type ("flat", "hilly", "mountainous", "urban", "off_road")
        brake_material: Brake pad material ("organic", "semi-metallic", "ceramic", "sintered")
        rider_weight_kg: Rider weight in kilograms
        bike_weight_kg: Bike weight in kilograms
        average_speed_kmh: Average riding speed in km/h
        braking_frequency: Braking frequency on 1-10 scale
        temperature_celsius: Ambient temperature (optional)
        
    Returns:
        Dictionary with wear estimates
    """
    # Create brake pad specs
    brake_specs = BrakePadSpecs(
        material=brake_material,
        compound_hardness=5.0,  # Default medium hardness
        initial_thickness_mm=4.0,  # Standard initial thickness
        minimum_thickness_mm=1.0   # Standard minimum thickness
    )
    
    # Create riding conditions
    try:
        weather_enum = WeatherCondition(weather.lower())
    except ValueError:
        weather_enum = WeatherCondition.DRY  # Default to dry if invalid
        
    try:
        terrain_enum = TerrainType(terrain.lower())
    except ValueError:
        terrain_enum = TerrainType.FLAT  # Default to flat if invalid
    
    conditions = RidingConditions(
        weather=weather_enum,
        terrain=terrain_enum,
        rider_weight_kg=rider_weight_kg,
        bike_weight_kg=bike_weight_kg,
        average_speed_kmh=average_speed_kmh,
        braking_frequency=braking_frequency
    )
    
    # Create estimator and calculate wear
    estimator = BrakeWearEstimator(brake_specs)
    return estimator.estimate_wear(miles_ridden, conditions, temperature_celsius)


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Mountain biking in wet conditions
    print("=== Mountain Biking Example ===")
    mountain_result = estimate_brake_pad_wear(
        miles_ridden=500,
        weather="wet",
        terrain="mountainous",
        brake_material="sintered",
        rider_weight_kg=80,
        bike_weight_kg=12,
        average_speed_kmh=15,
        braking_frequency=8,
        temperature_celsius=10
    )
    
    for key, value in mountain_result.items():
        print(f"{key}: {value}")
    
    print("\n=== Urban Commuting Example ===")
    urban_result = estimate_brake_pad_wear(
        miles_ridden=1000,
        weather="dry",
        terrain="urban",
        brake_material="organic",
        rider_weight_kg=70,
        bike_weight_kg=10,
        average_speed_kmh=20,
        braking_frequency=6,
        temperature_celsius=25
    )
    
    for key, value in urban_result.items():
        print(f"{key}: {value}") 
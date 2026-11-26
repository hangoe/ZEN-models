"""Display names and colours of model identifiers, shared by the single-run figures.

DISPLAY_NAMES follows the table of model identifiers in the appendix of the thesis.
Colours: one ETH hue per carrier family (CARRIER_COLORS) and per sector (SECTOR_COLORS);
variants of a family are tints of its hue.
"""

from .style import (
    ETH_BLUE,
    ETH_BRONZE,
    ETH_GREEN,
    ETH_GREY,
    ETH_PETROL,
    ETH_PURPLE,
    ETH_RED,
    SOLAR_YELLOW,
    eth_tint,
)

HP_WASTE_BLUE = "#48658F"  # desaturated ETH blue: waste-heat heat pumps

CARRIER_COLORS = {
    "natural_gas": ETH_PETROL, "lng": eth_tint(ETH_PETROL, 0.5),
    "natural_gas_ccs": eth_tint(ETH_PETROL, 0.3),
    "oil": ETH_BRONZE,
    "hard_coal": ETH_GREY, "lignite": eth_tint(ETH_GREY, 0.45),
    "biomass": eth_tint(ETH_GREEN, 0.5), "biomass_ccs": eth_tint(ETH_GREEN, 0.25),
    "electrode_boiler": ETH_GREEN,
    "waste": ETH_RED,
    "nuclear": ETH_PURPLE,
    "hydrogen": eth_tint(ETH_PURPLE, 0.5),
    "solar": SOLAR_YELLOW,
    "wind_onshore": eth_tint(ETH_BLUE, 0.6), "wind_offshore": eth_tint(ETH_BLUE, 0.4),
    "hydro_reservoir": "#1A3F78", "hydro_ror": eth_tint(ETH_BLUE, 0.2),
    "battery": ETH_BLUE, "pumped_hydro": eth_tint(ETH_BLUE, 0.35),
    "carbon_storage": eth_tint(ETH_GREEN, 0.6),
    "tes": eth_tint(ETH_PURPLE, 0.7),
    # heat pumps: one blue family, darker = hotter; waste-heat source = desaturated blue
    "hp_water_150_200": ETH_BLUE, "hp_water_100_150": eth_tint(ETH_BLUE, 0.35),
    "hp_water_0_100": eth_tint(ETH_BLUE, 0.65),
    "hp_waste_150_200": HP_WASTE_BLUE, "hp_waste_100_150": eth_tint(HP_WASTE_BLUE, 0.35),
    "hp_waste_0_100": eth_tint(HP_WASTE_BLUE, 0.65),
}

SECTOR_COLORS = {
    "steel": ETH_BLUE, "primary_steel": ETH_BLUE, "secondary_steel": eth_tint(ETH_BLUE, 0.45),
    "cement": ETH_GREY, "clinker": ETH_GREY,
    "chemicals": ETH_PURPLE, "ammonia": ETH_PURPLE, "methanol": eth_tint(ETH_PURPLE, 0.35),
    "olefin": eth_tint(ETH_PURPLE, 0.6),
    "paper": ETH_PETROL, "food": ETH_GREEN,
    "glass": ETH_BRONZE, "ceramic": eth_tint(ETH_BRONZE, 0.45),
}

DISPLAY_NAMES = {
    # industrial heat supply
    "heat_pump_industry_0_100_water": "Water-source heat pump, 0–100 °C",
    "heat_pump_industry_100_150_water": "Water-source heat pump, 100–150 °C",
    "heat_pump_industry_150_200_water": "Water-source heat pump, 150–200 °C",
    "heat_pump_industry_0_100_waste_heat": "Waste-heat heat pump, 0–100 °C",
    "heat_pump_industry_100_150_waste_heat": "Waste-heat heat pump, 100–150 °C",
    "heat_pump_industry_150_200_waste_heat": "Waste-heat heat pump, 150–200 °C",
    "electrode_boiler_industry": "Electrode boiler",
    "natural_gas_boiler_industry": "Natural gas boiler",
    "coal_boiler_industry": "Hard coal boiler",
    "oil_boiler_industry": "Oil boiler",
    "biomass_boiler_industry": "Biomass boiler",
    "waste_boiler_industry": "Waste boiler",
    "industry_TES": "Thermal energy storage",
    # power generation
    "photovoltaics": "Photovoltaics", "wind_onshore": "Onshore wind", "wind_offshore": "Offshore wind",
    "reservoir_hydro": "Reservoir hydro", "run-of-river_hydro": "Run-of-river hydro",
    "nuclear": "Nuclear", "natural_gas_turbine": "Natural gas turbine",
    "natural_gas_turbine_CCS": "Natural gas turbine with CCS", "hard_coal_plant": "Hard coal plant",
    "lignite_coal_plant": "Lignite plant", "oil_plant": "Oil plant", "biomass_plant": "Biomass plant",
    "biomass_plant_CCS": "Biomass plant with CCS", "waste_plant": "Waste plant",
    # storage
    "battery": "Battery", "pumped_hydro": "Pumped hydro", "natural_gas_storage": "Natural gas storage",
    "oil_storage": "Oil storage", "salt_cavern_storage": "Hydrogen storage (salt cavern)",
    # emissions: carriers (combustion) and technologies (process, capture)
    "crude_oil": "Crude oil", "natural_gas": "Natural gas", "lng": "LNG", "hard_coal": "Hard coal",
    "lignite": "Lignite", "waste": "Waste", "biomass": "Biomass", "diesel": "Diesel", "petrol": "Petrol",
    "glass_production": "Glass production", "ceramic_production": "Ceramic production",
    "paper_production": "Paper production", "food_production": "Food production",
    "cement_kiln": "Cement clinker plant", "BF_BOF": "Blast furnace",
    "BF_BOF_CCS": "Blast furnace with CCS", "EAF": "Electric arc furnace",
    "NG_DRI": "Natural gas direct reduction", "NG_DRI_CCS": "Natural gas direct reduction with CCS",
    "H2_DRI": "Hydrogen direct reduction", "carbon_storage": "Carbon storage",
    # DSM products
    "ammonia_DSM": "Ammonia", "ceramic_DSM": "Ceramic", "clinker_DSM": "Clinker", "food_DSM": "Food",
    "glass_DSM": "Glass", "methanol_DSM": "Methanol", "olefin_DSM": "Olefins", "paper_DSM": "Paper",
    "primary_steel_DSM": "Primary steel", "secondary_steel_DSM": "Secondary steel",
}


def display_name(identifier: str) -> str:
    """Thesis name of a model identifier; unknown ones get "_" -> " ", capitalised."""
    if identifier in DISPLAY_NAMES:
        return DISPLAY_NAMES[identifier]
    s = identifier.replace("_", " ")
    return s[:1].upper() + s[1:]


HEAT_SUPPLY_COLOR_MAP = {
    "heat_pump_industry_150_200_water": CARRIER_COLORS["hp_water_150_200"],
    "heat_pump_industry_100_150_water": CARRIER_COLORS["hp_water_100_150"],
    "heat_pump_industry_0_100_water": CARRIER_COLORS["hp_water_0_100"],
    "heat_pump_industry_150_200_waste_heat": CARRIER_COLORS["hp_waste_150_200"],
    "heat_pump_industry_100_150_waste_heat": CARRIER_COLORS["hp_waste_100_150"],
    "heat_pump_industry_0_100_waste_heat": CARRIER_COLORS["hp_waste_0_100"],
    "electrode_boiler_industry": CARRIER_COLORS["electrode_boiler"],
    "natural_gas_boiler_industry": CARRIER_COLORS["natural_gas"],
    "coal_boiler_industry": CARRIER_COLORS["hard_coal"],
    "oil_boiler_industry": CARRIER_COLORS["oil"],
    "biomass_boiler_industry": CARRIER_COLORS["biomass"],
    "waste_boiler_industry": CARRIER_COLORS["waste"],
}

# Bottom to top: boilers (waste ... electrode), then heat pumps from the hottest to the
# coldest band, waste-heat source before water source within a band.
HEAT_SUPPLY_STACK_ORDER = [
    "waste_boiler_industry", "coal_boiler_industry", "oil_boiler_industry", "biomass_boiler_industry",
    "natural_gas_boiler_industry", "electrode_boiler_industry",
    "heat_pump_industry_150_200_waste_heat", "heat_pump_industry_150_200_water",
    "heat_pump_industry_100_150_waste_heat", "heat_pump_industry_100_150_water",
    "heat_pump_industry_0_100_waste_heat", "heat_pump_industry_0_100_water",
]

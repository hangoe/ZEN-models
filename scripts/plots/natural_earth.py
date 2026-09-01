"""Shared Natural Earth country-polygon loader for Europe maps.

Country borders come from Natural Earth's 50m admin-0-countries dataset,
downloaded once and cached under data/naturalearth/ (gitignored). Used by
plot_country_groups_map.py and plot_mga_investment_map.py, which previously
each carried their own identical copy of this block.
"""

import io
import urllib.request
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

NATURALEARTH_DIR = REPO_ROOT / "data" / "naturalearth"
NATURALEARTH_URL = "https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip"
NATURALEARTH_SHP = NATURALEARTH_DIR / "ne_50m_admin_0_countries.shp"

# set_nodes.csv follows the EU statistical convention (EL, UK), which differs
# from Natural Earth's ISO_A2_EH codes (GR, GB) for those two.
ISO_A2_EH_OVERRIDES = {"EL": "GR", "UK": "GB"}

EUROPE_EXTENT = {"lon": (-25, 45), "lat": (34, 72)}


def ensure_naturalearth_data() -> Path:
    if NATURALEARTH_SHP.exists():
        return NATURALEARTH_SHP
    NATURALEARTH_DIR.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(NATURALEARTH_URL) as response:
        zip_bytes = response.read()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(NATURALEARTH_DIR)
    return NATURALEARTH_SHP

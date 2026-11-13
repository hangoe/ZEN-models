lng
===

availability_import
-------------------

Step 1
LNG import availability data is derived from multiple sources. The main source is the ENTSOG dataset. We use the SciGRID dataset to determine the existing capacity of LNG terminals and thereby distribute the availability. 

**Citations**

- **gie_lng_map**: Gas Infrastructure Europe (GIE) (2024). GIE LNG Map. GIE. https://www.gie.eu/publications/maps/gie-lng-map/
- **entsog**: ENTSOG (2022). Extra EU supply potentials TYNDP 2022. ENTSOG. https://www.entsog.eu/sites/default/files/2021-05/7_ENTSOG%20-%20Extra%20EU%20supply%20potentials%20part%201.pdf. Note: We use the April 2022 update of the extra supply potentials from ENTSOG. The data is available in the TYNDP 2022 dataset.
- **import_increase_gas**: Mike Fulwood, Anouk Honoré, Jack Sharples, Marshall Hall (2022). The EU plan to reduce Russian gas imports by two-thirds by the end of 2022: Practical realities and implications. The Oxford Institute for Energy Studies. https://www.oxfordenergy.org/publications/the-eu-plan-to-reduce-russian-gas-imports-by-two-thirds-by-the-end-of-2022-practical-realities-and-implications/

price_import
------------

Step 1
Carrier import price data is derived from the BloombergNEF LCOE dataset. The data is provided in $/MWh (2021 real) and is converted to Euro/MWh using the ECB dollar-to-euro exchange rate and inflation rate.

**Citation**

BloombergNEF (2022). 1H 2022 LCOE Update - Charts. BloombergNEF. https://about.bnef.com/insights/commodities/2h-2022-levelized-cost-of-electricity-update/. Note: Link is for the 2H 2022 update, but the data is from the 1H 2022 update; original link to the 1H 2022 update is no longer available.

carbon_intensity_carrier_import
-------------------------------

Step 1
Carbon intensity of lng from the IPCC emission factors dataset, converted from kgCO2/TJ to tonsCO2/MWh.

**Citation**

IPCC (2006). 2006 IPCC Guidelines for National Greenhouse Gas Inventories - Volume 2: Energy. 2006 IPCC Guidelines for National Greenhouse Gas Inventories. https://www.ipcc-nggip.iges.or.jp/public/2006gl/. Note: Introduction, Table 1.4
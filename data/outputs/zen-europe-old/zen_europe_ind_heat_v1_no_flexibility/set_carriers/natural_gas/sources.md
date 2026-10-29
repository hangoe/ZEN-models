natural_gas
===========

availability_import
-------------------

Step 1
Natural gas import availability data is derived from multiple sources. First, the SciGRID dataset is used to calculate the import availability of natural gas through cross-border pipelines. Second, the ENTSOG Transmission Capacity Map (TCM) dataset is used to adjust the import availability by adding additional gas import capacity that is not yet part of the SciGRID Database. Third, the ENTSOG dataset is used to adjust the import availability by considering the increase in natural gas imports from other countries. Finally, the Eurostat dataset is used to add domestic production of natural gas.

**Citations**

- **scigrid**: Jan Diettrich, Adam Pluta, Wided Medjroubi, Jan Dasenbrock, Javier Sandoval (2021). SciGRID_gas IGGIELGNC-1. DLR - German Aerospace Center. https://zenodo.org/records/5509988. Note: Significant data inaccuracies are observed for storage data points that are only found in the INET dataset, especially for the UK. Thus, we exclude those storages with only an INET source ID.The original folder has more files (PipeSegments, Nodes, Compressors,...), which are not used here.
- **entsogTCM**: ENTSOG (2021). ENTSOG Transmission Capacity Map 2021. ENTSOG. https://www.entsog.eu/maps#transmission-capacity-map-2021
- **entsog**: ENTSOG (2022). Extra EU supply potentials TYNDP 2022. ENTSOG. https://www.entsog.eu/sites/default/files/2021-05/7_ENTSOG%20-%20Extra%20EU%20supply%20potentials%20part%201.pdf. Note: We use the April 2022 update of the extra supply potentials from ENTSOG. The data is available in the TYNDP 2022 dataset.
- **import_increase_gas**: Mike Fulwood, Anouk Honoré, Jack Sharples, Marshall Hall (2022). The EU plan to reduce Russian gas imports by two-thirds by the end of 2022: Practical realities and implications. The Oxford Institute for Energy Studies. https://www.oxfordenergy.org/publications/the-eu-plan-to-reduce-russian-gas-imports-by-two-thirds-by-the-end-of-2022-practical-realities-and-implications/
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en

price_import
------------

Step 1
Carrier import price data is derived from the BloombergNEF LCOE dataset. The data is provided in $/MWh (2021 real) and is converted to Euro/MWh using the ECB dollar-to-euro exchange rate and inflation rate.

**Citation**

BloombergNEF (2022). 1H 2022 LCOE Update - Charts. BloombergNEF. https://about.bnef.com/insights/commodities/2h-2022-levelized-cost-of-electricity-update/. Note: Link is for the 2H 2022 update, but the data is from the 1H 2022 update; original link to the 1H 2022 update is no longer available.

carbon_intensity_carrier_import
-------------------------------

Step 1
Carbon intensity of natural_gas from the IPCC emission factors dataset, converted from kgCO2/TJ to tonsCO2/MWh.

**Citation**

IPCC (2006). 2006 IPCC Guidelines for National Greenhouse Gas Inventories - Volume 2: Energy. 2006 IPCC Guidelines for National Greenhouse Gas Inventories. https://www.ipcc-nggip.iges.or.jp/public/2006gl/. Note: Introduction, Table 1.4
crude_oil
=========

availability_import
-------------------

Step 1
Oil availability data is derived from the Eurostat dataset, which provides availability data for various energy carriers. Additional data for missing countries (only CH) is obtained from the following datasets: Swiss Energy Balance dataset

**Citations**

- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **swiss_energy_balance**: Swiss Federal Statistical Office (2026). Swiss Energy Balance. Swiss Federal Statistical Office. https://opendata.swiss/en/dataset/energiebilanz-der-schweiz
- **swiss_oil_balance**: Swiss Federal Statistical Office (2026). Swiss Crude Oil Balance. Swiss Federal Statistical Office. https://opendata.swiss/de/dataset/schweizerische-gesamtenergiestatistik-erdolbilanz-der-schweiz
- **shipping_technologies_korberg**: A.D. Korberg, S. Brynolf, M. Grahn, I.R. Skov (2021). Techno-economic assessment of advanced fuels and propulsion systems in future fossil-free ships. Renewable and Sustainable Energy Reviews. https://doi.org/https://doi.org/10.1016/j.rser.2021.110861

price_import
------------

Step 1
Carrier import price data is derived from the BloombergNEF LCOE dataset. The data is provided in $/MWh (2021 real) and is converted to Euro/MWh using the ECB dollar-to-euro exchange rate and inflation rate.

**Citation**

BloombergNEF (2022). 1H 2022 LCOE Update - Charts. BloombergNEF. https://about.bnef.com/insights/commodities/2h-2022-levelized-cost-of-electricity-update/. Note: Link is for the 2H 2022 update, but the data is from the 1H 2022 update; original link to the 1H 2022 update is no longer available.

carbon_intensity_carrier_import
-------------------------------

Step 1
Carbon intensity of crude_oil from the IPCC emission factors dataset, converted from kgCO2/TJ to tonsCO2/MWh.

**Citation**

IPCC (2006). 2006 IPCC Guidelines for National Greenhouse Gas Inventories - Volume 2: Energy. 2006 IPCC Guidelines for National Greenhouse Gas Inventories. https://www.ipcc-nggip.iges.or.jp/public/2006gl/. Note: Introduction, Table 1.4
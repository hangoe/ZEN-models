biomass_plant_CCS
=================

lifetime
--------

Step 1
Technical lifetime for 'biomass_plant_CCS' is the median across all available data for the agencies diw, euref, potencia reporting data for this technology at plant size 'None'. Monetary values are rebased to 2022 Euro using ECB HICP inflation.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
- **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
- **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
- **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
- **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
- **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
- **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016

capacity_addition_unbounded
---------------------------

Step 1
The unbounded capacity addition of carbon storage is based on the median existing and future capacity from the IOGP report, divided by the number of nodes in the dataset.

**Citation**

IOGP (2026). CO2 storage projects in Europe. IOGP. https://iogpeurope.org/carbon-capture-use-storage-feb2023/

capacity_existing
-----------------

Step 1
The existing carbon capture capacity is based on the IOGP report 'CO2 Storage Projects in Europe'. For industrial clusters, the capture capacity is split among the different technologies based on the mapping defined in MAPPING_INDUSTRIAL_CLUSTERS.

**Citation**

IOGP (2026). CO2 storage projects in Europe. IOGP. https://iogpeurope.org/carbon-capture-use-storage-feb2023/

opex_specific_variable
----------------------

Step 1
Variable operational cost for 'biomass_plant_CCS' is the cost of retrofitting 'biomass_plant', i.e. the difference between the two technologies' mean across all available data for the agencies euref, luw, potencia reporting data at plant size 'M', divided by the retrofit flow coupling factor (1.154 tCO2/MWh) to express it per unit of captured CO2. Monetary values are rebased to 2022 Euro using ECB HICP inflation.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
- **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
- **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
- **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
- **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
- **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
- **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016

opex_specific_fixed
-------------------

Step 1
Fixed operational cost for 'biomass_plant_CCS' is the cost of retrofitting 'biomass_plant', i.e. the difference between the two technologies' mean across all available data for the agencies euref, luw, potencia reporting data at plant size 'M', divided by the retrofit flow coupling factor (1.154 tCO2/MWh) to express it per unit of captured CO2. Monetary values are rebased to 2022 Euro using ECB HICP inflation.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
- **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
- **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
- **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
- **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
- **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
- **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016

capex_specific_conversion
-------------------------

Step 1
Specific investment cost (capex) for 'biomass_plant_CCS' is the cost of retrofitting 'biomass_plant', i.e. the difference between the two technologies' mean across all available data for the agencies diw, euref, luw, potencia reporting data at plant size 'M', divided by the retrofit flow coupling factor (1.154 tCO2/MWh) to express it per unit of captured CO2. Monetary values are rebased to 2022 Euro using ECB HICP inflation.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
- **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
- **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
- **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
- **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
- **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
- **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016

conversion_factor
-----------------

Step 1
The conversion factor for CCS technologies is calculated as the difference in efficiency between the base technology and the CCS technology, divided by the carbon intensity of the input fuel and the capture rate of the CCS technology. This factor represents the amount of extra electricity required per unit of sequestered carbon.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **technology_cost_database**:
  - **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
  - **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
  - **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
  - **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
  - **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
  - **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
  - **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
  - **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016
- **ipcc_emission_factors**: IPCC (2006). 2006 IPCC Guidelines for National Greenhouse Gas Inventories - Volume 2: Energy. 2006 IPCC Guidelines for National Greenhouse Gas Inventories. https://www.ipcc-nggip.iges.or.jp/public/2006gl/. Note: Introduction, Table 1.4

retrofit_flow_coupling_factor
-----------------------------

Step 1
The retrofit flow coupling factor of CCS technologies is calculated as the product of the carbon intensity of the input fuel, the capture rate of the CCS technology, and the inverse of the combined base + ccs technology's efficiency (from ['euref', 'potencia']). This factor represents the amount of CO2 captured per unit of fuel input.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **technology_cost_database**:
  - **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
  - **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
  - **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
  - **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
  - **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
  - **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
  - **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
  - **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016
- **ipcc_emission_factors**: IPCC (2006). 2006 IPCC Guidelines for National Greenhouse Gas Inventories - Volume 2: Energy. 2006 IPCC Guidelines for National Greenhouse Gas Inventories. https://www.ipcc-nggip.iges.or.jp/public/2006gl/. Note: Introduction, Table 1.4
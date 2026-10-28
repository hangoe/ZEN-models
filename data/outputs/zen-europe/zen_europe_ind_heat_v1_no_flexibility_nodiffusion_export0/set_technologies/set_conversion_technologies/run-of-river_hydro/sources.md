run-of-river_hydro
==================

lifetime
--------

Step 1
The lifetime of run-of-river hydro is set to 200 years, as specified in the investment settings.

capacity_existing
-----------------

Step 1
The existing capacity of run-of-river_hydro is derived from the hydropower modelling data of the Pan-European Climate Database, aggregated from the ENTSO-E market zones to the nodes.

**Citation**

Matteo De Felice (2020). ENTSO-E Hydropower modelling data (PECD) in CSV format. Zenodo. https://doi.org/https://doi.org/10.5281/zenodo.3985078

capacity_limit
--------------

Step 1
The capacity limit is set to the sum of thehistorical capacity additions across all years.

**Citation**

Matteo De Felice (2020). ENTSO-E Hydropower modelling data (PECD) in CSV format. Zenodo. https://doi.org/https://doi.org/10.5281/zenodo.3985078

max_load
--------

Step 1
Maximum load data for run-of-river hydro technologies is derived from the generation and capacity data from the ENTSOE Transparency Platform for 2019. If available, the Pan-European Climate Database is used to fill in missing nodes.  For SE, DK, the maximum load is estimated based on other countries. For ES, the maximum load is above 1; therefore, the maximum load is normalized to 1 based on the maximum generation.

**Citations**

- **pan_european_climate_database**: Copernicus (2026). Climate and energy related variables from the Pan-European Climate Database derived from reanalysis and climate projections. Copernicus. https://doi.org/https://doi.org/10.24381/cds.f323c5ec
- **entsoe**: ENTSO-E (2026). ENTSO-E Transparency Platform. ENTSO-E Transparency Platform. https://transparency.entsoe.eu/. Note: Queried via the entsoe-py package against the ENTSO-E Transparency Platform RESTful API; requires an API security token in the ENTSOE_API_KEY environment variable.
- **hydro_existing_capacity**:
  - **jrc_hydro_power_database**: Matteo De Felice, Konstantinos Kanellopoulos, Ignacio Hidalgo-Gonzaléz (2019). JRC Hydro-power plants database. JRC. https://github.com/energy-modelling-toolkit/hydro-power-database/
  - **powerplantmatching**: Fabian Gotzens, Heidi Heinrichs, Jonas Hörsch, Fabian Hofmann (2019). Performing energy modelling exercises in a transparent way - The issue of data quality in power plant databases. Energy Strategy Reviews. https://doi.org/https://doi.org/10.1016/j.esr.2018.11.004
  - **entsoe**: ENTSO-E (2026). ENTSO-E Transparency Platform. ENTSO-E Transparency Platform. https://transparency.entsoe.eu/. Note: Queried via the entsoe-py package against the ENTSO-E Transparency Platform RESTful API; requires an API security token in the ENTSOE_API_KEY environment variable.
  - **glohydrores**: Jignesh Shah, Jing Hu, Oreane Y. Edelenbosch, Michelle T. H. van Vliet (2025). Global dataset combining open-source hydropower plant and reservoir data. Scientific Data. https://doi.org/https://doi.org/10.1038/s41597-025-04975-0
  - **pecd_hydro_capacity**: Matteo De Felice (2020). ENTSO-E Hydropower modelling data (PECD) in CSV format. Zenodo. https://doi.org/https://doi.org/10.5281/zenodo.3985078

opex_specific_variable
----------------------

Step 1
Variable operational cost for 'run-of-river_hydro' is the mean across all available data for the agencies euref, luw, potencia reporting data for this technology at plant size 'None'. Monetary values are rebased to 2022 Euro using ECB HICP inflation.

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
Fixed operational cost for 'run-of-river_hydro' is the mean across all available data for the agencies euref, luw, potencia reporting data for this technology at plant size 'None'. Monetary values are rebased to 2022 Euro using ECB HICP inflation.

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
Specific investment cost (capex) for 'run-of-river_hydro' is the mean across all available data for the agencies diw, euref, luw, potencia reporting data for this technology at plant size 'None'. Monetary values are rebased to 2022 Euro using ECB HICP inflation.

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
The conversion factor of run-of-river hydro is manually set to an empty list, as it has no input carrier.
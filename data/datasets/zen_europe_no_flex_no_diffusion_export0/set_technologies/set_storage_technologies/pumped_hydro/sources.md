pumped_hydro
============

lifetime
--------

Step 1
The lifetime of pumped_hydro is based on Schmidt et al. (2019).

**Citation**

Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008

capacity_existing
-----------------

Step 1
The existing turbining power of pumped_hydro is derived from the hydropower modelling data of the Pan-European Climate Database, aggregated from ENTSO-E market zones to model nodes. It combines the complete PECD closed-loop pumped-storage category with the pumped share of open-loop pumped storage. For each node, the open-loop pumped share is the smaller of pumping and turbining power divided by turbining power. This share is applied identically to open-loop turbining power and upper/head-reservoir energy capacity.

**Citation**

Matteo De Felice (2020). ENTSO-E Hydropower modelling data (PECD) in CSV format. Zenodo. https://doi.org/https://doi.org/10.5281/zenodo.3985078

capacity_limit
--------------

Step 1
The capacity limit is set to the sum of thehistorical capacity additions across all years.

**Citation**

Matteo De Felice (2020). ENTSO-E Hydropower modelling data (PECD) in CSV format. Zenodo. https://doi.org/https://doi.org/10.5281/zenodo.3985078

opex_specific_fixed
-------------------

Step 1
Fixed operational cost for 'pumped_hydro' is the mean across all available data for the agencies schmidt reporting data for this technology at plant size 'None'. Monetary values are rebased to 2025 Euro using ECB HICP inflation.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
- **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
- **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
- **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
- **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
- **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
- **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016

efficiency_charge
-----------------

Step 1
The round-trip efficiency of pumped_hydro is 0.78 in Schmidt et al. (2019) and is split evenly between charging and discharging.

**Citation**

Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008

efficiency_discharge
--------------------

Step 1
The round-trip efficiency of pumped_hydro is 0.78 in Schmidt et al. (2019) and is split evenly between charging and discharging.

**Citation**

Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008

capex_specific_storage
----------------------

Step 1
Specific investment cost (capex) of the power capacity for 'pumped_hydro' is the mean across all available data for the agencies schmidt reporting data for this technology at plant size 'None'. Monetary values are rebased to 2025 Euro using ECB HICP inflation.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
- **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
- **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
- **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
- **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
- **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
- **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016

capex_specific_storage_energy
-----------------------------

Step 1
Specific investment cost (capex) of the energy capacity for 'pumped_hydro' is the mean across all available data for the agencies schmidt reporting data for this technology at plant size 'None'. Monetary values are rebased to 2025 Euro using ECB HICP inflation.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
- **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
- **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
- **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
- **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
- **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
- **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016

capacity_existing_energy
------------------------

Step 1
The existing storage-energy capacity of pumped_hydro is derived from the hydropower modelling data of the Pan-European Climate Database, aggregated from ENTSO-E market zones to model nodes. It combines the complete PECD closed-loop pumped-storage category with the pumped share of open-loop pumped storage. For each node, the open-loop pumped share is the smaller of pumping and turbining power divided by turbining power. This share is applied identically to open-loop turbining power and upper/head-reservoir energy capacity.

**Citation**

Matteo De Felice (2020). ENTSO-E Hydropower modelling data (PECD) in CSV format. Zenodo. https://doi.org/https://doi.org/10.5281/zenodo.3985078

capacity_limit_energy
---------------------

Step 1
The energy capacity limit is set to the sum of thehistorical capacity additions across all years.

**Citation**

Matteo De Felice (2020). ENTSO-E Hydropower modelling data (PECD) in CSV format. Zenodo. https://doi.org/https://doi.org/10.5281/zenodo.3985078

flow_storage_inflow
-------------------

Step 1
The natural inflow of pumped_hydro uses PECD 4.2. Open-loop pumped-storage inflow is allocated with the same legacy PECD fractions as its power and energy capacities. Weekly energy is converted to an hourly profile, with the final weekly rate extended over the remaining 24 hours of the year. No run-of-river energy was reclassified as reservoir inflow.

**Citation**

Copernicus (2026). Climate and energy related variables from the Pan-European Climate Database derived from reanalysis and climate projections. Copernicus. https://doi.org/https://doi.org/10.24381/cds.f323c5ec
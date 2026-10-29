heat_pump_industry_150_200_waste_heat_paper
===========================================

lifetime
--------

Step 1
Technical lifetime for 'heat_pump_industry_150_200_waste_heat_paper' ('heat_pump_industry_150' used as a proxy) is the median across all available data for the agencies dea reporting data for this technology at plant size 'None'. Monetary values are rebased to 2025 Euro using ECB HICP inflation.

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
Annual build-out of the DH heat pumps (fleet / 15.0 yr, general industry assumptions) per period, split by sector-band demand share, heat source and node, see docs, 'Diffusion'.

**Citations**

- **industry_production_data**:
  - **rehfeldt2017**: Rehfeldt, M., Fleiter, T., Toro, F. (2017). A bottom-up estimation of the heating and cooling demand in European industry. Energy Efficiency. https://doi.org/10.1007/s12053-017-9571-y. Note: Sub-process energy intensities and temperature distributions.
  - **aidres**: Luc Girardin, Juan Correa Laguna, Joris Valee (2023). Advancing industrial decarbonisation by assessing the future use of renewable energies in industrial processes. Publications Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/d80943a6-5116-11ee-9220-01aa75ed71a1/language-en
  - **wolf2017**: Wolf, S. (2017). Integration von Wärmepumpen in industrielle Produktionssysteme - Potenziale und Instrumente zur Potenzialerschließung. PhD thesis, University of Stuttgart.. Note: Table 4-7, process heat up to 150 °C and up to 200 °C.
  - **jrc_idees**: Mate Rozsai, Marc Jaxa-Rozen, Raffaele Salvucci, Przemyslaw Sikora, Juan Gea Bermudez, Frederik Neuwahl (2026). JRC-IDEES-2023: the Integrated Database of the European Energy System. JRC. https://doi.org/10.2760/6945021
  - **faostat_food**: Food and Agriculture Organization of the United Nations (2026). FAOSTAT: Crops and livestock products. FAOSTAT. https://www.fao.org/faostat/en/#data/QCL
  - **jrc_bat_paper**: European Commission, Joint Research Centre (2015). Best Available Techniques (BAT) reference document for the production of pulp, paper and board. Publications Office of the European Union. https://doi.org/10.2791/370629. Note: Tables 1.1-1.2, paper consumption 2008.
  - **jrc_eu_times_industry**: European Commission, Joint Research Centre (2019). JRC-EU-TIMES model, industry technologies. JRC-EU-TIMES. https://doi.org/10.2790/97596. Note: JRC_EU_TIMES_model_input.xls (2019.11), sheet IND. The DOI is the one of the model description (2013).
  - **cement_production_gardarsdottir**: Stefania Osk Gardarsdottir, Edoardo De Lena, Matteo Romano, Simon Roussanaly, Mari Voldsund, JosÃ©-Francisco PÃ©rez-Calvo, David Berstad, Chao Fu, Rahul Anantharaman, Daniel Sutter, Matteo Gazzani, Marco Mazzotti, Giovanni Cinti (2019). Comparison of Technologies for CO2 Capture from Cement Productionâ€”Part 2: Cost Analysis. MDPI Energies. https://www.mdpi.com/1996-1073/12/3/542
  - **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
  - **ecb**: European Central Bank (2026). HICP - Overall index, Euro area, Monthly. European Central Bank. https://data.ecb.europa.eu/
  - **worldbank_population**: World Bank (2026). Population estimates and projections. World Bank DataBank. https://databank.worldbank.org/source/population-estimates-and-projections#. Note: Indicator SP.POP.TOTL, total population in persons.
  - **industry_production_costs**: Goericke, H. (2026). Costs of industrial production technologies, literature review. docs/files/user_guide/industry.md.. Note: The sources of each value are given in the description column.
  - **industry_general_assumptions**: Goericke, H. (2026). General assumptions of the industry sectors. docs/files/user_guide/industry.md.. Note: The reasoning of each value is given in the description column.
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **bfe_industry**: Bundesamt für Energie BFE (2025). Energieverbrauch in der Industrie und im Dienstleistungssektor. Bundesamt für Energie BFE. https://pubdb.bfe.admin.ch/de/publication/download/12230. Note: Branches 1 (food), 3 (paper) and 6 (other non-metallic minerals).
- **jrc_idees**: Mate Rozsai, Marc Jaxa-Rozen, Raffaele Salvucci, Przemyslaw Sikora, Juan Gea Bermudez, Frederik Neuwahl (2026). JRC-IDEES-2023: the Integrated Database of the European Energy System. JRC. https://doi.org/10.2760/6945021
- **technology_cost_database**:
  - **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
  - **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
  - **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
  - **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
  - **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
  - **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
  - **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
  - **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016
- **industry_general_assumptions**: Goericke, H. (2026). General assumptions of the industry sectors. docs/files/user_guide/industry.md.. Note: The reasoning of each value is given in the description column.

capacity_existing
-----------------

Step 1
No existing industrial heat pumps.

capacity_limit
--------------

Step 1
Waste heat of processes > 200 °C (their fuel demand), split by band heat demand. 2022: at most 2% of band demand per node (general industry assumptions), split by heat source.

**Citations**

- **industry_production_data**:
  - **rehfeldt2017**: Rehfeldt, M., Fleiter, T., Toro, F. (2017). A bottom-up estimation of the heating and cooling demand in European industry. Energy Efficiency. https://doi.org/10.1007/s12053-017-9571-y. Note: Sub-process energy intensities and temperature distributions.
  - **aidres**: Luc Girardin, Juan Correa Laguna, Joris Valee (2023). Advancing industrial decarbonisation by assessing the future use of renewable energies in industrial processes. Publications Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/d80943a6-5116-11ee-9220-01aa75ed71a1/language-en
  - **wolf2017**: Wolf, S. (2017). Integration von Wärmepumpen in industrielle Produktionssysteme - Potenziale und Instrumente zur Potenzialerschließung. PhD thesis, University of Stuttgart.. Note: Table 4-7, process heat up to 150 °C and up to 200 °C.
  - **jrc_idees**: Mate Rozsai, Marc Jaxa-Rozen, Raffaele Salvucci, Przemyslaw Sikora, Juan Gea Bermudez, Frederik Neuwahl (2026). JRC-IDEES-2023: the Integrated Database of the European Energy System. JRC. https://doi.org/10.2760/6945021
  - **faostat_food**: Food and Agriculture Organization of the United Nations (2026). FAOSTAT: Crops and livestock products. FAOSTAT. https://www.fao.org/faostat/en/#data/QCL
  - **jrc_bat_paper**: European Commission, Joint Research Centre (2015). Best Available Techniques (BAT) reference document for the production of pulp, paper and board. Publications Office of the European Union. https://doi.org/10.2791/370629. Note: Tables 1.1-1.2, paper consumption 2008.
  - **jrc_eu_times_industry**: European Commission, Joint Research Centre (2019). JRC-EU-TIMES model, industry technologies. JRC-EU-TIMES. https://doi.org/10.2790/97596. Note: JRC_EU_TIMES_model_input.xls (2019.11), sheet IND. The DOI is the one of the model description (2013).
  - **cement_production_gardarsdottir**: Stefania Osk Gardarsdottir, Edoardo De Lena, Matteo Romano, Simon Roussanaly, Mari Voldsund, JosÃ©-Francisco PÃ©rez-Calvo, David Berstad, Chao Fu, Rahul Anantharaman, Daniel Sutter, Matteo Gazzani, Marco Mazzotti, Giovanni Cinti (2019). Comparison of Technologies for CO2 Capture from Cement Productionâ€”Part 2: Cost Analysis. MDPI Energies. https://www.mdpi.com/1996-1073/12/3/542
  - **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
  - **ecb**: European Central Bank (2026). HICP - Overall index, Euro area, Monthly. European Central Bank. https://data.ecb.europa.eu/
  - **worldbank_population**: World Bank (2026). Population estimates and projections. World Bank DataBank. https://databank.worldbank.org/source/population-estimates-and-projections#. Note: Indicator SP.POP.TOTL, total population in persons.
  - **industry_production_costs**: Goericke, H. (2026). Costs of industrial production technologies, literature review. docs/files/user_guide/industry.md.. Note: The sources of each value are given in the description column.
  - **industry_general_assumptions**: Goericke, H. (2026). General assumptions of the industry sectors. docs/files/user_guide/industry.md.. Note: The reasoning of each value is given in the description column.
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **bfe_industry**: Bundesamt für Energie BFE (2025). Energieverbrauch in der Industrie und im Dienstleistungssektor. Bundesamt für Energie BFE. https://pubdb.bfe.admin.ch/de/publication/download/12230. Note: Branches 1 (food), 3 (paper) and 6 (other non-metallic minerals).
- **jrc_idees**: Mate Rozsai, Marc Jaxa-Rozen, Raffaele Salvucci, Przemyslaw Sikora, Juan Gea Bermudez, Frederik Neuwahl (2026). JRC-IDEES-2023: the Integrated Database of the European Energy System. JRC. https://doi.org/10.2760/6945021
- **technology_cost_database**:
  - **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
  - **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
  - **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
  - **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
  - **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
  - **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
  - **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
  - **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016
- **industry_general_assumptions**: Goericke, H. (2026). General assumptions of the industry sectors. docs/files/user_guide/industry.md.. Note: The reasoning of each value is given in the description column.

opex_specific_variable
----------------------

Step 1
Variable operational cost for 'heat_pump_industry_150_200_waste_heat_paper' ('heat_pump_industry_150' used as a proxy) is the mean across all available data for the agencies dea reporting data for this technology at plant size 'None'. Monetary values are rebased to 2025 Euro using ECB HICP inflation.

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
Fixed operational cost for 'heat_pump_industry_150_200_waste_heat_paper' ('heat_pump_industry_150' used as a proxy) is the mean across all available data for the agencies dea reporting data for this technology at plant size 'None'. Monetary values are rebased to 2025 Euro using ECB HICP inflation.

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
Specific investment cost (capex) for 'heat_pump_industry_150_200_waste_heat_paper' ('heat_pump_industry_150' used as a proxy) is the mean across all available data for the agencies dea reporting data for this technology at plant size 'None'. Monetary values are rebased to 2025 Euro using ECB HICP inflation.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **tyndp**: ENTSOG, ENTSO-E (2020). TYNDP 2020 Scenario Building Guidelines - Cost Assumptions. ENTSOG/ENTSO-E. https://2020.entsos-tyndp-scenarios.eu/wp-content/uploads/2020/07/TYNDP_2020_Scenario_Building-Guidelines_03_Annex_2_Cost_Assumptions_final_report.pdf. Note: Cost figures transcribed into TYNDP_cost_assumptions.xlsx from the PDF above.
- **diw**: Wolf-Peter Schill, Alexander Zerrahn, Fabian Kunz (2018). Current and Prospective Costs of Electricity Generation until 2050. DIW Data Documentation 94. https://www.diw.de/documents/publikationen/73/diw_01.c.573921.de/diwkompakt_2018-128.pdf
- **luw**: Christian Breyer, Dmitrii Bogdanov, Manish Ram, Siavash Khalili, Eero Vartiainen, David Moser, Eduardo Román Medina, Gaetan Masson, Arman Aghahosseini, Theophilus N. O. MensahGabriel Lopez, Michael Schmela, Raffaele Rossi, Walburga Hemetsberger, Arnulf Jaeger-Waldau (2022). Reflecting the energy transition from a European perspective and in the global context—Relevance of solar photovoltaics benchmarking two ambitious scenarios. Progress in Photovoltaics. https://onlinelibrary.wiley.com/doi/10.1002/pip.3659
- **euref**: European Commission (2021). EU Reference Scenario 2020 - Technology Assumptions for the Power and Heat Sector. European Commission, DG Energy. https://energy.ec.europa.eu/data-and-analysis/energy-modelling/eu-reference-scenario-2020_en
- **potencia**: European Commission Joint Research Centre (2018). POTEnCIA Central scenario 2018 - technology cost and performance projections. European Commission, JRC POTEnCIA model. https://ec.europa.eu/jrc/potencia
- **schmidt**: Oliver Schmidt, Sylvain Melchior, Adam Hawkes, Iain Staffell (2019). Projecting the Future Levelized Cost of Electricity Storage Technologies. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2018.12.008
- **victoria**: Marta Victoria, Elisabeth Zeyen, Tom Brown (2022). Speed of technological transformations required in Europe to achieve different climate goals. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2022.04.016

----

Step 2
The DEA investment cost of 'heat_pump_industry_150' (Danish Energy Agency, Technology Data for Industrial Process Heat, https://www.ens.dk/technologydata) plus an assumed 1500.0 Euro/kW for the waste-heat recovery, within the range of 1,234-1,645 Euro/kW in Stark et al. (2025), Waste heat is mostly a waste of time, Joule 9, 102157, Table 2, doi:10.1016/j.joule.2025.102157.

conversion_factor
-----------------

Step 1
The COP of 1.7926 is 50% of the Carnot COP between the source (50 °C) and the centre of the temperature band (175 °C). Carnot fraction and source temperatures are assumptions based on Bever et al. (2024), High-Temperature Heat Pumps for Industrial Use, Chemie Ingenieur Technik, doi:10.1002/cite.202300241, and Agora Energiewende and Fraunhofer IEG (2023), Roll-out von Großwärmepumpen in Deutschland.
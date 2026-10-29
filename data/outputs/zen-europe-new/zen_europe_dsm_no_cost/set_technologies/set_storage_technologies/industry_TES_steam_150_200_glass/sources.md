industry_TES_steam_150_200_glass
================================

lifetime
--------

Step 1
Lifetime of a steam accumulator.

**Citation**

Mayer, P., Heer, M., Shu, D. Y., Zielonka, N., Leenders, L., Baader, F. J., Bardow, A. (2024). Flexibility from industrial demand-side management in net-zero sector-coupled national energy systems. Frontiers in Energy Research. https://doi.org/10.3389/fenrg.2024.1443506. Note: Table 3, thermal energy storage technologies.

capacity_limit
--------------

Step 1
The flat heat demand of the storage's band and all lower bands (reachable via the temperature cascade) times the capacity limit margin of 2.0 (general industry assumptions); 0 at nodes without demand.

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
Against cycling.

efficiency_charge
-----------------

Step 1
Losses neglected.

efficiency_discharge
--------------------

Step 1
Losses neglected.

self_discharge
--------------

Step 1
hot water tank central, tau = 180 days.

**Citation**

Brown, T., Schlachtberger, D., Kies, A., Schramm, S., Greiner, M. (2018). Synergies of sector coupling and transmission reinforcement in a cost-optimised, highly renewable European energy system. Energy. https://doi.org/10.1016/j.energy.2018.06.222. Note: Table 1 and Section 3, hot water tanks.

capex_specific_storage_energy
-----------------------------

Step 1
Investment cost of a steam accumulator.

**Citation**

Mayer, P., Heer, M., Shu, D. Y., Zielonka, N., Leenders, L., Baader, F. J., Bardow, A. (2024). Flexibility from industrial demand-side management in net-zero sector-coupled national energy systems. Frontiers in Energy Research. https://doi.org/10.3389/fenrg.2024.1443506. Note: Table 3, thermal energy storage technologies.

opex_specific_fixed_energy
--------------------------

Step 1
Fixed O&M cost of a steam accumulator.

**Citation**

Mayer, P., Heer, M., Shu, D. Y., Zielonka, N., Leenders, L., Baader, F. J., Bardow, A. (2024). Flexibility from industrial demand-side management in net-zero sector-coupled national energy systems. Frontiers in Energy Research. https://doi.org/10.3389/fenrg.2024.1443506. Note: Table 3, thermal energy storage technologies.

energy_to_power_ratio_min
-------------------------

Step 1
Minimum duration of a steam accumulator.

energy_to_power_ratio_max
-------------------------

Step 1
Maximum duration of a steam accumulator.
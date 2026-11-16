food
====

demand
------

Step 1
The food demand equals today's physical production, flat over the 8760 hours of the year. The production is taken from the JRC-IDEES physical output (glass, paper), derived from the JRC-IDEES thermal energy consumption and the Rehfeldt et al. (2017) fuel intensity (ceramic), or from the Rehfeldt et al. (2017) activity split by the FAOSTAT production (food). Nodes without JRC-IDEES data use a proxy node (CH as AT, NO as FI, UK as DE scaled by the World Bank population); for paper, their consumption from the JRC BAT reference document is used.

**Citations**

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

availability_export_yearly
--------------------------

Step 1
No export limit.
district_heating_grid
=====================

lifetime
--------

Step 1
The lifetime of district heating grids is based on data from the DEA dataset, which provides information on the distribution of lifetimes for district heating grids. The specific value used here is the reference value for suburban district heating grids.

**Citation**

Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.

capacity_existing
-----------------

Step 1
The existing capacity of a heat conversion technology is calculated based on the peak heat demand and the heating share of the technology. The peak heat demand is derived from the heat demand time series, while the heating share is obtained mainly from the Eurostat dataset. 

**Citations**

- **jrc_idees**: Mate Rozsai, Marc Jaxa-Rozen, Raffaele Salvucci, Przemyslaw Sikora, Juan Gea Bermudez, Frederik Neuwahl (2026). JRC-IDEES-2023: the Integrated Database of the European Energy System. JRC. https://publications.jrc.ec.europa.eu/repository/handle/JRC144707
- **when2heat**: Oliver Ruhnau, Lion Hirth, Aaron Praktiknjo, Jarusch Muessel (2023). When2Heat. Open power system data. https://data.open-power-system-data.org/when2heat/
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **desnz**: Department for Energy Security and Net Zero (DESNZ) (2025). Energy Consumption in the UK (ECUK): End Use Tables. DESNZ. https://www.gov.uk/government/statistics/energy-consumption-in-the-uk-2025
- **bfe**: Bundesamt für Energie (BFE) (2025). Energieverbrauch nach Verwendungszweck. BFE. https://www.bfe.admin.ch/bfe/de/home/versorgung/statistik-und-geodaten/energiestatistiken/energieverbrauch-nach-verwendungszweck.html
- **energifaktanorge**: Energifaktanorge (2025). Energy use by sector. Energifaktanorge. https://energifaktanorge.no/en/norsk-energibruk/energibruken-i-ulike-sektorer/#household-and-service-industries
- **energieschweiz**: Diego Hangartner, Andreas Hurni (2021). Liste 'Thermische Netze' - Auswertungsbericht 2021. EnergieSchweiz. https://pubdb.bfe.admin.ch/de/publication/download/10878

capacity_limit
--------------

Step 1
The capacity limit for district heating grids is derived from the HRE dataset, which provides data on the potential for district heating in different regions. For countries with missing data, a linear regression model is used to predict the potential based on the share of the population in urban, suburban, and rural areas obtained from the Eurostat dataset. The final capacity limit is calculated by multiplying the district heating potential by the peak heat demand.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **ecb**: European Central Bank (2026). HICP - Overall index, Euro area, Monthly. European Central Bank. https://data.ecb.europa.eu/
- **heat_demand**:
  - **jrc_idees**: Mate Rozsai, Marc Jaxa-Rozen, Raffaele Salvucci, Przemyslaw Sikora, Juan Gea Bermudez, Frederik Neuwahl (2026). JRC-IDEES-2023: the Integrated Database of the European Energy System. JRC. https://publications.jrc.ec.europa.eu/repository/handle/JRC144707
  - **when2heat**: Oliver Ruhnau, Lion Hirth, Aaron Praktiknjo, Jarusch Muessel (2023). When2Heat. Open power system data. https://data.open-power-system-data.org/when2heat/
  - **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
  - **desnz**: Department for Energy Security and Net Zero (DESNZ) (2025). Energy Consumption in the UK (ECUK): End Use Tables. DESNZ. https://www.gov.uk/government/statistics/energy-consumption-in-the-uk-2025
  - **bfe**: Bundesamt für Energie (BFE) (2025). Energieverbrauch nach Verwendungszweck. BFE. https://www.bfe.admin.ch/bfe/de/home/versorgung/statistik-und-geodaten/energiestatistiken/energieverbrauch-nach-verwendungszweck.html
  - **energifaktanorge**: Energifaktanorge (2025). Energy use by sector. Energifaktanorge. https://energifaktanorge.no/en/norsk-energibruk/energibruken-i-ulike-sektorer/#household-and-service-industries
  - **energieschweiz**: Diego Hangartner, Andreas Hurni (2021). Liste 'Thermische Netze' - Auswertungsbericht 2021. EnergieSchweiz. https://pubdb.bfe.admin.ch/de/publication/download/10878
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **hre**: Brian Vad Mathiesen, Enric Gonzalez Gonzalo, Marina Georgati, Steffen Nielsen, Jelena Nikolic, Alisson Aparecido Vitoriano Julio, Nikolaj Lottrup Bruun-Nielsen (2025). HRE5: Heat Roadmap Europe 5. Aalborg Universitet. https://vbn.aau.dk/en/projects/hre5-heat-roadmap-europe-5/

max_load
--------

Step 1
The maximum load of a heat conversion technology is derived from the heat demand, divided by the peak heat demand.

**Citations**

- **jrc_idees**: Mate Rozsai, Marc Jaxa-Rozen, Raffaele Salvucci, Przemyslaw Sikora, Juan Gea Bermudez, Frederik Neuwahl (2026). JRC-IDEES-2023: the Integrated Database of the European Energy System. JRC. https://publications.jrc.ec.europa.eu/repository/handle/JRC144707
- **when2heat**: Oliver Ruhnau, Lion Hirth, Aaron Praktiknjo, Jarusch Muessel (2023). When2Heat. Open power system data. https://data.open-power-system-data.org/when2heat/
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **desnz**: Department for Energy Security and Net Zero (DESNZ) (2025). Energy Consumption in the UK (ECUK): End Use Tables. DESNZ. https://www.gov.uk/government/statistics/energy-consumption-in-the-uk-2025
- **bfe**: Bundesamt für Energie (BFE) (2025). Energieverbrauch nach Verwendungszweck. BFE. https://www.bfe.admin.ch/bfe/de/home/versorgung/statistik-und-geodaten/energiestatistiken/energieverbrauch-nach-verwendungszweck.html
- **energifaktanorge**: Energifaktanorge (2025). Energy use by sector. Energifaktanorge. https://energifaktanorge.no/en/norsk-energibruk/energibruken-i-ulike-sektorer/#household-and-service-industries
- **energieschweiz**: Diego Hangartner, Andreas Hurni (2021). Liste 'Thermische Netze' - Auswertungsbericht 2021. EnergieSchweiz. https://pubdb.bfe.admin.ch/de/publication/download/10878

opex_specific_variable
----------------------

Step 1
The variable operational expenditure (opex) for district heating grids is obtained from the DEA dataset, which provides cost data for district heating infrastructure.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **ecb**: European Central Bank (2026). HICP - Overall index, Euro area, Monthly. European Central Bank. https://data.ecb.europa.eu/
- **heat_demand**:
  - **jrc_idees**: Mate Rozsai, Marc Jaxa-Rozen, Raffaele Salvucci, Przemyslaw Sikora, Juan Gea Bermudez, Frederik Neuwahl (2026). JRC-IDEES-2023: the Integrated Database of the European Energy System. JRC. https://publications.jrc.ec.europa.eu/repository/handle/JRC144707
  - **when2heat**: Oliver Ruhnau, Lion Hirth, Aaron Praktiknjo, Jarusch Muessel (2023). When2Heat. Open power system data. https://data.open-power-system-data.org/when2heat/
  - **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
  - **desnz**: Department for Energy Security and Net Zero (DESNZ) (2025). Energy Consumption in the UK (ECUK): End Use Tables. DESNZ. https://www.gov.uk/government/statistics/energy-consumption-in-the-uk-2025
  - **bfe**: Bundesamt für Energie (BFE) (2025). Energieverbrauch nach Verwendungszweck. BFE. https://www.bfe.admin.ch/bfe/de/home/versorgung/statistik-und-geodaten/energiestatistiken/energieverbrauch-nach-verwendungszweck.html
  - **energifaktanorge**: Energifaktanorge (2025). Energy use by sector. Energifaktanorge. https://energifaktanorge.no/en/norsk-energibruk/energibruken-i-ulike-sektorer/#household-and-service-industries
  - **energieschweiz**: Diego Hangartner, Andreas Hurni (2021). Liste 'Thermische Netze' - Auswertungsbericht 2021. EnergieSchweiz. https://pubdb.bfe.admin.ch/de/publication/download/10878
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **hre**: Brian Vad Mathiesen, Enric Gonzalez Gonzalo, Marina Georgati, Steffen Nielsen, Jelena Nikolic, Alisson Aparecido Vitoriano Julio, Nikolaj Lottrup Bruun-Nielsen (2025). HRE5: Heat Roadmap Europe 5. Aalborg Universitet. https://vbn.aau.dk/en/projects/hre5-heat-roadmap-europe-5/

opex_specific_fixed
-------------------

Step 1
The fixed operational expenditure (opex) for district heating grids is obtained from the DEA dataset, which provides cost data for district heating infrastructure.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **ecb**: European Central Bank (2026). HICP - Overall index, Euro area, Monthly. European Central Bank. https://data.ecb.europa.eu/
- **heat_demand**:
  - **jrc_idees**: Mate Rozsai, Marc Jaxa-Rozen, Raffaele Salvucci, Przemyslaw Sikora, Juan Gea Bermudez, Frederik Neuwahl (2026). JRC-IDEES-2023: the Integrated Database of the European Energy System. JRC. https://publications.jrc.ec.europa.eu/repository/handle/JRC144707
  - **when2heat**: Oliver Ruhnau, Lion Hirth, Aaron Praktiknjo, Jarusch Muessel (2023). When2Heat. Open power system data. https://data.open-power-system-data.org/when2heat/
  - **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
  - **desnz**: Department for Energy Security and Net Zero (DESNZ) (2025). Energy Consumption in the UK (ECUK): End Use Tables. DESNZ. https://www.gov.uk/government/statistics/energy-consumption-in-the-uk-2025
  - **bfe**: Bundesamt für Energie (BFE) (2025). Energieverbrauch nach Verwendungszweck. BFE. https://www.bfe.admin.ch/bfe/de/home/versorgung/statistik-und-geodaten/energiestatistiken/energieverbrauch-nach-verwendungszweck.html
  - **energifaktanorge**: Energifaktanorge (2025). Energy use by sector. Energifaktanorge. https://energifaktanorge.no/en/norsk-energibruk/energibruken-i-ulike-sektorer/#household-and-service-industries
  - **energieschweiz**: Diego Hangartner, Andreas Hurni (2021). Liste 'Thermische Netze' - Auswertungsbericht 2021. EnergieSchweiz. https://pubdb.bfe.admin.ch/de/publication/download/10878
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **hre**: Brian Vad Mathiesen, Enric Gonzalez Gonzalo, Marina Georgati, Steffen Nielsen, Jelena Nikolic, Alisson Aparecido Vitoriano Julio, Nikolaj Lottrup Bruun-Nielsen (2025). HRE5: Heat Roadmap Europe 5. Aalborg Universitet. https://vbn.aau.dk/en/projects/hre5-heat-roadmap-europe-5/

capex_specific_conversion
-------------------------

Step 1
The specific capital expenditure (capex) for district heating grids is derived from the DEA dataset, which provides cost data for district heating infrastructure in Eur/m**2. The capex values are adjusted for inflation using the ECB Inflation dataset. The final capex values are expressed in Euro per kW, taking into account the average full load hours (flh) calculated from the heat demand data.

**Citations**

- **dea**: Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
- **ecb**: European Central Bank (2026). HICP - Overall index, Euro area, Monthly. European Central Bank. https://data.ecb.europa.eu/
- **heat_demand**:
  - **jrc_idees**: Mate Rozsai, Marc Jaxa-Rozen, Raffaele Salvucci, Przemyslaw Sikora, Juan Gea Bermudez, Frederik Neuwahl (2026). JRC-IDEES-2023: the Integrated Database of the European Energy System. JRC. https://publications.jrc.ec.europa.eu/repository/handle/JRC144707
  - **when2heat**: Oliver Ruhnau, Lion Hirth, Aaron Praktiknjo, Jarusch Muessel (2023). When2Heat. Open power system data. https://data.open-power-system-data.org/when2heat/
  - **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
  - **desnz**: Department for Energy Security and Net Zero (DESNZ) (2025). Energy Consumption in the UK (ECUK): End Use Tables. DESNZ. https://www.gov.uk/government/statistics/energy-consumption-in-the-uk-2025
  - **bfe**: Bundesamt für Energie (BFE) (2025). Energieverbrauch nach Verwendungszweck. BFE. https://www.bfe.admin.ch/bfe/de/home/versorgung/statistik-und-geodaten/energiestatistiken/energieverbrauch-nach-verwendungszweck.html
  - **energifaktanorge**: Energifaktanorge (2025). Energy use by sector. Energifaktanorge. https://energifaktanorge.no/en/norsk-energibruk/energibruken-i-ulike-sektorer/#household-and-service-industries
  - **energieschweiz**: Diego Hangartner, Andreas Hurni (2021). Liste 'Thermische Netze' - Auswertungsbericht 2021. EnergieSchweiz. https://pubdb.bfe.admin.ch/de/publication/download/10878
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **hre**: Brian Vad Mathiesen, Enric Gonzalez Gonzalo, Marina Georgati, Steffen Nielsen, Jelena Nikolic, Alisson Aparecido Vitoriano Julio, Nikolaj Lottrup Bruun-Nielsen (2025). HRE5: Heat Roadmap Europe 5. Aalborg Universitet. https://vbn.aau.dk/en/projects/hre5-heat-roadmap-europe-5/

conversion_factor
-----------------

Step 1
The conversion factor of district heating grids is based on data from the DEA dataset, which provides information on the distribution of energy losses for district heating grids. The specific value used here is the reference value for suburban district heating grids.

**Citation**

Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
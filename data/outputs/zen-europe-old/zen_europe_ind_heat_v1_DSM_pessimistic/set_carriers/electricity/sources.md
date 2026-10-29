electricity
===========

demand
------

Step 1
The electricity demand data is derived from multiple sources:First, the ENTSOE dataset provides the base electricity demand data. Second, the electricity demand must be corrected for theelectricity demand of heat pumps and electrode boilers. The heat demand data is derived from the HeatDemand dataset, which combines data from the JRC IDEES, Eurostat, DESNZ, BFE, and Energifaktanorge datasets. The heating share data by technology is derived from the HeatDemand dataset, especially from Eurostat. Finally, the COP data for heat pumps is derived from the When2Heat dataset.Note that we neglect the embedded electricity demand for district heating, which is assumed to be small.

**Citations**

- **entsoe**: ENTSO-E (2026). ENTSO-E Transparency Platform. ENTSO-E Transparency Platform. https://transparency.entsoe.eu/. Note: Queried via the entsoe-py package against the ENTSO-E Transparency Platform RESTful API; requires an API security token in the ENTSOE_API_KEY environment variable.
- **heat_demand**:
  - **jrc_idees**: Mate Rozsai, Marc Jaxa-Rozen, Raffaele Salvucci, Przemyslaw Sikora, Juan Gea Bermudez, Frederik Neuwahl (2026). JRC-IDEES-2023: the Integrated Database of the European Energy System. JRC. https://publications.jrc.ec.europa.eu/repository/handle/JRC144707
  - **when2heat**: Oliver Ruhnau, Lion Hirth, Aaron Praktiknjo, Jarusch Muessel (2023). When2Heat. Open power system data. https://data.open-power-system-data.org/when2heat/
  - **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
  - **desnz**: Department for Energy Security and Net Zero (DESNZ) (2025). Energy Consumption in the UK (ECUK): End Use Tables. DESNZ. https://www.gov.uk/government/statistics/energy-consumption-in-the-uk-2025
  - **bfe**: Bundesamt für Energie (BFE) (2025). Energieverbrauch nach Verwendungszweck. BFE. https://www.bfe.admin.ch/bfe/de/home/versorgung/statistik-und-geodaten/energiestatistiken/energieverbrauch-nach-verwendungszweck.html
  - **energifaktanorge**: Energifaktanorge (2025). Energy use by sector. Energifaktanorge. https://energifaktanorge.no/en/norsk-energibruk/energibruken-i-ulike-sektorer/#household-and-service-industries
  - **energieschweiz**: Diego Hangartner, Andreas Hurni (2021). Liste 'Thermische Netze' - Auswertungsbericht 2021. EnergieSchweiz. https://pubdb.bfe.admin.ch/de/publication/download/10878
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **when2heat**: Oliver Ruhnau, Lion Hirth, Aaron Praktiknjo, Jarusch Muessel (2023). When2Heat. Open power system data. https://data.open-power-system-data.org/when2heat/
- **bfe**: Bundesamt für Energie (BFE) (2025). Energieverbrauch nach Verwendungszweck. BFE. https://www.bfe.admin.ch/bfe/de/home/versorgung/statistik-und-geodaten/energiestatistiken/energieverbrauch-nach-verwendungszweck.html
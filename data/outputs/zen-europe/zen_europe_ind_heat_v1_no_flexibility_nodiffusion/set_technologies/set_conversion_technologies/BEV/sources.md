BEV
===

lifetime
--------

Step 1
The lifetime of BEV is obtained by dividing the lifetime mileage of the lower medium car of Cox et al. (2020) by its annual mileage, rounded to full years.

**Citation**

Brian Cox, Christian Bauer, Angelica Mendoza Beltran, Detlef P. van Vuuren, Christopher L. Mutel (2020). Life cycle environmental and cost comparison of current and future passenger cars under different energy scenarios. Applied Energy. https://doi.org/10.1016/j.apenergy.2020.115021

capacity_existing
-----------------

Step 1
The existing capacity of BEV is calculated from the existing fleet of BEV vehicles and the total passenger mileage demand. The existing fleet is sourced from the UNECE dataset, and the total passenger mileage demand is sourced from the PassengerMileageDemand dataset. The capacity is corrected for the peak demand share.

**Citations**

- **unece**: United Nations Economic Commission for Europe (2026). Road vehicle fleet at 31 December and new road vehicle registrations, by vehicle category and fuel type. UNECE Transport Statistics Database. https://w3.unece.org/PXWeb2015/pxweb/en/STAT/STAT__40-TRTRANS__03-TRRoadFleet
- **pass_demand**:
  - **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
  - **statistical_pocketbook_transport**: Directorate-General for Mobility and Transport (European Commission) (2022). EU transport in figures: Statistical pocketbook 2022. Publication Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/f656ef8e-3e0e-11ed-92ed-01aa75ed71a1/language-en
  - **standard_load_profiles**: Daniel Heinz (2018). Erstellung und Auswertung repräsentativer Mobilitäts- und Ladeprofile für Elektrofahrzeuge in Deutschland. Institut für Industriebetriebslehre und Industrielle Produktion. https://publikationen.bibliothek.kit.edu/1000086372
- **truck_mileage**:
  - **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
  - **statistical_pocketbook_transport**: Directorate-General for Mobility and Transport (European Commission) (2022). EU transport in figures: Statistical pocketbook 2022. Publication Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/f656ef8e-3e0e-11ed-92ed-01aa75ed71a1/language-en
  - **truck_standard_load_profiles**: Brennan Borlaug, Matteo Muratori, Madeline Gilleran, David Woody, William Muston, Thomas Canada, Andrew Ingram, Hal Gresham, Charlie McQueen (2021). Heavy-duty truck electrification and the impacts of depot charging on electricity distribution systems. Nature Energy. https://doi.org/10.1038/s41560-021-00855-0. Note: Supplementary Figure 8, 100 EVs, Constant min. power
  - **truck_technologies**: Hussein Basma, Felipe Rodriguez (2023). THE EUROPEAN HEAVY-DUTY VEHICLE MARKET UNTIL 2040: ANALYSIS OF DECARBONIZATION PATHWAYS. International Council on Clean Transportation (ICCT). https://theicct.org/wp-content/uploads/2023/01/hdv-europe-decarb-costs-jan23.pdf
- **truck_technologies**: Hussein Basma, Felipe Rodriguez (2023). THE EUROPEAN HEAVY-DUTY VEHICLE MARKET UNTIL 2040: ANALYSIS OF DECARBONIZATION PATHWAYS. International Council on Clean Transportation (ICCT). https://theicct.org/wp-content/uploads/2023/01/hdv-europe-decarb-costs-jan23.pdf
- **passenger_cars**: Brian Cox, Christian Bauer, Angelica Mendoza Beltran, Detlef P. van Vuuren, Christopher L. Mutel (2020). Life cycle environmental and cost comparison of current and future passenger cars under different energy scenarios. Applied Energy. https://doi.org/10.1016/j.apenergy.2020.115021
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en

max_load
--------

Step 1
The maximum load of the passenger mileage demand is calculated by dividing the hourly passenger mileage demand by the maximum hourly demand. The hourly passenger mileage demand is derived from the Statistical Pocketbook Transport dataset and the standard load profiles for urban, suburban and rural areas.

**Citations**

- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **statistical_pocketbook_transport**: Directorate-General for Mobility and Transport (European Commission) (2022). EU transport in figures: Statistical pocketbook 2022. Publication Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/f656ef8e-3e0e-11ed-92ed-01aa75ed71a1/language-en
- **standard_load_profiles**: Daniel Heinz (2018). Erstellung und Auswertung repräsentativer Mobilitäts- und Ladeprofile für Elektrofahrzeuge in Deutschland. Institut für Industriebetriebslehre und Industrielle Produktion. https://publikationen.bibliothek.kit.edu/1000086372

opex_specific_variable
----------------------

Step 1
The specific variable OPEX of BEV is the maintenance cost of the lower medium car of Cox et al. (2020), taken at the manufacturing cost rather than at the consumer price, i.e. divided by the markup factor. Monetary values are rebased from 2020 to 2022 Euro using ECB HICP inflation.

**Citation**

Brian Cox, Christian Bauer, Angelica Mendoza Beltran, Detlef P. van Vuuren, Christopher L. Mutel (2020). Life cycle environmental and cost comparison of current and future passenger cars under different energy scenarios. Applied Energy. https://doi.org/10.1016/j.apenergy.2020.115021

capex_specific_conversion
-------------------------

Step 1
The specific conversion CAPEX of BEV is the purchase price of the lower medium car of Cox et al. (2020), taken at the manufacturing cost rather than at the consumer price, i.e. divided by the markup factor. It is divided by the hourly mileage of the car and adjusted for the peak demand share. Monetary values are rebased from 2020 to 2022 Euro using ECB HICP inflation. The battery share of the price follows the battery cost of Cox et al. from the reference year to their 2040 value and stays constant afterwards.

**Citations**

- **unece**: United Nations Economic Commission for Europe (2026). Road vehicle fleet at 31 December and new road vehicle registrations, by vehicle category and fuel type. UNECE Transport Statistics Database. https://w3.unece.org/PXWeb2015/pxweb/en/STAT/STAT__40-TRTRANS__03-TRRoadFleet
- **pass_demand**:
  - **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
  - **statistical_pocketbook_transport**: Directorate-General for Mobility and Transport (European Commission) (2022). EU transport in figures: Statistical pocketbook 2022. Publication Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/f656ef8e-3e0e-11ed-92ed-01aa75ed71a1/language-en
  - **standard_load_profiles**: Daniel Heinz (2018). Erstellung und Auswertung repräsentativer Mobilitäts- und Ladeprofile für Elektrofahrzeuge in Deutschland. Institut für Industriebetriebslehre und Industrielle Produktion. https://publikationen.bibliothek.kit.edu/1000086372
- **truck_mileage**:
  - **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
  - **statistical_pocketbook_transport**: Directorate-General for Mobility and Transport (European Commission) (2022). EU transport in figures: Statistical pocketbook 2022. Publication Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/f656ef8e-3e0e-11ed-92ed-01aa75ed71a1/language-en
  - **truck_standard_load_profiles**: Brennan Borlaug, Matteo Muratori, Madeline Gilleran, David Woody, William Muston, Thomas Canada, Andrew Ingram, Hal Gresham, Charlie McQueen (2021). Heavy-duty truck electrification and the impacts of depot charging on electricity distribution systems. Nature Energy. https://doi.org/10.1038/s41560-021-00855-0. Note: Supplementary Figure 8, 100 EVs, Constant min. power
  - **truck_technologies**: Hussein Basma, Felipe Rodriguez (2023). THE EUROPEAN HEAVY-DUTY VEHICLE MARKET UNTIL 2040: ANALYSIS OF DECARBONIZATION PATHWAYS. International Council on Clean Transportation (ICCT). https://theicct.org/wp-content/uploads/2023/01/hdv-europe-decarb-costs-jan23.pdf
- **truck_technologies**: Hussein Basma, Felipe Rodriguez (2023). THE EUROPEAN HEAVY-DUTY VEHICLE MARKET UNTIL 2040: ANALYSIS OF DECARBONIZATION PATHWAYS. International Council on Clean Transportation (ICCT). https://theicct.org/wp-content/uploads/2023/01/hdv-europe-decarb-costs-jan23.pdf
- **passenger_cars**: Brian Cox, Christian Bauer, Angelica Mendoza Beltran, Detlef P. van Vuuren, Christopher L. Mutel (2020). Life cycle environmental and cost comparison of current and future passenger cars under different energy scenarios. Applied Energy. https://doi.org/10.1016/j.apenergy.2020.115021
- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en

conversion_factor
-----------------

Step 1
The conversion factor of BEV is the tank-to-wheel energy demand of the lower medium car of Cox et al. (2020) over the WLTC driving cycle. For a battery electric car it is the electricity drawn from the grid, so it includes the charging and drivetrain losses.

**Citation**

Brian Cox, Christian Bauer, Angelica Mendoza Beltran, Detlef P. van Vuuren, Christopher L. Mutel (2020). Life cycle environmental and cost comparison of current and future passenger cars under different energy scenarios. Applied Energy. https://doi.org/10.1016/j.apenergy.2020.115021
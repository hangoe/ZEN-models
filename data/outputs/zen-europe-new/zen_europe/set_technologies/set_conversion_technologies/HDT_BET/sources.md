HDT_BET
=======

lifetime
--------

Step 1
The lifetime of HDT_BET is sourced from the ICCT (2023) dataset for the 5-LH truck model. It is obtained by dividing the total mileage of the truck by the average annual mileage (Tab 6).

**Citation**

Hussein Basma, Felipe Rodriguez (2023). THE EUROPEAN HEAVY-DUTY VEHICLE MARKET UNTIL 2040: ANALYSIS OF DECARBONIZATION PATHWAYS. International Council on Clean Transportation (ICCT). https://theicct.org/wp-content/uploads/2023/01/hdv-europe-decarb-costs-jan23.pdf

capacity_existing
-----------------

Step 1
The existing capacity of HDT BET is calculated from the existing fleet of HDT BET vehicles and the total truck mileage demand. The existing fleet is sourced from the UNECE dataset, and the total truck mileage demand is sourced from the TruckMileageDemand dataset. The capacity is corrected for the peak demand share.

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
The maximum load of the truck mileage demand is calculated by dividing the hourly truck mileage demand by the maximum hourly demand. The hourly truck mileage demand is derived from the Statistical Pocketbook Transport dataset and the standard load profiles for trucks.

**Citations**

- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **statistical_pocketbook_transport**: Directorate-General for Mobility and Transport (European Commission) (2022). EU transport in figures: Statistical pocketbook 2022. Publication Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/f656ef8e-3e0e-11ed-92ed-01aa75ed71a1/language-en
- **truck_standard_load_profiles**: Brennan Borlaug, Matteo Muratori, Madeline Gilleran, David Woody, William Muston, Thomas Canada, Andrew Ingram, Hal Gresham, Charlie McQueen (2021). Heavy-duty truck electrification and the impacts of depot charging on electricity distribution systems. Nature Energy. https://doi.org/10.1038/s41560-021-00855-0. Note: Supplementary Figure 8, 100 EVs, Constant min. power
- **truck_technologies**: Hussein Basma, Felipe Rodriguez (2023). THE EUROPEAN HEAVY-DUTY VEHICLE MARKET UNTIL 2040: ANALYSIS OF DECARBONIZATION PATHWAYS. International Council on Clean Transportation (ICCT). https://theicct.org/wp-content/uploads/2023/01/hdv-europe-decarb-costs-jan23.pdf

opex_specific_variable
----------------------

Step 1
The specific variable OPEX of HDT_BET is sourced from the ICCT (2023) dataset for the 5-LH truck model (Tab A20). 

**Citation**

Hussein Basma, Felipe Rodriguez (2023). THE EUROPEAN HEAVY-DUTY VEHICLE MARKET UNTIL 2040: ANALYSIS OF DECARBONIZATION PATHWAYS. International Council on Clean Transportation (ICCT). https://theicct.org/wp-content/uploads/2023/01/hdv-europe-decarb-costs-jan23.pdf

max_diffusion_rate
------------------

Step 1
The maximum diffusion rate of HDT_BET is set to the historically observed diffusion rate of photovoltaics from Mannhardt et al. (2024).

**Citation**

Jacob Mannhardt, Paolo Gabrielli, Giovanni Sansavini (2024). Understanding the vicious cycle of myopic foresight and constrained technology deployment in transforming the European energy system. iScience. https://doi.org/https://doi.org/10.1016/j.isci.2024.111369

capex_specific_conversion
-------------------------

Step 1
The specific conversion CAPEX of HDT_BET is sourced from the ICCT (2023) dataset for the 5-LH truck model (Fig. 8). It is obtained by dividing the total CAPEX of the truck by the total mileage demand, adjusted for the peak demand share.

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
The conversion factor of HDT_BET is sourced from the ICCT (2023) dataset for the 5-LH truck model. It is obtained from Tab A9 of the dataset.

**Citation**

Hussein Basma, Felipe Rodriguez (2023). THE EUROPEAN HEAVY-DUTY VEHICLE MARKET UNTIL 2040: ANALYSIS OF DECARBONIZATION PATHWAYS. International Council on Clean Transportation (ICCT). https://theicct.org/wp-content/uploads/2023/01/hdv-europe-decarb-costs-jan23.pdf
passenger_mileage
=================

demand
------

Step 1
Total passenger mileage demand is derived from the Statistical Pocketbook Transport dataset, which provides data on passenger and truck mileage in the EU. The total passenger mileage is adjusted for vehicle occupancy using data from Eurostat. The standard load profiles for urban, suburban, and rural areas are obtained from the Standard Load Profiles dataset, which provides hourly load profiles for different types of days and region types. The final passenger mileage demand is calculated by multiplying the total passenger mileage by the weighted standard load profiles based on the share of the population in each region type.

**Citations**

- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **statistical_pocketbook_transport**: Directorate-General for Mobility and Transport (European Commission) (2022). EU transport in figures: Statistical pocketbook 2022. Publication Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/f656ef8e-3e0e-11ed-92ed-01aa75ed71a1/language-en
- **standard_load_profiles**: Daniel Heinz (2018). Erstellung und Auswertung repräsentativer Mobilitäts- und Ladeprofile für Elektrofahrzeuge in Deutschland. Institut für Industriebetriebslehre und Industrielle Produktion. https://publikationen.bibliothek.kit.edu/1000086372
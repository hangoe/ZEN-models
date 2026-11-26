shipping
========

demand
------

Step 1
Shipping fuel demand data is derived from the Eurostat dataset. For CH it is assumed that there is no shipping demand, as Switzerland is a landlocked country. The demand is converted to shipping fuel demand using conversion factors from the Korberg et al. (2021) paper, which provides conversion factors for various shipping technologies.

**Citations**

- **eurostat**: Eurostat (2026). Eurostat energy balances. Eurostat. https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table?lang=en
- **swiss_energy_balance**: Swiss Federal Statistical Office (2026). Swiss Energy Balance. Swiss Federal Statistical Office. https://opendata.swiss/en/dataset/energiebilanz-der-schweiz
- **swiss_oil_balance**: Swiss Federal Statistical Office (2026). Swiss Crude Oil Balance. Swiss Federal Statistical Office. https://opendata.swiss/de/dataset/schweizerische-gesamtenergiestatistik-erdolbilanz-der-schweiz
- **shipping_technologies_korberg**: A.D. Korberg, S. Brynolf, M. Grahn, I.R. Skov (2021). Techno-economic assessment of advanced fuels and propulsion systems in future fossil-free ships. Renewable and Sustainable Energy Reviews. https://doi.org/https://doi.org/10.1016/j.rser.2021.110861
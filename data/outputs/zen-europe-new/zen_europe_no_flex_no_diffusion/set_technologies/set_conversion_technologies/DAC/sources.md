DAC
===

lifetime
--------

Step 1
Technical lifetime for 'DAC' is the median across all available data for the agencies dea, luw reporting data for this technology at plant size 'None'. Monetary values are rebased to 2025 Euro using ECB HICP inflation.

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
The unbounded capacity addition of carbon storage is based on the median planned capacity from the Zurbriggen et al. paper, divided by the number of nodes in the dataset.

**Citation**

Tatjana Zurbriggen, Nicoletta Brazzola, Adrian Odenweller, Falko Ueckerdt, Joeri Rogelj (2026). Short-term action is key for gigaton-scale Direct Air Capture by 2050. Nature Communications. https://doi.org/https://doi.org/10.1038/s41467-026-72691-3

capacity_existing
-----------------

Step 1
The existing DAC capacity is based on the Zurbriggen et al. paper 'Short-term action is key for gigaton-scale Direct Air Capture by 2050'.

**Citation**

Tatjana Zurbriggen, Nicoletta Brazzola, Adrian Odenweller, Falko Ueckerdt, Joeri Rogelj (2026). Short-term action is key for gigaton-scale Direct Air Capture by 2050. Nature Communications. https://doi.org/https://doi.org/10.1038/s41467-026-72691-3

opex_specific_variable
----------------------

Step 1
Variable operational cost without electricity, heat, co2 transport and co2 storage of 'DAC' is the median of the experience curve of the solid_sorbent DAC technology of Sievert et al. (2024), evaluated at the cumulative global DAC capacity of the deployment pathway of the IEA Net Zero Roadmap (2023), Net Zero Emissions scenario, starting from the operational projects in the DAC project database of Zurbriggen et al. (2026). Converted from US$2022 with the ECB exchange rate and rebased to 2022 Euro with ECB HICP inflation.

**Citations**

- **sievert**: Katrin Sievert, Tobias S. Schmidt, Bjarne Steffen (2024). Considering technology characteristics to project future costs of direct air capture. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2024.02.005. Note: Reconstructed from the supplemental tables S6, S7, S9-S16 and S19-S21. Cost curves are the median of a Monte Carlo simulation against the cumulative global DAC capacity. Electricity, heat, CO2 transport and CO2 storage are excluded from the variable opex.
- **iea**: International Energy Agency (2023). Net Zero Roadmap:Carbon capture, utilisation and storage. International Energy Agency. https://www.iea.org/reports/CCUS
- **zurbriggen**: Tatjana Zurbriggen, Nicoletta Brazzola, Adrian Odenweller, Falko Ueckerdt, Joeri Rogelj (2026). Short-term action is key for gigaton-scale Direct Air Capture by 2050. Nature Communications. https://doi.org/https://doi.org/10.1038/s41467-026-72691-3

opex_specific_fixed
-------------------

Step 1
Fixed operational cost of 'DAC' is the median of the experience curve of the solid_sorbent DAC technology of Sievert et al. (2024), evaluated at the cumulative global DAC capacity of the deployment pathway of the IEA Net Zero Roadmap (2023), Net Zero Emissions scenario, starting from the operational projects in the DAC project database of Zurbriggen et al. (2026). Converted from US$2022 with the ECB exchange rate and rebased to 2022 Euro with ECB HICP inflation.

**Citations**

- **sievert**: Katrin Sievert, Tobias S. Schmidt, Bjarne Steffen (2024). Considering technology characteristics to project future costs of direct air capture. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2024.02.005. Note: Reconstructed from the supplemental tables S6, S7, S9-S16 and S19-S21. Cost curves are the median of a Monte Carlo simulation against the cumulative global DAC capacity. Electricity, heat, CO2 transport and CO2 storage are excluded from the variable opex.
- **iea**: International Energy Agency (2023). Net Zero Roadmap:Carbon capture, utilisation and storage. International Energy Agency. https://www.iea.org/reports/CCUS
- **zurbriggen**: Tatjana Zurbriggen, Nicoletta Brazzola, Adrian Odenweller, Falko Ueckerdt, Joeri Rogelj (2026). Short-term action is key for gigaton-scale Direct Air Capture by 2050. Nature Communications. https://doi.org/https://doi.org/10.1038/s41467-026-72691-3

capex_specific_conversion
-------------------------

Step 1
Specific investment cost (total overnight cost) of 'DAC' is the median of the experience curve of the solid_sorbent DAC technology of Sievert et al. (2024), evaluated at the cumulative global DAC capacity of the deployment pathway of the IEA Net Zero Roadmap (2023), Net Zero Emissions scenario, starting from the operational projects in the DAC project database of Zurbriggen et al. (2026). Converted from US$2022 with the ECB exchange rate and rebased to 2022 Euro with ECB HICP inflation.

**Citations**

- **sievert**: Katrin Sievert, Tobias S. Schmidt, Bjarne Steffen (2024). Considering technology characteristics to project future costs of direct air capture. Joule. https://doi.org/https://doi.org/10.1016/j.joule.2024.02.005. Note: Reconstructed from the supplemental tables S6, S7, S9-S16 and S19-S21. Cost curves are the median of a Monte Carlo simulation against the cumulative global DAC capacity. Electricity, heat, CO2 transport and CO2 storage are excluded from the variable opex.
- **iea**: International Energy Agency (2023). Net Zero Roadmap:Carbon capture, utilisation and storage. International Energy Agency. https://www.iea.org/reports/CCUS
- **zurbriggen**: Tatjana Zurbriggen, Nicoletta Brazzola, Adrian Odenweller, Falko Ueckerdt, Joeri Rogelj (2026). Short-term action is key for gigaton-scale Direct Air Capture by 2050. Nature Communications. https://doi.org/https://doi.org/10.1038/s41467-026-72691-3

conversion_factor
-----------------

Step 1
The conversion factor of DAC is a manually derived value based on the DEA technology catalogue for carbon capture, transport and storage (Solid Adsorption Direct Air Capture Plant).

**Citation**

Danish Energy Agency (2026). Technology catalogues. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-catalogues. Note: Includes data for electricity, district heating, individual heating,renewable fuels, carbon capture, and more technologies.
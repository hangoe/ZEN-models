energy_system_nuts0
===================

price_carbon_emissions_annual_overshoot
---------------------------------------

Step 1
The penalty price for overshooting the annual carbon emissions limit is manually set to 5000 Euro per ton, far above any abatement cost, so that the limit is only overshot if the model would be infeasible otherwise.

carbon_emissions_budget
-----------------------

Step 1
The remaining carbon budget is calculated based on the remaining global carbon budget from the IPCC AR6 report, the population share of Europe, and the sectoral emissions from the EEA GHG inventory and the DESNZ GHG inventory (UK).

**Citations**

- **worldbank_population**: World Bank (2026). Population estimates and projections. World Bank DataBank. https://databank.worldbank.org/source/population-estimates-and-projections#. Note: Indicator SP.POP.TOTL, total population in persons.
- **eea_ghg_inventory**: European Environment Agency (2026). GovReg: National emissions reported to the UNFCCC and to the EU under the Governance Regulation. EEA Datahub. https://www.eea.europa.eu/en/datahub/datahubitem-view/3b7fe76c-524a-439a-bfd2-a6e4046302a2. Note: UNFCCC_v32.csv, pollutant CO2 in Gg.
- **ipcc_ar6**: IPCC (2021). Climate Change 2021 The Physical Science Basis. Sixth Assessment Report of the Intergovernmental Panel on Climate Change. https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_SPM_final.pdf#page=33
- **desnz_ghg_inventory**: Department for Energy Security and Net Zero (2026). Final UK greenhouse gas emissions national statistics: 1990 to 2024. GOV.UK. https://www.gov.uk/government/statistics/final-uk-greenhouse-gas-emissions-statistics-1990-to-2024. Note: Data tables, sheet 1.3 for the territorial emissions and sheet 5.1 for the international bunkers, gas Carbon dioxide (CO2).
- **global_carbon_budget**: Friedlingstein, P. et al. (2025). Global Carbon Budget 2025. Global Carbon Project. https://globalcarbonbudget.org/datahub/. Note: Sheet 'Global Carbon Budget', columns 'fossil emissions excluding carbonation' and 'land-use change emissions' in GtC/yr, converted to GtCO2/yr.
- **ons_industry_emissions**: Office for National Statistics (2026). Atmospheric emissions: greenhouse gases by industry and gas, United Kingdom. ONS. https://www.ons.gov.uk/economy/environmentalaccounts/datasets/ukenvironmentalaccountsatmosphericemissionsgreenhousegasemissionsbyeconomicsectorandgasunitedkingdom. Note: Sheet CO2, SIC 17 and SIC 10-12 (summed), UK residence basis.

carbon_emissions_annual_limit
-----------------------------

Step 1
The annual carbon emissions limit is infinite, because the annual limit is not used in the model.

price_carbon_emissions_budget_overshoot
---------------------------------------

Step 1
The penalty price for overshooting the carbon budget is manually set to 5000 Euro per ton, far above any abatement cost, so that the budget is only overshot if the model would be infeasible otherwise.

discount_rate
-------------

Step 1
https://iopscience.iop.org/article/10.1088/1748-9326/ac228a

**Citation**

Löffler, Konstantin (2021). Social discounting, social costs of carbon, and their use in energy system models. Environmental Research Letters. https://doi.org/10.1088/1748-9326/ac228a

----

Step 2
The discount rate is set to 0.05.

knowledge_spillover_rate
------------------------

Step 1
The knowledge spillover rate between the nodes is infinite, so that knowledge is shared without any loss between the nodes.

knowledge_depreciation_rate
---------------------------

Step 1
Taken from [leibowicz_2016].

**Citation**

Leibowicz, B. D., Krey, V., Grubler, A. (2016). Representing spatial technology diffusion in an energy system optimization model. Technological Forecasting and Social Change. https://doi.org/10.1016/j.techfore.2015.06.001

----

Step 2
The knowledge depreciation rate is 0.1, one of the rates Mannhardt et al. (2024) assume when they regress the diffusion rates.

**Citation**

Jacob Mannhardt, Paolo Gabrielli, Giovanni Sansavini (2024). Understanding the vicious cycle of myopic foresight and constrained technology deployment in transforming the European energy system. iScience. https://doi.org/https://doi.org/10.1016/j.isci.2024.111369

market_share_unbounded
----------------------

Step 1
Taken from [Mannhardt_2024]

**Citation**

Mannhardt, J., Gabrielli, P., Sansavini, G. (2024). Understanding the vicious cycle of myopic foresight and constrained technology deployment in transforming the European energy system. iScience. https://doi.org/10.1016/j.isci.2024.111369

----

Step 2
The market share that is exempt from the diffusion limit is taken from Mannhardt et al. (2024).

**Citation**

Jacob Mannhardt, Paolo Gabrielli, Giovanni Sansavini (2024). Understanding the vicious cycle of myopic foresight and constrained technology deployment in transforming the European energy system. iScience. https://doi.org/https://doi.org/10.1016/j.isci.2024.111369

set_nodes
---------

Step 1
For each node specified in the config, the centroid of the node is added as the location of the node. The centroids are computed in the WGS84 projection and the final coordinates are provided in longitude and latitude.

**Citation**

Eurostat (2026). Territorial units for statistics (NUTS). Eurostat. https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics

set_edges
---------

Step 1
Creates a set of edges based on adjacency between NUTS0 regions. Any two regions that are touching each other are considered adjacent and therefore an edge is created between them.

**Citation**

Eurostat (2026). Territorial units for statistics (NUTS). Eurostat. https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics

----

Step 2
Edges area added between all All NUTS0 regions that are have transmission lines connecting them in the ENTSO-E TYNDP 2020 data

**Citation**

Jane Doe (2026). TYNDP 2020 transmission edges. ENTSO-E. https://example.com/dataset.csv

----

Step 3
Edges are constructed in two steps: first, NUTS0 countries that share a border are assumed to be connected by an edge [NUTSshp]; second, transmission edges from TYNDP are added to this adjacency-based network.[tyndp_2020_edges]

**Citations**

- **nuts_shp**: Eurostat (2026). Territorial units for statistics (NUTS). Eurostat. https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics
- **tyndp_2020_edges**: Jane Doe (2026). TYNDP 2020 transmission edges. ENTSO-E. https://example.com/dataset.csv

----

Step 4
The connections NO-BE and NO-FR for gas, and SE-LT for electricity, are added manually.
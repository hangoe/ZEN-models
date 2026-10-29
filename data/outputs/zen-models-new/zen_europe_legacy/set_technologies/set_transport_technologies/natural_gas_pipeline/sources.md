natural_gas_pipeline
====================

lifetime
--------

Step 1
The lifetime of natural gas pipelines is manually set to 60 years, in line with the lifetime of the other linear transport infrastructure.

capacity_existing
-----------------

Step 1
The existing capacity of natural_gas_pipeline is the technical physical capacity of the interconnection points of the ENTSOG system capacity map, summed over the points of each edge. All pipelines are assumed to exist since 2010, as the map reports no commissioning year.

**Citation**

ENTSOG (2026). System Capacity Map 2026. ENTSOG. https://www.entsog.eu/maps

max_diffusion_rate
------------------

Step 1
The maximum diffusion rate of natural_gas_pipeline is set to the historically observed diffusion rate of wind onshore from Mannhardt et al. (2024).

**Citation**

Jacob Mannhardt, Paolo Gabrielli, Giovanni Sansavini (2024). Understanding the vicious cycle of myopic foresight and constrained technology deployment in transforming the European energy system. iScience. https://doi.org/https://doi.org/10.1016/j.isci.2024.111369

transport_loss_factor_linear
----------------------------

Step 1
The transport losses of natural gas pipelines are manually set to 5e-5 per km, in line with the losses of the other linear transport infrastructure.

capex_per_distance_transport
----------------------------

Step 1
The distance-specific investment cost of natural_gas_pipeline is based on Technology Data for Energy Transport. On the 36 edges that do not connect two adjacent countries, the offshore cost of 1179 Euro/(MW)/km applies. The offshore cost increase of ammonia_pipelines_galimova is used as a proxy, as the onshore cost source reports no offshore cost.

**Citations**

- **dea_energy_transport**: Danish Energy Agency (2026). Technology Data for Energy Transport. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-data-transport-energy
- **ammonia_pipelines_galimova**: Tansu Galimova, Mahdi Fasihi, Dmitrii Bogdanov, Christian Breyer (2023). Feasibility of green ammonia trading via pipelines and shipping: Cases of Europe, North Africa, and South America. Journal of Cleaner Production. https://doi.org/https://doi.org/10.1016/j.jclepro.2023.139212
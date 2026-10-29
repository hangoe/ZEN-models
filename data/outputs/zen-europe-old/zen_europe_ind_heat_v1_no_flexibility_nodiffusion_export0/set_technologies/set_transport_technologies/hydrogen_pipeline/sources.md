hydrogen_pipeline
=================

lifetime
--------

Step 1
The lifetime of hydrogen_pipeline is based on Pipeline transp. 90 bar (12 inch line) of the energy transport catalogue of the Danish Energy Agency.

**Citation**

Danish Energy Agency (2026). Technology Data for Energy Transport. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-data-transport-energy

capacity_addition_unbounded
---------------------------

Step 1
The unbounded capacity addition is the size of the Mosahyc pipeline (5.5 GWh per day).

**Citation**

European Commission (2024). Technical document accompanying the first list of Projects of Common Interest and Projects of Mutual Interest. European Commission. https://energy.ec.europa.eu/document/download/944b96b9-4efd-44a3-bbfe-45b752b0b55f_en

capacity_limit
--------------

Step 1
hydrogen_pipeline cannot be built on the edges that do not connect two adjacent countries, so its capacity limit is 0 on those 36 edges.

**Citations**

- **nuts_shp**: Eurostat (2026). Territorial units for statistics (NUTS). Eurostat. https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics
- **tyndp_2020_edges**: Jane Doe (2026). TYNDP 2020 transmission edges. ENTSO-E. https://example.com/dataset.csv

transport_loss_factor_linear
----------------------------

Step 1
The transport losses of hydrogen_pipeline are based on the Pipeline transp. 90 bar (12 inch line) of the energy transport catalogue of the Danish Energy Agency.

**Citation**

Danish Energy Agency (2026). Technology Data for Energy Transport. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-data-transport-energy

capex_per_distance_transport
----------------------------

Step 1
The distance-specific investment cost of hydrogen_pipeline is based on Long-distance renewable hydrogen transmission via cables and pipelines. On the 36 edges that do not connect two adjacent countries, the offshore cost of 914.1 Euro/(MW)/km applies.

**Citation**

Bin Miao, Lorenzo Giordano, Siew Hwa Chan (2021). Long-distance renewable hydrogen transmission via cables and pipelines. International Journal of Hydrogen Energy. https://doi.org/https://doi.org/10.1016/j.ijhydene.2021.03.067
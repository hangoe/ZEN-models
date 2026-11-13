methanol_pipeline
=================

lifetime
--------

Step 1
The lifetime of methanol_pipeline is based on Galimova et al. (2025) of the methanol pipelines dataset.

**Citation**

Tansu Galimova, Mahdi Fasihi, Dmitrii Bogdanov, Gabriel Lopez, Christian Breyer (2025). Analysis of green e-methanol supply costs: Domestic production in Europe versus imports via pipelines and sea shipping. Renewable Energy. https://doi.org/https://doi.org/10.1016/j.renene.2024.122336

capacity_limit
--------------

Step 1
methanol_pipeline cannot be built on the edges that do not connect two adjacent countries, so its capacity limit is 0 on those 36 edges.

**Citations**

- **nuts_shp**: Eurostat (2026). Territorial units for statistics (NUTS). Eurostat. https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics
- **tyndp_2020_edges**: Jane Doe (2026). TYNDP 2020 transmission edges. ENTSO-E. https://example.com/dataset.csv

transport_loss_factor_linear
----------------------------

Step 1
The losses of methanol_pipeline is based on Galimova et al. (2025) of the methanol pipelines dataset.

**Citation**

Tansu Galimova, Mahdi Fasihi, Dmitrii Bogdanov, Gabriel Lopez, Christian Breyer (2025). Analysis of green e-methanol supply costs: Domestic production in Europe versus imports via pipelines and sea shipping. Renewable Energy. https://doi.org/https://doi.org/10.1016/j.renene.2024.122336

capex_per_distance_transport
----------------------------

Step 1
The distance-specific investment cost of methanol_pipeline is based on Analysis of green e-methanol supply costs: Domestic production in Europe versus imports via pipelines and sea shipping. On the 36 edges that do not connect two adjacent countries, the offshore cost of 167 Euro/(MW)/km applies.

**Citation**

Tansu Galimova, Mahdi Fasihi, Dmitrii Bogdanov, Gabriel Lopez, Christian Breyer (2025). Analysis of green e-methanol supply costs: Domestic production in Europe versus imports via pipelines and sea shipping. Renewable Energy. https://doi.org/https://doi.org/10.1016/j.renene.2024.122336
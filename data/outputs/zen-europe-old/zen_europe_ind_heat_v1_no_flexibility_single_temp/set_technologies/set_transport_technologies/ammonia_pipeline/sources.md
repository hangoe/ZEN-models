ammonia_pipeline
================

lifetime
--------

Step 1
The lifetime of ammonia_pipeline is based on Galimova et al. (2023) of the ammonia pipelines dataset.

**Citation**

Tansu Galimova, Mahdi Fasihi, Dmitrii Bogdanov, Christian Breyer (2023). Feasibility of green ammonia trading via pipelines and shipping: Cases of Europe, North Africa, and South America. Journal of Cleaner Production. https://doi.org/https://doi.org/10.1016/j.jclepro.2023.139212

capacity_limit
--------------

Step 1
ammonia_pipeline cannot be built on the edges that do not connect two adjacent countries, so its capacity limit is 0 on those 36 edges.

**Citations**

- **nuts_shp**: Eurostat (2026). Territorial units for statistics (NUTS). Eurostat. https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics
- **tyndp_2020_edges**: Jane Doe (2026). TYNDP 2020 transmission edges. ENTSO-E. https://example.com/dataset.csv

transport_loss_factor_linear
----------------------------

Step 1
The losses of ammonia_pipeline are based on Galimova et al. (2023) of the ammonia pipelines dataset.

**Citation**

Tansu Galimova, Mahdi Fasihi, Dmitrii Bogdanov, Christian Breyer (2023). Feasibility of green ammonia trading via pipelines and shipping: Cases of Europe, North Africa, and South America. Journal of Cleaner Production. https://doi.org/https://doi.org/10.1016/j.jclepro.2023.139212

capex_per_distance_transport
----------------------------

Step 1
The distance-specific investment cost of ammonia_pipeline is based on Feasibility of green ammonia trading via pipelines and shipping: Cases of Europe, North Africa, and South America. On the 36 edges that do not connect two adjacent countries, the offshore cost of 899 Euro/(MW)/km applies.

**Citation**

Tansu Galimova, Mahdi Fasihi, Dmitrii Bogdanov, Christian Breyer (2023). Feasibility of green ammonia trading via pipelines and shipping: Cases of Europe, North Africa, and South America. Journal of Cleaner Production. https://doi.org/https://doi.org/10.1016/j.jclepro.2023.139212
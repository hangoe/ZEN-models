carbon_storage
==============

lifetime
--------

Step 1
The lifetime of carbon storage is based on the ZEP report 'The Costs of CO2 Storage: Post-Demonstration CCS in the EU'. (Table 4, Case 6, Medium).

**Citation**

ZEP, ieaghg (2011). The Costs of CO2 Storage: Post-Demonstration CCS in the EU. ZEP. https://carbonmanagementeurope.org/publication/the-costs-of-co2-storage/

capacity_addition_unbounded
---------------------------

Step 1
The unbounded capacity addition of carbon storage is based on the median existing and future capacity from the IOGP report, divided by the number of nodes in the dataset.

**Citation**

IOGP (2026). CO2 storage projects in Europe. IOGP. https://iogpeurope.org/carbon-capture-use-storage-feb2023/

capacity_existing
-----------------

Step 1
The existing carbon storage capacity is based on the IOGP report 'CO2 Storage Projects in Europe'.

**Citation**

IOGP (2026). CO2 storage projects in Europe. IOGP. https://iogpeurope.org/carbon-capture-use-storage-feb2023/

capacity_limit
--------------

Step 1
The limit on carbon storage capacity is based on historic oil and gas production data. The idea is that the injection capacity of CO2 storage is limited by the amount of oil and gas that has been extracted, as the storage sites are often located in depleted oil and gas fields. The dataset uses the Energy Institute's data on oil and gas extraction to estimate the potential CO2 storage capacity in Europe.

**Citation**

Energy Institute (2023). Energy Institute Statistical Review of World Energy. Energy Institute. https://www.energyinst.org/statistical-review

opex_specific_variable
----------------------

Step 1
The variable opex of carbon storage is based on the ZEP report 'The Costs of CO2 Storage: Post-Demonstration CCS in the EU'. (Table 4, Case 6, Medium).

**Citation**

ZEP, ieaghg (2011). The Costs of CO2 Storage: Post-Demonstration CCS in the EU. ZEP. https://carbonmanagementeurope.org/publication/the-costs-of-co2-storage/

carbon_intensity_technology
---------------------------

Step 1
The carbon intensity of carbon storage is manually set to -1, crediting one unit of permanently stored CO2 per unit of carbon processed.

capex_specific_conversion
-------------------------

Step 1
The specific conversion capex of carbon storage is obtained from the Northern Lights costs dataset.

**Citation**

Gassnova SF (2025). Potential for Cost Reductions in the CCS Value Chain. Gassnova. https://ccsnorway.com/gassnova-fremtidens-ccs-prosjekter-kan-koste-mindre/

conversion_factor
-----------------

Step 1
The conversion factor of carbon storage is manually set to an empty list, as carbon storage has no dependent carrier (input carrier = output carrier = carbon).
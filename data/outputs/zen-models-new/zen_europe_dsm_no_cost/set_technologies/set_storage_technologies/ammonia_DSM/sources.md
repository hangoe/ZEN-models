ammonia_DSM
===========

lifetime
--------

Step 1
No physical asset.

capacity_limit
--------------

Step 1
Stock up to the product demand.

opex_specific_variable
----------------------

Step 1
ammonia: demand-shiftability category 2 (optimistic, setting industry_flexibility.dsm_shiftability), from a literature review: flexible Haber-Bosch designs reach 10 % turndown; Salmon and Banares-Alcantara (2023), doi:10.1039/D3SU00067B; Fahr et al. (2025), doi:10.1016/j.ijhydene.2025.01.039. The storage cost, variable cost and shifting horizon of the category are own assumptions, see docs, 'Demand-side management'.

efficiency_charge
-----------------

Step 1
Small loss against cycling.

efficiency_discharge
--------------------

Step 1
Small loss against cycling.

capex_specific_storage_energy
-----------------------------

Step 1
ammonia: demand-shiftability category 2 (optimistic, setting industry_flexibility.dsm_shiftability), from a literature review: flexible Haber-Bosch designs reach 10 % turndown; Salmon and Banares-Alcantara (2023), doi:10.1039/D3SU00067B; Fahr et al. (2025), doi:10.1016/j.ijhydene.2025.01.039. The storage cost, variable cost and shifting horizon of the category are own assumptions, see docs, 'Demand-side management'.

energy_to_power_ratio_max
-------------------------

Step 1
ammonia: demand-shiftability category 2 (optimistic, setting industry_flexibility.dsm_shiftability), from a literature review: flexible Haber-Bosch designs reach 10 % turndown; Salmon and Banares-Alcantara (2023), doi:10.1039/D3SU00067B; Fahr et al. (2025), doi:10.1016/j.ijhydene.2025.01.039. The storage cost, variable cost and shifting horizon of the category are own assumptions, see docs, 'Demand-side management'.
dsm_no_cost scenario
--------------------

Manual override of the full flexibility dataset: opex_specific_variable and capex_specific_storage_energy set to 0.001, energy_to_power_ratio_max set to 336 h (category 3).

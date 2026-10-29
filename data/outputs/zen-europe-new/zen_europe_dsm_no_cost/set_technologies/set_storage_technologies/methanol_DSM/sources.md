methanol_DSM
============

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
methanol: demand-shiftability category 3 (optimistic, setting industry_flexibility.dsm_shiftability), from a literature review: power-to-methanol can ramp; Schneider and Lagoni (2023), https://projekter.aau.dk/projekter/files/535029626/Flexibility_of_Power_to_Methanol_in_2030.pdf; Chen and Yang (2021), doi:10.1016/j.enconman.2020.113673. The storage cost, variable cost and shifting horizon of the category are own assumptions, see docs, 'Demand-side management'.

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
methanol: demand-shiftability category 3 (optimistic, setting industry_flexibility.dsm_shiftability), from a literature review: power-to-methanol can ramp; Schneider and Lagoni (2023), https://projekter.aau.dk/projekter/files/535029626/Flexibility_of_Power_to_Methanol_in_2030.pdf; Chen and Yang (2021), doi:10.1016/j.enconman.2020.113673. The storage cost, variable cost and shifting horizon of the category are own assumptions, see docs, 'Demand-side management'.

energy_to_power_ratio_max
-------------------------

Step 1
methanol: demand-shiftability category 3 (optimistic, setting industry_flexibility.dsm_shiftability), from a literature review: power-to-methanol can ramp; Schneider and Lagoni (2023), https://projekter.aau.dk/projekter/files/535029626/Flexibility_of_Power_to_Methanol_in_2030.pdf; Chen and Yang (2021), doi:10.1016/j.enconman.2020.113673. The storage cost, variable cost and shifting horizon of the category are own assumptions, see docs, 'Demand-side management'.
dsm_no_cost scenario
--------------------

Manual override of the full flexibility dataset: opex_specific_variable and capex_specific_storage_energy set to 0.001, energy_to_power_ratio_max set to 336 h (category 3).

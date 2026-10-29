natural_gas_storage
===================

lifetime
--------

Step 1
The lifetime of natural gas storage is manually set to 200 years. Only the existing storages are modeled, which do not retire within the modeling horizon.

capacity_existing
-----------------

Step 1
The existing capacity of natural_gas_storage is derived from the storages of the SciGRID_gas IGGIELGNC-1 dataset. The volumes are converted to energy with the mean gross calorific value of the border points of the respective country.

**Citation**

Jan Diettrich, Adam Pluta, Wided Medjroubi, Jan Dasenbrock, Javier Sandoval (2021). SciGRID_gas IGGIELGNC-1. DLR - German Aerospace Center. https://zenodo.org/records/5509988. Note: Significant data inaccuracies are observed for storage data points that are only found in the INET dataset, especially for the UK. Thus, we exclude those storages with only an INET source ID.The original folder has more files (PipeSegments, Nodes, Compressors,...), which are not used here.

capacity_limit
--------------

Step 1
No new natural gas storage can be built, so the power capacity limit is manually set to 0.

efficiency_charge
-----------------

Step 1
The round-trip efficiency of natural gas storage is manually set to 0.995, and is split evenly between charging and discharging.

efficiency_discharge
--------------------

Step 1
The round-trip efficiency of natural gas storage is manually set to 0.995, and is split evenly between charging and discharging.

capex_specific_storage
----------------------

Step 1
The power-specific capex of natural gas storage is manually set to 0, as only the existing storages are modeled.

capex_specific_storage_energy
-----------------------------

Step 1
The energy-specific capex of natural gas storage is manually set to 0, as only the existing storages are modeled.

capacity_existing_energy
------------------------

Step 1
The existing capacity of natural_gas_storage is derived from the storages of the SciGRID_gas IGGIELGNC-1 dataset. The volumes are converted to energy with the mean gross calorific value of the border points of the respective country.

**Citation**

Jan Diettrich, Adam Pluta, Wided Medjroubi, Jan Dasenbrock, Javier Sandoval (2021). SciGRID_gas IGGIELGNC-1. DLR - German Aerospace Center. https://zenodo.org/records/5509988. Note: Significant data inaccuracies are observed for storage data points that are only found in the INET dataset, especially for the UK. Thus, we exclude those storages with only an INET source ID.The original folder has more files (PipeSegments, Nodes, Compressors,...), which are not used here.

capacity_limit_energy
---------------------

Step 1
No new natural gas storage can be built, so the energy capacity limit is manually set to 0.
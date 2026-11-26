wet_biomass
===========

availability_import
-------------------

Step 1
Biomass import availability derived from ENSPRESO NUTS0 energy commodity potentials ['MINBIOGAS1', 'MINBIOSLU1'], scenario 'ENS_Med'. Values are converted from PJ/a to GW and interpolated to fill missing years; the yearly variation is expressed relative to the reference year.

**Citation**

Joint Research Centre (JRC) (2019). ENSPRESO - BIOMASS. European Commission. https://data.jrc.ec.europa.eu/dataset/74ed5a04-7d74-4807-9eab-b94774309d9f

price_import
------------

Step 1
Biomass import price derived from ENSPRESO NUTS0 energy commodity prices ['MINBIOGAS1', 'MINBIOSLU1'], scenario 'ENS_Med'. Values are converted from Euro/GJ to Euro/MWh and interpolated to fill missing years; the yearly variation is expressed relative to the reference year. If regional_prices is True, national prices are used; otherwise, the average price across all NUTS0 regions is used. The average price is weighted by the availability of each biomass type in each region.

**Citation**

Joint Research Centre (JRC) (2019). ENSPRESO - BIOMASS. European Commission. https://data.jrc.ec.europa.eu/dataset/74ed5a04-7d74-4807-9eab-b94774309d9f
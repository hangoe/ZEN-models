coal_to_cement_fuel
===================

lifetime
--------

Step 1
The lifetime of coal to cement fuel is assumed to be the same as the lifetime of cement kilns, since the fuel supply is tied to the cement kiln operation.

capacity_existing
-----------------

Step 1
The existing capacity for cement fuel technologies is mainly derived from the Aidres dataset, which provides data on existing capacities for various industrial sectors.

**Citations**

- **aidres**: Luc Girardin, Juan Correa Laguna, Joris Valee (2023). Advancing industrial decarbonisation by assessing the future use of renewable energies in industrial processes. Publications Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/d80943a6-5116-11ee-9220-01aa75ed71a1/language-en
- **british_geological_survey**: N E Idoine, E R Raycraft, F Price, S F Hobbs, E A Deady, P Everett, R A Shaw, E J Evans, A J Mills  (2023). World Mineral Production 2017 - 2021. British Geological Survey. https://www.bgs.ac.uk/news/world-mineral-production-2017-to-2021-is-now-available/
- **material_economics**: Material Economics (2019). Industrial Transformation 2050 - Pathways to Net-Zero Emissions from EU Heavy Industry. Material Economics. https://materialeconomics.com/publications/publication/industrial-transformation-2050
- **ecra_technology_papers**: ECRA (European Cement Research Academy) (2022). THE ECRA TECHNOLOGY PAPERS 2022 - State of the Art Cement Manufacturing. ECRA Technology Papers. https://www.ecra-online.org/research/technology-papers

max_diffusion_rate
------------------

Step 1
The maximum diffusion rate of coal_to_cement_fuel is set to the historically observed diffusion rate of wind onshore from Mannhardt et al. (2024).

**Citation**

Jacob Mannhardt, Paolo Gabrielli, Giovanni Sansavini (2024). Understanding the vicious cycle of myopic foresight and constrained technology deployment in transforming the European energy system. iScience. https://doi.org/https://doi.org/10.1016/j.isci.2024.111369

capex_specific_conversion
-------------------------

Step 1
The specific capital expenditure (capex) for coal to cement fuel is set to 0, since hard coal is the reference fuel for cement kilns and no additional retrofitting costs are assumed for coal to cement fuel conversion.

conversion_factor
-----------------

Step 1
The conversion factor for cement fuel technologies is based on the work of Aidres et al. (2023).

**Citation**

Luc Girardin, Juan Correa Laguna, Joris Valee (2023). Advancing industrial decarbonisation by assessing the future use of renewable energies in industrial processes. Publications Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/d80943a6-5116-11ee-9220-01aa75ed71a1/language-en

retrofit_flow_coupling_factor
-----------------------------

Step 1
The retrofit flow coupling factor of cement fuel technologies is the product of the substitution potential of the fuel (100% of the kiln fuel demand, ECRA (2022), Technology Papers 2022) and the fuel consumption of the cement kiln of 3.7 GJ per ton of clinker (Material Economics (2019), 'Industrial Transformation 2050').

**Citations**

- **aidres**: Luc Girardin, Juan Correa Laguna, Joris Valee (2023). Advancing industrial decarbonisation by assessing the future use of renewable energies in industrial processes. Publications Office of the European Union. https://op.europa.eu/en/publication-detail/-/publication/d80943a6-5116-11ee-9220-01aa75ed71a1/language-en
- **british_geological_survey**: N E Idoine, E R Raycraft, F Price, S F Hobbs, E A Deady, P Everett, R A Shaw, E J Evans, A J Mills  (2023). World Mineral Production 2017 - 2021. British Geological Survey. https://www.bgs.ac.uk/news/world-mineral-production-2017-to-2021-is-now-available/
- **material_economics**: Material Economics (2019). Industrial Transformation 2050 - Pathways to Net-Zero Emissions from EU Heavy Industry. Material Economics. https://materialeconomics.com/publications/publication/industrial-transformation-2050
- **ecra_technology_papers**: ECRA (European Cement Research Academy) (2022). THE ECRA TECHNOLOGY PAPERS 2022 - State of the Art Cement Manufacturing. ECRA Technology Papers. https://www.ecra-online.org/research/technology-papers
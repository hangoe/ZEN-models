lng_terminal
============

lifetime
--------

Step 1
The lifetime of lng_terminal is based on Brauers et al. (2021) (p. 13).

**Citation**

Hanna Brauers, Isabell Braunger, Jessice Jewell (2021). Liquefied natural gas expansion plans in Germany: The risk of gas lock-in under energy transitions. Energy Research & Social Science. https://doi.org/https://doi.org/10.1016/j.erss.2021.102059

capacity_existing
-----------------

Step 1
The existing capacity of LNG terminals is derived from the SciGRID GIE dataset of LNG terminal storage-to-pipeline send-out capacities.

**Citation**

Gas Infrastructure Europe (GIE) (2024). GIE LNG Map. GIE. https://www.gie.eu/publications/maps/gie-lng-map/

capacity_limit
--------------

Step 1
Assume infinite capacity limit for those countries with existing lng terminals.

opex_specific_variable
----------------------

Step 1
The variable opex of lng_terminal is set to the regasification cost of 0.5 dollar per MMBtu of Toledano et al. (2018), converted to Euro per MWh.

**Citation**

Perrine Toledano, Nicolas Maennling, Thomas Mitro, Felipe Botelho Tavares (2018). The Open LNG Regasification Model: A Manual. CCSI. https://www.researchgate.net/publication/329641146_Manual_for_the_Open_LNG_Regasification_Model

capex_specific_conversion
-------------------------

Step 1
The specific capital expenditure of lng_terminal is based on the Brunsbuettel LNG terminal data of Brauers et al. (2021).

**Citation**

Hanna Brauers, Isabell Braunger, Jessice Jewell (2021). Liquefied natural gas expansion plans in Germany: The risk of gas lock-in under energy transitions. Energy Research & Social Science. https://doi.org/https://doi.org/10.1016/j.erss.2021.102059

conversion_factor
-----------------

Step 1
The conversion factor of LNG terminals is manually set to 1, assuming lossless regasification of LNG to natural gas.
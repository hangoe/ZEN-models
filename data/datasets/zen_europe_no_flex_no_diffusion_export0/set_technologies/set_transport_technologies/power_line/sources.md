power_line
==========

lifetime
--------

Step 1
The lifetime of power_line is based on Overhead AC line of the energy transport catalogue of the Danish Energy Agency.

**Citation**

Danish Energy Agency (2026). Technology Data for Energy Transport. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-data-transport-energy

capacity_existing
-----------------

Step 1
The existing capacity of power lines is the net transfer capacity between neighbouring countries of the ENTSO-E Transparency Platform.

**Citation**

ENTSO-E (2026). ENTSO-E Transparency Platform. ENTSO-E Transparency Platform. https://transparency.entsoe.eu/. Note: Queried via the entsoe-py package against the ENTSO-E Transparency Platform RESTful API; requires an API security token in the ENTSOE_API_KEY environment variable.

capacity_limit
--------------

Step 1
The capacity limit of the power lines is the existing net transfer capacity of the ENTSO-E Transparency Platform plus the capacity increase of all investment candidates of the TYNDP 2022 system needs study. Both directions of an edge get the larger of their values, and an edge that is not reported cannot be expanded.

**Citations**

- **iosn_candidate_units**: ENTSO-E (2023). TYNDP 2022 System Needs Study: Implementation Guidelines. ENTSO-E.. Note: Appendix 2 of the final version of May 2023, investment candidates (capacity increases) and cost assumptions, documented in IoSN-IG.pdf next to the data. The candidates are screened for the 2030 and the 2040 time horizon of the TYNDP 2022 National Trends scenarios.
- **entsoe**: ENTSO-E (2026). ENTSO-E Transparency Platform. ENTSO-E Transparency Platform. https://transparency.entsoe.eu/. Note: Queried via the entsoe-py package against the ENTSO-E Transparency Platform RESTful API; requires an API security token in the ENTSOE_API_KEY environment variable.

transport_loss_factor_linear
----------------------------

Step 1
The transport losses of power_line are based on the Overhead AC line of the energy transport catalogue of the Danish Energy Agency.

**Citation**

Danish Energy Agency (2026). Technology Data for Energy Transport. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-data-transport-energy

capex_per_distance_transport
----------------------------

Step 1
The distance-specific investment cost of power_line is based on Technology Data for Energy Transport.

**Citation**

Danish Energy Agency (2026). Technology Data for Energy Transport. Danish Energy Agency. https://ens.dk/en/analyses-and-statistics/technology-data-transport-energy
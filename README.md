# OOH Rental Equivalence Scraper

This repository contains starter code for estimating owner-occupied housing
(OOH) services using the **rental equivalence** approach.  The provided script
`scrape_rentals.py` pulls rental listings from [Lianjia](https://www.lianjia.com)
and computes a simple average monthly rent for a given city.  The script can be
extended to perform the full workflow described in the project outline:

1. Fetch rental data at the city level and stratify by tier, floor area and
   dwelling age.
2. Aggregate to the provincial level using population weights and adjust for
   quality differences.
3. Multiply effective floor area by annualized rent to obtain nominal OOH.

## Usage

```bash
pip install -r requirements.txt
python scrape_rentals.py sh --pages 1  # scrape Shanghai first page
```

The script prints a preview of the scraped listings and reports the average
monthly rent.  Additional tooling—such as CPI deflators and vacancy-rate
scenarios—can be layered on top of this foundation.

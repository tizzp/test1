"""Scrape rental listing information from Lianjia.

This module fetches rental listings for a given city from
https://www.lianjia.com and computes the average monthly rent.
It is a starting point for the workflow described in the repository
README and can be extended to stratify results across city tiers,
area buckets, and dwelling age as needed.

Example:
    python scrape_rentals.py sh --pages 2
"""
from __future__ import annotations

import argparse
import time
from typing import List, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL_TEMPLATE = "https://{city}.lianjia.com/zufang/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0 Safari/537.36"
    ),
    "Referer": "https://www.baidu.com",
}

def fetch_city_rent(city: str, pages: int = 1, delay: float = 1.0) -> pd.DataFrame:
    """Fetch rental listings for a city from Lianjia.

    Parameters
    ----------
    city: str
        Subdomain used by Lianjia for the city (e.g., ``sh`` for Shanghai).
    pages: int
        Number of result pages to scrape.
    delay: float
        Delay between page requests in seconds.  Helps reduce the chance of
        being rate-limited.

    Returns
    -------
    pandas.DataFrame
        Data frame with columns ``title``, ``price`` (RMB/month) and
        ``detail`` (raw description text).
    """
    base = BASE_URL_TEMPLATE.format(city=city)
    records: List[Dict[str, str]] = []

    with requests.Session() as session:
        for page in range(1, pages + 1):
            url = base if page == 1 else f"{base}pg{page}/"
            resp = session.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"warning: received status {resp.status_code} for {url}")
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select(".content__list .content__list--item")
            for item in items:
                title_el = item.select_one("p.content__list--item--title a")
                price_el = item.select_one("em")
                desc_el = item.select_one("p.content__list--item--des")
                if not (title_el and price_el):
                    # Some entries might be advertisements or placeholders
                    continue
                records.append(
                    {
                        "title": title_el.get_text(strip=True),
                        "price": price_el.get_text(strip=True),
                        "detail": desc_el.get_text(" | ", strip=True) if desc_el else "",
                    }
                )
            time.sleep(delay)

    df = pd.DataFrame(records)
    if not df.empty:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    return df

def compute_average_rent(city: str, pages: int = 1) -> float | None:
    """Compute the average monthly rent for a city.

    Parameters
    ----------
    city: str
        City subdomain understood by Lianjia.
    pages: int
        Number of pages to scrape.

    Returns
    -------
    float | None
        Average monthly rent in RMB if listings were found, otherwise ``None``.
    """
    df = fetch_city_rent(city, pages)
    if df.empty:
        return None
    return float(df["price"].mean())

def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape rental listings from Lianjia")
    parser.add_argument("city", help="City subdomain, e.g., sh for Shanghai or bj for Beijing")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to scrape")
    args = parser.parse_args()

    df = fetch_city_rent(args.city, pages=args.pages)
    if df.empty:
        print("No data fetched. The site may have blocked the request or returned no listings.")
        return

    print(df.head())
    avg = df["price"].mean()
    print(f"Average monthly rent: {avg:.2f} RMB")

if __name__ == "__main__":
    main()

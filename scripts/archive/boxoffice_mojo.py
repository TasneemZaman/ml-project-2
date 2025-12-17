"""
Simple Box Office Mojo scraper helpers.

Notes:
- Uses requests + BeautifulSoup to search Box Office Mojo and parse title pages.
- Attempts to extract opening weekend, first-week gross (week 1), and domestic total.
- This is a best-effort parser: Box Office Mojo HTML can change; if a value isn't found,
  functions return None for that field.

Use responsibly and respect robots.txt / rate limits.
"""
from typing import Optional, Dict
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import re
import time

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
}


def _clean_money(s: str) -> Optional[int]:
    if not s:
        return None
    s = s.strip()
    # Accept things like "$1,234,567" or "–" or "N/A"
    if s in ("", "–", "N/A", "—"):
        return None
    m = re.search(r"([\d,]+)", s)
    if not m:
        return None
    num = m.group(1).replace(',', '')
    try:
        return int(num)
    except ValueError:
        return None


def search_title(title: str, year: Optional[int] = None, session: Optional[requests.Session] = None) -> Optional[str]:
    """Search Box Office Mojo for a title and return the first matching title/release URL (absolute).

    Returns None if nothing found.
    """
    session = session or requests.Session()
    q = quote_plus(title)
    url = f'https://www.boxofficemojo.com/search/?q={q}'
    r = session.get(url, headers=DEFAULT_HEADERS, timeout=15)
    if not r.ok:
        return None
    soup = BeautifulSoup(r.text, 'lxml')

    # Search results often include links to /title/ or /release/ pages
    anchors = soup.find_all('a', href=True)
    candidates = []
    for a in anchors:
        href = a['href']
        if href.startswith('/') and ('/title/' in href or '/release/' in href or '/release/rl' in href):
            text = a.get_text(separator=' ').strip()
            candidates.append((href, text))

    # prefer links that contain the year if provided
    for href, text in candidates:
        if year and str(year) in text:
            return urljoin('https://www.boxofficemojo.com', href)

    if candidates:
        return urljoin('https://www.boxofficemojo.com', candidates[0][0])
    return None


def fetch_title_page(bom_url: str, session: Optional[requests.Session] = None) -> Optional[BeautifulSoup]:
    session = session or requests.Session()
    r = session.get(bom_url, headers=DEFAULT_HEADERS, timeout=15)
    if not r.ok:
        return None
    return BeautifulSoup(r.text, 'lxml')


def parse_summary_values(soup: BeautifulSoup) -> Dict[str, Optional[int]]:
    """Try to parse summary values from the title/release page.

    Returns dict with keys: opening_weekend, domestic_total, worldwide_total, international_total
    """
    result = {
        'opening_weekend': None,
        'domestic_total': None,
        'worldwide_total': None,
        'international_total': None,
    }

    # METHOD 1: Parse the performance summary table (most reliable)
    perf_div = soup.find('div', class_='mojo-performance-summary-table')
    if perf_div:
        rows = perf_div.find_all('div', recursive=False)
        for row in rows:
            text = row.get_text(strip=True).lower()
            money = row.find('span', class_='money')
            if money:
                val = _clean_money(money.get_text(strip=True))
                if 'domestic' in text and '(' in text:  # "Domestic (38.4%)"
                    result['domestic_total'] = val
                elif 'international' in text and '(' in text:  # "International (61.6%)"
                    result['international_total'] = val
                elif 'worldwide' in text:
                    result['worldwide_total'] = val

    # METHOD 2: Look for "Domestic Opening" value in mojo-summary-values section
    summary_section = soup.find('div', class_='mojo-summary-values')
    if summary_section:
        for elem in summary_section.find_all('div', class_='a-section'):
            spans = elem.find_all('span')
            if len(spans) >= 2:
                label = spans[0].get_text(strip=True)
                if 'Domestic Opening' in label or 'Opening' in label:
                    # The value is in the next span (sometimes with class 'money')
                    value_span = spans[1] if len(spans) > 1 else None
                    if value_span:
                        # Check if it has money class or extract from text
                        money_child = value_span.find('span', class_='money')
                        if money_child:
                            result['opening_weekend'] = _clean_money(money_child.get_text(strip=True))
                        else:
                            result['opening_weekend'] = _clean_money(value_span.get_text(strip=True))
                        if result['opening_weekend']:
                            break

    # FALLBACK: Use regex on full text (less reliable but catches edge cases)
    text = soup.get_text(separator='|')
    
    if result['opening_weekend'] is None:
        m = re.search(r'Opening(?: Weekend)?[^$\d\n\|\t\r\:]*\$?([\d,]+)', text, re.IGNORECASE)
        if m:
            try:
                result['opening_weekend'] = int(m.group(1).replace(',', ''))
            except ValueError:
                pass

    # Calculate international if we have worldwide and domestic but not international
    if result['international_total'] is None and result['worldwide_total'] and result['domestic_total']:
        result['international_total'] = result['worldwide_total'] - result['domestic_total']

    return result


def parse_weekly_table_for_week1(soup: BeautifulSoup) -> Optional[int]:
    """Attempt to find the weekly box office table and return gross for week 1 (first row with '1')."""
    # BOM uses tables with class 'mojo-body-table' for box office breakdowns
    tables = soup.find_all('table')
    for table in tables:
        # find header cells to locate a 'Week' and 'Gross' column
        headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
        if not headers:
            continue
        if any('week' in h for h in headers) and any('gross' in h for h in headers):
            # find rows
            rows = table.find_all('tr')
            for tr in rows:
                cols = [td.get_text(strip=True) for td in tr.find_all(['td','th'])]
                if not cols:
                    continue
                # first column may be week number
                if re.match(r'^1\b', cols[0]):
                    # find gross column index
                    gross_idx = None
                    for i, h in enumerate(headers):
                        if 'gross' in h:
                            gross_idx = i
                            break
                    if gross_idx is None:
                        # fallback: last numeric-looking column
                        for c in reversed(cols):
                            if re.search(r'\$[\d,]+', c):
                                return _clean_money(c)
                        return None
                    if gross_idx < len(cols):
                        return _clean_money(cols[gross_idx])
    return None


def get_bom_data(title: str, year: Optional[int] = None, session: Optional[requests.Session] = None) -> Dict[str, Optional[object]]:
    """Top-level helper: search BOM, fetch page, and extract opening weekend, first-week gross, domestic total, worldwide total, international total, and the bom URL.

    Returns a dict:
      { 'bom_url': str or None, 'bom_opening_weekend': int|None, 'bom_first_week': int|None, 
        'bom_domestic_total': int|None, 'bom_worldwide_total': int|None, 'bom_international_total': int|None }
    """
    session = session or requests.Session()
    out = {
        'bom_url': None,
        'bom_opening_weekend': None,
        'bom_first_week': None,
        'bom_domestic_total': None,
        'bom_worldwide_total': None,
        'bom_international_total': None,
    }

    try:
        bom_url = search_title(title, year=year, session=session)
        if not bom_url:
            return out
        out['bom_url'] = bom_url
        soup = fetch_title_page(bom_url, session=session)
        if not soup:
            return out

        summary = parse_summary_values(soup)
        out['bom_opening_weekend'] = summary.get('opening_weekend')
        out['bom_domestic_total'] = summary.get('domestic_total')
        out['bom_worldwide_total'] = summary.get('worldwide_total')
        out['bom_international_total'] = summary.get('international_total')

        # Attempt weekly table parsing for week 1
        week1 = parse_weekly_table_for_week1(soup)
        out['bom_first_week'] = week1

        # If week1 missing but opening_weekend exists, use opening as approximation
        if out['bom_first_week'] is None and out['bom_opening_weekend'] is not None:
            out['bom_first_week'] = out['bom_opening_weekend']

        # small polite delay to avoid hammering
        time.sleep(0.5)
    except Exception:
        # be silent on parser exceptions; return what we have
        pass

    return out


if __name__ == '__main__':
    # quick manual test
    import sys
    sess = requests.Session()
    for pair in [("Inside Out 2", 2024), ("Venom: The Last Dance", 2024)]:
        title, year = pair
        print('Querying:', title, year)
        print(get_bom_data(title, year=year, session=sess))

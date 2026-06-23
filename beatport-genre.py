#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from difflib import SequenceMatcher
import re
import urllib.parse

import argparse

# Argument parsing
parser = argparse.ArgumentParser(description='get song genre from beatport')
parser.add_argument('song', type=str, help="song name")
parser.add_argument('-p', '--pretty', action='store_true', help="Pretty print output with indentation")
args = parser.parse_args()

def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    # drop mix/version details in parentheses/brackets
    s = re.sub(r"\(.*?\)|\[.*?\]", " ", s)
    # collapse whitespace & strip punctuation-like clutter
    s = re.sub(r"[^a-z0-9\s\-\&/']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def get_genre_from_beatport(query: str, timeout: int = 15):
    options = Options()
    # added useragent might need to switch to undetected-chromedriver if beatport makes cloudflare harder
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
    
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")

    driver = webdriver.Chrome(options=options)

    try:
        q = urllib.parse.quote_plus(query)
        url = f"https://www.beatport.com/search?q={q}"
        driver.get(url)

        wait = WebDriverWait(driver, timeout)

        rows = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '[data-testid="tracks-table-row"]')
            )
        )

        candidates = []
        for row in rows:
            try:
                title_a = row.find_element(By.CSS_SELECTOR, 'div.cell.title a[title]')
                track_title = (title_a.get_attribute("title") or "").strip()

                visible_title = title_a.text.strip() or track_title

                try:
                    artists_block = row.find_element(By.CSS_SELECTOR, 'div.cell.title .ArtistNames-sc-f2e950a1-0')
                    artists = artists_block.text.strip()
                except Exception:
                    try:
                        container_text = row.find_element(By.CSS_SELECTOR, 'div.cell.title .container').text
                        artists = "\n".join(container_text.split("\n")[1:]).strip()
                        if len(artists) > 200:
                            artists = ""
                    except Exception:
                        artists = ""

                genre_a = row.find_element(By.CSS_SELECTOR, 'div.cell.bpm a[title]')
                genre = (genre_a.get_attribute("title") or "").strip()

                candidate_string = (artists + " - " if artists else "") + visible_title
                score = similarity(query, candidate_string)

                candidates.append({
                    "score": score,
                    "genre": genre,
                    "title": visible_title,
                    "artists": artists
                })
            except Exception:
                continue

        if not candidates:
            return None

        best = max(candidates, key=lambda x: x["score"])
        return {
            "genre": best["genre"],
            "matched_title": best["title"],
            "matched_artists": best["artists"],
            "score": round(best["score"], 3),
        }

    finally:
        driver.quit()


if __name__ == "__main__":
    genre_info = get_genre_from_beatport(args.song)
    if genre_info:
        if args.pretty:
            print(f"Genre information for: {args.song}")
            print(f"  Matched Title  : {genre_info['matched_title']}")
            print(f"  Matched Artists: {genre_info['matched_artists'] or 'N/A'}")
            print(f"  Genre          : {genre_info['genre']}")
            print(f"  Match Score    : {genre_info['score']}")
        else:
            print(f"'{args.song}': {genre_info}")
    else:
        print(f"Could not find genre for '{args.song}'.")

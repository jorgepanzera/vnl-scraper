from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

BASE_URLS = {
    "women": "https://www.flashscore.com/volleyball/world/nations-league-women-{year}/results/",
    "men": "https://www.flashscore.com/volleyball/world/nations-league-{year}/results/"
}

OUTPUT_DIR = "vnl_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_set_score(el):
    try:
        return int(float(el.inner_text().strip()))
    except:
        return None  # fallback if score is missing or malformed


def scrape_vnl_season(year, gender):
    url = BASE_URLS[gender].format(year=year)
    print(f"Scraping {gender.upper()} {year}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # ✅ Check for empty season (e.g., 2020)
        match_locator = page.locator("div.event__match")
        match_count = match_locator.count()

        if match_count == 0:
            print(f"⚠️ No matches found for {gender} {year} — skipping.")
            browser.close()
            return []
        else:
            page.wait_for_selector("div.event__match")
            match_elements = page.query_selector_all("div.event__match")

        match_data = []

        for match in match_elements:
            try:
                home_team = match.query_selector(".event__participant--home").inner_text().strip()
                away_team = match.query_selector(".event__participant--away").inner_text().strip()

                # Remove trailing " W" only in women matches
                if gender == "women":
                    home_team = home_team.removesuffix(" W")
                    away_team = away_team.removesuffix(" W")


                # Date parsing
                date_text = match.query_selector(".event__time").inner_text()
                day_month = date_text.split(" ")[0]
                clean_day_month = day_month.strip().replace("..", ".").rstrip(".")
                match_date_str = f"{clean_day_month}.{year}"
                match_date = datetime.strptime(match_date_str, "%d.%m.%Y").date()

                # Match ID and URL
                match_id_attr = match.get_attribute("id")
                match_id = match_id_attr.split("_")[-1]
                match_url = f"https://www.flashscore.com/match/{match_id}/#/match-summary"

                # --- SET SCORE EXTRACTION ---
                sets_home = []
                sets_away = []

                def extract_int(el):
                    try:
                        return int(float(el.inner_text().strip()))
                    except:
                        return None

                for i in range(1, 6):
                    home_el = match.query_selector(f".event__part--home.event__part--{i}")
                    away_el = match.query_selector(f".event__part--away.event__part--{i}")

                    if home_el and away_el:
                        h = extract_int(home_el)
                        a = extract_int(away_el)
                        sets_home.append(h)
                        sets_away.append(a)
                    else:
                        break

                # ✅ Corrected: calculate sets won instead of using incorrect DOM values
                home_sets_won = sum(1 for h, a in zip(sets_home, sets_away) if h > a)
                away_sets_won = sum(1 for h, a in zip(sets_home, sets_away) if a > h)

                row = {
                    "season": year,
                    "gender": gender,
                    "match_date": match_date.isoformat(),
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_sets_won,
                    "away_score": away_sets_won,
                    "outcome": 1 if home_sets_won > away_sets_won else 0,
                }


                # Always produce 5 set columns, filling with None if missing
                for idx in range(5):
                    row[f"set_{idx+1}_home"] = sets_home[idx] if idx < len(sets_home) else None
                    row[f"set_{idx+1}_away"] = sets_away[idx] if idx < len(sets_away) else None

                # Add match_url last for aesthetic reasons
                row["match_url"] = match_url

                match_data.append(row)

            except Exception as e:
                print(f"Skipping match due to error: {e}")
                continue

        browser.close()
        return match_data



# Main loop: scrape both genders and save files
all_women = []
all_men = []

# Main loop: scrape both genders and save files
for gender in ["women", "men"]:
    all_data = []

    for season in range(2018, 2025):
        season_results = scrape_vnl_season(season, gender)
        if not season_results:
            print(f"No data found for {gender} {season}")
            continue

        df = pd.DataFrame(season_results)

        # Convert set columns to nullable Int64 to prevent float .0
        for i in range(1, 6):
            df[f"set_{i}_home"] = df[f"set_{i}_home"].astype("Int64")
            df[f"set_{i}_away"] = df[f"set_{i}_away"].astype("Int64")

        # Save CSV
        csv_filename = f"{OUTPUT_DIR}/vnl_{gender}_{season}.csv"
        df.to_csv(csv_filename, index=False)

        # Save JSON
        json_filename = f"{OUTPUT_DIR}/vnl_{gender}_{season}.json"
        df.to_json(json_filename, orient="records", indent=2)

        print(f"✅ Saved {len(df)} matches to {csv_filename} and {json_filename}")

        all_data.extend(season_results)

    # Save merged file
    df_all = pd.DataFrame(all_data)

    # Merged CSV
    merged_csv = f"{OUTPUT_DIR}/vnl_{gender}_all.csv"
    df_all.to_csv(merged_csv, index=False)

    # Merged JSON
    merged_json = f"{OUTPUT_DIR}/vnl_{gender}_all.json"
    df_all.to_json(merged_json, orient="records", indent=2)

    print(f"📁 Merged files saved: {merged_csv} and {merged_json}")


    if gender == "women":
        all_women = df_all
    else:
        all_men = df_all

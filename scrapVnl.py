from playwright.sync_api import sync_playwright
import pandas as pd

URL = "https://www.flashscore.com/volleyball/world/nations-league-women-2024/results/"

def scrape_vnl_scores():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)

        page.wait_for_selector("div.event__match")
        match_elements = page.query_selector_all("div.event__match")

        match_data = []

        for match in match_elements:
            try:
                home_team = match.query_selector(".event__participant--home").inner_text()
                away_team = match.query_selector(".event__participant--away").inner_text()

                home_score = match.query_selector(".event__score--home").inner_text()
                away_score = match.query_selector(".event__score--away").inner_text()

                # Set scores (up to 5 sets max)
                set_scores = []
                for i in range(1, 6):
                    home_set = match.query_selector(f".event__part--home.event__part--{i}")
                    away_set = match.query_selector(f".event__part--away.event__part--{i}")

                    if home_set and away_set:
                        set_scores.append(f"{home_set.inner_text()}–{away_set.inner_text()}")
                    else:
                        break  # Stop if no more sets

                match_data.append({
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    "sets": set_scores
                })

            except Exception as e:
                print("Skipping one match due to error:", e)
                continue

        browser.close()
        return match_data


results = scrape_vnl_scores()
df = pd.DataFrame(results)

# Separate sets into columns
max_sets = df["sets"].apply(len).max()
for i in range(max_sets):
    df[f"set_{i+1}"] = df["sets"].apply(lambda x: x[i] if i < len(x) else None)

df.drop(columns="sets", inplace=True)

# Save to CSV
df.to_csv("vnl_2024_full_results.csv", index=False)
print(df.head())

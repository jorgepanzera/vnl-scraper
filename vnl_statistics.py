import pandas as pd

def load_data():
    path = input("Enter the path to the CSV file (e.g., vnl_scraped_data.csv): ").strip()
    try:
        df = pd.read_csv(path)
        print(f"✅ Loaded {len(df)} matches from {path}")
        return df
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None

def first_set_winner_wins_match(df):
    total_matches = 0
    wins_by_set1_winner = 0

    for _, row in df.iterrows():
        set1_home = row["set_1_home"]
        set1_away = row["set_1_away"]

        if set1_home == set1_away:
            continue  # skip if set 1 is a tie (bad data)

        total_matches += 1

        set1_winner = "home" if set1_home > set1_away else "away"
        match_winner = "home" if row["home_score"] > row["away_score"] else "away"

        if set1_winner == match_winner:
            wins_by_set1_winner += 1

    if total_matches == 0:
        print("\n📊 [First Set Winner] No valid matches found.")
        return

    pct = (wins_by_set1_winner / total_matches) * 100

    print("\n📊 [First Set Winner Match Outcome] Stats:")
    print(f"- Total matches: {total_matches}")
    print(f"- First set winner also won match: {wins_by_set1_winner} ({pct:.2f}%)")


def first_two_sets_winner_wins_match(df):
    total_matches = 0
    wins_by_2set_winner = 0

    for _, row in df.iterrows():
        s1h, s1a = row["set_1_home"], row["set_1_away"]
        s2h, s2a = row["set_2_home"], row["set_2_away"]

        # Skip incomplete or tied sets (bad data)
        if (s1h == s1a) or (s2h == s2a):
            continue

        # Who won both sets?
        if (s1h > s1a) and (s2h > s2a):
            early_leader = "home"
        elif (s1h < s1a) and (s2h < s2a):
            early_leader = "away"
        else:
            continue  # not a 2-0 situation

        total_matches += 1

        match_winner = "home" if row["home_score"] > row["away_score"] else "away"

        if early_leader == match_winner:
            wins_by_2set_winner += 1

    if total_matches == 0:
        print("\n📊 [2–0 Start] No matches with a 2–0 lead found.")
        return

    pct = (wins_by_2set_winner / total_matches) * 100

    print("\n📊 [2–0 Set Lead Match Outcome] Stats:")
    print(f"- Total matches with 2–0 start: {total_matches}")
    print(f"- Team with 2–0 lead won match: {wins_by_2set_winner} ({pct:.2f}%)")



def one_one_set3_winner_match_winner(df):
    one_one_matches = df[
        ((df["set_1_home"] > df["set_1_away"]) & (df["set_2_home"] < df["set_2_away"])) |
        ((df["set_1_home"] < df["set_1_away"]) & (df["set_2_home"] > df["set_2_away"]))
    ].copy()

    one_one_matches["set3_winner"] = one_one_matches.apply(
        lambda row: "home" if row["set_3_home"] > row["set_3_away"]
        else "away" if row["set_3_home"] < row["set_3_away"]
        else "tie", axis=1
    )

    one_one_matches["match_winner"] = one_one_matches.apply(
        lambda row: "home" if row["home_score"] > row["away_score"]
        else "away" if row["home_score"] < row["away_score"]
        else "tie", axis=1
    )

    total = len(one_one_matches)
    matches_won_by_set3_winner = one_one_matches[one_one_matches["set3_winner"] == one_one_matches["match_winner"]]

    home_set3 = one_one_matches[one_one_matches["set3_winner"] == "home"]
    away_set3 = one_one_matches[one_one_matches["set3_winner"] == "away"]

    home_conversion = home_set3[home_set3["match_winner"] == "home"]
    away_conversion = away_set3[away_set3["match_winner"] == "away"]

    print("\n📊 [1-1 After 2 Sets] Stats:")
    print(f"- Total 1-1 Matches: {total}")
    print(f"- Set 3 winner also won match: {len(matches_won_by_set3_winner)} ({len(matches_won_by_set3_winner) / total * 100:.2f}%)")
    #print(f"- Home won Set 3 & match: {len(home_conversion) / len(home_set3) * 100:.2f}%" if len(home_set3) else "- No home wins in Set 3")
    #print(f"- Away won Set 3 & match: {len(away_conversion) / len(away_set3) * 100:.2f}%" if len(away_set3) else "- No away wins in Set 3")


def comeback_from_0_2_to_win(df):
    five_set_matches = df[(df["home_score"] + df["away_score"]) == 5].copy()

    total_five_sets = len(five_set_matches)
    total_comeback_attempts = 0
    comeback_wins = 0
    total_matches = len(df)

    for _, row in five_set_matches.iterrows():
        # Case 1: Home wins sets 1 & 2, Away wins sets 3 & 4 (2-2)
        if (row["set_1_home"] > row["set_1_away"]) and (row["set_2_home"] > row["set_2_away"]) and \
           (row["set_3_home"] < row["set_3_away"]) and (row["set_4_home"] < row["set_4_away"]):
            total_comeback_attempts += 1
            if row["set_5_home"] > row["set_5_away"]:
                comeback_wins += 1  # Away team came back and won

        # Case 2: Away wins sets 1 & 2, Home wins sets 3 & 4 (2-2)
        elif (row["set_1_home"] < row["set_1_away"]) and (row["set_2_home"] < row["set_2_away"]) and \
             (row["set_3_home"] > row["set_3_away"]) and (row["set_4_home"] > row["set_4_away"]):
            total_comeback_attempts += 1
            if row["set_5_home"] < row["set_5_away"]:
                comeback_wins += 1  # Home team came back and won

    if total_five_sets == 0:
        print("\n📊 [0–2 to 2–2 Comeback] No 5-set matches found.")
        return

    comeback_rate = (total_comeback_attempts / total_matches) * 100
    win_rate = (comeback_wins / total_comeback_attempts) * 100 if total_comeback_attempts > 0 else 0
    win_rate_over_total = (comeback_wins / total_matches) * 100 if total_matches > 0 else 0

    print("\n📊 [0–2 to 2–2 Comeback] Stats:")
    print(f"- Total 5-set matches: {total_five_sets}")
    print(f"- Total matches: {total_matches}")
    print(f"- Comeback attempts (0–2 to 2–2): {total_comeback_attempts} ({comeback_rate:.2f}%)")
    print(f"- Comeback team won the match: {comeback_wins} ({win_rate:.2f}%) after comeback, ({win_rate_over_total:.2f}%) over total games")

def two_one_equalizer_wins_match(df):
    five_set_matches = df[(df["home_score"] + df["away_score"]) == 5].copy()

    total_cases = 0
    wins_by_equalizer = 0

    for _, row in five_set_matches.iterrows():
        sets = [
            (row["set_1_home"], row["set_1_away"]),
            (row["set_2_home"], row["set_2_away"]),
            (row["set_3_home"], row["set_3_away"]),
            (row["set_4_home"], row["set_4_away"]),
            (row["set_5_home"], row["set_5_away"]),
        ]

        # Count set wins after 3 sets
        home_wins_3 = sum(1 for i in range(3) if sets[i][0] > sets[i][1])
        away_wins_3 = sum(1 for i in range(3) if sets[i][1] > sets[i][0])

        # Set 4 winner
        set4_home, set4_away = sets[3]

        # Identify who equalized and won
        if (home_wins_3 == 2 and away_wins_3 == 1) and (set4_away > set4_home):
            # Away equalized to 2–2
            total_cases += 1
            if sets[4][1] > sets[4][0]:
                wins_by_equalizer += 1

        elif (away_wins_3 == 2 and home_wins_3 == 1) and (set4_home > set4_away):
            # Home equalized to 2–2
            total_cases += 1
            if sets[4][0] > sets[4][1]:
                wins_by_equalizer += 1

    if total_cases == 0:
        print("\n📊 [2–1 to 2–2] No cases found.")
        return

    percentage = wins_by_equalizer / total_cases * 100

    print("\n📊 [2–1 to 2–2 Equalizer Wins Match] Stats:")
    print(f"- Total matches with 2–1 → 2–2 situation: {total_cases}")
    print(f"- Equalizer team won the match: {wins_by_equalizer} ({percentage:.2f}%)")


def show_menu():
    print("\n=== VNL Statistic Calculator ===")
    print("1 - [Set 1 winner] Percentage of matches they won")
    print("2 - [Set 1 & 2 winner] Percentage of matches they won")
    print("3 - [1-1 after 2 sets] Set 3 winner vs match winner")
    print("4 - [2–1 lead tied to 2–2] Did equalizer win the match?")
    print("5 - [0-2 to 2-2 comeback] Did comeback team win the match?")
    print("0 - Exit")
    return input("Choose an option: ")

def main():
    df = load_data()
    if df is None:
        return

    while True:
        choice = show_menu()
        if choice == "1":
            first_set_winner_wins_match(df)
        elif choice == "2":            
            first_two_sets_winner_wins_match(df)
        elif choice == "3":
            one_one_set3_winner_match_winner(df)
        elif choice == "4":
            two_one_equalizer_wins_match(df)
        elif choice == "5": 
            comeback_from_0_2_to_win(df)
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❗ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

import pandas as pd
from difflib import get_close_matches

HIGH_THRESHOLD = 100_000
MEDIUM_THRESHOLD = 10_000

def categorize_search_volume(volume: int) -> str:
    if volume >= HIGH_THRESHOLD:
        return 'High'
    elif volume >= MEDIUM_THRESHOLD:
        return 'Medium'
    else:
        return 'Low'

def match_headline_to_keyword(headline: str) -> dict:
    """
    Given a product headline, find the best-matching keyword in df_keywords,
    then return its Competition and a High/Medium/Low bucket for avg monthly searches.

    Strategy:
      1. Lowercase everything for comparison.
      2. Check for any exact substring match: if a keyword string appears within the headline.
      3. If no substring match, fall back to a fuzzy match (difflib.get_close_matches).
    
    Args:
        headline (str): The product headline (e.g., "Leather Coach Bags for Sale").
        df_keywords (pd.DataFrame): DataFrame containing the keyword dataset.
    
    Returns:
        dict: {
            'Keyword': str,                # The matched keyword
            'Competition': str,            # Original 'Competition' value (e.g., "High")
            'Avg. monthly searches': int,  # Raw numeric value
            'Search Category': str         # Bucketed: "High"/"Medium"/"Low"
        }
        or None if no match is found.
    """
    df_keywords = pd.read_excel("Google_Analytics/Analytics_report.xlsx")
    if not isinstance(headline, str) or not headline.strip():
        return {}
    headline_lower = headline.strip().lower()
    keywords_list = df_keywords['Keyword'].astype(str).tolist()
    keywords_lower = [k.lower() for k in keywords_list]

    # 1. Try substring match: look for any keyword that appears in the headline text
    for idx, kw_lower in enumerate(keywords_lower):
        if kw_lower in headline_lower:
            matched_keyword = keywords_list[idx]
            row = df_keywords.iloc[idx]
            avg_search = int(row['Avg. monthly searches'])
            return {
                'Keyword': matched_keyword,
                'Competition': row['Competition'],
                'Avg. monthly searches': avg_search,
                'Search Category': categorize_search_volume(avg_search)
            }

    # 2. If no substring match, use fuzzy matching with difflib
    #    Lowercase keywords passed into get_close_matches
    match = get_close_matches(headline_lower, keywords_lower, n=1, cutoff=0.6)
    if match:
        matched_lower = match[0]
        # Find the index of the original keyword
        idx = keywords_lower.index(matched_lower)
        matched_keyword = keywords_list[idx]
        row = df_keywords.iloc[idx]
        avg_search = int(row['Avg. monthly searches'])
        return {
            'Keyword': matched_keyword,
            'Competition': row['Competition'],
            'Avg. monthly searches': avg_search,
            'Search Category': categorize_search_volume(avg_search)
        }

    # No match found
    return None

# -------------------------------------------------------------------
# Example usage
# -------------------------------------------------------------------
# if __name__ == "__main__":
#     # Example: load a few sample headlines
#     sample_headlines = [
#         "Coach Leather Hobo Tote Bag"
#     ]

#     results = []
#     for head in sample_headlines:
#         match_info = match_headline_to_keyword(head, df)
#         if match_info:
#             results.append((head, match_info))
#         else:
#             results.append((head, {'Keyword': None, 'Competition': None, 'Avg. monthly searches': None, 'Search Category': None}))

#     # Print the results
#     for headline, info in results:
#         print(f"Headline: \"{headline}\"")
#         if info['Keyword']:
#             print(f"  → Matched Keyword         : {info['Keyword']}")
#             print(f"  → Competition             : {info['Competition']}")
#             print(f"  → Avg. Monthly Searches   : {info['Avg. monthly searches']}")
#             print(f"  → Search Category (H/M/L) : {info['Search Category']}")
#         else:
#             print("  → No matching keyword found in dataset.")
#         print("-" * 60)

import re
import pandas as pd

def count_sentences(text: str) -> int:
    """
    Splits on '.', '!' or '?' followed by space or end of string,
    then filters out empty fragments.
    """
    sentences = re.split(r'[.!?](?:\s|$)', str(text).strip())
    return sum(1 for s in sentences if s.strip())

def find_blacklisted(text: str, blacklist: list[str]) -> list[str]:
    """
    Finds all whole‐word matches of any keyword in blacklist (case‐insensitive).
    """
    if not text or not blacklist:
        return []
    pattern = r'\b(?:' + '|'.join(map(re.escape, blacklist)) + r')\b'
    return list({m.lower() for m in re.findall(pattern, text, flags=re.IGNORECASE)})

def process_workbook(
    input_path: str,
    blacklist: list[str],
    output_path: str,
    sheet_name_suffix: str = "_results"
):
    """
    Reads all sheets from `input_path`, processes each, and writes a new workbook to `output_path`.
    """
    xls = pd.ExcelFile(input_path)
    writer = pd.ExcelWriter(
        output_path,
        engine="xlsxwriter",
        engine_kwargs={"options": {"strings_to_urls": False}}
    )
    
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        results = []
        df = df.dropna(
            subset=[
                "editorial_tagline",
                "editorial_tagline_genz_variation",
            ],
            how="any",
        )
        
        for idx, row in df.iterrows():
            row_result = {}
            for col in [
                "editorial_tagline",
                "editorial_tagline_genz_variation",
            ]:
                text = row.get(col, "")
                # Sentence count
                cnt = count_sentences(text)
                # Determine allowed count
                allowed = 5 if col=="editorial_tagline_appended_genz_line" else 4
                if cnt == allowed:
                    row_result[f"{col}_sentences"] = "OK"
                elif cnt < allowed:
                    row_result[f"{col}_sentences"] = f"Too few ({cnt})"
                else:
                    row_result[f"{col}_sentences"] = f"Too many ({cnt})"
                
                # Blacklist check
                found = find_blacklisted(text, blacklist)
                row_result[f"{col}_blacklisted"] = ", ".join(found) if found else ""
            
            results.append(row_result)
        
        res_df = pd.DataFrame(results)
        # Combine original and results side by side if you like:
        out_df = pd.concat([df, res_df], axis=1)
        out_df.to_excel(writer, sheet_name=sheet + sheet_name_suffix, index=False)
    
    writer._save()
    print(f"Processed '{input_path}' → '{output_path}'")

if __name__ == "__main__":
    # Example usage for your two files:
    files_and_blacklists = [
        ("Combined_Coach_Results_1.xlsx", [
            "inspired by", "chic", "exudes sophistication", "gen-z customer", "gen-z", 
            "aesthetic", "affordable", "ageless", "body", "chic", "coachie", "couture", 
            "craftsman", "customer", "cute", "dainty", "daintier", "darling", "deal", 
            "delightful", "designer", "discount", "disruptive", "don", "donning", 
            "easy win", "elegant", "elegance", "embellished", "enchanting", "engineered", 
            "eternal", "expressive luxury", "fabulous", "fabulousness", "fashion", 
            "fashion lover", "fashionista", "fave", "footwear", "gang", "gender-neutral", 
            "handbag", "hot", "it bag", "it girl", "it’s giving", "jet-set", "lovely", 
            "multifunctional", "must have", "new you", "obsess", "obsessed", "mindful", 
            "green", "conscious", "eco-conscious", "pioneering", "pleasing", "pretty", 
            "purse", "quiet luxury", "sale", "sassy", "savage", "sensations", "sleek", 
            "splendid", "sueded", "sustainable", "szn", "tender", "treasures", 
            "trendsetter", "turn heads", "unearth", "unveil", "unveiling", "uptown style", 
            "downtown style", "urban", "vibes", "but make it fashion", "meet", 
            "experience", "introducing", "just", "literally", "figuratively", 
            "audacious", "pvc", "PVC", "mundane", "nitty-gritties", "beauty scores", 
            "best", "boast", "booster", "statement", "promise", "declaration", "go-to", 
            "taste", "impeccable", "pretty face", "testament", "touches", "must-have", 
            "impraczcal", "unassuming", "overlook", "unusual", "friend", "flair", 
            "fierce", "efforzless", "glamour", "outing", "fashionable", "stylish", 
            "more than a pretty face", "your new best friend", "accessories collection", 
            "boasts", "modern fashion", "this is Coach Outlet's promise to you", 
            "declaration of style", "testament to your impeccable taste", 
            "finishing touches from Coach Outlet", "fashion adventures", "flair", 
            "audacious modern style", "this beauty scores high", "meziculously", 
            "captivating", "aesthetics", "simplicity and class", "dash of the unusual", 
            "crafted to fulfill", "unassuming elegance", "it's impractical to overlook", 
            "sexy", "let's talk about", "inspiration can come", "fall in love", 
            "inspiration can strike", "picture this", "picture themselves", "imagine", 
            "bio-attributed", "bio-based", "biodegradable", "bio-finished", 
            "carbon neutral", "certified b corp", "chemical recycling", "circular", 
            "closed loop", "compostable", "fair trade", "FSC", "forest stewardship", 
            "council", "mechanical recycling", "natural", "PEFC", "recyclable", 
            "upcycled", "SFI", "responsible", "synthetic", "traceable", "transparent", 
            "vegan", "zero waste"
        ]),
        ("Combined_Spade_Results_1.xlsx", [
            "earned a treat", "NO.really", "s.a.l.e.", "expires", "celebrating", "psst", 
            "customer", "hello", "sale on sale", "leaving soon", "Rewarding", "surprise", 
            "elevate", "girl on the go", "hang", "you've bagged", "it's your final chance", 
            "treating you to code", "e_legance", "elegant", "hot", "vintage", "discount", 
            "attention", "you have", "glamorous", "kitsch", "lady", "splurge", "Official", 
            "we're releasing", "discover", "ob_sessed", "got to", "major bag alert", "Officially", 
            "releasing", "open immediately", "retro", "Win", "edgy", "all for you", 
            "you're getting", "order today", "utterly", "#win", "open asap", "now trending", 
            "confirm", "Announcement", "chic", "deal", "1-day", "yes", "all caps", 
            "Announcing", "officially in stock", "adorable", "(1-day special!)", "take", 
            "Lucky you", "Score", "cute", "fresh", "released", "explore", "presenting", 
            "all eyes on", "classy", "gorgeous", "markdown", "Checkout", "no joke", 
            "for you", "awesome", "hung", "Babe", "redeem", "Oooh", "get one", 
            "is sure to excite", "smile", "snack", "hey", "reserved", "make one yours", 
            "nice", "Knott", "as a thank you", "calling your name", "P_ssst", "Psst", 
            "view", "tons", "oh", "no", "earn", "just in", "flirty", "secure", 
            "hello gorgeous", "oof", "glow on", "just reduced", "sexy", "Deserve", 
            "hello", "gorgeous", "sale just dropped", "buy more", "save more", "unlock", 
            "name a more iconic", "Shop", "kind of time-sensitive", "we're confirming", 
            "offering", "treat", "duo", "Styles made to last", "must-have", "alert", 
            "compliments of us", "claim", "New you", "Enhance", "special message", 
            "you're receiving", "upgraded", "we're giving you", "One-day", "No exclusions", 
            "special feature", "just-reduced", "shipment", "hi there", "Snag", "Expires", 
            "girl", "sale confirmed", "wristlet", "Hey you", "Continue", "Leaving soon", 
            "because you rock", "you've secured", "all emojis", "Landed", "check out", 
            "It's your final chance", "the modern woman", "fashion-forward individual", "smart", 
            "PVC", "sophisticated", "modern wardrobe", "luxurious", "logo", 
            "logo embellishment", "Saffiano PVC", "the modern woman", "smart", 
            "sophisticated", "fashion-forward individual", "modern wardrobe", "sophistication", 
            "we", "casual day", "flair", "causal outings", "casual", 
            "brighter days", "metal material", "sophistication", "trust us", "day party", 
            "fashion-savvy individual", "elegance", "elegant", "modern fashion", "modern","precision edge painting"
        ])
    ]
    for infile, bl in files_and_blacklists:
        outfile = infile.replace(".xlsx", "_checked.xlsx")
        process_workbook(infile, bl, outfile)

import pandas as pd

df = pd.read_excel("Google_Analytics/Analytics_report.xlsx")

print(df.head())

# unique_keywords = df["Keyword"].drop_duplicates()

# print(df["Keyword"].unique().tolist())



########################################################

# import pandas as pd
# import numpy as np
# from collections import defaultdict
# import re
# from difflib import SequenceMatcher
# import matplotlib.pyplot as plt
# import warnings
# warnings.filterwarnings('ignore')

# class KeywordAnalyzer:
#     def __init__(self, csv_file_path):
#         """Initialize the analyzer with the CSV file path"""
#         self.df = pd.read_excel("Google_Analytics/Analytics_report.xlsx")
#         self.processed_df = None
#         self.category_mapping = {}
        
#     def clean_data(self):
#         """Clean and preprocess the data"""
#         # Remove any rows with missing keywords
#         self.df = self.df.dropna(subset=['Keyword'])
        
#         # Convert numeric columns
#         numeric_cols = ['Avg. monthly searches', 'Competition (indexed value)', 
#                        'Top of page bid (low range)', 'Top of page bid (high range)']
        
#         for col in numeric_cols:
#             if col in self.df.columns:
#                 self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
#         # Clean percentage columns
#         percentage_cols = ['Three month change', 'YoY change']
#         for col in percentage_cols:
#             if col in self.df.columns:
#                 self.df[col] = self.df[col].astype(str).str.replace('%', '').replace('', '0')
#                 self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
#         print(f"Data cleaned. Shape: {self.df.shape}")
        
#     def categorize_search_volume(self):
#         """Categorize keywords based on average monthly searches"""
#         def get_search_category(searches):
#             if pd.isna(searches):
#                 return 'Unknown'
#             elif searches > 50000:
#                 return 'High User Searched'
#             elif searches < 1000:
#                 return 'Least Frequently Visited'
#             else:
#                 return 'Moderate Visits'
        
#         self.df['Search_Volume_Category'] = self.df['Avg. monthly searches'].apply(get_search_category)
        
#     def extract_product_categories(self):
#         """Extract and categorize products from keywords - PRODUCT CATEGORIES ONLY"""
#         product_categories = {
#             'handbags_purses': ['bag', 'bags', 'handbag', 'handbags', 'purse', 'purses', 'tote', 'satchel', 'pocketbook', 'hand bag', 'pocketbooks'],
#             'wallets': ['wallet', 'wallets', 'billfold', 'card holder', 'zip wallet', 'long wallet', 'compact wallet', 'trifold wallet'],
#             'backpacks': ['backpack', 'backpacks', 'book bag', 'travel backpack', 'mini backpack', 'large backpack', 'leather backpack'],
#             'crossbody_bags': ['crossbody', 'cross body', 'crossbody bag', 'messenger bag', 'messenger', 'sling bag', 'chest bag', 'body bag', 'side bag'],
#             'shoes': ['shoes', 'sneakers', 'loafers', 'boots', 'slippers', 'dress shoes'],
#             'accessories': ['sunglasses', 'belt', 'keychain', 'scarf', 'hoodie']
#         }
        
#         def categorize_keyword(keyword):
#             keyword_lower = keyword.lower()
            
#             # Find the primary product category (only one category per keyword)
#             for category, terms in product_categories.items():
#                 if any(term in keyword_lower for term in terms):
#                     return category
            
#             # If no specific product found, check for general coach terms
#             if 'coach' in keyword_lower:
#                 return 'general_coach'
            
#             return 'other'
        
#         self.df['Product_Category'] = self.df['Keyword'].apply(categorize_keyword)
        
#     def group_similar_keywords(self, similarity_threshold=0.7):
#         """Group similar keywords together"""
#         keywords = self.df['Keyword'].tolist()
#         groups = []
#         used_indices = set()
        
#         for i, keyword1 in enumerate(keywords):
#             if i in used_indices:
#                 continue
                
#             group = [i]
#             used_indices.add(i)
            
#             for j, keyword2 in enumerate(keywords[i+1:], i+1):
#                 if j in used_indices:
#                     continue
                    
#                 # Calculate similarity
#                 similarity = SequenceMatcher(None, keyword1.lower(), keyword2.lower()).ratio()
                
#                 # Also check for common word overlap
#                 words1 = set(keyword1.lower().split())
#                 words2 = set(keyword2.lower().split())
#                 word_overlap = len(words1.intersection(words2)) / len(words1.union(words2))
                
#                 if similarity > similarity_threshold or word_overlap > 0.6:
#                     group.append(j)
#                     used_indices.add(j)
            
#             groups.append(group)
        
#         # Create group mapping
#         group_mapping = {}
#         for group_id, indices in enumerate(groups):
#             # Find the keyword with highest search volume as representative
#             group_keywords = [keywords[i] for i in indices]
#             group_searches = [self.df.iloc[i]['Avg. monthly searches'] for i in indices]
#             representative_idx = group_searches.index(max(group_searches))
#             representative = group_keywords[representative_idx]
            
#             for idx in indices:
#                 group_mapping[keywords[idx]] = {
#                     'group_id': group_id,
#                     'representative': representative,
#                     'group_size': len(indices),
#                     'total_searches': sum(group_searches)
#                 }
        
#         self.df['Keyword_Group'] = self.df['Keyword'].map(lambda x: group_mapping[x]['representative'])
#         self.df['Group_Size'] = self.df['Keyword'].map(lambda x: group_mapping[x]['group_size'])
#         self.df['Group_Total_Searches'] = self.df['Keyword'].map(lambda x: group_mapping[x]['total_searches'])
        
#         return group_mapping
    
#     def analyze_competition_vs_searches(self):
#         """Analyze the relationship between competition and search volume"""
#         if 'Competition (indexed value)' in self.df.columns:
#             self.df['Competition_Category'] = pd.cut(
#                 self.df['Competition (indexed value)'], 
#                 bins=[0, 33, 66, 100], 
#                 labels=['Low', 'Medium', 'High']
#             )
    
#     def calculate_opportunity_score(self):
#         """Calculate opportunity score based on search volume, competition, and bid prices"""
#         # Normalize metrics (0-1 scale)
#         max_searches = self.df['Avg. monthly searches'].max()
#         self.df['normalized_searches'] = self.df['Avg. monthly searches'] / max_searches
        
#         if 'Competition (indexed value)' in self.df.columns:
#             self.df['normalized_competition'] = self.df['Competition (indexed value)'] / 100
#         else:
#             self.df['normalized_competition'] = 0.5  # Default medium competition
        
#         # Calculate opportunity score (high searches, low competition = high opportunity)
#         self.df['Opportunity_Score'] = (
#             self.df['normalized_searches'] * 0.6 - 
#             self.df['normalized_competition'] * 0.4
#         ) * 100
        
#         # Categorize opportunities
#         self.df['Opportunity_Category'] = pd.cut(
#             self.df['Opportunity_Score'],
#             bins=[-100, 20, 50, 100],
#             labels=['Low Opportunity', 'Medium Opportunity', 'High Opportunity']
#         )
    
#     def generate_final_category_summary(self):
#         """Generate final summary with only product categories, competition, and search levels"""
        
#         # Group by product category
#         category_summary = {}
        
#         for category in self.df['Product_Category'].unique():
#             if category in ['other']:  # Skip non-product categories
#                 continue
                
#             category_df = self.df[self.df['Product_Category'] == category]
            
#             # Calculate metrics
#             total_searches = category_df['Avg. monthly searches'].sum()
#             avg_searches = category_df['Avg. monthly searches'].mean()
#             keyword_count = len(category_df)
            
#             # Determine search level
#             if avg_searches > 50000:
#                 search_level = 'High'
#             elif avg_searches < 1000:
#                 search_level = 'Low'
#             else:
#                 search_level = 'Moderate'
            
#             # Determine competition level
#             if 'Competition (indexed value)' in self.df.columns:
#                 avg_competition = category_df['Competition (indexed value)'].mean()
#                 if avg_competition > 70:
#                     competition_level = 'High'
#                 elif avg_competition < 30:
#                     competition_level = 'Low'
#                 else:
#                     competition_level = 'Moderate'
#             else:
#                 # Fallback based on Competition column
#                 competition_counts = category_df['Competition'].value_counts()
#                 if len(competition_counts) > 0 and competition_counts.index[0] == 'High':
#                     competition_level = 'High'
#                 elif len(competition_counts) > 0 and competition_counts.index[0] == 'Low':
#                     competition_level = 'Low'
#                 else:
#                     competition_level = 'Moderate'
            
#             # Get top performing keyword in category
#             top_keyword = category_df.loc[category_df['Avg. monthly searches'].idxmax(), 'Keyword']
#             top_keyword_searches = category_df['Avg. monthly searches'].max()
            
#             category_summary[category] = {
#                 'search_level': search_level,
#                 'competition_level': competition_level,
#                 'total_searches': int(total_searches),
#                 'avg_searches': int(avg_searches),
#                 'keyword_count': keyword_count,
#                 'top_keyword': top_keyword,
#                 'top_keyword_searches': int(top_keyword_searches)
#             }
        
#         return category_summary
    
#     def generate_tagline_recommendations(self, insights):
#         """Generate tagline and editor note recommendations based on insights"""
#         recommendations = []
        
#         # Based on most popular product categories
#         product_summary = insights['product_category_summary']
#         top_categories = sorted(product_summary.items(), key=lambda x: x[1]['total_searches'], reverse=True)[:3]
        
#         for category, data in top_categories:
#             if category == 'bags':
#                 recommendations.append({
#                     'tagline': "Your Perfect Coach Bag Awaits - From Handbags to Totes",
#                     'editor_note': f"Focus on bag variety - {data['total_keywords']} different bag-related searches with {data['total_searches']:,} monthly searches",
#                     'category': category
#                 })
#             elif category == 'outlet_sales':
#                 recommendations.append({
#                     'tagline': "Unbeatable Coach Deals - Outlet Prices, Authentic Quality",
#                     'editor_note': f"Price-conscious shoppers dominate - {data['total_keywords']} sale-related terms with {data['total_searches']:,} searches",
#                     'category': category
#                 })
#             elif category == 'crossbody':
#                 recommendations.append({
#                     'tagline': "Stay Hands-Free with Stylish Coach Crossbody Collections",
#                     'editor_note': f"Crossbody trend is strong - {data['total_keywords']} variants with high engagement",
#                     'category': category
#                 })
        
#         # Based on search volume categories
#         volume_dist = insights['search_volume_distribution']
#         if volume_dist.get('High User Searched', 0) > volume_dist.get('Moderate Visits', 0):
#             recommendations.append({
#                 'tagline': "Join Millions Who Choose Coach - Premium Quality, Timeless Style",
#                 'editor_note': "High search volume indicates strong brand demand - emphasize popularity and trust",
#                 'category': 'brand_strength'
#             })
        
#         # Based on opportunity analysis
#         if insights.get('high_opportunity_keywords'):
#             top_opportunity = insights['high_opportunity_keywords'][0]
#             recommendations.append({
#                 'tagline': f"Discover Hidden Gems Like {top_opportunity['Keyword']} - Less Competition, More Style",
#                 'editor_note': f"Target underutilized high-potential keywords for better ROI",
#                 'category': 'opportunity'
#             })
        
#         return recommendations
    
#     def process_all(self):
#         """Run the complete analysis pipeline"""
#         print("Starting product-focused keyword analysis...")
        
#         # Step 1: Clean data
#         self.clean_data()
        
#         # Step 2: Categorize search volumes
#         self.categorize_search_volume()
#         print("✓ Search volume categorization completed")
        
#         # Step 3: Extract product categories
#         self.extract_product_categories()
#         print("✓ Product categorization completed")
        
#         # Step 4: Analyze competition
#         self.analyze_competition_vs_searches()
#         print("✓ Competition analysis completed")
        
#         # Step 5: Calculate opportunity scores
#         self.calculate_opportunity_score()
#         print("✓ Opportunity scoring completed")
        
#         # Step 6: Generate final category summary
#         category_summary = self.generate_final_category_summary()
#         print("✓ Final category summary generated")
        
#         self.processed_df = self.df.copy()
        
#         return category_summary
    
#     def create_visualizations(self):
#         """Create visualizations for better understanding"""
#         plt.style.use('seaborn-v0_8')
#         fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
#         # 1. Search Volume Distribution
#         volume_counts = self.df['Search_Volume_Category'].value_counts()
#         axes[0,0].pie(volume_counts.values, labels=volume_counts.index, autopct='%1.1f%%')
#         axes[0,0].set_title('Search Volume Distribution')
        
#         # 2. Top 15 Keywords by Search Volume
#         top_keywords = self.df.nlargest(15, 'Avg. monthly searches')
#         axes[0,1].barh(range(len(top_keywords)), top_keywords['Avg. monthly searches'])
#         axes[0,1].set_yticks(range(len(top_keywords)))
#         axes[0,1].set_yticklabels(top_keywords['Keyword'], fontsize=8)
#         axes[0,1].set_title('Top 15 Keywords by Search Volume')
#         axes[0,1].set_xlabel('Average Monthly Searches')
        
#         # 3. Opportunity Score Distribution
#         axes[1,0].hist(self.df['Opportunity_Score'].dropna(), bins=20, alpha=0.7)
#         axes[1,0].set_title('Opportunity Score Distribution')
#         axes[1,0].set_xlabel('Opportunity Score')
#         axes[1,0].set_ylabel('Frequency')
        
#         # 4. Competition vs Search Volume Scatter
#         if 'Competition (indexed value)' in self.df.columns:
#             scatter = axes[1,1].scatter(
#                 self.df['Competition (indexed value)'], 
#                 self.df['Avg. monthly searches'],
#                 alpha=0.6,
#                 c=self.df['Opportunity_Score'],
#                 cmap='viridis'
#             )
#             axes[1,1].set_xlabel('Competition Index')
#             axes[1,1].set_ylabel('Average Monthly Searches')
#             axes[1,1].set_title('Competition vs Search Volume')
#             plt.colorbar(scatter, ax=axes[1,1], label='Opportunity Score')
        
#         plt.tight_layout()
#         plt.show()
    
#     def export_results(self, filename='processed_keywords.csv'):
#         """Export processed data to CSV"""
#         if self.processed_df is not None:
#             self.processed_df.to_csv(filename, index=False)
#             print(f"Results exported to {filename}")
#         else:
#             print("No processed data to export. Run process_all() first.")

# # Usage Example
# def main():
#     # Initialize analyzer
#     analyzer = KeywordAnalyzer('your_file.csv')  # Replace with your CSV file path
    
#     # Process all data
#     category_summary = analyzer.process_all()
    
#     # Display final results in clean format
#     print("\n" + "="*80)
#     print("FINAL PRODUCT CATEGORY ANALYSIS")
#     print("="*80)
#     print(f"{'PRODUCT CATEGORY':<20} {'SEARCH LEVEL':<15} {'COMPETITION':<15} {'KEYWORDS':<10} {'TOP PERFORMER'}")
#     print("-" * 80)
    
#     # Sort categories by total searches (descending)
#     sorted_categories = sorted(category_summary.items(), 
#                              key=lambda x: x[1]['total_searches'], reverse=True)
    
#     for category, data in sorted_categories:
#         category_name = category.replace('_', ' ').title()
#         print(f"{category_name:<20} {data['search_level']:<15} {data['competition_level']:<15} {data['keyword_count']:<10} {data['top_keyword'][:30]}")
    
#     print("\n" + "="*80)
#     print("DETAILED BREAKDOWN")
#     print("="*80)
    
#     for category, data in sorted_categories:
#         category_name = category.replace('_', ' ').title()
#         print(f"\n📂 {category_name.upper()}")
#         print(f"   Search Level: {data['search_level']}")
#         print(f"   Competition: {data['competition_level']}")  
#         print(f"   Total Monthly Searches: {data['total_searches']:,}")
#         print(f"   Average Monthly Searches: {data['avg_searches']:,}")
#         print(f"   Number of Keywords: {data['keyword_count']}")
#         print(f"   Top Performing Keyword: '{data['top_keyword']}' ({data['top_keyword_searches']:,} searches)")
    
#     # Export results
#     analyzer.export_results('final_categorized_keywords.csv')
    
#     # Create a summary DataFrame and export it
#     summary_df = pd.DataFrame(category_summary).T
#     summary_df.index.name = 'Product_Category'
#     summary_df.to_csv('category_summary.csv')
#     print(f"\n✓ Summary exported to 'category_summary.csv'")
    
#     return analyzer, category_summary

# if __name__ == "__main__":
#     # Run the analysis
#     analyzer, category_summary = main()
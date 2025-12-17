"""
Comprehensive Data Distribution Analysis
Analyze the 5000 IMDB movies dataset before model training
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

print("="*80)
print("DATA DISTRIBUTION ANALYSIS")
print("="*80)

# Load dataset
print("\n📊 Loading dataset...")
df = pd.read_csv('data/raw/imdb_movies_large.csv')
print(f"✓ Loaded {len(df):,} movies with {len(df.columns)} features")

# Basic info
print("\n" + "="*80)
print("1. DATASET OVERVIEW")
print("="*80)
print(f"\nShape: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print(f"\nDate range: {df['release_date'].min()} to {df['release_date'].max()}")

# Missing values
print("\n" + "-"*80)
print("Missing Values:")
print("-"*80)
missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100
missing_df = pd.DataFrame({
    'Missing Count': missing[missing > 0],
    'Percentage': missing_pct[missing > 0]
})
if len(missing_df) > 0:
    print(missing_df.sort_values('Percentage', ascending=False))
else:
    print("✓ No missing values!")

# Data types
print("\n" + "-"*80)
print("Data Types:")
print("-"*80)
print(df.dtypes.value_counts())

# Numerical features statistics
print("\n" + "="*80)
print("2. NUMERICAL FEATURES STATISTICS")
print("="*80)

numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print(f"\nTotal numerical features: {len(numerical_cols)}")

# Key financial metrics
financial_metrics = ['budget', 'revenue', 'first_week', 'opening_weekend', 'total_gross']
print("\n" + "-"*80)
print("Financial Metrics (in millions $):")
print("-"*80)
for col in financial_metrics:
    if col in df.columns:
        print(f"\n{col.upper()}:")
        print(f"  Mean:   ${df[col].mean()/1e6:>10.2f}M")
        print(f"  Median: ${df[col].median()/1e6:>10.2f}M")
        print(f"  Std:    ${df[col].std()/1e6:>10.2f}M")
        print(f"  Min:    ${df[col].min()/1e6:>10.2f}M")
        print(f"  Max:    ${df[col].max()/1e6:>10.2f}M")
        print(f"  Q1:     ${df[col].quantile(0.25)/1e6:>10.2f}M")
        print(f"  Q3:     ${df[col].quantile(0.75)/1e6:>10.2f}M")

# Rating metrics
print("\n" + "-"*80)
print("Rating Metrics:")
print("-"*80)
rating_cols = ['imdb_rating', 'imdb_votes', 'metascore', 'popularity']
for col in rating_cols:
    if col in df.columns:
        print(f"\n{col.upper()}:")
        print(f"  Mean:   {df[col].mean():>10.2f}")
        print(f"  Median: {df[col].median():>10.2f}")
        print(f"  Std:    {df[col].std():>10.2f}")
        print(f"  Min:    {df[col].min():>10.2f}")
        print(f"  Max:    {df[col].max():>10.2f}")

# Social media metrics
print("\n" + "-"*80)
print("Social Media Metrics (T-7 Data):")
print("-"*80)
social_cols = ['twitter_mentions', 'youtube_trailer_views', 'instagram_hashtag_count', 
               'facebook_page_likes', 'ticket_presales']
for col in social_cols:
    if col in df.columns:
        print(f"\n{col}:")
        print(f"  Mean:   {df[col].mean():>15,.0f}")
        print(f"  Median: {df[col].median():>15,.0f}")
        print(f"  Max:    {df[col].max():>15,.0f}")

# Categorical features
print("\n" + "="*80)
print("3. CATEGORICAL FEATURES")
print("="*80)

# Genres
if 'genre' in df.columns:
    print("\n" + "-"*80)
    print("Top 20 Most Common Genres:")
    print("-"*80)
    genre_counts = df['genre'].value_counts().head(20)
    for genre, count in genre_counts.items():
        pct = (count / len(df)) * 100
        print(f"  {genre:<40} {count:>5} ({pct:>5.2f}%)")

# Directors
if 'director' in df.columns:
    print("\n" + "-"*80)
    print("Top 20 Most Prolific Directors:")
    print("-"*80)
    director_counts = df['director'].value_counts().head(20)
    for director, count in director_counts.items():
        print(f"  {director:<40} {count:>3} movies")

# Temporal analysis
print("\n" + "="*80)
print("4. TEMPORAL DISTRIBUTION")
print("="*80)

# Extract year
df['year'] = pd.to_datetime(df['release_date']).dt.year

print("\n" + "-"*80)
print("Movies per Year:")
print("-"*80)
year_counts = df['year'].value_counts().sort_index()
for year in range(1990, 2025, 5):
    if year in year_counts.index:
        print(f"  {year}: {year_counts[year]:>4} movies")

print("\n" + "-"*80)
print("Movies by Release Month:")
print("-"*80)
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
if 'release_month' in df.columns:
    month_counts = df['release_month'].value_counts().sort_index()
    for month in range(1, 13):
        if month in month_counts.index:
            print(f"  {month_names[month-1]}: {month_counts[month]:>4} movies")

# Season distribution
if 'is_summer' in df.columns and 'is_holiday_season' in df.columns:
    print("\n" + "-"*80)
    print("Seasonal Distribution:")
    print("-"*80)
    print(f"  Summer releases: {df['is_summer'].sum()} ({df['is_summer'].mean()*100:.1f}%)")
    print(f"  Holiday season:  {df['is_holiday_season'].sum()} ({df['is_holiday_season'].mean()*100:.1f}%)")

# Franchise analysis
if 'is_sequel' in df.columns:
    print("\n" + "-"*80)
    print("Franchise Analysis:")
    print("-"*80)
    print(f"  Sequels: {df['is_sequel'].sum()} ({df['is_sequel'].mean()*100:.1f}%)")
    print(f"  Original: {(~df['is_sequel'].astype(bool)).sum()} ({(~df['is_sequel'].astype(bool)).mean()*100:.1f}%)")

# Correlation analysis
print("\n" + "="*80)
print("5. CORRELATION WITH TARGET (first_week)")
print("="*80)

# Calculate correlations with target
target_correlations = df[numerical_cols].corrwith(df['first_week']).sort_values(ascending=False)
print("\n" + "-"*80)
print("Top 20 Features Correlated with First Week Income:")
print("-"*80)
for feature, corr in target_correlations.head(20).items():
    print(f"  {feature:<40} {corr:>7.4f}")

print("\n" + "-"*80)
print("Bottom 10 Features (Least Correlated):")
print("-"*80)
for feature, corr in target_correlations.tail(10).items():
    print(f"  {feature:<40} {corr:>7.4f}")

# Distribution analysis
print("\n" + "="*80)
print("6. DISTRIBUTION ANALYSIS")
print("="*80)

key_features = ['budget', 'revenue', 'first_week', 'imdb_rating', 'imdb_votes']
print("\n" + "-"*80)
print("Skewness and Kurtosis:")
print("-"*80)
print(f"{'Feature':<25} {'Skewness':>12} {'Kurtosis':>12} {'Distribution'}")
print("-"*80)
for col in key_features:
    if col in df.columns and df[col].std() > 0:
        skew = stats.skew(df[col].dropna())
        kurt = stats.kurtosis(df[col].dropna())
        
        # Interpret distribution
        if abs(skew) < 0.5:
            dist = "Normal"
        elif skew > 0:
            dist = "Right-skewed"
        else:
            dist = "Left-skewed"
        
        print(f"{col:<25} {skew:>12.4f} {kurt:>12.4f} {dist}")

# Outlier detection
print("\n" + "="*80)
print("7. OUTLIER DETECTION (IQR Method)")
print("="*80)

outlier_features = ['budget', 'revenue', 'first_week', 'opening_weekend', 'imdb_votes']
print("\n" + "-"*80)
print(f"{'Feature':<25} {'Outliers':>10} {'Percentage':>12}")
print("-"*80)
for col in outlier_features:
    if col in df.columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
        pct = (outliers / len(df)) * 100
        print(f"{col:<25} {outliers:>10} {pct:>11.2f}%")

# Feature ranges
print("\n" + "="*80)
print("8. FEATURE RANGES (for scaling)")
print("="*80)
print("\n" + "-"*80)
print(f"{'Feature':<30} {'Min':>15} {'Max':>15} {'Range':>15}")
print("-"*80)
important_features = ['budget', 'revenue', 'first_week', 'imdb_rating', 'imdb_votes', 
                      'runtime', 'num_theaters', 'twitter_mentions', 'popularity']
for col in important_features:
    if col in df.columns:
        min_val = df[col].min()
        max_val = df[col].max()
        range_val = max_val - min_val
        print(f"{col:<30} {min_val:>15,.0f} {max_val:>15,.0f} {range_val:>15,.0f}")

# Target variable analysis
print("\n" + "="*80)
print("9. TARGET VARIABLE (first_week) DETAILED ANALYSIS")
print("="*80)

target = 'first_week'
print(f"\n{'Statistic':<30} {'Value'}")
print("-"*80)
print(f"{'Count':<30} {df[target].count():>15,}")
print(f"{'Mean':<30} ${df[target].mean():>14,.2f}")
print(f"{'Median':<30} ${df[target].median():>14,.2f}")
print(f"{'Std Dev':<30} ${df[target].std():>14,.2f}")
print(f"{'Min':<30} ${df[target].min():>14,.2f}")
print(f"{'25th Percentile':<30} ${df[target].quantile(0.25):>14,.2f}")
print(f"{'50th Percentile':<30} ${df[target].quantile(0.50):>14,.2f}")
print(f"{'75th Percentile':<30} ${df[target].quantile(0.75):>14,.2f}")
print(f"{'90th Percentile':<30} ${df[target].quantile(0.90):>14,.2f}")
print(f"{'95th Percentile':<30} ${df[target].quantile(0.95):>14,.2f}")
print(f"{'99th Percentile':<30} ${df[target].quantile(0.99):>14,.2f}")
print(f"{'Max':<30} ${df[target].max():>14,.2f}")
print(f"{'Coefficient of Variation':<30} {(df[target].std() / df[target].mean()) * 100:>14.2f}%")

# Recommendations
print("\n" + "="*80)
print("10. DATA QUALITY RECOMMENDATIONS")
print("="*80)

recommendations = []

# Check skewness
for col in ['budget', 'revenue', 'first_week']:
    if col in df.columns:
        skew = stats.skew(df[col].dropna())
        if abs(skew) > 1:
            recommendations.append(f"⚠️  {col} is highly skewed ({skew:.2f}). Consider log transformation.")

# Check outliers
for col in outlier_features:
    if col in df.columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
        pct = (outliers / len(df)) * 100
        if pct > 5:
            recommendations.append(f"⚠️  {col} has {pct:.1f}% outliers. Consider outlier treatment.")

# Check scale differences
ranges = {}
for col in important_features:
    if col in df.columns:
        ranges[col] = df[col].max() - df[col].min()
if len(ranges) > 0:
    max_range = max(ranges.values())
    min_range = min([r for r in ranges.values() if r > 0])
    if max_range / min_range > 1000:
        recommendations.append("⚠️  Features have very different scales. Use StandardScaler or RobustScaler.")

# Check correlation
high_corr = target_correlations[target_correlations > 0.9]
if len(high_corr) > 2:  # More than just target and highly related features
    recommendations.append(f"⚠️  {len(high_corr)-1} features highly correlated with target. Check for data leakage.")

# Print recommendations
if recommendations:
    print("\n📋 Recommendations for Model Training:\n")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
else:
    print("\n✅ Data quality looks good! Ready for model training.")

# Additional insights
print("\n" + "="*80)
print("11. KEY INSIGHTS")
print("="*80)

insights = []

# Budget vs Revenue insight
if 'budget' in df.columns and 'revenue' in df.columns:
    roi = (df['revenue'] / df['budget']).median()
    insights.append(f"💰 Median ROI: {roi:.2f}x (revenue/budget)")

# Rating insight
if 'imdb_rating' in df.columns:
    high_rated = (df['imdb_rating'] >= 8.0).sum()
    insights.append(f"⭐ {high_rated} movies ({high_rated/len(df)*100:.1f}%) rated 8.0+")

# Vote insight
if 'imdb_votes' in df.columns:
    popular = (df['imdb_votes'] >= 500000).sum()
    insights.append(f"🎬 {popular} movies ({popular/len(df)*100:.1f}%) have 500K+ votes")

# Sequel insight
if 'is_sequel' in df.columns:
    sequel_avg = df[df['is_sequel'] == 1]['first_week'].mean() if df['is_sequel'].sum() > 0 else 0
    original_avg = df[df['is_sequel'] == 0]['first_week'].mean()
    if sequel_avg > original_avg:
        insights.append(f"🎭 Sequels perform {sequel_avg/original_avg:.1f}x better in first week")
    else:
        insights.append(f"🎭 Original films perform {original_avg/sequel_avg:.1f}x better in first week")

# Seasonal insight
if 'is_summer' in df.columns:
    summer_avg = df[df['is_summer'] == 1]['first_week'].mean()
    non_summer_avg = df[df['is_summer'] == 0]['first_week'].mean()
    if summer_avg > non_summer_avg:
        insights.append(f"☀️  Summer releases earn {summer_avg/non_summer_avg:.1f}x more in first week")

print()
for insight in insights:
    print(f"  {insight}")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE!")
print("="*80)
print(f"\nDataset: data/raw/imdb_movies_large.csv")
print(f"Movies: {len(df):,}")
print(f"Features: {len(df.columns)}")
print(f"Target: first_week (${df['first_week'].mean():,.0f} average)")
print("\n💡 Data is ready for model training!")
print("="*80)

"""
Results Analysis Script для BestTime Pilot Test
================================================

Этот скрипт анализирует результаты pilot test и создает визуализации.

Использование:
python analyze_besttime_results.py

Требует:
- besttime_results.csv (созданный besttime_pilot_test.py)
- matplotlib, seaborn, pandas
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import sys
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10


def load_results(filepath='besttime_results.csv'):
    """Load test results"""
    try:
        df = pd.read_csv(filepath)
        return df
    except FileNotFoundError:
        print(f"❌ Error: {filepath} not found!")
        print("Please run besttime_pilot_test.py first.")
        sys.exit(1)


def calculate_statistics(df):
    """Calculate key statistics"""
    stats = {}
    
    # Overall coverage
    stats['total_homes'] = len(df)
    stats['homes_with_data'] = df['data_available'].sum()
    stats['coverage_rate'] = (stats['homes_with_data'] / stats['total_homes']) * 100
    
    # Coverage by location type
    if 'location_type' in df.columns:
        stats['coverage_by_location'] = df.groupby('location_type')['data_available'].mean() * 100
    
    # Coverage by CQC rating
    stats['coverage_by_cqc'] = df.groupby('cqc_rating')['data_available'].mean() * 100
    
    # Activity scores
    df_with_data = df[df['data_available'] == True]
    if len(df_with_data) > 0 and 'activity_score' in df_with_data.columns:
        stats['mean_activity'] = df_with_data['activity_score'].mean()
        stats['median_activity'] = df_with_data['activity_score'].median()
        stats['std_activity'] = df_with_data['activity_score'].std()
        
        # By CQC rating
        stats['activity_by_cqc'] = df_with_data.groupby('cqc_rating')['activity_score'].mean()
        
        # Correlation
        cqc_map = {
            'Outstanding': 4,
            'Good': 3,
            'Requires Improvement': 2,
            'Inadequate': 1
        }
        df_with_data['cqc_numeric'] = df_with_data['cqc_rating'].map(cqc_map)
        if df_with_data['activity_score'].notna().sum() > 2:
            stats['correlation'] = df_with_data[['cqc_numeric', 'activity_score']].corr().iloc[0, 1]
        else:
            stats['correlation'] = None
    
    return stats


def print_detailed_report(df, stats):
    """Print comprehensive analysis report"""
    
    print("\n" + "="*80)
    print("📊 BESTTIME.APP PILOT TEST - DETAILED ANALYSIS REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # Section 1: Executive Summary
    print("🎯 EXECUTIVE SUMMARY")
    print("-" * 80)
    print(f"Total Care Homes Tested:     {stats['total_homes']}")
    print(f"Homes with BestTime Data:    {stats['homes_with_data']}")
    print(f"Overall Coverage Rate:       {stats['coverage_rate']:.1f}%\n")
    
    # Coverage assessment
    if stats['coverage_rate'] >= 70:
        recommendation = "✅ PROCEED - Excellent coverage"
        color = "🟢"
    elif stats['coverage_rate'] >= 50:
        recommendation = "⚠️  CONDITIONAL PROCEED - Moderate coverage"
        color = "🟡"
    elif stats['coverage_rate'] >= 30:
        recommendation = "⚠️  CAUTION - Low coverage"
        color = "🟠"
    else:
        recommendation = "❌ DO NOT PROCEED - Very low coverage"
        color = "🔴"
    
    print(f"Recommendation: {recommendation}")
    print(f"Coverage Rating: {color}\n")
    
    # Section 2: Coverage Breakdown
    print("📈 COVERAGE BREAKDOWN")
    print("-" * 80)
    
    # By location type
    if 'coverage_by_location' in stats:
        print("\nBy Location Type:")
        for loc_type, coverage in stats['coverage_by_location'].items():
            emoji = "🟢" if coverage >= 70 else "🟡" if coverage >= 50 else "🔴"
            print(f"  {emoji} {loc_type.capitalize():15s}: {coverage:5.1f}%")
    
    # By CQC rating
    print("\nBy CQC Rating:")
    cqc_order = ['Outstanding', 'Good', 'Requires Improvement', 'Inadequate']
    for rating in cqc_order:
        if rating in stats['coverage_by_cqc'].index:
            coverage = stats['coverage_by_cqc'][rating]
            emoji = "🟢" if coverage >= 70 else "🟡" if coverage >= 50 else "🔴"
            print(f"  {emoji} {rating:25s}: {coverage:5.1f}%")
    
    # By home size
    if 'beds' in df.columns and df['beds'].notna().any():
        print("\nBy Home Size:")
        df['size_category'] = pd.cut(
            df['beds'], 
            bins=[0, 30, 60, 100], 
            labels=['Small (<30)', 'Medium (30-60)', 'Large (60+)']
        )
        size_coverage = df.groupby('size_category')['data_available'].mean() * 100
        for size, coverage in size_coverage.items():
            emoji = "🟢" if coverage >= 70 else "🟡" if coverage >= 50 else "🔴"
            print(f"  {emoji} {size:15s}: {coverage:5.1f}%")
    
    print()
    
    # Section 3: Activity Analysis (for homes with data)
    df_with_data = df[df['data_available'] == True]
    
    if len(df_with_data) > 0 and 'activity_score' in df_with_data.columns:
        print("📊 ACTIVITY SCORE ANALYSIS")
        print("-" * 80)
        print(f"Homes analyzed: {len(df_with_data)}\n")
        
        print("Score Distribution:")
        print(f"  Mean:   {stats['mean_activity']:.1f}/100")
        print(f"  Median: {stats['median_activity']:.1f}/100")
        print(f"  Std:    {stats['std_activity']:.1f}")
        print(f"  Min:    {df_with_data['activity_score'].min():.1f}/100")
        print(f"  Max:    {df_with_data['activity_score'].max():.1f}/100\n")
        
        # Score categories
        high_score = (df_with_data['activity_score'] >= 70).sum()
        medium_score = ((df_with_data['activity_score'] >= 50) & 
                       (df_with_data['activity_score'] < 70)).sum()
        low_score = (df_with_data['activity_score'] < 50).sum()
        
        print("Score Categories:")
        print(f"  🟢 High (≥70):   {high_score:3d} homes ({high_score/len(df_with_data)*100:.1f}%)")
        print(f"  🟡 Medium (50-69): {medium_score:3d} homes ({medium_score/len(df_with_data)*100:.1f}%)")
        print(f"  🔴 Low (<50):    {low_score:3d} homes ({low_score/len(df_with_data)*100:.1f}%)\n")
        
        # Average by CQC rating
        print("Average Activity Score by CQC Rating:")
        for rating in cqc_order:
            if rating in stats['activity_by_cqc'].index:
                score = stats['activity_by_cqc'][rating]
                emoji = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                print(f"  {emoji} {rating:25s}: {score:5.1f}/100")
        
        # Correlation with CQC
        if stats.get('correlation') is not None:
            corr = stats['correlation']
            print(f"\nCorrelation (Activity Score vs CQC Rating): {corr:.3f}")
            
            if abs(corr) >= 0.5:
                corr_strength = "🟢 STRONG"
            elif abs(corr) >= 0.3:
                corr_strength = "🟡 MODERATE"
            else:
                corr_strength = "🔴 WEAK"
            
            print(f"Correlation Strength: {corr_strength}")
            
            if corr > 0.3:
                print("✅ Good correlation validates using activity as quality proxy")
            else:
                print("⚠️  Weak correlation - activity may not predict quality well")
        
        print()
    
    # Section 4: Pattern Analysis
    if 'weekend_activity' in df.columns or 'evening_visits' in df.columns:
        print("🔍 PATTERN ANALYSIS")
        print("-" * 80)
        
        if 'weekend_activity' in df.columns:
            weekend_homes = df['weekend_activity'].sum()
            weekend_pct = (weekend_homes / stats['homes_with_data']) * 100 if stats['homes_with_data'] > 0 else 0
            print(f"Weekend Activity Detected:  {weekend_homes:3d} homes ({weekend_pct:.1f}%)")
        
        if 'evening_visits' in df.columns:
            evening_homes = df['evening_visits'].sum()
            evening_pct = (evening_homes / stats['homes_with_data']) * 100 if stats['homes_with_data'] > 0 else 0
            print(f"Evening Visits Detected:    {evening_homes:3d} homes ({evening_pct:.1f}%)")
        
        print()
    
    # Section 5: Red Flags
    df_with_flags = df[df['red_flags'].notna() & (df['red_flags'] != '')]
    
    if len(df_with_flags) > 0:
        print("⚠️  RED FLAGS DETECTED")
        print("-" * 80)
        print(f"Homes with red flags: {len(df_with_flags)} ({len(df_with_flags)/len(df)*100:.1f}%)\n")
        
        all_flags = []
        for flags_str in df_with_flags['red_flags']:
            all_flags.extend(str(flags_str).split('; '))
        
        from collections import Counter
        flag_counts = Counter(all_flags)
        
        print("Most Common Issues:")
        for flag, count in flag_counts.most_common(10):
            print(f"  • {flag:40s}: {count:2d} homes")
        
        print()
    
    # Section 6: Data Quality Issues
    df_with_warnings = df[df['warnings'].notna() & (df['warnings'] != '')]
    
    if len(df_with_warnings) > 0:
        print("⚠️  DATA QUALITY WARNINGS")
        print("-" * 80)
        print(f"Homes with warnings: {len(df_with_warnings)}\n")
        
        all_warnings = []
        for warnings_str in df_with_warnings['warnings']:
            all_warnings.extend(str(warnings_str).split('; '))
        
        from collections import Counter
        warning_counts = Counter(all_warnings)
        
        print("Common Data Issues:")
        for warning, count in warning_counts.most_common(10):
            print(f"  • {warning:50s}: {count:2d} homes")
        
        print()
    
    # Section 7: Top & Bottom Performers
    if len(df_with_data) > 0 and 'activity_score' in df_with_data.columns:
        print("🏆 TOP PERFORMERS")
        print("-" * 80)
        
        top_5 = df_with_data.nlargest(5, 'activity_score')[['name', 'cqc_rating', 'activity_score', 'city']]
        for idx, (_, row) in enumerate(top_5.iterrows(), 1):
            print(f"{idx}. {row['name']:35s} | {row['cqc_rating']:20s} | Score: {row['activity_score']:.1f} | {row['city']}")
        
        print("\n🔻 BOTTOM PERFORMERS")
        print("-" * 80)
        
        bottom_5 = df_with_data.nsmallest(5, 'activity_score')[['name', 'cqc_rating', 'activity_score', 'city']]
        for idx, (_, row) in enumerate(bottom_5.iterrows(), 1):
            print(f"{idx}. {row['name']:35s} | {row['cqc_rating']:20s} | Score: {row['activity_score']:.1f} | {row['city']}")
        
        print()
    
    # Section 8: Cost Analysis
    print("💰 COST ANALYSIS")
    print("-" * 80)
    
    # BestTime costs
    homes_tested = stats['total_homes']
    credits_used = homes_tested * 2  # 2 credits per forecast
    cost_per_credit = 0.008  # USD
    
    test_cost_usd = credits_used * cost_per_credit
    test_cost_gbp = test_cost_usd * 0.79
    
    print(f"Pilot Test:")
    print(f"  Homes tested:      {homes_tested}")
    print(f"  Credits used:      {credits_used}")
    print(f"  Cost:              ${test_cost_usd:.2f} (£{test_cost_gbp:.2f})\n")
    
    # Scale to full deployment
    full_scale = 2500
    annual_credits = full_scale * 2 * 13  # Initial + 12 monthly refreshes
    annual_cost_usd = annual_credits * cost_per_credit
    annual_cost_gbp = annual_cost_usd * 0.79
    
    print(f"Full Deployment (2,500 homes):")
    print(f"  Initial forecast:  ${full_scale * 2 * cost_per_credit:.2f} (£{full_scale * 2 * cost_per_credit * 0.79:.2f})")
    print(f"  Annual refreshes:  ${annual_cost_usd:.2f} (£{annual_cost_gbp:.2f})")
    print(f"  Cost per home/year: ${annual_cost_usd/full_scale:.2f} (£{annual_cost_gbp/full_scale:.2f})\n")
    
    # Section 9: Final Recommendation
    print("="*80)
    print("🎯 FINAL RECOMMENDATION")
    print("="*80 + "\n")
    
    if stats['coverage_rate'] >= 70:
        print("✅ RECOMMENDATION: PROCEED WITH BESTTIME.APP\n")
        print("Rationale:")
        print(f"  • Coverage rate of {stats['coverage_rate']:.1f}% is excellent")
        print(f"  • Sufficient data for {stats['homes_with_data']} homes")
        print(f"  • Annual cost of £{annual_cost_gbp:.0f} is cost-effective")
        print("\nNext Steps:")
        print("  1. Scale test to 100-200 homes")
        print("  2. Manual validation of top 5-10 homes")
        print("  3. Integrate into production pipeline")
        print("  4. Set up monthly refresh automation")
        
    elif stats['coverage_rate'] >= 50:
        print("⚠️  RECOMMENDATION: CONDITIONAL PROCEED\n")
        print("Rationale:")
        print(f"  • Coverage rate of {stats['coverage_rate']:.1f}% is moderate")
        print(f"  • Works for {stats['homes_with_data']} homes, but gaps exist")
        print("\nRecommendations:")
        print("  • Use BestTime as SUPPLEMENTARY data, not primary")
        print("  • Combine with: Google Reviews, FSA inspections, CQC data")
        print("  • Focus on urban areas with better coverage")
        print("\nNext Steps:")
        print("  1. Analyze which types of homes have good coverage")
        print("  2. Test alternative providers (Huq)")
        print("  3. Develop proxy metrics for homes without data")
        
    elif stats['coverage_rate'] >= 30:
        print("⚠️  RECOMMENDATION: PROCEED WITH CAUTION\n")
        print("Rationale:")
        print(f"  • Coverage rate of {stats['coverage_rate']:.1f}% is low")
        print(f"  • Only {stats['homes_with_data']} homes have data")
        print("\nAlternatives to Consider:")
        print("  • Huq (UK-focused provider, £1,000/year)")
        print("  • Proxy metrics approach (free, requires more work):")
        print("    - Google Reviews velocity")
        print("    - Photo upload frequency")
        print("    - FSA inspection patterns")
        print("\nNext Steps:")
        print("  1. Test Huq with same dataset")
        print("  2. Develop robust proxy metrics system")
        print("  3. Consider manual data collection")
        
    else:
        print("❌ RECOMMENDATION: DO NOT PROCEED WITH BESTTIME.APP\n")
        print("Rationale:")
        print(f"  • Coverage rate of {stats['coverage_rate']:.1f}% is too low")
        print(f"  • Insufficient data for reliable analysis")
        print("\nAlternatives:")
        print("  1. TEST HUQ:")
        print("     - UK-specific provider")
        print("     - Better coverage for UK venues")
        print("     - Cost: ~£1,000/year")
        print("\n  2. PROXY METRICS APPROACH:")
        print("     - Google Reviews activity (free)")
        print("     - FSA inspection frequency (free)")
        print("     - Social media engagement (free)")
        print("\n  3. PARTNERSHIP:")
        print("     - Integrate with care home management software")
        print("     - Access their operational data")
        
    print("\n" + "="*80)
    print("Report complete. See visualizations in besttime_analysis.png")
    print("="*80 + "\n")


def create_visualizations(df, stats):
    """Create comprehensive visualizations"""
    
    fig = plt.figure(figsize=(16, 12))
    
    # Define color scheme
    colors = {
        'primary': '#3498db',
        'success': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'info': '#9b59b6'
    }
    
    # Plot 1: Coverage Rate (Gauge-style)
    ax1 = plt.subplot(3, 3, 1)
    coverage = stats['coverage_rate']
    colors_gauge = ['#e74c3c', '#f39c12', '#f39c12', '#2ecc71']
    
    ax1.barh([0], [coverage], color=colors_gauge[min(int(coverage/25), 3)], height=0.3)
    ax1.set_xlim([0, 100])
    ax1.set_ylim([-0.5, 0.5])
    ax1.set_xlabel('Coverage %')
    ax1.set_title(f'Overall Coverage: {coverage:.1f}%', fontweight='bold', fontsize=12)
    ax1.set_yticks([])
    ax1.axvline(x=70, color='green', linestyle='--', alpha=0.5, label='Target')
    ax1.axvline(x=50, color='orange', linestyle='--', alpha=0.5)
    ax1.grid(axis='x', alpha=0.3)
    
    # Plot 2: Coverage by Location Type
    if 'coverage_by_location' in stats:
        ax2 = plt.subplot(3, 3, 2)
        loc_data = stats['coverage_by_location']
        bars = ax2.bar(range(len(loc_data)), loc_data.values, 
                      color=[colors['success'] if v >= 70 else colors['warning'] if v >= 50 else colors['danger'] 
                             for v in loc_data.values])
        ax2.set_xticks(range(len(loc_data)))
        ax2.set_xticklabels(loc_data.index, rotation=45)
        ax2.set_ylabel('Coverage %')
        ax2.set_title('Coverage by Location Type', fontweight='bold')
        ax2.set_ylim([0, 100])
        ax2.axhline(y=70, color='green', linestyle='--', alpha=0.5)
        ax2.grid(axis='y', alpha=0.3)
        
        for bar, val in zip(bars, loc_data.values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{val:.0f}%', ha='center', va='bottom', fontsize=9)
    
    # Plot 3: Coverage by CQC Rating
    ax3 = plt.subplot(3, 3, 3)
    cqc_data = stats['coverage_by_cqc']
    cqc_order = ['Outstanding', 'Good', 'Requires Improvement', 'Inadequate']
    cqc_data = cqc_data.reindex([x for x in cqc_order if x in cqc_data.index])
    
    bars = ax3.bar(range(len(cqc_data)), cqc_data.values,
                  color=[colors['success'], colors['primary'], colors['warning'], colors['danger']][:len(cqc_data)])
    ax3.set_xticks(range(len(cqc_data)))
    ax3.set_xticklabels([x[:12]+'...' if len(x) > 12 else x for x in cqc_data.index], rotation=45, ha='right')
    ax3.set_ylabel('Coverage %')
    ax3.set_title('Coverage by CQC Rating', fontweight='bold')
    ax3.set_ylim([0, 100])
    ax3.axhline(y=70, color='green', linestyle='--', alpha=0.5)
    ax3.grid(axis='y', alpha=0.3)
    
    for bar, val in zip(bars, cqc_data.values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{val:.0f}%', ha='center', va='bottom', fontsize=9)
    
    # Plots 4-9: Activity Analysis (if data available)
    df_with_data = df[df['data_available'] == True]
    
    if len(df_with_data) > 0 and 'activity_score' in df_with_data.columns:
        
        # Plot 4: Activity Score Distribution
        ax4 = plt.subplot(3, 3, 4)
        ax4.hist(df_with_data['activity_score'], bins=15, color=colors['primary'], 
                edgecolor='black', alpha=0.7)
        ax4.axvline(x=df_with_data['activity_score'].mean(), color='red', 
                   linestyle='--', label=f'Mean: {df_with_data["activity_score"].mean():.1f}')
        ax4.set_xlabel('Activity Score')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Activity Score Distribution', fontweight='bold')
        ax4.legend()
        ax4.grid(axis='y', alpha=0.3)
        
        # Plot 5: Activity Score by CQC Rating
        ax5 = plt.subplot(3, 3, 5)
        cqc_scores = stats['activity_by_cqc']
        cqc_scores = cqc_scores.reindex([x for x in cqc_order if x in cqc_scores.index])
        
        bars = ax5.bar(range(len(cqc_scores)), cqc_scores.values,
                      color=[colors['success'], colors['primary'], colors['warning'], colors['danger']][:len(cqc_scores)])
        ax5.set_xticks(range(len(cqc_scores)))
        ax5.set_xticklabels([x[:12]+'...' if len(x) > 12 else x for x in cqc_scores.index], rotation=45, ha='right')
        ax5.set_ylabel('Activity Score')
        ax5.set_title('Avg Activity Score by CQC', fontweight='bold')
        ax5.set_ylim([0, 100])
        ax5.grid(axis='y', alpha=0.3)
        
        for bar, val in zip(bars, cqc_scores.values):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=9)
        
        # Plot 6: Scatter - Activity vs CQC
        ax6 = plt.subplot(3, 3, 6)
        cqc_map = {'Outstanding': 4, 'Good': 3, 'Requires Improvement': 2, 'Inadequate': 1}
        df_with_data['cqc_numeric'] = df_with_data['cqc_rating'].map(cqc_map)
        
        scatter = ax6.scatter(df_with_data['cqc_numeric'], df_with_data['activity_score'],
                            c=df_with_data['cqc_numeric'], cmap='RdYlGn', s=100, alpha=0.6, edgecolors='black')
        
        # Add trend line
        if len(df_with_data) > 2:
            z = np.polyfit(df_with_data['cqc_numeric'].dropna(), 
                          df_with_data['activity_score'].dropna(), 1)
            p = np.poly1d(z)
            ax6.plot(df_with_data['cqc_numeric'].sort_values().unique(), 
                    p(df_with_data['cqc_numeric'].sort_values().unique()), 
                    "r--", alpha=0.8, linewidth=2)
        
        ax6.set_xlabel('CQC Rating (1=Inadequate, 4=Outstanding)')
        ax6.set_ylabel('Activity Score')
        ax6.set_title('Activity Score vs CQC Rating', fontweight='bold')
        ax6.set_xticks([1, 2, 3, 4])
        ax6.set_xticklabels(['Inad', 'Req Imp', 'Good', 'Outst'])
        ax6.grid(alpha=0.3)
        
        if stats.get('correlation'):
            ax6.text(0.05, 0.95, f'r = {stats["correlation"]:.3f}', 
                    transform=ax6.transAxes, fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Plot 7: Score Categories
        ax7 = plt.subplot(3, 3, 7)
        high = (df_with_data['activity_score'] >= 70).sum()
        medium = ((df_with_data['activity_score'] >= 50) & (df_with_data['activity_score'] < 70)).sum()
        low = (df_with_data['activity_score'] < 50).sum()
        
        categories = ['High\n(≥70)', 'Medium\n(50-69)', 'Low\n(<50)']
        values = [high, medium, low]
        colors_cat = [colors['success'], colors['warning'], colors['danger']]
        
        bars = ax7.bar(categories, values, color=colors_cat)
        ax7.set_ylabel('Number of Homes')
        ax7.set_title('Activity Score Categories', fontweight='bold')
        ax7.grid(axis='y', alpha=0.3)
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            pct = (val / len(df_with_data)) * 100
            ax7.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{val}\n({pct:.0f}%)', ha='center', va='bottom', fontsize=9)
        
        # Plot 8: Weekend vs Evening Activity
        if 'weekend_activity' in df_with_data.columns and 'evening_visits' in df_with_data.columns:
            ax8 = plt.subplot(3, 3, 8)
            
            weekend = df_with_data['weekend_activity'].sum()
            evening = df_with_data['evening_visits'].sum()
            both = (df_with_data['weekend_activity'] & df_with_data['evening_visits']).sum()
            neither = (~df_with_data['weekend_activity'] & ~df_with_data['evening_visits']).sum()
            
            patterns = ['Weekend\nOnly', 'Evening\nOnly', 'Both', 'Neither']
            values = [weekend - both, evening - both, both, neither]
            
            bars = ax8.bar(patterns, values, color=[colors['primary'], colors['info'], colors['success'], colors['danger']])
            ax8.set_ylabel('Number of Homes')
            ax8.set_title('Visit Pattern Distribution', fontweight='bold')
            ax8.grid(axis='y', alpha=0.3)
            
            for bar, val in zip(bars, values):
                if val > 0:
                    height = bar.get_height()
                    ax8.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                            f'{val}', ha='center', va='bottom', fontsize=9)
        
        # Plot 9: Top 10 Homes
        ax9 = plt.subplot(3, 3, 9)
        top_10 = df_with_data.nlargest(10, 'activity_score')[['name', 'activity_score']]
        
        y_pos = range(len(top_10))
        bars = ax9.barh(y_pos, top_10['activity_score'].values, 
                       color=[colors['success'] if s >= 70 else colors['warning'] for s in top_10['activity_score'].values])
        ax9.set_yticks(y_pos)
        ax9.set_yticklabels([name[:25]+'...' if len(name) > 25 else name for name in top_10['name']], fontsize=8)
        ax9.set_xlabel('Activity Score')
        ax9.set_title('Top 10 Homes by Activity', fontweight='bold')
        ax9.set_xlim([0, 100])
        ax9.grid(axis='x', alpha=0.3)
        
        for bar, val in zip(bars, top_10['activity_score'].values):
            width = bar.get_width()
            ax9.text(width + 2, bar.get_y() + bar.get_height()/2.,
                    f'{val:.1f}', ha='left', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('besttime_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Visualization saved: besttime_analysis.png")


def export_summary_csv(df, stats):
    """Export summary statistics to CSV"""
    
    summary_data = {
        'Metric': [],
        'Value': []
    }
    
    # Add all key metrics
    summary_data['Metric'].extend([
        'Total Homes Tested',
        'Homes with Data',
        'Coverage Rate (%)',
        'Mean Activity Score',
        'Median Activity Score',
        'High Score Homes (≥70)',
        'Medium Score Homes (50-69)',
        'Low Score Homes (<50)',
        'Correlation with CQC'
    ])
    
    df_with_data = df[df['data_available'] == True]
    high = (df_with_data['activity_score'] >= 70).sum() if len(df_with_data) > 0 else 0
    medium = ((df_with_data['activity_score'] >= 50) & (df_with_data['activity_score'] < 70)).sum() if len(df_with_data) > 0 else 0
    low = (df_with_data['activity_score'] < 50).sum() if len(df_with_data) > 0 else 0
    
    summary_data['Value'].extend([
        stats['total_homes'],
        stats['homes_with_data'],
        f"{stats['coverage_rate']:.1f}",
        f"{stats.get('mean_activity', 0):.1f}",
        f"{stats.get('median_activity', 0):.1f}",
        high,
        medium,
        low,
        f"{stats.get('correlation', 0):.3f}"
    ])
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('besttime_summary.csv', index=False)
    print("✅ Summary saved: besttime_summary.csv")


def main():
    """Main execution"""
    
    print("\n" + "="*80)
    print("BestTime.app Results Analysis")
    print("="*80 + "\n")
    
    # Load results
    df = load_results()
    print(f"✅ Loaded {len(df)} test results\n")
    
    # Calculate statistics
    stats = calculate_statistics(df)
    
    # Print detailed report
    print_detailed_report(df, stats)
    
    # Create visualizations
    print("\n📊 Generating visualizations...")
    create_visualizations(df, stats)
    
    # Export summary
    print("\n💾 Exporting summary...")
    export_summary_csv(df, stats)
    
    print("\n" + "="*80)
    print("✅ Analysis complete!")
    print("="*80)
    print("\nGenerated files:")
    print("  • besttime_analysis.png  - Comprehensive visualizations")
    print("  • besttime_summary.csv   - Key metrics summary")
    print("\n")


if __name__ == "__main__":
    main()

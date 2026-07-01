#!/usr/bin/env python3
"""
Test script for news sources functionality
Tests the expanded list of RSS feeds to ensure they're accessible
"""

import sys
import os
import feedparser
import time
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.news_analyzer import NewsAnalyzer

def test_news_sources():
    """Test all news sources to check accessibility and content"""
    print("=" * 60)
    print("Testing News Sources - Stock Trading Web App")
    print("=" * 60)
    
    # Initialize news analyzer
    analyzer = NewsAnalyzer()
    
    print(f"\nTotal news sources configured: {len(analyzer.news_sources)}")
    print("\nTesting each RSS feed...\n")
    
    successful_sources = []
    failed_sources = []
    total_articles = 0
    
    for i, source in enumerate(analyzer.news_sources, 1):
        print(f"[{i:2d}/{len(analyzer.news_sources)}] Testing: {source}")
        
        try:
            # Add delay to avoid rate limiting
            time.sleep(0.5)
            
            # Parse the feed
            feed = feedparser.parse(source, request_headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if feed.bozo:
                print(f"  WARNING: Feed has parsing errors (may still work)")
            
            entries_count = len(feed.entries)
            total_articles += entries_count
            
            if entries_count > 0:
                successful_sources.append({
                    'url': source,
                    'entries': entries_count,
                    'title': feed.feed.get('title', 'No title'),
                    'updated': feed.feed.get('updated', 'No update info')
                })
                print(f"  SUCCESS - {entries_count} articles found")
                
                # Show sample article title
                if feed.entries:
                    sample_title = feed.entries[0].get('title', 'No title')
                    print(f"      Sample: {sample_title[:60]}...")
            else:
                print(f"  FAILED - No articles found")
                failed_sources.append(source)
                
        except Exception as e:
            print(f"  ERROR - {str(e)}")
            failed_sources.append(source)
        
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Successful sources: {len(successful_sources)}/{len(analyzer.news_sources)}")
    print(f"Failed sources: {len(failed_sources)}")
    print(f"Total articles available: {total_articles}")
    
    if successful_sources:
        print(f"\nTop 5 sources by article count:")
        successful_sources.sort(key=lambda x: x['entries'], reverse=True)
        for i, source in enumerate(successful_sources[:5], 1):
            print(f"  {i}. {source['title'][:40]}... ({source['entries']} articles)")
    
    if failed_sources:
        print(f"\nFailed sources:")
        for source in failed_sources:
            print(f"  - {source}")
    
    # Test actual news fetching
    print(f"\n" + "=" * 60)
    print("Testing actual news fetching with Indian filtering...")
    print("=" * 60)
    
    try:
        news_articles = analyzer.fetch_news(force_refresh=True)
        print(f"Successfully fetched {len(news_articles)} Indian-relevant articles")
        
        if news_articles:
            print(f"\nSample articles:")
            for i, article in enumerate(news_articles[:3], 1):
                print(f"  {i}. {article.get('title', 'No title')[:60]}...")
                print(f"     Source: {article.get('source', 'Unknown')}")
                print(f"     Stocks: {len(article.get('stocks', []))} mentioned")
                
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return len(successful_sources), len(failed_sources)

if __name__ == "__main__":
    success_count, fail_count = test_news_sources()
    
    if fail_count == 0:
        print("\nAll news sources are working perfectly!")
    elif success_count > len(sys.argv[1:]) * 0.8:  # At least 80% success rate
        print(f"\nGood! {success_count} sources working ({success_count/(success_count+fail_count)*100:.1f}%)")
    else:
        print(f"\nWarning: Only {success_count} sources working. Consider checking failed sources.")

#!/usr/bin/env python3
"""
Debug script to test MQL5 article discovery mechanism.
Tests multiple "more" link clicks to load all articles.
"""

import asyncio
from playwright.async_api import async_playwright


async def debug_discovery(user_id: str):
    """Debug article discovery for a user."""
    url = f"https://www.mql5.com/en/users/{user_id}/publications"

    print(f"🔍 Testing discovery for: {url}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible for debugging

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        # Navigate
        print(f"📄 Loading page...")
        await page.goto(url, timeout=30000)
        await page.wait_for_timeout(3000)

        # Count initial articles
        initial_links = await page.query_selector_all('a[href*="/en/articles/"]')
        print(f"✅ Initial articles visible: {len(initial_links)}")

        # Try clicking "more" multiple times
        click_count = 0
        max_clicks = 10  # Safety limit

        while click_count < max_clicks:
            try:
                # Look for "more" link - try different selectors
                more_link = await page.query_selector('a:has-text("more")')

                if not more_link:
                    # Try alternative selectors
                    more_link = await page.query_selector('a.link-more')

                if not more_link:
                    more_link = await page.query_selector('a[href*="offset"]')

                if more_link:
                    click_count += 1
                    print(f"\n🖱️  Click #{click_count}: Found 'more' link, clicking...")

                    # Check if visible
                    is_visible = await more_link.is_visible()
                    print(f"   Visible: {is_visible}")

                    if is_visible:
                        await more_link.click()
                        await page.wait_for_timeout(3000)  # Wait for new content

                        # Count articles after click
                        current_links = await page.query_selector_all('a[href*="/en/articles/"]')
                        print(f"   ✅ Articles now: {len(current_links)}")
                    else:
                        print(f"   ⚠️  Link not visible, stopping")
                        break
                else:
                    print(f"\n✅ No more 'more' links found - all articles loaded")
                    break

            except Exception as e:
                print(f"\n❌ Error clicking 'more': {e}")
                break

        # Final count
        print(f"\n" + "="*60)
        final_links = await page.query_selector_all('a[href*="/en/articles/"]')
        print(f"📊 FINAL: {len(final_links)} article links found")

        # Extract unique article URLs
        urls = set()
        for link in final_links:
            href = await link.get_attribute('href')
            if href and '/en/articles/' in href and href.count('/') >= 4:
                if href.startswith('/'):
                    href = f"https://www.mql5.com{href}"
                # Extract article ID
                import re
                match = re.search(r'/articles/(\d+)', href)
                if match:
                    article_id = match.group(1)
                    article_url = f"https://www.mql5.com/en/articles/{article_id}"
                    urls.add(article_url)

        print(f"📝 Unique articles: {len(urls)}")
        print(f"\n📋 First 10 article IDs:")
        sorted_urls = sorted(urls, key=lambda x: int(x.split('/')[-1]), reverse=True)
        for i, url in enumerate(sorted_urls[:10], 1):
            article_id = url.split('/')[-1]
            print(f"   {i}. Article {article_id}")

        print(f"\n⏸️  Browser will stay open for 10 seconds for inspection...")
        await page.wait_for_timeout(10000)

        await browser.close()

        return sorted_urls


if __name__ == "__main__":
    # Test with omegajoctan
    urls = asyncio.run(debug_discovery("omegajoctan"))

    print(f"\n" + "="*60)
    print(f"✅ Discovery complete: {len(urls)} articles")
    print(f"="*60)

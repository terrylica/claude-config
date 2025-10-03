#!/usr/bin/env python3
"""Gentle test to check if MQL5.com access is restored."""

import asyncio
from playwright.async_api import async_playwright

async def test_access():
    url = "https://www.mql5.com/en/users/omegajoctan/publications"

    print(f"Testing access to: {url}")
    print("(This is a single, gentle request)\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        try:
            response = await page.goto(url, timeout=30000)
            status = response.status

            print(f"✅ Response status: {status}")

            if status == 200:
                # Check if we can see article links
                article_links = await page.query_selector_all('a[href*="/en/articles/"]')
                print(f"✅ Found {len(article_links)} article links on page")
                print("\n✅ ACCESS RESTORED - Safe to continue extraction")
            elif status == 403:
                print("❌ 403 Forbidden - Still blocked")
            elif status == 404:
                print("❌ 404 Not Found - Still blocked or invalid URL")
            else:
                print(f"⚠️  Unexpected status: {status}")

        except Exception as e:
            print(f"❌ Error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_access())

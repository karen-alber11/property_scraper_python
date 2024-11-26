import asyncio
from playwright.async_api import async_playwright
import nest_asyncio
import re
from datetime import datetime

# Allow nested event loops (useful in Jupyter)
nest_asyncio.apply()


class HouseScraping:
    def __init__(self, url, retries=3):
        self.url = url
        self.retries = retries  # Retry count for robustness

    async def get_property_details(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Set timeouts
            page.set_default_navigation_timeout(30000)  # 30 seconds
            page.set_default_timeout(30000)  # General timeout

            properties = []  # To store scraped properties

            for attempt in range(self.retries):
                try:
                    # Navigate to the page
                    await page.goto(self.url, wait_until="domcontentloaded")
                    await page.wait_for_selector('.StackedCard_card__Kvggc', timeout=15000)

                    # Extract property details
                    property_cards = await page.query_selector_all('.StackedCard_card__Kvggc')
                    for card in property_cards:
                        # Extract property information
                        link = await self.scrape_link(card)
                        property_type = await self.scrape_property_type(card)
                        title = await self.scrape_title(card)
                        description = await self.scrape_description(card)
                        date_published = await self.scrape_date_published(page, card)
                        relative_date = await self.scrape_relative_date(card)

                        # Format the published date
                        date_published = self.format_date(date_published)

                        properties.append({
                            'date_published': date_published,
                            'relative_date': relative_date,
                            'type': property_type,
                            'title': title,
                            'description': description,
                            'link': link,
                        })
                    break  # Exit loop if successful

                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for {self.url}: {e}")
                    if attempt + 1 == self.retries:
                        print(f"Max retries reached for {self.url}. Returning partial results.")
                        break
                finally:
                    # Close page between attempts to ensure proper cleanup
                    await page.close()
                    if attempt + 1 < self.retries:
                        page = await browser.new_page()

            await browser.close()
            return properties

    # Method to scrape the link
    async def scrape_link(self, card):
        rawlink = await card.get_attribute('href')
        base_url = 'https://www.q84sale.com'
        return f"{base_url}{rawlink}" if rawlink else None

    # Method to scrape the property type
    async def scrape_property_type(self, card):
        selector = '.text-6-med.text-neutral_600.styles_category__NQAci'
        element = await card.query_selector(selector)
        return await element.inner_text() if element else None

    # Method to scrape the property title
    async def scrape_title(self, card):
        selector = '.text-4-med.text-neutral_900.styles_title__l5TTA'
        element = await card.query_selector(selector)
        return await element.inner_text() if element else None

    # Method to scrape the property description
    async def scrape_description(self, card):
        selector = '.text-5-regular.text-neutral_500.StackedCard_description__aXpyG'
        element = await card.query_selector(selector)
        return await element.inner_text() if element else None

    # Method to scrape the relative date
    async def scrape_relative_date(self, card):
        selector = '.styles_tail__82mnX p.text-6-med.text-neutral_600'
        elements = await card.query_selector_all(selector)
        return (await elements[0].inner_text()) if elements else None

    # Method to scrape date_published
    async def scrape_date_published(self, page, card):
        date_selector = '[data-testid="date_published"]'
        date_element = await card.query_selector(date_selector)
        if date_element:
            return await date_element.get_attribute('content')

        # Fallback: search page content
        page_content = await page.content()
        matches = re.findall(r'"date_published":"(.*?)"', page_content)
        return matches[0] if matches else None

    # Method to format date
    def format_date(self, date_string):
        if not date_string:
            return None
        try:
            return datetime.fromisoformat(date_string).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None

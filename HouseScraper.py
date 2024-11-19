from typing_extensions import Concatenate
from playwright.async_api import async_playwright
import nest_asyncio
import asyncio
import re
from datetime import datetime

# Allow nested event loops in Jupyter
nest_asyncio.apply()


class HouseScraping:
    def __init__(self, url):
        self.url = url

    # Define the async function to get the content
    async def get_property_details(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Navigate to the page
            await page.goto(self.url)

            # Wait for the page to load completely
            await page.wait_for_load_state('load')

            # Extract property details
            properties = []  # This will hold the list of property details
            property_cards = await page.query_selector_all('.StackedCard_card__Kvggc')  # Select all property cards

            for card in property_cards:
                # Extract the link
                link = await self.scrape_link(card)
                # Extract other property details
                property_type = await self.scrape_property_type(card)
                title = await self.scrape_title(card)
                description = await self.scrape_description(card)
                date_published = await self.scrape_date_published(page, card)
                relative_date = await self.scrape_relative_date(card)

                # Format date_published to match the format
                date_published = self.format_date(date_published)

                # Collect the details into a dictionary
                property_details = {
                    'date_published': date_published,
                    'relative_date': relative_date,
                    'type': property_type,
                    'title': title,
                    'description': description,
                    'link': link,
                }
                properties.append(property_details)

            # Close the browser
            await browser.close()

            # Return the list of property details (as array of objects)
            return properties

    # Method to scrape the link
    async def scrape_link(self, card):
        rawlink = await card.get_attribute('href')
        cons = 'https://www.q84sale.com'
        link = cons + rawlink  # Concatenate the base URL and the relative link
        return link

    # Method to scrape the property type
    async def scrape_property_type(self, card):
        type_selector = '.text-6-med.text-neutral_600.styles_category__NQAci'
        property_type = await card.query_selector(type_selector)
        return await property_type.inner_text() if property_type else None

    # Method to scrape the property title
    async def scrape_title(self, card):
        title_selector = '.text-4-med.text-neutral_900.styles_title__l5TTA'
        title = await card.query_selector(title_selector)
        return await title.inner_text() if title else None

    # Method to scrape the property description
    async def scrape_description(self, card):
        description_selector = '.text-5-regular.text-neutral_500.StackedCard_description__aXpyG'
        description = await card.query_selector(description_selector)
        return await description.inner_text() if description else None

    # Method to scrape the relative date
    async def scrape_relative_date(self, card):
        relative_time_selector = '.styles_tail__82mnX p.text-6-med.text-neutral_600'
        relative_time_elements = await card.query_selector_all(relative_time_selector)
        relative_dates = [await element.inner_text() for element in relative_time_elements]
        return relative_dates[0] if relative_dates else None

    # Method to scrape date_published
    async def scrape_date_published(self, page, card):
        # Extract date_published from a specific card if available in a script tag or attribute
        date_published = None
        date_published_selector = '[data-testid="date_published"]'
        date_element = await card.query_selector(date_published_selector)

        if date_element:
            date_published = await date_element.get_attribute('content')

        if not date_published:  # If the date wasn't found in the card element, check the page's content
            page_content = await page.content()  # Use the page object to get the full page content
            if 'date_published' in page_content:
                matches = re.findall(r'"date_published":"(.*?)"', page_content)
                if matches:
                    date_published = matches[0]  # Take the first match if there are any
        return date_published

    # Method to format date into the required format (YYYY-MM-DD HH:MM:SS)
    def format_date(self, date_string):
        if not date_string:
            return None
        try:
            # Attempt to parse the date and format it
            date_obj = datetime.fromisoformat(date_string)
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            return None  # In case date formatting fails


async def main():
   # Initialize the scraper with the URLs
   house_scraper_1 = HouseScraping("https://www.q84sale.com/en/property/for-sale/house-for-sale/1")
   house_scraper_2 = HouseScraping("https://www.q84sale.com/en/property/for-sale/house-for-sale/2")
   house_scraper_3 = HouseScraping("https://www.q84sale.com/en/property/for-sale/house-for-sale/3")

   # Run the async functions to get property details
   properties_1 = await house_scraper_1.get_property_details()
   properties_2 = await house_scraper_2.get_property_details()
   properties_3 = await house_scraper_3.get_property_details()

   # Combine the results from all scrapers into a single array of objects
   all_properties = properties_1 + properties_2 + properties_3

   # Print the combined properties as an array of objects
   print(all_properties)

if __name__ == '__main__':
   asyncio.run(main())
import asyncio
from playwright.async_api import async_playwright
import nest_asyncio
from DetailsScraper import DetailsScraping
import json
import pandas as pd
from datetime import datetime, timedelta
from SavingOnDrive import SavingOnDrive


class MainScraper:
    def __init__(self, categories):
        self.categories = categories  # List of (name, base_url, pages)
        self.results = {}  # Dictionary to store results for each category

    async def scrape_category(self, name, base_url, pages):
        all_properties = []
        # Calculate yesterday's date in 'YYYY-MM-DD' format
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"Filtering properties published on: {yesterday}")

        for i in range(1, pages + 1):
            url = base_url.format(i)
            print(f"Scraping page: {url} for category: {name}")
            scraper = DetailsScraping(url)
            try:
                properties = await scraper.get_property_details()
                # Filter properties by published_date
                filtered_properties = [
                    prop for prop in properties
                    if 'date_published' in prop and prop['date_published'].split(' ')[0] == yesterday
                ]
                if not filtered_properties:
                    print(f"No properties found on page {i} for category {name} with the specified date.")
                all_properties.extend(filtered_properties)
            except Exception as e:
                print(f"Error scraping {url}: {e}")

        if all_properties:
            self.results[name] = all_properties
        else:
            print(f"No data collected for category {name}.")

    async def run(self):
        tasks = []
        for name, base_url, pages in self.categories:
            tasks.append(self.scrape_category(name, base_url, pages))
        await asyncio.gather(*tasks)

    def save_to_excel(self, file_name):
        try:
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                for name, properties in self.results.items():
                    if properties:  # Only save sheets with data
                        df = pd.DataFrame(properties)
                        df.to_excel(writer, sheet_name=name, index=False)
                        print(f"Data for '{name}' saved to Excel.")
            print(f"All data successfully saved to {file_name}.")
        except PermissionError:
            print(f"Error: Unable to save the file '{file_name}'. It may be open in another application.")
            backup_file_name = file_name.replace('.xlsx', '_backup.xlsx')
            print(f"Attempting to save data to '{backup_file_name}' instead.")
            try:
                with pd.ExcelWriter(backup_file_name, engine='openpyxl') as writer:
                    for name, properties in self.results.items():
                        if properties:
                            df = pd.DataFrame(properties)
                            df.to_excel(writer, sheet_name=name, index=False)
                            print(f"Data for '{name}' saved to backup file.")
                print(f"All data successfully saved to {backup_file_name}.")
            except Exception as e:
                print(f"Failed to save to backup file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving to Excel: {e}")



if __name__ == "__main__":
    nest_asyncio.apply()  # Ensure compatibility with nested event loops

    # Define the scraping categories
    categories_1 = [
        # ("House for Sale", "https://www.q84sale.com/en/property/for-sale/house-for-sale/{}", 5),
        ("Building or floors", "https://www.q84sale.com/en/property/for-sale/building-or-floors/{}", 1),
        ("Apartment for Sale", "https://www.q84sale.com/en/property/for-sale/apartment-for-sale/{}", 2),
        # ("Demolishing", "https://www.q84sale.com/en/property/for-sale/demolishing/{}", 1),
        # ("Lounge for Sale", "https://www.q84sale.com/en/property/for-sale/lounge-for-sale/{}", 1),
        # ("Chalet for Sale", "https://www.q84sale.com/en/property/for-sale/chalet-for-sale/{}", 1),
        # ("Farms for Sale", "https://www.q84sale.com/en/property/for-sale/farms-for-sale/{}", 1),
        # ("Land", "https://www.q84sale.com/en/property/for-sale/land/{}", 1),
        # ("Residential Certificate", "https://www.q84sale.com/en/property/for-sale/residential-certificate/{}", 1),
        # ("Commercial Land Certificate", "https://www.q84sale.com/en/property/for-sale/commercial-land-certificate/{}", 1),
        # ("Shop for Sale", "https://www.q84sale.com/en/property/for-sale/shop-for-sale/{}", 2),
        # ("Company", "https://www.q84sale.com/en/property/for-sale/company/{}", 1),
        # ("Wanted Property for Sale", "https://www.q84sale.com/en/property/for-sale/wanted-property-for-sale/{}", 1),
    ]

    # categories_2 = [
    #     ("House for Rent", "https://www.q84sale.com/en/property/for-rent/house-for-rent/{}", 2),
    #     ("Floor", "https://www.q84sale.com/en/property/for-rent/floor/{}", 2),
    #     ("Furnished Apartment", "https://www.q84sale.com/en/property/for-rent/furnished-apartment/{}", 1),
    #     ("Apartment For Rent", "https://www.q84sale.com/en/property/for-rent/apartment-for-rent/{}", 7),
    #     ("Duplex", "https://www.q84sale.com/en/property/for-rent/duplex/{}", 1),
    #     ("House Sharing", "https://www.q84sale.com/en/property/for-rent/house-sharing/{}", 1),
    #     ("Shop For Rent", "https://www.q84sale.com/en/property/for-rent/shop-for-rent/{}", 1),
    #     ("Office", "https://www.q84sale.com/en/property/for-rent/office/{}", 1),
    #     ("Stores", "https://www.q84sale.com/en/property/for-rent/stores/{}", 1),
    #     ("Farms For Rent", "https://www.q84sale.com/en/property/for-rent/farms-for-rent/{}", 2),
    #     ("Lounge For Rent", "https://www.q84sale.com/en/property/for-rent/lounge-for-rent/{}", 2),
    #     ("Industrial Certificate", "https://www.q84sale.com/en/property/for-rent/industrial-certificate/{}", 1),
    #     ("Chalet For Rent", "https://www.q84sale.com/en/property/for-rent/chalet-for-rent/{}", 2),
    #     ("Rental Playgrounds", "https://www.q84sale.com/en/property/for-rent/rental-playgrounds/{}", 1),
    #     ("Wanted Property for Rent", "https://www.q84sale.com/en/property/for-rent/wanted-property-for-rent/{}", 1),
    # ]

    categories_3 = [
        ("Property For Exchange", "https://www.q84sale.com/en/property/for-exchange/{}", 2),
    ]

    # Create an instance of the scraper
    PropertyForSale_scraper = MainScraper(categories_1)
    # PropertyForRent_scraper = MainScraper(categories_2)
    PropertyForExchange_scraper = MainScraper(categories_3)


    # Run the scraper
    asyncio.run(PropertyForSale_scraper.run())
    # asyncio.run(PropertyForRent_scraper.run())
    asyncio.run(PropertyForExchange_scraper.run())

    # Save all results to an Excel file
    excel_file_name_1 = "Property for Sale.xlsx"
    # excel_file_name_2 = "Property for Rent.xlsx"
    excel_file_name_3 = "Property For Exchange.xlsx"

    PropertyForSale_scraper.save_to_excel(excel_file_name_1)
    # PropertyForRent_scraper.save_to_excel(excel_file_name_2)
    PropertyForExchange_scraper.save_to_excel(excel_file_name_3)

    # Google Drive credentials file
    credentials_file = "credentials/real-estate-property-scraper-4d9f71a7ded4.json"

    # Initialize the SavingOnDrive class
    drive_saver = SavingOnDrive(credentials_file)
    drive_saver.authenticate()

    # List of files to save
    excel_files = [excel_file_name_1, excel_file_name_3] # , excel_file_name_2

    # Save files to Google Drive
    drive_saver.save_files(excel_files)


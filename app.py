import logging
from quart import Quart, jsonify

# Import your HouseScraping class (assuming it's defined in another file)
from HouseScraper import HouseScraping

# Create a Quart app
app = Quart(__name__)

# Configure logging to display debug and error messages
logging.basicConfig(level=logging.INFO)

@app.route('/')
async def index():
    try:
        house_scraper_1 = HouseScraping("https://www.q84sale.com/en/property/for-sale/house-for-sale/1")
        house_scraper_2 = HouseScraping("https://www.q84sale.com/en/property/for-sale/house-for-sale/2")
        house_scraper_3 = HouseScraping("https://www.q84sale.com/en/property/for-sale/house-for-sale/3")

        app.logger.info("Starting property scraping...")

        # Run the async functions to get property details
        properties_1 = await house_scraper_1.get_property_details()
        properties_2 = await house_scraper_2.get_property_details()
        properties_3 = await house_scraper_3.get_property_details()

        all_properties = properties_1 + properties_2 + properties_3
        app.logger.info(f"Scraped {len(all_properties)} properties.")
        return jsonify(all_properties)

    except Exception as e:
        app.logger.error(f"Error occurred: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error"}), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

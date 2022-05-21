"""script with functions for fetching product data from amazon"""
import json
import os
import time

from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver import firefox


def fetch_url(url):
    """fetch url and return response

    Args:
        url (String): url to fetch

    Returns:
        Text: html response from amazon

    Raises:
        None: None

    Test:
        What happens if url returns non 200 status code
        What happens if url returns 200 status code
        What happens if Firefox, Gecko or important libraries are not installed
    """
    display = Display(visible=False, size=(800, 600))
    display.start()

    firefox_options = firefox.options.Options()
    firefox_options.set_preference('browser.download.folderList', 2)
    firefox_options.set_preference(
        'browser.download.manager.showWhenStarting', False
    )
    firefox_options.set_preference('browser.download.dir', os.getcwd())
    firefox_options.set_preference(
        'browser.helperApps.neverAsk.saveToDisk', 'text/csv'
    )

    browser = webdriver.Firefox(options=firefox_options)

    browser.get(url)

    source = browser.page_source

    browser.quit()
    display.stop()

    return source


def get_title(response):
    """Get title from response

    Args:
        response (Text): html response from amazon

    Returns:
        String: title of product

    Raises:
        None: None

    Test:
        Response contains meta tag with title attribute
        Response doesn't contain meta tag
        Response is invalid html
    """
    soup = BeautifulSoup(response, 'html.parser')

    title = soup.find_all("meta", attrs={'name': 'title'})

    if len(title) > 0:
        return title[0]["content"].split(":")[0].strip()
    else:
        return None


def get_image(response):
    """Get image urls from response

    Args:
        response (Text): html response from amazon

    Returns:
        String: product image url

    Raises:
        None: None

    Test:
        Response contains div with "imgTagWrapperId" id and includes json data
        Response doesn't contain div
        Response is invalid html
        JSON is not valid
    """
    soup = BeautifulSoup(response, 'html.parser')

    div = soup.find_all("div", attrs={"id": "imgTagWrapperId"})

    if len(div) > 0:
        images = json.loads(div[0].img["data-a-dynamic-image"])

        # Find largest image
        largest_image_url = None
        largest_image_size = 0
        for image in images:
            if largest_image_url is None and largest_image_size == 0 or images[image][0] > largest_image_size:
                largest_image_url = image
                largest_image_size = images[image][0]

        return largest_image_url

    return None


def get_description(response):
    """Get description from response

    Args:
        response (Text): html response from amazon

    Returns:
        String: product description

    Raises:
        None: None

    Test:
        Response contains div with "feature-bullets" id
        Response doesn't contain div
        Response is invalid html
    """
    soup = BeautifulSoup(response, 'html.parser')

    description = soup.find_all("div", id="feature-bullets")

    ret = ""
    if len(description) > 0:
        for item in description[0].find_all("span"):
            if "um sicherzustellen, dass dieser Artikel passt." not in item.text and "›" not in item.text:
                ret += item.text.strip() + "\n"

        # Remove last newline and return
        return ret[:-1]
    else:
        return None


def get_price(response):
    """Get price from response

    Args:
        response (Text): html response from amazon

    Returns:
        Array: product price and currency

    Raises:
        None: None

    Test:
        Response contains div with class "twister-plus-buying-options-price-data"
        Response doesn't contain div
        No valid JSON
        Only price, currency missing
        Response is invalid html
    """
    soup = BeautifulSoup(response, 'html.parser')

    price = soup.find_all("div", {"class": "twister-plus-buying-options-price-data"})

    if len(price) > 0:
        j = json.loads(price[0].text)

        if len(j) > 0:
            return [j[0]["priceAmount"], j[0]["currencySymbol"]]
        else:
            return None
    else:
        return None


if __name__ == "__main__":
    """Main function"""
    products = [
        'B082QDB6CG',
        'B07MBQPQ62',
        'B07MBQPQ62',
        'B09Y64QV33',
        'B00F0DGRZO',
        'B071J8CZP9',
        'B001MF002A',
        'B082QM712M',
        'B091DV8SXG',
    ]

    for p in products:
        prod_src = fetch_url('https://www.amazon.de/dp/' + p)

        print("-----------------------------------------------------" + p + "-----------------------------------------------------")
        print("Title:       " + str(get_title(prod_src)) + "\n")
        print("Image:       " + str(get_image(prod_src)) + "\n")
        print("Price:       " + str(get_price(prod_src)) + "\n")
        print("Description: " + str(get_description(prod_src)) + "\n\n")

        time.sleep(2)

"""script with functions for fetching product data from amazon"""
import json

import requests
from bs4 import BeautifulSoup


def fetch_url(url):
    """fetch url and return response

    Args:
        url (String): url to fetch

    Returns:
        Text: html response from amazon

    Raises:
        None: None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
    }

    response = requests.get(url, headers=headers)
    return response.text


def get_title(response):
    """Get title from response

    Args:
        response (Text): html response from amazon

    Returns:
        String: title of product

    Raises:
        None: None
    """
    soup = BeautifulSoup(response, 'html.parser')

    title = soup.find_all("meta", attrs={'name': 'title'})

    if len(title) > 0:
        return title[0]["content"].split(":")[0].strip()
    else:
        return None


def get_image(response, title):
    """Get image urls from response

    Args:
        response (Text): html response from amazon
        title (String): title of product

    Returns:
        String: product image url

    Raises:
        None: None
    """
    soup = BeautifulSoup(response, 'html.parser')

    images = soup.find_all("img", alt=lambda a: a == title.replace("&", "&amp;"))

    if len(images) > 0:
        images = json.loads(images[0]["data-a-dynamic-image"])

        # Find largest image
        largest_image_url = None
        largest_image_size = 0
        for image in images:
            if largest_image_url is None and largest_image_size == 0 or images[image][0] > largest_image_size:
                largest_image_url = image
                largest_image_size = images[image][0]

        return largest_image_url
    else:
        return None


def get_description(response):
    """Get description from response

    Args:
        response (Text): html response from amazon

    Returns:
        String: product description

    Raises:
        None: None
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
    prod_src = fetch_url('https://www.amazon.de/dp/B082QDB6CG')

    print("Title:       " + get_title(prod_src) + "\n")
    print("Image:       " + get_image(prod_src, get_title(prod_src)) + "\n")
    print("Price:       " + str(get_price(prod_src)) + "\n")
    print("Description: " + get_description(prod_src))

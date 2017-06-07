import re
from urllib import parse
from urllib.request import urlopen

import time
from bs4 import BeautifulSoup

from constant import BASE_URL, QUERY_TIME_INTERVAL

def get_soup_by_url(url: str) -> BeautifulSoup:
    # encoded_url = parse.quote(url, ':/')
    time.sleep(QUERY_TIME_INTERVAL)
    try:
        data = urlopen(url)
    except Exception:
        print(">>"*5, url)
        raise
    return BeautifulSoup(data, "html.parser")


def split_url_param(url_param) -> tuple:
    pattern = r"(?P<category_type>\w+)=(?P<id_number>\d+)"
    result = re.search(pattern, url_param)
    return result.group("category_type"), result.group("id_number")


def get_items_price(soup: BeautifulSoup) -> int:
     """ Item's price structure
     <div class="priceinfo>
          -> <span class="price">
     :param soup: BeautifulSoup
     :rtype: int 
     """
     for element in soup.find_all("div", class_="priceinfo"):
          return int(element.find("span", class_="price").text.replace(",", ""))


def get_hot_items(soup: BeautifulSoup) -> dict:
     """ Top 10 items structure
     <div id = cl-ordrank>
          -> <li>
               -> <a class="yui3-u> 
     :param soup: 
     :rtype: dict 
     """
     result = {}
     for div_element in soup.find(id="cl-ordrank"):
          try:
               li_elements = div_element.findChildren("li")
          except AttributeError:
               continue

          for li in li_elements:
               for a_element in li.findChildren("a", class_="yui3-u"):
                    result[int(li["pos"])] = f"{BASE_URL}{a_element['href']}"
     return result


def get_current_categories(soup: BeautifulSoup) -> dict:
    result = {
        "z_url": "",
        "z_text": "",
        "sub_url": "",
        "sub_text": "",
        "catid_url": "",
        "catid_text": "",
        "catitemid_url": "",
        "catitemid_text": "",
    }
    for div_tag in soup.find_all("div", attrs={"class": "yui3-menu-label"}):
        for a_tag in div_tag.findChildren("a"):
            category_type, id_number = split_url_param(a_tag["href"])
            result[f"{category_type}_url"] = f"{BASE_URL}{a_tag['href']}"
            result[f"{category_type}_text"] = a_tag.text
    return result


def get_best_items_info(soup: BeautifulSoup) -> dict:
    hot_items = get_hot_items(soup)
    best_item_url = hot_items[1]
    best_soup = get_soup_by_url(best_item_url)
    category_of_best_item = get_current_categories(best_soup)
    item_price = get_items_price(best_soup)
    category_of_best_item.update({"best_item_price": item_price})
    return category_of_best_item

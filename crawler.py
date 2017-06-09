import json

import time
from bs4 import BeautifulSoup, Comment

from constant import BASE_URL
from items_info import get_soup_by_url, split_url_param, get_best_items_info


def get_categories_from_yahoo(soup: BeautifulSoup):
     """ I think this part can be ignored, there are too many categories group
     :param soup: 
     :return: 
     """
     for i in soup.find(id="category"):
          try:
               print(i.findChildren("a"))
          except AttributeError:
               continue


def get_sub_categories(soup: BeautifulSoup) -> list:
     result = []
     for sub_category in soup.find_all(string=lambda text: isinstance(text, Comment)):
          sub_soup = BeautifulSoup(sub_category.extract(), "html.parser")
          for sub_category in sub_soup.find_all("a"):
               result.append({
                    "url": f"{BASE_URL}{sub_category['href']}",
                    "text": sub_category.text
               })
     return result


def get_sub_category_items(soup: BeautifulSoup) -> list:
     prefix = "/?catitemid"
     result = []
     for category in soup.find(id="cl-menucate"):
          try:
               find_a_iter = category.find_all("a")
          except AttributeError:
               continue
          for link in find_a_iter:
               if link["href"].startswith(prefix):
                    result.append({
                         "url": f"{BASE_URL}{link['href']}",
                         "text": link.text
                    })
     return result


def get_first_item_url(url: str) -> str:
     soup = get_soup_by_url(url)
     for a_tag in soup.find_all("a"):
          if a_tag.get("href") and a_tag.get("href").startswith("/gdsale/") and a_tag.get("href").endswith(".html"):
               return f"{BASE_URL}{a_tag['href']}"

          if a_tag.get("href") and "gdsale" in a_tag.get("href"):
               return f"{BASE_URL}{a_tag['href']}"


def get_all_categories(soup: BeautifulSoup) -> dict:
     result = {
          "z": [],
          "sub": [],
          "catid": [],
          "catitemid": [],
     }
     for div_tag in soup.find_all("div", attrs={"class": "yui3-menu yui3-menu-hidden"}):
          for a_tag in div_tag.findChildren("a"):
               category_type, id_number = split_url_param(a_tag["href"])
               result[category_type].append(id_number)
     return result


def get_current_categories(soup: BeautifulSoup) -> list:
     result = []
     for div_tag in soup.find_all("div", attrs={"class": "yui3-menu-label"}):
          for a_tag in div_tag.findChildren("a"):
               result.append({
                    "url": f"{BASE_URL}{a_tag['href']}",
                    "text": a_tag.text
               })
     return result


def get_soup_by_category_type_and_id(category_type:str, id_number: str) -> BeautifulSoup:
     url = f"{BASE_URL}/?{category_type}={id_number}"
     item_url = get_first_item_url(url)
     return get_soup_by_url(item_url)


def get_best_item_of_cateitems(id_number):
     soup = get_soup_by_category_type_and_id("catitemid", id_number)
     return get_best_items_info(soup)


def get_best_item_by_catitemid(catitemid_iter: iter) -> list:
     result = []
     for id_number in catitemid_iter:
          result.append(get_best_item_of_cateitems(id_number))
          break
     return result


def get_refreshed_iter(category_type: str, id_number: str, iter_key_name: str) -> iter:
     soup = get_soup_by_category_type_and_id(category_type, id_number)
     refreshed_result = get_all_categories(soup)
     return iter(refreshed_result[iter_key_name])


def main(item_url):
     soup = get_soup_by_url(item_url)
     category_result = get_all_categories(soup)

     z_iter = iter(category_result["z"])
     sub_iter = iter(category_result["sub"])
     catid_iter = iter(category_result["catid"])
     catitemid_iter = iter(category_result["catitemid"])

     result = []

     for z in z_iter:
          for sub in sub_iter:
               for catid in catid_iter:
                    result += get_best_item_by_catitemid(catitemid_iter)

                    # refresh `catitemid`
                    catitemid_iter = get_refreshed_iter("catid", catid, "catitemid")
                    break
               # refresh `catid`
               catid_iter = get_refreshed_iter("sub", sub, "catid")
               break
          # refresh `sub`
          sub_iter = get_refreshed_iter("z", z, "sub")
          break

     print(result)
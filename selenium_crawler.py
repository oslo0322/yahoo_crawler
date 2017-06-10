from contextlib import contextmanager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from constant import BASE_URL, QUERY_TIME_INTERVAL


def find_first_item(href):
    if href and "gdsale" in href:
        return href


@contextmanager
def browser_helper():
    browser = webdriver.Chrome("./chromedriver")
    try:
        yield browser
    finally:
        browser.quit()


def get_first_item(browser, link):
    browser.get(link)
    browser.execute_script("window.scrollTo(0, 1500);")
    element_present = EC.presence_of_element_located((By.CLASS_NAME, 'recmdbillboard'))
    WebDriverWait(browser, QUERY_TIME_INTERVAL).until(element_present)

    for i in browser.find_elements_by_tag_name("a"):
        href = i.get_property("href")
        if find_first_item(href):
            return href


def go_to_best(browser, link):
    browser.get(link)
    for element in browser.find_elements_by_id("cl-ordrank"):
        best = element.find_elements_by_xpath("//li[@pos='1']/a[@class='yui3-u-1 desc']")
        if not best:
            # refresh and re-get
            return go_to_best(browser, link)
        best[0].click()
        return browser


def get_best_item_price(browser):
    element = browser.find_elements_by_xpath("//div[@class='priceinfo']/span[@class='price']")
    if element:
         return element[0].get_attribute("innerHTML")


def init_browser():
    with browser_helper() as browser:
        first_link = get_first_item(browser, BASE_URL)
        best_object = go_to_best(browser, first_link)
        price = get_best_item_price(best_object)


if __name__ == '__main__':
    init_browser()

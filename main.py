from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import gspread
import logging



logging.basicConfig(filename=str((time.strftime("""%d.%m.%Y_%H%M%S""", (time.localtime()))) + '_Log.log'), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def getDominosMainPage(url):
    logging.info("getting Url")
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    try:
        logging.info("trying to find pizza lists last child")
        pizzaListLastChld = driver.find_element(By.CSS_SELECTOR, "#pizzaList > div:last-child")
        time.sleep(1)
    except FileNotFoundError:
        logging.info('Pizza lists last child not found')

    pizzaList = driver.find_elements(By.CSS_SELECTOR, "#pizzaList > div")
    viewAllPizzaList(driver, pizzaList, pizzaListLastChld)

    #Получение HTML разметки
    html = driver.page_source
    return html

def viewAllPizzaList(driver, range, pizzaListLastChld):
    pizzaList = driver.find_elements(By.CSS_SELECTOR, "#pizzaList > div")
    logging.info("scrolling to pizza list last child")
    driver.execute_script("arguments[0].scrollIntoView();", pizzaListLastChld)
    time.sleep(0.5)
    if len(pizzaList) == range:
        logging.debug("all pizza list viewed")
    else:
        viewAllPizzaList(driver, len(pizzaList), pizzaListLastChld)

def htmlParseToProduct(html):
    product = pd.DataFrame()
    try:
        logging.info("trying to find all pizza cards")
        cardsSoup = BeautifulSoup(html, 'html.parser').find_all("div", {"class": "sc-1g5me89-12 lkFkIu"})
    except:
        logging.debug("can't find")
    try:
        logging.info("trying to filter data on cards")
        for item in cardsSoup:
            card = item.find("div", {"class": "sc-1g5me89-5 jOYAjO"})
            try:
                price = item.find("div", {"sc-1g5me89-16 jRHKei"}).text
            except:
                price = " "
            pizzaRow = [[card.text, price]]
            pizzaDF = pd.DataFrame(pizzaRow, columns=['Names', 'Prices'])
            product = pd.concat([product, pizzaDF], ignore_index=True)
    except ModuleNotFoundError:
        logging.debug("can't filter")

    allProduct = [product.columns.values.tolist()] + product.values.tolist()
    return allProduct


def uploadToGTable(serviceAccount, tableName, data):
    gc = gspread.service_account(filename=serviceAccount)

    sh = gc.open(tableName)
    sh.sheet1.clear()
    sh.sheet1.update(data)

data = htmlParseToProduct(getDominosMainPage('https://dominospizza.ru/'))
uploadToGTable('ringed-trail-360313-722fa45f047d.json', "DominosPizzaAllProd", data)
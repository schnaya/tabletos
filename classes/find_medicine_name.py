import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import re

def get_product_name(gtin):
    """Извлекает наименование товара из сайта gepir.gs1by.by по его GTIN коду.

    Args:
        gtin (str): GTIN код товара.

    Returns:
        str: Наименование товара или None, если не найдено.
    """

    # Настройка драйвера Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    browser = webdriver.Chrome("C:\\chromedriver.exe", options=options)

    # Открытие сайта gepir.gs1by.by
    browser.get("http://gepir.gs1by.by/Home/SearchByGtin")

    # Ввод GTIN кода
    input_element = browser.find_element_by_id('keyValue')
    input_element.send_keys(gtin)

    # Выбор типа запроса "О товаре"
    select_element = browser.find_element_by_id('requestTradeItemType')
    select = Select(select_element)
    select.select_by_visible_text('О товаре')

    # Отправка запроса
    button_element = browser.find_element_by_id('submit-button')
    button_element.click()

    # Ожидание загрузки страницы
    time.sleep(3)

    # Получение HTML кода блока ответа
    response_text = browser.execute_script("return arguments[0].outerHTML;",  browser.find_element_by_id('response'))

    # Шаблон для поиска строки
    pattern = (r"<td>Наименование товара<\/td>")

    # Поиск строки в HTML коде
    match = re.search(pattern, response_text)

    if match:
        # Извлечение наименования товара
        start = match.end() + re.search("<td>", response_text[match.end():]).end()
        finish = match.end()+re.search("</td>",response_text[match.end():]).start()
        next_line = response_text[start:finish]
        browser.quit()
        return next_line
    else:
        browser.quit()
        return None

# Пример использования
gtin_code = "4810201015620"
product_name = get_product_name(gtin_code)

if product_name:
    print(f"Наименование товара: {product_name}")
else:
    print(f"Товар с GTIN {gtin_code} не найден.")
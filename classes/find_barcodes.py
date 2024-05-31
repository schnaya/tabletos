import os
import re
import shutil
import time
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import re
from pyzxing import BarCodeReader
import pandas as pd

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
def find_barcodes_in_folder(folder_path):
    reader = BarCodeReader()
    data = []

    # Получение списка всех изображений в папке
    all_images = [f for f in os.listdir(folder_path) if f.endswith(".png") or f.endswith(".jpg")]

    for filename in all_images:
        image_path = os.path.join(folder_path, filename)
        results = reader.decode(image_path)
        if results:
            for result in results:
                # Если в результате больше информации, чем просто имя файла
                if len(result) > 1:
                    barcode_type = str(result.get('format', None))
                    if barcode_type == "b'EAN_13'":
                        barcode_text = ""
                        for c in str(result.get('raw', None)):
                            if c.isdigit():
                                barcode_text += c
                        name = get_product_name(barcode_text)
                        data.append([barcode_text, name, barcode_type, filename])

    return data

def save_to_csv(data, csv_file):
    # Создание DataFrame
    df = pd.DataFrame(data, columns=['Barcode','Name', 'Type', 'Image_with_code'])

    # Если файл существует, добавляем строки без записи заголовка
    if os.path.isfile(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)
    else:  # Иначе создаем новый файл с заголовком
        df.to_csv(csv_file, index=False)

def create_barcode_folders(data, folder_path):
    all_images = [f for f in os.listdir(folder_path) if f.endswith(".png") or f.endswith(".jpg")]
    new_folder_path = os.path.join(folder_path, "barcodes")
    for barcode_text, _, _ in data:
        new_folder_path = os.path.join('images/database', barcode_text)
        os.makedirs(new_folder_path, exist_ok=True)
        for img in all_images:
            shutil.copy(os.path.join(folder_path, img), new_folder_path)
    return new_folder_path



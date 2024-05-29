import os
import shutil
from pyzxing import BarCodeReader
import pandas as pd


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
                        data.append([barcode_text, barcode_type, filename])

    return data

def save_to_csv(data, csv_file):
    # Создание DataFrame
    df = pd.DataFrame(data, columns=['Barcode', 'Type', 'Image_with_code'])

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



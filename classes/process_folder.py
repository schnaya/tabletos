import os
import cv2
import pillow_heif

import classes.polygon_detection as poly_detection
from PIL import Image
import classes.image_processing as ip
def process_image(folder_path, filename):
    load_image = cv2.imread(os.path.join(folder_path, filename))
    my_polygon = poly_detection.polygon_detection(load_image )
    countour = my_polygon.mark_polygon()
    cropped_image = ip.crop_contour(cv2.imread(os.path.join(folder_path, filename)), countour)

    output_path = "images/boxes/result/cropped_"+os.path.split(folder_path)[1]
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if cropped_image is not None and not cropped_image.size == 0:
        cv2.imwrite(os.path.join(output_path, filename), cropped_image)
    else:
        print("Изображение для записи пустое или не инициализировано")

    return os.path.join(output_path,filename)



def process_folder(folder_path):
    filenames = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Если файл в формате HEIC
        if filename.endswith(".HEIC"):
            # Чтение файла HEIC
            heif_file = pillow_heif.read_heif(file_path)
            # Конвертация в объект изображения PIL
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
            # Сохранение изображения в формате PNG
            filename = filename.replace(".HEIC", ".png")
            png_file_path = os.path.join(folder_path, filename)
            image.save(png_file_path)
            # Удаление исходного файла HEIC
            os.remove(file_path)
            # Обработка изображения
            filenames.append(process_image(folder_path, filename))
        elif filename.endswith(".jpg") or filename.endswith(".png"): # проверка формата файла
            filenames.append(process_image(folder_path, filename))
    return "images/boxes/result/cropped_"+os.path.split(folder_path)[1]
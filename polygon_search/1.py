import os
import cv2
import numpy as np

def mark_polygon(path):
    # Загрузка изображения
    image = cv2.imread(path)
    # Преобразование изображения в оттенки серого
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(grayscale_image, 75, 250, cv2.THRESH_BINARY)
    # Поиск всех контуров
    all_contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(c) for c in all_contours]
    max_index = np.argmax(areas)
    cnt = all_contours[max_index]
    approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)

    return image, approx
def process_images_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"): # проверка формата файла
            image_path = os.path.join(folder_path, filename)
            image, approx = mark_polygon(image_path)
            y = [elem for i in (approx[:,:,1]) for elem in i]
            x = [elem for i in (approx[:,:,0]) for elem in i]
            x.sort()
            y.sort()
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_dub = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            cropped_image = image_dub[y[1]:y[2], x[1]:x[2]]
            output_path = os.path.join("images/boxes/result/antigrip", 'cropped_' + filename)
            print(output_path)
            cv2.imwrite(output_path, cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR))

# вызов функции
process_images_in_folder("images/boxes/antigrip")

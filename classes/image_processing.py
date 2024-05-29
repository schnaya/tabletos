import re
import cv2
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from sklearn.cluster import KMeans


def add_mask(image,num_pixels=100):
    """
    Функция для добавления маски к изображению на основе цветов на границе изображения.

    Параметры:
    image (numpy.ndarray): Исходное изображение в формате BGR.

    Возвращает:
    image (numpy.ndarray): Изображение с примененной маской.
    """

    def process_border(border):
        border_pixels = np.unique(border.reshape(-1, 3), axis=0)
        if len(border_pixels) >500:
            border_pixels= border_pixels[:500//2]
        masks = []
        for color in border_pixels:
            color = cv2.cvtColor(np.uint8(color).reshape(1, 1, 3), cv2.COLOR_BGR2HSV)[0][0]
            # Вычисление динамического диапазона на основе цвета
            dynamic_range = np.std(color)
            lower_bound = color - np.array([20, dynamic_range, dynamic_range])
            upper_bound = color + np.array([20, 255 - dynamic_range, 255 - dynamic_range])
            masks.append(cv2.inRange(hsv_image, lower_bound, upper_bound))
        return np.sum(masks, axis=0)
    # Выбор цветов на границе изображения
    borders = [image[:4*num_pixels:, :], image[-4*num_pixels::, :], image[:, :num_pixels:], image[:, -num_pixels::]]
    # Преобразование исходного изображения из BGR в HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Создание маски на основе цветов границы
    mask = np.zeros_like(hsv_image[:, :, 1])
    mask[mask == 0] = 255
    # Сначала добавляем пиксели границ в маску
    for border in borders:
        mask[np.where((border != [0, 0, 0]).all(axis=2))] = 0

    # Создание массива половин границ
    half_borders1 = [border[:, border.shape[1] // 2:] for border in borders]
    half_borders2 = [border[:, border.shape[1] // 2 ] for border in borders]

    # Распределение половин границ по двум потокам
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures1 = [executor.submit(process_border, border) for border in half_borders1]
        futures2 = [executor.submit(process_border, border) for border in half_borders2]

        for future in futures1:
            result = future.result()
            mask[result > 0] = 0

        for future in futures2:
            result = future.result()
            mask[result > 0] = 0
    # Установка в 0 только тех пикселей, которые соответствуют цветам границы
    # Применение маски к исходному изображению
    result = cv2.bitwise_and(image, image, mask=mask)

    return result



def add_sobel(image):
    """
    Функция для применения оператора Собеля к изображению.

    Параметры:
    image (numpy.ndarray): Исходное изображение в формате BGR.

    Возвращает:
    image (numpy.ndarray): Изображение после применения оператора Собеля.
    """
    # Применение оператора Собеля по оси X
    sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=5)
    # Применение оператора Собеля по оси Y
    sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=5)
    # Суммирование результатов применения оператора Собеля по обеим осям
    return sobel_x + sobel_y


def grayscale_and_threshold(image):
    """
    Функция для преобразования изображения в оттенки серого и применения бинаризации.

    Параметры:
    image (numpy.ndarray): Исходное изображение в формате BGR.

    Возвращает:
    binary_image (numpy.ndarray): Бинаризованное изображение.
    """
    # Преобразование изображения в оттенки серого
    grayscale_image = cv2.cvtColor(cv2.convertScaleAbs(image), cv2.COLOR_BGR2GRAY)
    # Применение адаптивного порогового значения для бинаризации изображения
    _, binary_image = cv2.threshold(grayscale_image, 100, 255, cv2.THRESH_BINARY)
    return binary_image



def find_contour(image):
    """
    Функция для поиска контуров.

    Параметры:
    image (numpy.ndarray): Исходное изображение.

    Возвращает:
    contour (numpy.ndarray): Контур, образованный нижним левым и верхним правым нечерным пикселем.
    """

    # Находим индексы всех нечерных пикселей
    # Добавляем дополнительный край вокруг изображения
    padded_image = np.pad(image, pad_width=2, mode='constant', constant_values=0)

    # Находим ненулевые пиксели
    non_black_pixels = np.where(padded_image > 20)

    # Проверяем, есть ли вокруг ненулевых пикселей другие ненулевые пиксели
    valid_pixels = []
    for y, x in zip(*non_black_pixels):
        # Проверяем соседние пиксели
        neighborhood = padded_image[y - 2:y + 10, x - 10:x + 3]
        if np.all(neighborhood != 0):
            valid_pixels.append((y, x))

    # Преобразуем список в numpy массив
    valid_pixels = np.array(valid_pixels)

    # Находим верхний левый и нижний правый пиксели
    upper_left = np.min(valid_pixels, axis=0)
    lower_right = np.max(valid_pixels, axis=0)

    # Создаем контур
    contour = np.array([upper_left, [upper_left[0], lower_right[1]], lower_right, [lower_right[0], upper_left[1]]])
    return contour

def crop_contour(image, contour):
    """
    Функция для обрезки изображения по контуру.

    Параметры:
    image (numpy.ndarray): Исходное изображение.
    contour (numpy.ndarray): Контур.

    Возвращает:
    cropped_image (numpy.ndarray): Обрезанное изображение.
    """

    y = contour[:, 1]
    x =contour[:, 0]
    # Сортировка координат
    x.sort()
    y.sort()
    # Обрезка изображения по контуру
    return image[x[1]:x[2], y[1]:y[2]]



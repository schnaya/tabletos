import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import image_processing as ip
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


path = "../images/views/IMG_9424.JPG"
filename = "../images/database/4810201015620/4810201015620_keypoints.txt"

image = (cv2.imread(path))
sift = cv2.SIFT_create()
keypoints, descriptors = sift.detectAndCompute(image, None)

# Загрузка данных из файла
def process_line(parts, keypoints_dict, filename):
    """Обрабатывает строку из файла ключевых точек и добавляет данные в словарь.

    Args:
        parts: Список слов, полученный из разделения строки файла.
        keypoints_dict: Словарь, хранящий данные по изображениям.
        filename: Имя файла, из которого получена строка.
    """

    if len(parts) < 5:
        # Если строка содержит информацию о размере изображения
        keypoints_dict[filename]['shape'] = [int(parts[1]), int(parts[2])]
    else:
        # Если строка содержит информацию о ключевой точке
        x, y, size, angle, octave, response = map(float, parts[1:7])
        desc = np.array(list(map(float, parts[7:])))
        keypoints_dict[filename]['keypoints'].append(
            cv2.KeyPoint(x, y, size, angle, octave=int(octave), response=response)
        )
        keypoints_dict[filename]['descriptors'].append(desc)

def load_keypoints_and_descriptors(filename):
    """Загружает ключевые точки и дескрипторы из файла.

    Args:
        filename: Путь к файлу с ключевыми точками.

    Returns:
        Словарь, содержащий данные по изображениям (ключевые точки, дескрипторы, размеры).
    """
    keypoints_dict = {}
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            filename = parts[0]
            if filename not in keypoints_dict:
                keypoints_dict[filename] = {'keypoints': [], 'descriptors': [], 'shape': []}
            process_line(parts, keypoints_dict, filename)

    # Преобразование дескрипторов в NumPy массивы
    for key in keypoints_dict:
        arr = np.zeros((len(keypoints_dict[key]['descriptors']), 128))
        for i, line in enumerate(keypoints_dict[key]['descriptors']):
            for j, n in enumerate(line):
                arr[i][j] = n
        keypoints_dict[key]['descriptors'] = arr

    return keypoints_dict

def find_matches(keypoints_by_image, descriptors):
    """Находит соответствия ключевых точек между изображениями."""
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=21)
    search_params = dict(checks=300)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    Matches = {}  # Словарь для хранения совпадений по файлам
    Matches_kp = {}  # Словарь для хранения ключевых точек из файлов
    kp = {}  # Словарь для хранения ключевых точек из текущего изображения
    for filename, data in keypoints_by_image.items():
        train_descriptors = data['descriptors'].astype(np.float32)
        match = flann.knnMatch(train_descriptors, descriptors, k=2)
        Matches[filename] = []  # Создаем пустой список для совпадений этого файла
        Matches_kp[filename] = []  # Создаем пустой список для ключевых точек этого файла
        kp[filename] = []  # Создаем пустой список для ключевых точек текущего изображения (для этого файла)
        for m, n in match:
            if m.distance < 0.5 * n.distance:
                Matches[filename].append([m, n])  # Добавляем совпадения в список для этого файла
                Matches_kp[filename].append(data['keypoints'][m.queryIdx])  # Добавляем ключевые точки из файла
                kp[filename].append(keypoints[n.trainIdx])  # Добавляем ключевые точки из текущего изображения
    return Matches, Matches_kp, kp


import cv2
import numpy as np
import os

def find_homography_and_filter_matches(image, Matches, Matches_kp, kp, keypoints_dict):
    """Находит гомографию и фильтрует совпадения, не попадающие в прямоугольник."""

    mask = np.zeros_like(image, dtype=np.uint8)  # Initialize the mask outside the loop
    matchesMask = (mask == 0).astype(np.uint8).ravel()
    for filename in Matches:

        # Create a mask with the same size as Matches[filename]
        matchesMask = matchesMask[:len(Matches[filename])]
        Matches[filename] = np.array(Matches[filename])[matchesMask == 1].tolist()
        Matches_kp[filename] = np.array(Matches_kp[filename])[matchesMask == 1].tolist()
        kp[filename] = np.array(kp[filename])[matchesMask == 1].tolist()
        while len(Matches[filename]) > 15:
            if len(Matches_kp[filename]) != len(kp[filename]):
                print(f"Ошибка: количество точек в Matches_kp и kp не совпадает для файла {filename}.")
                break
            src_pts = np.float32([m.pt for m in Matches_kp[filename]]).reshape(-1, 1, 2)
            dst_pts = np.float32([m.pt for m in kp[filename]]).reshape(-1, 1, 2)
            if src_pts.shape != dst_pts.shape:
                print(f"Ошибка: src_pts и dst_pts должны иметь одинаковую форму для файла {filename}.")
                break
            img = image.copy()
            for pt in dst_pts:
                cv2.circle(img, (int(pt[0][0]), int(pt[0][1])), 15, (0, 0, 255), -1)  # Red circles for Matches_kp
            plt.imshow(img)
            plt.show()
            # Calculate homography
            M, mask_tmp = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            # Get image dimensions from keypoints_dict
            h, w = keypoints_dict[filename]['shape'][0], keypoints_dict[filename]['shape'][1]
            # Create a rectangle with the image dimensions
            rect_pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            # Transform the rectangle using the found homography
            transformed_rect = cv2.perspectiveTransform(rect_pts, M)
            # Draw the rectangle on the image
            img2 = cv2.polylines(image.copy(), [np.int32(transformed_rect)], True, 150, 20, cv2.LINE_AA)

            # Update the mask with the new rectangle
            cv2.fillPoly(mask, [np.int32(transformed_rect)], (255, 255, 255))

            # Filter matches using NumPy indexing:
            matchesMask = (mask == 255).astype(np.uint8).ravel()
            # Create a mask with the same size as Matches[filename]
            matchesMask = matchesMask[:len(Matches[filename])]
            Matches[filename] = np.array(Matches[filename])[matchesMask == 1].tolist()
            Matches_kp[filename] = np.array(Matches_kp[filename])[matchesMask == 1].tolist()
            kp[filename] = np.array(kp[filename])[matchesMask == 1].tolist()

            plt.imshow(img2)
            plt.show()

    return Matches, Matches_kp, kp



def draw_keypoints(image, Matches_kp, kp, img2):
    """Рисует ключевые точки на изображении."""
    flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS + cv2.DRAW_MATCHES_FLAGS_DEFAULT
    img2 = cv2.drawKeypoints(image, Matches_kp, img2, color=(255, 0, 255), flags=flags)
    img2 = cv2.drawKeypoints(image, kp, img2, color=(255, 255, 0), flags=flags)
    return img2

keypoints_by_image = load_keypoints_and_descriptors(filename)
Matches = {}
Matches_kp = {}
kp = {}

# Вызов функции find_matches
Matches, Matches_kp, kp = find_matches(keypoints_by_image, descriptors)

find_homography_and_filter_matches(image, Matches, Matches_kp, kp, keypoints_by_image)

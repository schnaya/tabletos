import cv2
import os

def create_keypoints_file(image_folder):
    # Инициализация детектора SIFT
    sift = cv2.SIFT_create()

    # Создание общего файла для ключевых точек и дескрипторов
    output_filename = os.path.join(image_folder, os.path.split(image_folder)[-1] + '_keypoints.txt')
    with open(output_filename, 'w') as f:
        for filename in os.listdir(image_folder):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                image_path = os.path.join(image_folder, filename)
                image = cv2.imread(image_path)
                f.write(f"{filename} {image.shape[0]} {image.shape[1]}\n")
                # Вычисление ключевых точек и дескрипторов
                keypoints, descriptors = sift.detectAndCompute(image, None)

                # Запись в общий файл
                for kp, desc in zip(keypoints, descriptors):
                    f.write(f"{filename} {kp.pt[0]} {kp.pt[1]} {kp.size} {kp.angle} {kp.octave} {kp.response} {' '.join(map(str, desc))}\n")

    print(f"Создан общий файл {output_filename} с информацией о ключевых точках, дескрипторах и октавах.")


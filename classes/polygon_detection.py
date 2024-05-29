from matplotlib import pyplot as plt

import classes.image_processing as image_processing


class polygon_detection:
    def __init__(self, image=None, background_hex_color=None):
        self.image = image
        self.background_hex_color = background_hex_color

    def mark_polygon(self):
        # Загрузка изображения
        image = image_processing.add_mask(self.image)
        image = image_processing.add_sobel(image)
        bin_image = image_processing.grayscale_and_threshold(image)
        countour = image_processing.find_contour(bin_image)
        plt.imshow(image)
        plt.show()
        del image,bin_image
        # Возвращение исходного изображения и аппроксимированного контура
        return countour

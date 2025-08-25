import cv2
import numpy as np

class ImageProcessor:
 
    # creates an image object from a file path
    def __init__(self, name, path):
        self.path = path
        self.image = cv2.imread(path, 1)
        if self.image is None:
            raise FileNotFoundError(f"Could not load image from {path}")
 
    # replaces the current image with a new one
    def upload(self, user_path):
        self.path = user_path
        self.image = cv2.imread(user_path, 1)
        if self.image is None:
            raise FileNotFoundError(f"Could not load image from {user_path}")
 
    # saves image to either default or user specified path, default path will override the original image (I believe)
    def save(self, user_path=None):
        if user_path is None:
            user_path = self.path
        if not cv2.imwrite(user_path, self.image):
            raise IOError(f"Could not save image to {user_path}")
 
    # displays image with all currently applied edits
    def display(self):
        if self.image is None:
            raise ValueError("No image has been uploaded. Use upload() first.")
        cv2.imshow('Current Image', self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
 
    # resize image to provided pixel size
    def resize_pixel(self, x, y):
        self.image = cv2.resize(self.image, (x, y))
 
    # resize image using provided ratios
    def resize_ratio(self, x, y):
        self.image = cv2.resize(self.image, (0, 0), fx = x, fy = y)
 
    # crop image using a box select tool
    def crop(self):
        roi = cv2.selectROI("Select ROI", self.image, False)
        self.image = self.image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
 
    # rotate image clockwise by 90 degrees
    def rotate_90(self):
        self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
 
    # rotate image by 180 degrees
    def rotate_180(self):
        self.image = cv2.rotate(self.image, cv2.ROTATE_180)

    # flip image on x-axis
    def flip_on_x(self):
        self.image = cv2.flip(self.image, 0)
 
    # flip image on y-axis
    def flip_on_y(self):
        self.image = cv2.flip(self.image, 1)
 
    # flip image on both axes
    def flip_on_xy(self):
        self.image = cv2.flip(self.image, -1)
 
    # blur image, the higher the blur_amount, the stronger the blur
    def blur(self, blur_amount):
        kernel = (blur_amount, blur_amount)
        self.image = cv2.blur(self.image, kernel)
 
    # sharpen image
    def sharpen(self):
        kernel = np.array([
            [-1, -1, -1],
            [-1, 9, -1],
            [-1, -1, -1]
        ])
        self.image = cv2.filter2D(self.image, -1, kernel)
 
    # apply grayscale filter to image
    def grayscale(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
 
    # apply sepia filter to image
    def sepia(self):
        kernel = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ])
        self.image = cv2.transform(self.image, kernel)
        self.image = np.clip(self.image, 0, 255).astype(np.uint8)
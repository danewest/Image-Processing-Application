import cv2
import numpy as np
import os

class ImageProcessor:

    # creates an image object from a file path
    def __init__(self, name, path):
        self.path = path
        self.image = cv2.imread(path, 1)
        if self.image is None:
            raise FileNotFoundError(f"Could not load image from {path}")
        
    # check that an image has been uploaded
    def _confirm_upload(self):
        if self.image is None:
            raise ValueError("No image has been uploaded. Use upload() first.")
 
    # replaces the current image with a new one
    def upload(self, user_path):
        self.path = user_path
        self.image = cv2.imread(user_path, 1)
        if self.image is None:
            raise FileNotFoundError(f"Could not load image from {user_path}")
 
    # saves image to either default or user specified path, default path will override the original image (I believe)
    def save(self, user_path=None):
        self._confirm_upload()
        if user_path is None:
            raise ValueError("No output path specified. Use -o or --output to set one.")
        os.makedirs(os.path.dirname(user_path), exist_ok=True)
        if not cv2.imwrite(user_path, self.image):
            raise IOError(f"Could not save image to {user_path}")
 
    # displays image with all currently applied edits
    def display(self):
        self._confirm_upload()
        cv2.imshow('Current Image', self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
 
    # resize image to provided pixel size
    def resize_pixel(self, x, y):
        self._confirm_upload()
        self.image = cv2.resize(self.image, (x, y))
 
    # resize image using provided ratios
    def resize_ratio(self, x, y):
        self._confirm_upload()
        self.image = cv2.resize(self.image, (0, 0), fx = x, fy = y)
 
    # crop image using a box select tool
    def crop(self, roi=None):
        self._confirm_upload()
        if roi is None:
            # normal interactive mode
            roi = cv2.selectROI("Select ROI", self.image, False)
        if roi[2] == 0 or roi[3] == 0:
            raise ValueError("Invalid ROI selected")
        x, y, w, h = roi
        self.image = self.image[y:y+h, x:x+w]
 
    # rotate image clockwise by 90 degrees
    def rotate_90(self):
        self._confirm_upload()
        self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
 
    # rotate image by 180 degrees
    def rotate_180(self):
        self._confirm_upload()
        self.image = cv2.rotate(self.image, cv2.ROTATE_180)

    # flip image on x-axis
    def flip_on_x(self):
        self._confirm_upload()
        self.image = cv2.flip(self.image, 0)
 
    # flip image on y-axis
    def flip_on_y(self):
        self._confirm_upload()
        self.image = cv2.flip(self.image, 1)
 
    # flip image on both axes
    def flip_on_xy(self):
        self._confirm_upload()
        self.image = cv2.flip(self.image, -1)
 
    # blur image, the higher the blur_amount, the stronger the blur
    def blur(self, blur_amount):
        self._confirm_upload()
        kernel = (blur_amount, blur_amount)
        self.image = cv2.blur(self.image, kernel)
 
    # sharpen image
    def sharpen(self):
        self._confirm_upload()
        kernel = np.array([
            [-1, -1, -1],
            [-1, 9, -1],
            [-1, -1, -1]
        ])
        self.image = cv2.filter2D(self.image, -1, kernel)
 
    # apply grayscale filter to image
    def grayscale(self):
        # If image already has only 2 dimensions it's grayscale
        if len(self.image.shape) == 2:
            return self.image
    
        # If it has 3 channels convert to grayscale
        if len(self.image.shape) == 3 and self.image.shape[2] == 3:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        return self.image
 
    # apply sepia filter to image
    def sepia(self):
        self._confirm_upload()

        # Make image is 3 channels
        if len(self.image.shape) == 2 or self.image.shape[2] == 1:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
        
        kernel = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ])
        self.image = cv2.transform(self.image, kernel)
        self.image = np.clip(self.image, 0, 255).astype(np.uint8)
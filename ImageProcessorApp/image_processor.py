import cv2
import numpy as np
import argparse as ap
from PIL import Image
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
            user_path = self.path
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
    def crop(self):
        self._confirm_upload()
        roi = cv2.selectROI("Select ROI", self.image, False)
        self.image = self.image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
 
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
        self._confirm_upload()
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
 
    # apply sepia filter to image
    def sepia(self):
        self._confirm_upload()
        kernel = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ])
        self.image = cv2.transform(self.image, kernel)
        self.image = np.clip(self.image, 0, 255).astype(np.uint8)

def main():
    
    # Parser creation
    parser = ap.ArgumentParser(description="A command line-based image processing application.")

    # Adding parser arguments for different functions of the program
    parser.add_argument("-i", "--input", nargs="+", required=True, help="Input image path(s).")
    parser.add_argument("-o", "--output", help="Output image path (if not provided, overwrites input).")
    parser.add_argument("-r90", "--rotate90", action="store_true", help="Rotates an image 90 degrees clockwise.")
    parser.add_argument("-r180", "--rotate180", action="store_true", help="Rotates an image 180 degrees clockwise.")
    parser.add_argument("-x", "--flipx", action="store_true", help="Flips image on the x-axis.")
    parser.add_argument("-y", "--flipy", action="store_true", help="Flips image on the y-axis.")
    parser.add_argument("-xy", "--flipxy", action="store_true", help="Flips image on both the x and y axises.")
    parser.add_argument("-b", "--blur", type=int, help="Blurs image.")
    parser.add_argument("-sh", "--sharpen", action="store_true", help="Sharpens image.")
    parser.add_argument("-g", "--grayscale", action="store_true", help="Applies grayscale filter.")
    parser.add_argument("-se", "--sepia", action="store_true", help="Applies sepia filter.")
    parser.add_argument("-c", "--crop", action="store_true", help="Crops image.")
    parser.add_argument("-rp", "--resize-pixel", nargs=2, type=int, help="Resizes image width and height by pixel count.")
    parser.add_argument("-rr", "--resize-ratio", nargs=2, type=float, help="Resizes image ratio by scale factors.")

    # Assigning the different arguments to the functions of the ImageProcessor class
    argument_to_function = {
        "rotate90": lambda proc, _: proc.rotate_90(),
        "rotate180": lambda proc, _: proc.rotate_180(),
        "flipx": lambda proc, _: proc.flip_on_x(),
        "flipy": lambda proc, _: proc.flip_on_y(),
        "flipxy": lambda proc, _: proc.flip_on_xy(),
        "blur": lambda proc, arg_value: proc.blur(int(arg_value)),
        "sharpen": lambda proc, _: proc.sharpen(),
        "grayscale": lambda proc, _: proc.grayscale(),
        "sepia": lambda proc, _: proc.sepia(),
        "crop": lambda proc, _: proc.crop(),
        "resize-pixel": lambda proc, vals: proc.resize_pixel(vals[0], vals[1]),
        "resize-ratio": lambda proc, vals: proc.resize_ratio(vals[0], vals[1])
    }

    args = parser.parse_args()

    # Takes the input file(s) and creates an image object for it
    for file in args.input:
        image = ImageProcessor("input", file)

        # Cycle through arguments
        for arg_name, func in argument_to_function.items():
            arg_value = getattr(args, arg_name, None)
            if arg_value:
                func(image, arg_value)
        
        # Save
        if args.output:
            if os.path.isdir(args.output) or args.output.endswith("/"):
                # user gave an output folder → generate filename
                os.makedirs(args.output, exist_ok=True)
                base_name = os.path.basename(file)   # e.g., "snorlax.jpg"
                out_path = os.path.join(args.output, base_name)
            else:
                # user gave a specific output file
                os.makedirs(os.path.dirname(args.output), exist_ok=True)
                out_path = args.output
            image.save(out_path)
    else:
        # overwrite original
        image.save()


if __name__ == "__main__":
    main()

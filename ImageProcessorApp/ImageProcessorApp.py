from image_processor import ImageProcessor
import argparse as ap
import os

def main():
    
    # Parser creation
    parser = ap.ArgumentParser(description="A command line-based image processing application.")

    # Adding parser arguments for different functions of the program
    parser.add_argument("-i", "--input", nargs="+", required=True, metavar="", help="Input image path(s).")
    parser.add_argument("-o", "--output", metavar="", required=True, help="Output image path (if not provided, overwrites input).")
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
    parser.add_argument("-rp", "--resize-pixel", nargs=2, type=int, metavar=("W", "H"), help="Resizes image width and height by pixel count.")
    parser.add_argument("-rr", "--resize-ratio", nargs=2, type=float, metavar=("X", "Y"), help="Resizes image ratio by scale factors.")

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
                name, ext = os.path.splitext(os.path.basename(file))
                out_name = f"{name}_edited{ext}"
                out_path = os.path.join(args.output, out_name)
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
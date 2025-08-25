import argparse

# create parser object
parser = argparse.ArgumentParser(description="Input Project Desc")

# add arguments
parser.add_argument("input_image", help="Path to the image to open")
parser.add_argument("output_image", help="Path to save the edited image")

# parse arguments
args = parser.parse_args()

# print for testing purposes
# print(args.input_image)
# print(args.output_image)
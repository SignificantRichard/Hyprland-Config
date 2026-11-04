from PIL import Image, ImageFilter
import os
import sys

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
print(script_directory)

# Open the image
img = Image.open(f"{script_directory}/../background/background")

# Scale down to 720p height while maintaining aspect ratio
target_height = 720
aspect_ratio = img.width / img.height
target_width = int(target_height * aspect_ratio)

# Use Image.Resampling.LANCZOS for high-quality downscaling
img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

# Apply Gaussian blur
blurred_img = img.filter(ImageFilter.GaussianBlur(radius=8))

# Save the result
blurred_img.save(f"{script_directory}/../background/ready.jpg")
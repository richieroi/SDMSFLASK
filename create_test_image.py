from PIL import Image, ImageDraw, ImageFont
import os

# Create directory if it doesn't exist
os.makedirs('static/images', exist_ok=True)

# Create a simple school-themed background
img = Image.new('RGB', (1920, 1080), color = (245, 245, 245))
d = ImageDraw.Draw(img)

# Draw some school elements (simple shapes)
d.rectangle([(200, 200), (1720, 880)], fill=(235, 235, 235), outline=(52, 152, 219))
d.text((960, 540), "School Management System", fill=(52, 152, 219), anchor="mm")

# Save the image
img.save('static/images/school1.png')

print("Test background image created in static/images/school1.png")

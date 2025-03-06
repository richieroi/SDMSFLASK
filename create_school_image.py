from PIL import Image, ImageDraw, ImageFont
import os

# Create directory if it doesn't exist
os.makedirs('static/images', exist_ok=True)

# Create a simple school-themed background
img = Image.new('RGB', (1920, 1080), color=(52, 152, 219))
d = ImageDraw.Draw(img)

# Draw some school elements
d.rectangle([(0, 0), (1920, 1080)], fill=(52, 152, 219))

# Add some simple geometric shapes for visual interest
for i in range(20):
    # Draw random rectangles
    x1 = i * 100
    y1 = i * 50
    x2 = x1 + 300
    y2 = y1 + 200
    d.rectangle([(x1, y1), (x2, y2)], fill=(41, 128, 185), outline=None)

# Add a simple school icon pattern
for x in range(0, 1920, 200):
    for y in range(0, 1080, 200):
        d.rectangle([(x+50, y+50), (x+150, y+150)], fill=(36, 113, 163), outline=None)

# Save as school.png
img.save('static/images/school.png')

print("School background image created in static/images/school.png")

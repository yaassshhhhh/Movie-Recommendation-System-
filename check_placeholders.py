import os

img_dir = 'static/images'
PLACEHOLDER_SIZE = 4838 # The size of the generic placeholder

print("Minimally sized images (likely placeholders):")
count = 0
for filename in os.listdir(img_dir):
    filepath = os.path.join(img_dir, filename)
    size = os.path.getsize(filepath)
    # Check if close to placeholder size (allow some small variance)
    if size < 5000: 
        print(f"- {filename} ({size} bytes)")
        count += 1

print(f"\nTotal potential placeholders: {count}")

# Check if PIL/Pillow is installed
python3 -c "from PIL import Image; print('PIL works')"

# If that fails, install it:
pip3 install Pillow

# Then try a simpler approach with raw output
python3 << 'EOF'
with open('signal.bin', 'rb') as f:
    data = f.read()

hint_end = 25
zip_start = 2100025
image_data = data[hint_end:zip_start]

print(f"Image data length: {len(image_data)}")
print(f"Should process: {len(image_data) // 5} pixels")

# Extract RGB using pattern 0,1,2 from each 5-byte chunk
pixels = []
for i in range(0, len(image_data)-4, 5):
    pixels.extend([image_data[i], image_data[i+1], image_data[i+2]])

print(f"Extracted {len(pixels)} bytes ({len(pixels)//3} pixels)")
print(f"For 480x875: need {480*875*3} bytes")
print(f"For 500x840: need {500*840*3} bytes")

# Write raw RGB data
with open('raw_480x875.rgb', 'wb') as f:
    f.write(bytes(pixels[:480*875*3]))
print("Wrote raw_480x875.rgb")

with open('raw_500x840.rgb', 'wb') as f:
    f.write(bytes(pixels[:500*840*3]))
print("Wrote raw_500x840.rgb")
EOF

# Convert raw RGB to PNG using ImageMagick or ffmpeg
convert -size 480x875 -depth 8 rgb:raw_480x875.rgb output_480x875.png
convert -size 500x840 -depth 8 rgb:raw_500x840.rgb output_500x840.png

# Or with ffmpeg:
ffmpeg -f rawvideo -pixel_format rgb24 -video_size 480x875 -i raw_480x875.rgb output_480x875.png
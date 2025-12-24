#!/usr/bin/env python3
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

main_text = 'HIMNARIO'
subtitle = 'Misión Bíblica de la Gracia'
main_font_size = 190
subtitle_font_size = 70

# Get main text from command line or use default
if len(sys.argv) > 1:
  main_text = sys.argv[1] # Hymn number
  main_font_size = 400 # Larger font for hymn number

# Image dimensions for social media (1200x630)
width, height = 1200, 630
background_color = (44, 62, 80)  # #2C3E50 - Dark blue-gray
text_color = (236, 240, 241)     # #ECF0F1 - Light gray
subtitle_color = (160, 170, 175) # #A0AAAF - Darker gray

# Create image
img = Image.new('RGB', (width, height), background_color)
draw = ImageDraw.Draw(img)

# Load fonts
try:
    main_font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', main_font_size)
    subtitle_font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', subtitle_font_size)
except:
    main_font = ImageFont.load_default()
    subtitle_font = main_font

# Calculate text dimensions
main_bbox = draw.textbbox((0, 0), main_text, font=main_font)
main_width = main_bbox[2] - main_bbox[0]
main_height = main_bbox[3] - main_bbox[1]

subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]

# Calculate spacing and total block height
spacing = 100 if len(sys.argv) > 1 else 40
total_height = main_height + spacing + subtitle_height

# Center the entire block vertically
block_y = (height - total_height) // 2

# Draw main text (centered horizontally)
main_x = (width - main_width) // 2
main_y = block_y
draw.text((main_x, main_y), main_text, fill=text_color, font=main_font)

# Draw subtitle (centered horizontally, below main text)
subtitle_x = (width - subtitle_width) // 2
subtitle_y = main_y + main_height + spacing
draw.text((subtitle_x, subtitle_y), subtitle, fill=subtitle_color, font=subtitle_font)

# Determine output path (scripts/ -> static/images/)
script_dir = Path(__file__).parent
output_dir = script_dir.parent / 'static' / 'images'
output_dir.mkdir(parents=True, exist_ok=True)

# Output filename based on main_text
if len(sys.argv) > 1:
    hymn_num = int(main_text)
    output_path = output_dir / f'hymn-{hymn_num:03d}.jpg'
else:
    output_path = output_dir / 'hymns-social.jpg'

# Save image
img.save(output_path, 'JPEG', quality=95)
print(f'✓ Created {output_path} (1200x630 pixels)')

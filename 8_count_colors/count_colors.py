import random
import string
from PIL import Image, ImageDraw, ImageFont
import os
import argparse

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Generate an image with colored text.')
    parser.add_argument('--text_size', type=int, default=5, help='Number of color words to display (default: 5)')
    parser.add_argument('--count', type=int, default=1, help='Number of images to generate (default: 1)')
    args = parser.parse_args()
    
    # Get the word count from arguments (with a reasonable limit)
    word_count = max(1, min(args.text_size, 5))  # Limit between 1 and 5 words
    
    # Get the number of images to generate
    image_count = max(1, args.count)  # Ensure at least 1 image is generated
    
    # Define colors with their names and RGB values
    colors = [
        ("red", (255, 0, 0)),
        ("green", (0, 255, 0)),
        ("blue", (0, 0, 255)),
        ("yellow", (255, 255, 0)),
        ("purple", (128, 0, 128)),
        ("brown", (165, 42, 42)),
        ("black", (0, 0, 0)),
    ]
    
    # Set image parameters
    width, height = 800, 600
    background_color = (240, 240, 240)  # Light gray background
    
    # Calculate appropriate font size based on word count
    # More words = smaller font
    font_size = max(30, int(240 / (word_count ** 0.5)))
    
    # Try to load a bold font with calculated size, use default if not available
    try:
        # Using bold font variant with dynamic size
        font = ImageFont.truetype("Arial Bold.ttf", font_size)
    except IOError:
        try:
            # Try alternative bold font names
            font = ImageFont.truetype("Arial-Bold.ttf", font_size)
        except IOError:
            try:
                # If bold fonts not found, use regular font with the calculated size
                font = ImageFont.truetype("Arial.ttf", font_size)
            except IOError:
                # Use default font as last resort
                font = ImageFont.load_default()
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Dynamically calculate word positions based on word count
    positions = []
    if word_count <= 1:
        positions = [(width//2, height//2)]  # Single word in center
    else:
        vertical_spacing = height / (word_count + 1)
        for i in range(word_count):
            positions.append((width//2, int((i + 0.7) * vertical_spacing)))
    
    print(f"Generating {image_count} image(s) with {word_count} color word(s) each")
    
    for img_idx in range(image_count):
        # Create a new image with a light gray background
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)
        
        used_combinations = []
        used_color_names = set()
        used_display_colors = set()
        
        for i in range(word_count):
            # Select a random color name
            color_name, color_rgb = random.choice(colors)
            
            # Select a different color for display
            display_options = [c for c in colors if c[0] != color_name]
            display_name, display_rgb = random.choice(display_options)
            
            # Ensure combination hasn't been used before
            while (color_name, display_name) in used_combinations:
                color_name, color_rgb = random.choice(colors)
                display_options = [c for c in colors if c[0] != color_name]
                display_name, display_rgb = random.choice(display_options)
            
            used_combinations.append((color_name, display_name))
            used_color_names.add(color_name)
            used_display_colors.add(display_name)
            
            # Draw the text with the selected display color
            text = color_name.upper()
            text_width = draw.textlength(text, font=font)
            position = (positions[i][0] - text_width // 2, positions[i][1] - font_size//4)
            draw.text(position, text, font=font, fill=display_rgb)
        
        # Count unique colors (both mentioned and displayed)
        unique_colors = set()
        for color_name, display_name in used_combinations:
            unique_colors.add(color_name)
            unique_colors.add(display_name)
        
        # Generate a 4-character random UUID
        random_uuid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        # Save the image with the count of unique colors and random UUID as the filename
        filename = f"{len(unique_colors)}_{random_uuid}.png"
        filepath = os.path.join(output_dir, filename)
        img.save(filepath)
        
        print(f"Image {img_idx+1}/{image_count} generated: {filepath}")
        print(f"  Used color names: {', '.join(used_color_names)}")
        print(f"  Used display colors: {', '.join(used_display_colors)}")
        print(f"  Total unique colors: {len(unique_colors)}")

if __name__ == "__main__":
    main()

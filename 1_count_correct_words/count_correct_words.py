#!/usr/bin/env python3
import random
import os
import argparse
from PIL import Image, ImageDraw, ImageFont
import math

# Word lists by length
WORDS_BY_LENGTH = {
    3: ["act", "add", "air", "and", "ant", "arm", "art", "ask", "bad", "bag", "bat", "bed", 
        "bee", "big", "box", "boy", "bug", "bus", "but", "buy", "can", "cap", "car", "cat", 
        "cow", "cry", "cup", "cut", "dad", "day", "dog", "dry", "ear", "eat", "egg", "end",
        "eye", "fan", "far", "fat", "fit", "fix", "fly", "for", "fun", "gas", "get", "god", 
        "hat", "hit", "hot"],
    4: ["able", "acid", "aged", "also", "area", "army", "away", "baby", "back", "ball", 
        "band", "bank", "base", "bath", "bear", "beat", "been", "beer", "bell", "belt", 
        "best", "bird", "blow", "blue", "boat", "body", "bomb", "bond", "bone", "book", 
        "boom", "born", "boss", "both", "bowl", "bulk", "burn", "bush", "busy", "call", 
        "calm", "came", "camp", "card", "care", "case", "cash", "cast", "cell", "chat"],
    5: ["about", "above", "abuse", "actor", "adapt", "after", "again", "agree", "ahead", 
        "alarm", "album", "alert", "alike", "alive", "allow", "alone", "along", "alter", 
        "among", "anger", "angle", "angry", "ankle", "apart", "apple", "apply", "arena", 
        "argue", "arise", "armor", "array", "arrow", "asset", "avoid", "award", "aware", 
        "awful", "bacon", "badge", "badly", "basic", "basis", "beach", "beard", "beast", 
        "begin", "being", "below", "bench", "berry"]
}

# Difficulty presets
DIFFICULTY_PRESETS = {
    "easy": {
        "word_length": 3,
        "total_words_range": (5, 6),
        "image_density": 0.3,
        "font_size_range": (80, 100),
    },
    "medium": {
        "word_length": 4,
        "total_words_range": (7, 8),
        "image_density": 0.5,
        "font_size_range": (60, 80),
    },
    "hard": {
        "word_length": 5,
        "total_words_range": (9, 10),
        "image_density": 0.7,
        "font_size_range": (60, 80),
    }
}

ALLOWED_ROTATIONS = [0, 90, 180, 270]
IMAGE_SIZE = (800, 600)
DEFAULT_SAFE_MARGIN = 20
MAX_PLACEMENT_ATTEMPTS = 100


def scramble_word(word):
    """Generate an incorrect version of the word by randomly reordering characters"""
    chars = list(word)
    while True:
        random.shuffle(chars)
        scrambled = ''.join(chars)
        if scrambled != word:
            return scrambled


def load_font(font_size):
    """Attempt to load font with fallbacks"""
    try:
        return ImageFont.truetype("Arial Bold", font_size)
    except IOError:
        try:
            return ImageFont.truetype("Arial", font_size, index=1)
        except IOError:
            try:
                return ImageFont.truetype("Arial", font_size)
            except IOError:
                return ImageFont.load_default()


def calculate_corners(center_x, center_y, width, height, angle=0):
    """Calculate the four corners of a rectangle with given center, dimensions, and rotation"""
    # Calculate half-dimensions
    half_width, half_height = width / 2, height / 2
    
    # Calculate corner offsets from center (before rotation)
    corners = [
        (-half_width, -half_height),  # top-left
        (half_width, -half_height),   # top-right
        (half_width, half_height),    # bottom-right
        (-half_width, half_height)    # bottom-left
    ]
    
    if angle == 0:
        # No rotation, just add offsets to center
        return [(center_x + dx, center_y + dy) for dx, dy in corners]
    
    # Convert angle to radians for rotation calculation
    angle_rad = math.radians(angle)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    
    # Rotate each corner and add to center position
    return [(center_x + dx * cos_a - dy * sin_a, center_y + dx * sin_a + dy * cos_a) 
            for dx, dy in corners]


def check_corners_in_bounds(corners, image_width, image_height, margin=0):
    """Check if all corners are within the image boundaries"""
    for x, y in corners:
        if (x < margin or x >= image_width - margin or 
            y < margin or y >= image_height - margin):
            return False
    return True


def project_polygon(corners, axis):
    """Project polygon onto an axis"""
    min_proj, max_proj = float('inf'), float('-inf')
    
    for x, y in corners:
        # Dot product for projection
        proj = x * axis[0] + y * axis[1]
        min_proj = min(min_proj, proj)
        max_proj = max(max_proj, proj)
        
    return min_proj, max_proj


def get_polygon_axes(corners):
    """Get all axes (normals to edges) for polygon"""
    axes = []
    for i in range(len(corners)):
        # Get edge vector
        p1 = corners[i]
        p2 = corners[(i + 1) % len(corners)]
        edge = (p2[0] - p1[0], p2[1] - p1[1])
        
        # Normal to the edge (perpendicular)
        normal = (-edge[1], edge[0])
        
        # Normalize the normal vector
        length = math.sqrt(normal[0]**2 + normal[1]**2)
        if length > 0:  # Avoid division by zero
            normal = (normal[0]/length, normal[1]/length)
            axes.append(normal)
    return axes


def check_polygons_overlap(corners1, corners2, margin=0):
    """Check if two polygons overlap using Separating Axis Theorem (SAT)"""
    # Get all axes to check
    axes = get_polygon_axes(corners1) + get_polygon_axes(corners2)
    
    # Check for separation along each axis
    for axis in axes:
        proj1 = project_polygon(corners1, axis)
        proj2 = project_polygon(corners2, axis)
        
        # Add margin to projections (expands the range)
        proj1 = (proj1[0] - margin, proj1[1] + margin)
        proj2 = (proj2[0] - margin, proj2[1] + margin)
        
        # Check for separation
        if proj1[1] < proj2[0] or proj2[1] < proj1[0]:
            # Found a separating axis, no collision
            return False
    
    # No separating axis found, polygons overlap
    return True


def render_text_image(text, font, angle):
    """Render text to an image and rotate if needed"""
    # Create a temporary image with generous padding
    padding = 50
    temp_size = 1000  # Large enough for most text
    temp_img = Image.new('RGBA', (temp_size, temp_size), (255, 255, 255, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # Draw the text at the center
    center_pos = temp_size // 2
    try:
        temp_draw.text((center_pos, center_pos), text, fill=(0, 0, 0), 
                      font=font, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    except TypeError:
        # Fallback for older Pillow versions
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        temp_draw.text((center_pos - text_width//2, center_pos - text_height//2), 
                      text, fill=(0, 0, 0), font=font, stroke_width=3, stroke_fill=(0, 0, 0))
    
    # Get the actual text bounding box
    text_bbox = temp_img.getbbox()
    if not text_bbox:
        return None, 0, 0  # Return None if no visible text
    
    # Crop to the actual text with small padding
    padding = 10
    trimmed_img = temp_img.crop((
        text_bbox[0] - padding,
        text_bbox[1] - padding,
        text_bbox[2] + padding,
        text_bbox[3] + padding
    ))
    
    # Rotate if needed
    if angle != 0:
        trimmed_img = trimmed_img.rotate(angle, expand=True, resample=Image.BICUBIC)
    
    # Get final dimensions
    final_bbox = trimmed_img.getbbox()
    if not final_bbox:
        return None, 0, 0
    
    width = final_bbox[2] - final_bbox[0]
    height = final_bbox[3] - final_bbox[1]
    
    return trimmed_img, width + 20, height + 20  # Add padding for collision detection


def try_place_word(image_size, placed_words, width, height, angle, safe_margin):
    """Try to place a word without overlapping existing words"""
    min_x = width // 2 + safe_margin
    max_x = image_size[0] - width // 2 - safe_margin
    min_y = height // 2 + safe_margin
    max_y = image_size[1] - height // 2 - safe_margin
    
    # If the word is too large for the image with margins, reduce the margins
    if min_x >= max_x:
        min_x = width // 2
        max_x = image_size[0] - width // 2
        
    if min_y >= max_y:
        min_y = height // 2
        max_y = image_size[1] - height // 2
    
    # Get position within safe boundaries
    x = random.randint(min_x, max_x)
    y = random.randint(min_y, max_y)
    
    # Calculate corners for collision detection
    current_corners = calculate_corners(x, y, width, height, angle)
    
    # First check if all corners are within image boundaries
    if not check_corners_in_bounds(current_corners, image_size[0], image_size[1], safe_margin):
        return None
    
    # Check if this word overlaps with already placed words
    margin = 20  # Spacing between words
    for px, py, pw, ph, pangle in placed_words:
        placed_corners = calculate_corners(px, py, pw, ph, pangle)
        if check_polygons_overlap(current_corners, placed_corners, margin):
            return None
    
    # Word placement is valid
    return x, y

def generate_word_puzzle(difficulty="medium", correct_ratio=None, custom_word=None, 
                         custom_params=None, output_dir="."):
    """Generate a word puzzle image with randomly placed words"""
    # Set up parameters based on difficulty
    params = DIFFICULTY_PRESETS[difficulty].copy()
    if custom_params:
        params.update(custom_params)
    
    # Determine total words and correct ratio
    total_words = random.randint(*params["total_words_range"])
    if correct_ratio is None:
        correct_ratio = random.uniform(0.2, 0.6)  # Between 20% and 60% correct
    correct_count = max(1, int(total_words * correct_ratio))
    
    # Choose word
    word_length = params["word_length"]
    if custom_word:
        word = custom_word.lower()
    else:
        word = random.choice(WORDS_BY_LENGTH[word_length])
    
    # Create image
    image = Image.new('RGB', IMAGE_SIZE, color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Generate and place words
    placed_words = []
    actual_correct_count = 0  # Counter for successfully placed correct words
    actual_total_count = 0    # Counter for all successfully placed words
    
    for i in range(total_words):
        is_correct = i < correct_count
        current_word = word if is_correct else scramble_word(word)
        
        # Choose random font size based on difficulty
        font_size = random.randint(*params["font_size_range"])
        font = load_font(font_size)
        
        # Choose rotation angle
        angle = random.choice(ALLOWED_ROTATIONS)
        
        # Render the word to an image
        word_image, collision_width, collision_height = render_text_image(current_word, font, angle)
        if word_image is None:
            continue  # Skip if rendering failed
        
        # Try to place the word
        word_placed = False
        for attempt in range(MAX_PLACEMENT_ATTEMPTS):
            placement = try_place_word(IMAGE_SIZE, placed_words, 
                                      collision_width, collision_height, angle, DEFAULT_SAFE_MARGIN)
            
            if placement:
                x, y = placement
                # Store word for collision detection
                placed_words.append((x, y, collision_width, collision_height, angle))
                
                # Draw the word
                paste_x = int(x - word_image.width // 2)
                paste_y = int(y - word_image.height // 2)
                image.paste(word_image, (paste_x, paste_y), word_image)
                
                # Update counters for successfully placed words
                if is_correct:
                    actual_correct_count += 1
                actual_total_count += 1
                
                word_placed = True
                break
    
    # Save the image
    output_path = os.path.join(output_dir, f"{word}_{actual_correct_count}.png")
    image.save(output_path)
    
    print(f"Created puzzle image: {output_path}")
    print(f"Word: '{word}', Correct count: {actual_correct_count}, Total words: {actual_total_count}")
    
    return output_path


def main():
    # Define default output directory to be in 'output' folder in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_output_dir = os.path.join(script_dir, "output")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(default_output_dir):
        os.makedirs(default_output_dir)
        
    parser = argparse.ArgumentParser(description='Generate a word puzzle image')
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard'], default='easy',
                        help='Difficulty level of the puzzle')
    parser.add_argument('--word', type=str, 
                        help='Specific word to use (must be 3-5 letters)')
    parser.add_argument('--correct_ratio', type=float,
                        help='Ratio of correct words (0.0-1.0)')
    parser.add_argument('--output_dir', default=default_output_dir,
                        help='Directory to save the generated image')
    parser.add_argument('--count', type=int, default=1,
                        help='Number of puzzle images to generate')
    args = parser.parse_args()
    
    print(f"Generating {args.count} puzzle images...")
    for i in range(args.count):
        # For multiple images with same word, we'll generate different layouts
        generate_word_puzzle(
            difficulty=args.difficulty,
            correct_ratio=args.correct_ratio,
            custom_word=args.word,
            output_dir=args.output_dir,
        )
    print(f"Completed generating {args.count} puzzle images.")


if __name__ == "__main__":
    main()

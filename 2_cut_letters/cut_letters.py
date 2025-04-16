#!/usr/bin/env python3
"""
improved_cut_letters.py - Generate letter matching puzzles with masked options.

This script creates images with letter combinations at the top and
masked letter options at the bottom. The user must identify which
masked option matches the top letters.

Difficulty levels:
- Easy: 2 letters, 3 options
- Medium: 3 letters, 4 options
- Hard: 4 letters, 4 options

Improvements:
- Enhanced visibility of text and masking
- Added more contrast between elements
- Improved font fallback mechanism
"""

import random
import string
import sys
import os
import argparse

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageFont

class LetterPuzzleGenerator:
    """Class to generate letter matching puzzles."""
    
    def __init__(self, difficulty='easy'):
        """
        Initialize the puzzle generator with specified difficulty.
        
        Args:
            difficulty (str): Difficulty level ('easy', 'medium', or 'hard')
        """
        self.difficulty = difficulty.lower()
        
        # Set parameters based on difficulty
        if self.difficulty == 'easy':
            self.num_letters = 2
            self.num_options = 3
        elif self.difficulty == 'medium':
            self.num_letters = 3
            self.num_options = 4
        else:  # hard
            self.num_letters = 4
            self.num_options = 4
            
        # Visual similarity mapping for letter replacements
        self.visually_similar_letters = {
            'A': ['H', 'R', 'V'],
            'B': ['P', 'R', 'D'],
            'C': ['G', 'O', 'Q'],
            'D': ['O', 'Q', 'B'],
            'E': ['F', 'B', 'P'],
            'F': ['E', 'P', 'T'],
            'G': ['C', 'O', 'Q'],
            'H': ['A', 'M', 'N'],
            'I': ['J', 'L', 'T'],
            'J': ['I', 'L', 'U'],
            'K': ['R', 'X', 'Y'],
            'L': ['I', 'J', 'T'],
            'M': ['N', 'H', 'W'],
            'N': ['M', 'H', 'U'],
            'O': ['C', 'D', 'Q'],
            'P': ['B', 'R', 'D'],
            'Q': ['O', 'G', 'D'],
            'R': ['P', 'B', 'K'],
            'S': ['Z', 'E', 'G'],
            'T': ['I', 'L', 'F'],
            'U': ['V', 'Y', 'N'],
            'V': ['U', 'Y', 'W'],
            'W': ['V', 'M', 'N'],
            'X': ['K', 'Y', 'Z'],
            'Y': ['V', 'U', 'X'],
            'Z': ['S', 'X', 'N']
        }
        
        # Image settings - landscape orientation for better horizontal option placement
        if self.difficulty == 'easy':
            self.width = 900
        elif self.difficulty == 'medium':
            self.width = 1400
        else:
            self.width = 1900
        self.height = 600
        self.background_color = (255, 255, 255)  # White background
        self.text_color = (0, 0, 0)              # Black text
        self.mask_color = (240, 240, 240)        # Light grey mask instead of white
        self.border_color = (100, 100, 100)      # Darker border for better visibility
        self.font_size = 150
        
        # Always use Helvetica font
        self.font = self._get_font(self.font_size)
    
    def _get_font(self, size):
        """
        Get Helvetica font with fallback mechanism if Helvetica is not available.
        
        Args:
            size (int): Font size
            
        Returns:
            PIL.ImageFont: Font to use
        """
        # Prioritize Helvetica in all common locations
        font_paths = [
            # MacOS Helvetica locations
            '/Library/Fonts/Helvetica.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/Helvetica.dfont',
            # Linux Helvetica/similar locations
            '/usr/share/fonts/truetype/fonts-linuxlibertine/LinLibertine_R.ttf',  # Linux alternative to Helvetica
            '/usr/share/fonts/opentype/helvetica/Helvetica.otf',
            # Windows Helvetica/similar locations
            'C:/Windows/Fonts/helvetica.ttf',
            'C:/Windows/Fonts/arial.ttf',  # Windows alternative to Helvetica
            # Fallbacks if Helvetica is not available
            '/Library/Fonts/Arial.ttf',
            '/System/Library/Fonts/SFNSDisplay.ttf',  # San Francisco (modern Apple font)
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ]
        
        # Try each font path
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception:
                    continue
        
        # If no fonts work, create a default font
        try:
            # Try to use PIL's built-in default font with specified size
            return ImageFont.load_default().font_variant(size=size)
        except Exception:
            # Absolute fallback
            return ImageFont.load_default()

    def generate_random_letters(self, count):
        """
        Generate a random combination of letters.
        
        Args:
            count (int): Number of letters to generate
            
        Returns:
            str: Random letter combination
        """
        # Use uppercase letters for better visibility
        return ''.join(random.choice(string.ascii_uppercase) for _ in range(count))
    
    def generate_options(self, correct_letters):
        """
        Generate options including the correct one, with incorrect options
        created by replacing one letter with a visually similar letter.
        
        Args:
            correct_letters (str): The correct letter combination
            
        Returns:
            list: List of letter options
            int: Index of the correct option (0-based)
        """
        options = []
        correct_index = random.randint(0, self.num_options - 1)
        
        for i in range(self.num_options):
            if i == correct_index:
                options.append(correct_letters)
            else:
                # Generate an option with one letter changed to a visually similar letter or random letter
                while True:
                    # Choose a random position to change
                    pos = random.randint(0, len(correct_letters) - 1)
                    
                    # Get the letter at that position
                    letter = correct_letters[pos]
                    
                    # Get similar letters or fallback to a random different letter
                    similar_letters = self.visually_similar_letters.get(letter, [])
                    
                    # If we have similar letters for this letter, use one; otherwise choose a random letter
                    if similar_letters:
                        replacement = random.choice(similar_letters)
                    else:
                        # Fallback - choose any letter except the original
                        replacement = random.choice([c for c in string.ascii_uppercase if c != letter])
                    
                    # Create the new option by replacing that one letter
                    new_option = correct_letters[:pos] + replacement + correct_letters[pos+1:]
                    
                    # Make sure it's unique and different from the correct option
                    if new_option != correct_letters and new_option not in options:
                        options.append(new_option)
                        break
        
        # Check if there are any duplicate options
        if len(set(options)) != len(options):
            # If duplicates found, recursively regenerate all options
            return self.generate_options(correct_letters)
            
        return options, correct_index
    
    def create_masked_letter_image(self, letter_string, mask_strips=5):
        """
        Create an image with masked letters, improved for better visibility.
        
        Args:
            letter_string (str): Letters to draw with masking
            mask_strips (int): Number of horizontal mask strips
            
        Returns:
            PIL.Image: Image with masked letters
        """
        # Create a new image for this option
        option_width = self.width // self.num_options - 20
        option_height = self.height // 3
        img = Image.new('RGB', (option_width, option_height), self.background_color)
        draw = ImageDraw.Draw(img)
        
        # Get text size using getbbox or older method as fallback
        try:
            bbox = self.font.getbbox(letter_string)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            try:
                # Fallback for older Pillow versions
                text_width, text_height = self.font.getsize(letter_string)
            except Exception:
                # Ultra fallback
                text_width, text_height = option_width // 2, option_height // 2
        
        # Calculate position to center text
        pos_x = (option_width - text_width) // 2
        pos_y = (option_height - text_height) // 2
        
        # Draw the text directly, no background rectangle
        draw.text((pos_x, pos_y), letter_string, font=self.font, fill=self.text_color)
        
        # Create mask strips that match the background color (no border)
        strip_height = (option_height - 5) // (mask_strips * 2)
        for i in range(mask_strips):
            strip_y = pos_y + (i * strip_height * 2)
            # Draw a horizontal mask strip across the text using the background color
            draw.rectangle([(pos_x - 5, strip_y + 10), (pos_x + text_width + 5, strip_y + 10 + strip_height)], 
                          fill=self.background_color)
        
        return img
    
    def generate_puzzle(self, output_filename=None):
        """
        Generate a complete puzzle image with improved visualization.
        
        Args:
            output_filename (str, optional): File to save the image to
            
        Returns:
            tuple: (Image, correct_option_number)
        """
        # Create base image
        img = Image.new('RGB', (self.width, self.height), self.background_color)
        draw = ImageDraw.Draw(img)
        
        # Generate question letters
        question_letters = self.generate_random_letters(self.num_letters)
        
        # Generate options
        options, correct_index = self.generate_options(question_letters)
        correct_option_number = correct_index + 1  # 1-based indexing
        
        # Draw the question text at the top of the image
        try:
            bbox = self.font.getbbox(question_letters)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except (AttributeError, TypeError):
            try:
                text_width, text_height = self.font.getsize(question_letters)
            except:
                text_width, text_height = self.width // 3, self.height // 8
        
        # Calculate position
        q_pos_x = (self.width - text_width) // 2
        q_pos_y = self.height // 8
        
        # Draw question text directly on the background
        draw.text((q_pos_x, q_pos_y - 30), question_letters, font=self.font, fill=self.text_color)
        
        mask_intensity = 5
        
        # Draw options at bottom
        option_width = self.width // self.num_options
        for i, option_text in enumerate(options):
            # Create masked option image
            option_img = self.create_masked_letter_image(option_text, mask_intensity)
            
            # Calculate position
            x_pos = i * option_width + (option_width - option_img.width) // 2
            y_pos = self.height // 3 + 70
            
            # Paste option onto main image
            img.paste(option_img, (x_pos, y_pos))
            
            # Draw box around the option
            box_padding = 10
            draw.rectangle(
                [(x_pos - box_padding, y_pos - box_padding), 
                 (x_pos + option_img.width + box_padding, y_pos + option_img.height + box_padding)],
                outline=self.border_color,
                width=3  # Thicker border for better visibility
            )
            
            # Position the option number below each masked letter set
            number_x = i * option_width + option_width // 2
            number_y = self.height // 3 + 20
            
            # Draw number
            num_font = self._get_font(36)
            draw.text((number_x - 10, number_y + 50), str(i+1), 
                     font=num_font, fill=self.text_color)
        
        # Save if filename provided
        if output_filename:
            img.save(output_filename)
        
        return img, question_letters, correct_option_number

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Generate letter matching puzzles with masked options.')
    parser.add_argument('--count', '-c', type=int, default=1, 
                      help='Number of puzzles to generate for each difficulty level (default: 1)')
    args = parser.parse_args()
    
    # Get the number of puzzles to generate
    puzzle_count = max(1, args.count)  # Ensure at least 1 puzzle
    
    # Create main output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Generate puzzles for each difficulty level
    difficulties = ['easy', 'medium', 'hard']
    total_puzzles = 0
    
    for difficulty in difficulties:
        # Create difficulty-specific subdirectory
        difficulty_dir = os.path.join(output_dir, difficulty)
        if not os.path.exists(difficulty_dir):
            os.makedirs(difficulty_dir)
            print(f"Created {difficulty} subdirectory: {difficulty_dir}")
        
        print(f"Generating {puzzle_count} {difficulty} puzzles...")
        
        # Generate the specified number of puzzles for this difficulty
        for i in range(puzzle_count):
            generator = LetterPuzzleGenerator(difficulty)
            # First generate the puzzle to get the answer without saving
            puzzle_img, question_letters, answer = generator.generate_puzzle()
            # Then save with the answer as the filename in the difficulty subfolder
            output_file = os.path.join(difficulty_dir, f"{question_letters}_{answer}.png")
            puzzle_img.save(output_file)
            
            total_puzzles += 1
            print(f"  [{i+1}/{puzzle_count}] Generated {difficulty} puzzle: {output_file} (Answer: Option {answer})")
    
    print(f"Done! Successfully generated {total_puzzles} puzzles ({puzzle_count} for each difficulty level).")
    print(f"All puzzles saved in the output folder: {output_dir}")

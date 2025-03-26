import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np

TOTAL_NUMBER = 9
STARS = 3   # doenst have to be star, could also be 8 x's
NUMBER_OF_EXTRA_CLUES = 2    # This is the number of extra clues might be added

def should_add_extra_clues(clues):
    return clues.count("x") < 3

def generate_render(star_position, number_of_x, unnecessary=[]):
    """
    Generate a representation of a grid with 'x' markers and an optional star.

    :param star_position: The position of the star, if applicable
    :param number_of_x: The number of 'x' markers to place in the grid
    :param unnecessary: List of positions to unnecessary from consideration
    :return: A list representing the grid
    """
    clues = [" "] * TOTAL_NUMBER
    if random.choice([True, False]) and number_of_x == TOTAL_NUMBER-1:
        # Return star graph
        clues[star_position] = "*"
    else:
        # Add necessary clues
        for x_position in [n for n in range(TOTAL_NUMBER) if n not in unnecessary and n != star_position]:
            clues[x_position] = "x"

        # Add extra clues
        if should_add_extra_clues(clues):
            for x_position in random.sample(unnecessary, NUMBER_OF_EXTRA_CLUES):
                clues[x_position] = "x"
    return clues

def print_box(rows, cols, elements):
    """
    Print a list of elements in a grid format.

    :param rows: Number of elements per row
    :param cols: Number of elements per column
    :param elements: List of elements to be printed
    """
    for row in range(0, len(elements), rows):
        # Slice the list for the current row and join with spaces
        print(" ".join(elements[row:row + cols]))

def render_result(clues, answer):
    """
    Display the clues and the answer in a 3x3 grid format.

    :param clues: Dictionary where keys represent clue identifiers and values are 3x3 grids
    :param answer: List representing the 3x3 grid of the solution
    """
    # Loop through each clue in the clues
    for clue_id, clue_grid in clues.items():
        print(f"Clue for {clue_id}:")
        print_box(3, 3, clue_grid)  # Display the clue in a 3x3 grid format

    # Display the final answer
    print("Answer is:")
    print_box(3, 3, answer)

def generate_clues_and_answer():
    # generate answer
    answer = list(range(TOTAL_NUMBER))
    random.shuffle(answer)

    # create clues
    clues = dict()

    # generate stars
    stars = random.sample(range(TOTAL_NUMBER), STARS)
    for star in stars:
        clues[star] = generate_render(answer.index(star), TOTAL_NUMBER-1)   # 8 x's equals a star

    # generate cluess for rest of numbers
    needed_clues = TOTAL_NUMBER - STARS
    certain_indice = [answer.index(star) for star in stars]
    for number in answer:
        if number in stars: continue
        needed_clues -= 1
        clues[number] = generate_render(answer.index(number), needed_clues, certain_indice)
        certain_indice.append(answer.index(number))

    # re format answer and clues
    answer = [str(n + 1) for n in answer]
    clues = {key+1: value for key, value in clues.items()}
    clues = dict(sorted(clues.items()))

    # return clues and answer
    for k, v in clues.items():
        print(k, v)
    print("answer:", answer)
    return clues, answer

def convert_list_to_image(data, digit):
    # Define grid and cell sizes
    cell_size = 100  # Width and height of each grid cell (in pixels)
    grid_size = cell_size * 3 + 3  # Total grid size (3x3)
    margin = 20  # Margin size (in pixels)
    canvas_size = grid_size + margin * 4  # Total canvas size
    bg_color = "white"  # Background color of the image
    text_color = "black"  # Text color
    border_color = "black"  # Border color
    border_width = 4  # Border width in pixels
    star_color = "blue"  # Color for the star
    cross_color = "red"  # Color for the cross

    # Create a blank canvas with margins
    canvas_image = Image.new("RGB", (canvas_size, canvas_size), bg_color)

    # Create the grid image
    grid_image = Image.new("RGB", (grid_size, grid_size), bg_color)
    draw = ImageDraw.Draw(grid_image)

    # Optional: Load a font (use a TTF font if available)
    try:
        font = ImageFont.truetype("arial.ttf", size=30)  # Use a TTF font if available
    except IOError:
        font = ImageFont.load_default()  # Fall back to default font

    # Draw the grid borders
    for row in range(4):  # Draw horizontal lines, including bottom border
        y = row * cell_size
        draw.line([(0, y), (grid_size, y)], fill=border_color, width=border_width)
    for col in range(4):  # Draw vertical lines, including right-most border
        x = col * cell_size
        draw.line([(x, 0), (x, grid_size)], fill=border_color, width=border_width)

    # Draw the strings into the grid
    for index, text in enumerate(data):
        x_offset = (index % 3) * cell_size
        y_offset = (index // 3) * cell_size

        if text == '*':
            # Draw a fancy shooting star shape
            star_points = [
                (x_offset + cell_size // 2, y_offset + 10),
                (x_offset + cell_size // 2 + 10, y_offset + cell_size // 2 - 10),
                (x_offset + cell_size - 10, y_offset + cell_size // 2 - 10),
                (x_offset + cell_size // 2 + 20, y_offset + cell_size // 2 + 10),
                (x_offset + cell_size // 2 + 30, y_offset + cell_size - 10),
                (x_offset + cell_size // 2, y_offset + cell_size // 2 + 20),
                (x_offset + cell_size // 2 - 30, y_offset + cell_size - 10),
                (x_offset + cell_size // 2 - 20, y_offset + cell_size // 2 + 10),
                (x_offset + 10, y_offset + cell_size // 2 - 10),
                (x_offset + cell_size // 2 - 10, y_offset + cell_size // 2 - 10),
            ]
            draw.polygon(star_points, fill=star_color)
        elif text == 'x':
            # Draw a cross
            cross_size = cell_size // 4
            draw.line(
                [(x_offset + cell_size // 2 - cross_size, y_offset + cell_size // 2 - cross_size),
                 (x_offset + cell_size // 2 + cross_size, y_offset + cell_size // 2 + cross_size)],
                fill=cross_color, width=border_width)
            draw.line(
                [(x_offset + cell_size // 2 + cross_size, y_offset + cell_size // 2 - cross_size),
                 (x_offset + cell_size // 2 - cross_size, y_offset + cell_size // 2 + cross_size)],
                fill=cross_color, width=border_width)
        else:
            text_bbox = font.getbbox(text)  # Use getbbox() to calculate text dimensions
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            # Center the text in the cell
            text_x = x_offset + (cell_size - text_width) // 2
            text_y = y_offset + (cell_size - text_height) // 2
            draw.text((text_x, text_y), text, fill=text_color, font=font)

    # Paste the grid image onto the canvas with margins
    canvas_image.paste(grid_image, (margin*3, margin))

    # Add a digit "digit" in the top-left corner of the canvas
    digit_font_size = 60
    try:
        digit_font = ImageFont.truetype("calibri.ttf", size=digit_font_size)
    except IOError:
        digit_font = ImageFont.load_default()
    draw_canvas = ImageDraw.Draw(canvas_image)
    draw_canvas.text((margin // 2, margin // 2), str(digit), fill=text_color, font=digit_font)

    return canvas_image

def generate_picture(clues):
    images = []
    for key in range(1, 10):
        assert key in clues
        # Create an image from the array
        image = convert_list_to_image(clues[key], key)
        images.append(image)

    # Assume all images have the same size
    img_width, img_height = images[0].size

    # Create a blank image for the 3x3 grid
    grid_width = img_width * 3
    grid_height = img_height * 3
    grid_image = Image.new("RGB", (grid_width, grid_height))

    # Paste images into the grid
    for index, img in enumerate(images):
        x_offset = (index % 3) * img_width
        y_offset = (index // 3) * img_height
        grid_image.paste(img, (x_offset, y_offset))

    # Save or display the image
    grid_image.save("clues.png")
    grid_image.show()

clues, answer = generate_clues_and_answer()
generate_picture(clues)
#render_result(clues, answer)

# Workspace Overview

This workspace contains several Python projects, each organized into its own folder. Below is a description of each folder and its purpose. For all script, use `python <scipt_name>.py --help` to view the usage

---

## 1_count_correct_words
This folder contains a script to generate word puzzles where users must identify the correct words from a set of scrambled and correct options.

- **Script**: `count_correct_words.py`
- **Output**: Generated images of word puzzles are saved in the `output/` directory. Image format is `<goal_word>_<correct_answer_of_count>.png`

---

## 2_cut_letters
This folder contains a script to generate letter matching puzzles. Users must identify which masked option matches the given letters.

- **Script**: `cut_letters.py`
- **Output**: Generated puzzles are saved in the `output/` directory, organized by difficulty (`easy/`, `medium/`, `hard/`). Image format is `<question_letters>_<correct_option>.png`

---

## 8_count_colors
This folder contains a script to generate images with colored text. The task involves counting unique colors used in the image.

- **Script**: `count_colors.py`
- **Output**: Generated images are saved in the `output/` directory. Image format is `<correct_answer_of_count>_<random_uuid>.png`

---

## fill_in_matrix
This folder contains a script to generate a 3x3 grid puzzle with clues and answers. The puzzle involves identifying positions based on the provided clues.

- **Script**: `generate_clues_and_answer.py`
- **Output**: Generated images of the puzzle grid are saved as `clues.png`.

---

## Questions.pdf
This file may contain additional documentation or problem descriptions related to the projects in this workspace.

---

Feel free to explore each folder and run the scripts to generate puzzles and images!
# Sakura Sudoku 🌸

A pastel cherry-blossom themed Sudoku game built with Streamlit.

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run `pip install -r requirements.txt`
4. Run `streamlit run app.py`

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository.
2. Open https://share.streamlit.io/
3. Connect GitHub and choose this repository, branch, and `app.py`.

## Notes
- The menu and gameplay backgrounds use the images supplied with the project.
- Five difficulty stages, instant loss on an incorrect filled number, hints, level unlocking, replay and generated sound effects are included.
- Browsers often block autoplay audio. Use the audio player in the game to start the background loop.
- This starter version uses a fixed completed Sudoku grid with five different clue patterns. For production, replace it with five independently validated puzzles/solutions.

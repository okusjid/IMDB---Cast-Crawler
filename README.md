# IMDb Actor Data Scraper

This Python script scrapes actor names, profile pictures, and date of birth information from the full cast & crew page of a movie on IMDb. The script saves the actor data to a JSON file and downloads the images to a local folder.

## Features
- Scrapes actor names, profile pictures, and date of birth from IMDb.
- Saves actor data (name, image link, date of birth) in a JSON file.
- Downloads actor profile pictures and saves them in an `images/` folder.
- Automatically saves each actor’s data after processing to ensure no data is lost if the script fails.

## Requirements

Install the necessary Python packages:

```bash
pip install selenium requests pillow
```
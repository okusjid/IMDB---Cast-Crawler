import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def download_image(session, url, path):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            with open(path, 'wb') as file:
                file.write(response.content)
        else:
            print(f"Failed to download image: {response.status_code}")
    except Exception as e:
        print(f"Error downloading image: {e}")


def scroll_to_element(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
    except Exception as e:
        print(f"Error scrolling to element: {e}")


def extract_actor_data(session, driver, actor_url):
    try:
        driver.get(actor_url)
        actor_data = {}

        # Extract the name
        name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div/h1/span[1]'))
        )
        name = name_element.text
        actor_data['name'] = name
        print(f"Extracting data for {name}")

        # Extract the profile picture link
        image_link_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[1]/div[1]/div/a'))
        )
        image_link = image_link_element.get_attribute('href')
        actor_data['image_link'] = image_link
        print(f"Image link: {image_link} of {name}")

        # Download image
        if not os.path.exists('images'):
            os.makedirs('images')
        image_path = f'images/{name.replace("/", "-")}.jpg'
        download_image(session, image_link, image_path)

        # Extract the Date of Birth
        dob_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/section/aside/div/span[2]'))
        )
        dob_text = dob_element.text.split('\n')[-1]
        actor_data['dob'] = dob_text
        print(f"Date of Birth: {dob_text} of {name}")

        return actor_data
    except Exception as e:
        print(f"Error extracting data for actor at {actor_url}: {e}")
        return None


def save_to_json(data, filename='actor_data.json'):
    """Save the given data to the JSON file in bulk."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r+', encoding='utf-8') as file:
                current_data = json.load(file)
                current_data.extend(data)
                file.seek(0)
                json.dump(current_data, file, indent=4)
        else:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving data to JSON: {e}")


def extract_actor_links(driver):
    """Extract actor links from the IMDb page."""
    actor_links = []
    i = 2
    while True:
        xpath = f'//*[@id="fullcredits_content"]/table[3]/tbody/tr[{i}]'
        rows = driver.find_elements(By.XPATH, xpath)
        if not rows:
            print("No more rows to process")
            break
        for row in rows:
            try:
                link_element = row.find_element(By.XPATH, './/td[2]/a')
                actor_link = link_element.get_attribute('href')
                actor_links.append(actor_link)
            except Exception as e:
                print(f"Error extracting link: {e}")
        i += 2
    return actor_links


def main():
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        url = "https://www.imdb.com/title/tt0421463/fullcredits?ref_=ttfc_ql_1"
        driver.get(url)

        # Extract actor links
        actor_links = extract_actor_links(driver)

        actors = []
        session = requests.Session()  # Use a session to reuse connections
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(extract_actor_data, session, webdriver.Chrome(), actor_link)
                for actor_link in actor_links
            ]
            for future in as_completed(futures):
                actor_data = future.result()
                if actor_data:
                    actors.append(actor_data)

        # Save data in bulk at the end
        save_to_json(actors)

    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()

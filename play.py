import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def download_image(url, path):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
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
        time.sleep(2)
    except Exception as e:
        print(f"Error scrolling to element: {e}")

def extract_actor_data(driver, actor_url):
    try:
        driver.get(actor_url)
        actor_data = {}
        
        # Extract the name
        scroll_to_element(driver, driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div/h1/span[1]'))
        name = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div/h1/span[1]').text
        actor_data['name'] = name
        print(f"Extracting data for {name}")

        # Extract the profile picture link
        scroll_to_element(driver, driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[1]/div[1]/div/a'))
        image_link_element = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[1]/div[1]/div/a')
        image_link = image_link_element.get_attribute('href')
        actor_data['image_link'] = image_link
        print(f"Image link: {image_link} of {name}")

        # Download image
        if not os.path.exists('images'):
            os.makedirs('images')
        image_path = f'images/{name.replace("/", "-")}.jpg'
        download_image(image_link, image_path)

        # Extract the Date of Birth
        scroll_to_element(driver, driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/section/aside/div/span[2]'))
        dob_element = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/section/aside/div/span[2]')
        dob_text = dob_element.text
        if "\n" in dob_text:
            dob = dob_text.split('\n')[1]
        else:
            dob = dob_text
        actor_data['dob'] = dob
        print(f"Date of Birth: {dob} of {name}")
        driver.back()
        return actor_data
    except Exception as e:
        print(f"Error extracting data for actor at {actor_url}: {e}")
        return None


def save_to_json(data, filename='actor_data.json'):
    """Save the given data to the JSON file."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r+', encoding='utf-8') as file:
                # Load existing data
                current_data = json.load(file)
                current_data.append(data)
                file.seek(0)
                json.dump(current_data, file, indent=4)
        else:
            # Create a new file with the first record
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump([data], file, indent=4)
    except Exception as e:
        print(f"Error saving data to JSON: {e}")


def main():
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()  # Full screen
        url = "https://www.imdb.com/title/tt0421463/fullcredits?ref_=ttfc_ql_1"
        driver.get(url)
        actors = []

        # Use a loop to iterate through rows dynamically
        i = 2
        while True:
            xpath = f'//*[@id="fullcredits_content"]/table[3]/tbody/tr[{i}]'
            rows = driver.find_elements(By.XPATH, xpath)
            if not rows:
                print("No more rows to process")
                break
            else:
                print(f"Processing {len(rows)} rows")
                print(f"Current row: {i}")
            for row in rows:
                try:
                    link_element = row.find_element(By.XPATH, './/td[2]/a')
                    print(f"Processing {link_element.text}")
                    actor_link = link_element.get_attribute('href')
                    scroll_to_element(driver, link_element)
                    time.sleep(2)
                    actor_data = extract_actor_data(driver, actor_link)
                    time.sleep(2)
                    if actor_data:
                        actors.append(actor_data)
                        # Save each actor's data to the JSON file immediately after extraction
                        save_to_json(actor_data)
                except Exception as e_inner:
                    print(f"Error processing row: {e_inner}")
            i += 2  # Move to the next row of interest (skip one row)

    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()

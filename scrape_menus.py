
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup
import os

url = 'https://www.elmenus.com/cairo/asian-corner-44p3/6th-of-october-owd5/reviews'
csv_file = 'data/elmenus_reviews.csv'

# Load existing reviews if any
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    existing_texts = set(df['text'].tolist())
    print(f"Loaded {len(df)} existing reviews.")
else:
    df = pd.DataFrame(columns=["source", "text", "rating", "reviewer", "time_stamp"])
    existing_texts = set()

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(url)
time.sleep(3)

def extract_reviews_from_page():
    """Extract all reviews visible on current page."""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    reviews_data = []
    for review in soup.find_all('div', class_='review'):
        name_elem = review.find('h4', class_='review__name')
        name = name_elem.text.strip() if name_elem else "Unknown"

        date_elem = review.find('div', class_='review__time')
        date = date_elem.text.strip() if date_elem else "N/A"

        text_elem = review.find('div', class_='review__comment').find('p') \
            if review.find('div', class_='review__comment') else None
        text = text_elem.text.strip() if text_elem else ""

        rating_elems = review.find('ul', class_='rate-stars').find_all('li', class_='star') \
            if review.find('ul', class_='rate-stars') else []
        rating = str(sum(1 for li in rating_elems if 'active' in li.get('class', []))) if rating_elems else "N/A"

        if text and text not in existing_texts:
            reviews_data.append({
                "source": "Elmenus",
                "text": text,
                "rating": rating,
                "reviewer": name,
                "time_stamp": date
            })
            existing_texts.add(text)
    return reviews_data

all_new_reviews = []
max_attempts = 300

for attempt in range(1, max_attempts + 1):
    try:
        # Extract visible reviews
        new_reviews = extract_reviews_from_page()
        if new_reviews:
            all_new_reviews.extend(new_reviews)
            print(f"Attempt {attempt}: {len(all_new_reviews)} new reviews collected.")

        # Save progress every 50 reviews
        if len(all_new_reviews) >= 50:
            temp_df = pd.DataFrame(all_new_reviews)
            df = pd.concat([df, temp_df], ignore_index=True)
            df.drop_duplicates(subset=['text'], inplace=True)
            os.makedirs('data', exist_ok=True)
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"Saved {len(df)} total unique reviews.")
            all_new_reviews = []  # reset

        # Find and click Load More
        load_more_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="btn btn-primary btn--load-more"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
        load_more_button.click()
        time.sleep(3)

    except Exception as e:
        print(f"No more 'Load More' button or error at attempt {attempt}: {e}")
        break

# Save any remaining reviews
if all_new_reviews:
    temp_df = pd.DataFrame(all_new_reviews)
    df = pd.concat([df, temp_df], ignore_index=True)
    df.drop_duplicates(subset=['text'], inplace=True)
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"Final save: {len(df)} unique reviews.")

driver.quit()
print("Scraping finished.")

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_driver(website):
    #Launches Chrome and loads the given website.
    print("Launching Chrome browser...")
    chrome_driver_path = "./chromedriver.exe"
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
    driver.get(website)
    time.sleep(3)  
    print("Page loaded...")
    return driver

def close_popup(driver):
    #Check for and close the popup if it appears.
    try:
        # Wait briefly for the popup to appear
        popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ReactModal__Overlay.ReactModal__Overlay--after-open.Modal_maModalOverlay__PMYMj")
            )
        )
        try:
            close_button = popup.find_element(By.CSS_SELECTOR, ".close-button-selector")  # Update selector as needed
            close_button.click()
        except Exception:
            driver.execute_script("arguments[0].remove();", popup)
        time.sleep(0.1)
    except Exception:
        pass


def extract_body_content(driver: webdriver.Chrome) -> pd.DataFrame:
    
    #Extracts course data from the homepage using Selenium.
    
    
    courses_list = []
    
    course_cards = driver.find_elements(By.CSS_SELECTOR, ".ProfessionCard_cardWrapper__BCg0O[href]")
    
    if not course_cards:
        return pd.DataFrame(courses_list)
    
    for course_card in course_cards:

        
        # Scroll card into view to trigger any lazy-loading
        driver.execute_script("arguments[0].scrollIntoView(true);", course_card)
        close_popup(driver)

        time.sleep(0.5)  # Brief pause for dynamic content
        
        course_data = {}
        
        # Extract course name
        try:
            course_name_elem = course_card.find_element(By.CLASS_NAME, "ProfessionCard_title__m7uno")
            course_data["course_name"] = course_name_elem.text.strip()
        except Exception as e:
            course_data["course_name"] = "N/A"
        
        # Extract course description (if available) by hovering over the course card
        try:
            # Hover over the course card to trigger the display of the description
            action = ActionChains(driver)
            action.move_to_element(course_card).perform()

            description_elem = WebDriverWait(course_card, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "ProfessionCard_description__K8weo"))
            )
            course_data["course_description"] = description_elem.text.strip()
        except Exception as e:
            course_data["course_description"] = "N/A"
        
        # Extract course duration
        try:
            course_duration_elem = course_card.find_element(
                By.CSS_SELECTOR, 
                ".typography_paragraphMedium__FWO7K.ProfessionCard_text___l0Du.ProfessionCard_duration__13PwX"
            )
            course_data["course_duration"] = course_duration_elem.text.strip()
        except Exception as e:
            course_data["course_duration"] = "N/A"
        
        # Extract course tags
        try:
            tags_elems = course_card.find_elements(By.CLASS_NAME, "typography_labelMedium__bQMhy")
            course_tags = [tag.text.strip() for tag in tags_elems if tag.text.strip()]
            course_data["course_tags"] = ", ".join(course_tags)
        except Exception as e:
            course_data["course_tags"] = ""
        
        # Extract course URL from the href attribute
        try:
            href_attr = course_card.get_attribute("href")
            course_data["url"] = href_attr if href_attr else "N/A"
        except Exception as e:
            course_data["url"] = "N/A"
        
        courses_list.append(course_data)

        print(courses_list)

    
    return pd.DataFrame(courses_list)



def additional_task(df):
    #For each course, loads its page to extract additional details.

    chrome_driver_path = "./chromedriver.exe"
    options = webdriver.ChromeOptions()

    df["course_modules_count"] = None
    df["theme_number"] = None
    base_url = "https://mate.academy"

    for index, row in df.iterrows():
        course_url = row["url"]
        if not course_url.startswith("http"):
            course_url = base_url + course_url
        print("Processing course URL:", course_url)

        driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
        try:
            driver.get(course_url)
            time.sleep(3)

            modules_count = 0
            theme_number = "N/A"

            try:
                course_modules_list = driver.find_element(By.CLASS_NAME, "CourseModulesList_modulesList__C86yL")
                course_list_items = course_modules_list.find_elements(By.CLASS_NAME, "CourseModulesList_itemLeft__BKWFl")
                driver.execute_script("arguments[0].scrollIntoView(true);", course_modules_list)
                close_popup(driver)
                modules_count = len(course_list_items)
                print("Number of course list items:", modules_count)
            except Exception:
                print("No course modules list found for URL:", course_url)

            try:
                course_program = driver.find_element(By.CLASS_NAME, "CourseProgram_cards__CD13X")
                program_items = course_program.find_elements(
                    By.CSS_SELECTOR,
                    ".FactBlockIcon_factIconBlock__72SXK.CourseProgram_card__p5TPZ.FactBlockIcon_indigo__yH9KL.flex-container.flex-dir-column"
                )
                if program_items:
                    try:
                        theme_tag = program_items[0].find_element(By.CLASS_NAME, "FactBlockIcon_factNumber__FTmxv")
                        theme_number = theme_tag.text.strip()
                        print("Theme Number:", theme_number)
                    except Exception:
                        pass
            except Exception:
                pass

            df.at[index, "course_modules_count"] = modules_count
            df.at[index, "theme_number"] = theme_number
        finally:
            driver.quit()

    return df


if __name__ == "__main__":
    homepage_url = "https://mate.academy/"
    driver = get_driver(homepage_url)
    df_courses = extract_body_content(driver)
    driver.quit()
    
    df_updated = additional_task(df_courses)
    print(df_updated)

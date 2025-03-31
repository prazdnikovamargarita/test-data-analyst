import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

def scrape_website(website):
    print("Launching Chrome browser...")
    chrome_driver_path = "./chromedriver.exe"
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
    try:

        driver.get(website)
        time.sleep(3)  # Pause to allow any dynamic content to load

        print("Page loaded...")
        html = driver.page_source
        return html
    finally:
        driver.quit()


def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    courses_list = []
    
    # Find all course cards by class with an href attribute
    course_cards = soup.find_all(class_="ProfessionCard_cardWrapper__BCg0O", href=True)
    print("Course Cards:", course_cards)
    
    for course_card in course_cards:
        course_data = {}
        # Extract course name
        course_name_tag = course_card.find(
                                            class_="ProfessionCard_title__m7uno"
                                            )
        course_data["course_name"] = course_name_tag.text.strip() if course_name_tag else "N/A"
        # Extract course description
        course_description_tag = course_card.find(
                                            class_="ProfessionCard_description__K8weo"
                                            )
        course_data["course_description"] = course_description_tag.text.strip() if course_description_tag else "N/A"
        # Extract course duration
        course_duration_tag = course_card.find(
                                            class_="typography_paragraphMedium__FWO7K ProfessionCard_text___l0Du ProfessionCard_duration__13PwX"
                                            )
        course_data["course_duration"] = course_duration_tag.text.strip() if course_duration_tag else "N/A"
        # Extract course tags
        course_tags_tags = course_card.find_all(
                                            class_="typography_labelMedium__bQMhy"
                                            )
        course_tags = [tag.text.strip() for tag in course_tags_tags] if course_tags_tags else []
        course_data["course_tags"] = ", ".join(course_tags)
        # Extract course URL
        course_data["url"] = course_card.get('href', "N/A")
        
        courses_list.append(course_data)
        print("Course Data:", course_data)
    
    return pd.DataFrame(courses_list)


def additional_task(df):
    # Add new columns for additional data
    df["course_modules_count"] = None
    df["theme_number"] = None

    for index, row in df.iterrows():
        href = row["url"]
        html_content = scrape_website(f"https://mate.academy{href}")
        soup = BeautifulSoup(html_content, "html.parser")
        
        modules_count = 0
        extracted_theme_number = "N/A"
        
        # Find the course modules list
        course_modules_list = soup.find(class_="CourseModulesList_modulesList__C86yL")
        if course_modules_list:
            course_list_items = course_modules_list.find_all(class_="CourseModulesList_itemLeft__BKWFl")
            modules_count = len(course_list_items)
            print("Number of course list items:", modules_count)
        else:
            print("No course modules list found.")
        
        # Find the course program and extract the theme number from the first element
        course_program = soup.find(class_="CourseProgram_cards__CD13X")
        if course_program:
            program_items = course_program.find_all(
                class_="FactBlockIcon_factIconBlock__72SXK CourseProgram_card__p5TPZ FactBlockIcon_indigo__yH9KL flex-container flex-dir-column"
            )
            if program_items and len(program_items) > 0:
                theme_tag = program_items[0].find(class_="FactBlockIcon_factNumber__FTmxv")
                if theme_tag:
                    extracted_theme_number = theme_tag.get_text(strip=True)
                    print("Theme Number:", extracted_theme_number)
        
        df.loc[index, "course_modules_count"] = modules_count
        df.loc[index, "theme_number"] = extracted_theme_number

    return df


html_content = scrape_website('https://mate.academy/')
df_courses = extract_body_content(html_content)
df_updated = additional_task(df_courses)
print(df_updated)
df_updated.to_csv("task_2_with_bs4.csv", index=False)

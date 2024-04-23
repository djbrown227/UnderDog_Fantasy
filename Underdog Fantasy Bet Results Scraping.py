#!/usr/bin/env python
# coding: utf-8

# In[2]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
import pandas as pd
import re
import time
from bs4 import BeautifulSoup
import requests

# Specify the path to the ChromeDriver executable
chromedriver_path = "/Users/danielbrown/Desktop/chromedriver-mac-arm64"

# Create a new instance of the Chrome web driver
driver = webdriver.Chrome(chromedriver_path)

driver.set_window_size(1200, 800)

driver.set_script_timeout(4800)

# Use the web driver to interact with the web page
driver.get("https://underdogfantasy.com/login")

# Find the username input field and fill it in with your login username
wait = WebDriverWait(driver, 10)
username_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[data-testid='email_input'][autocomplete='email']")))
username_field.send_keys("djbrown227@gmail.com")

password_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[data-testid='password_input'][autocomplete='current-password']")))
password_field.send_keys("SeanScott227!")

# Find the "Sign in" button and click on it to submit the login form
sign_in_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='sign-in-button']")))
sign_in_button.click()

# Click on the "Results" tab
# Find the "results" tab and wait for it to become clickable before clicking on it
pickem_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.styles__link__C_eQ8[href='/results']")))
pickem_tab.click()

# #Pickem Rivals
wait = WebDriverWait(driver, 10)
rivals_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.styles__navLink__JAbVL[href='/results/pick-em']")))
rivals_tab.click()



###############################
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

# I assume that 'driver' and 'wait' are already defined somewhere else in your code.
# If not, you need to define them. For example:
# driver = webdriver.Firefox()
# wait = WebDriverWait(driver, 10)

max_attempts = 50  # Define a maximum number of attempts to click 'Load More' button

# Continuously click the "Load More" button until it can't be found anymore
for i in range(max_attempts):
    try:
        load_more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.styles__buttonWrapper__BgLMC button.styles__button__gmYRZ.styles__green__aqzHf.styles__small___s6i5.styles__solid__BthGK.styles__intrinsic__OkkMQ")))
        driver.execute_script("arguments[0].click();", load_more_button)
        time.sleep(4)
    except NoSuchElementException:
        print("No more 'Load More' button found, proceeding to the next step.")
        break  # Only break the loop if "Load More" button is not found.
    except TimeoutException:
        print(f"Attempt {i+1} of {max_attempts}: 'Load More' button was not clickable. Retrying in 2 seconds...")
        time.sleep(2)
        continue
    except Exception as e:
        print(f"Unexpected error on attempt {i+1} of {max_attempts} while trying to click 'Load More' button: {str(e)}")
        break

# Find the toggle button and click it
try:
    toggle_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "i.styles__icon__DijND.styles__toggleIcon__T_xUl")))
    for button in toggle_buttons:
        try:
            button.click()
            time.sleep(4)  # Wait for 2 seconds to let the new content load
        except Exception as e:
            print(f"Error while trying to click 'Toggle' button: {str(e)}")
            continue  # Skips to the next iteration of the loop
except Exception as e:
    print(f"Error while trying to find 'Toggle' buttons: {str(e)}")


####################


data = []
data_rival = []

# Wait for the page to load and reveal the elements
player_containers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class*="styles__overUnderLiveResultCell__PXEQT"]')))
player_containers_1 = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class*="styles__rivalLiveResult__psg6i"]')))

# Loop over all player containers
for container in player_containers:
    # Find sport icon, match info
    sport_icon_class = container.find_element(By.CSS_SELECTOR, "i.styles__icon__DijND").get_attribute("class")
    
    sport_identifier = sport_icon_class.split(" ")[-1].split("__")[-1]  # Get the last part of the class name
    match_info = container.find_element(By.CSS_SELECTOR, "p.styles__matchInfoText__ZOV5w").text

    # Get the outcome (like "won" or "lost")
    outcome_class_list = container.get_attribute("class").split(" ")
    outcome = [outcome_class.split("__")[-1] for outcome_class in outcome_class_list if outcome_class.startswith("styles__won") or outcome_class.startswith("styles__lost")]
    outcome = outcome[0] if outcome else None  # Get the outcome or None if not found

    # Extracting other information if present
    player_name = container.find_element(By.CSS_SELECTOR, "h1.styles__playerName__tRwnv").text
    player_stat = container.find_element(By.CSS_SELECTOR, "p.styles__statLine__QGxD2").text
    #result_stat = container.find_element(By.CSS_SELECTOR, "p.div.styles__resultStat__tHnnc").text
    #result_stat = container.find_element(By.CSS_SELECTOR, "div.styles__resultStat__tHnnc p").text
    # Add the data to the data list
    data.append({
        "Sport Identifier": sport_identifier,
        "Match Info": match_info,
        "Outcome": outcome,
        "Player Name": player_name,
        "Player Stat": player_stat
        #"Result Stat": result_stat
    })

data_rival = []
for container in player_containers_1:
    # Find sport icon, match info
    sport_icon_class = container.find_element(By.CSS_SELECTOR, "i.styles__icon__DijND").get_attribute("class")
    sport_identifier = sport_icon_class.split(" ")[-1].split("__")[-1]  # Get the last part of the class name

    # Find match info
    match_info_elements = container.find_elements(By.CSS_SELECTOR, "p.styles__matchInfoText__tlt9C")
    match_info = match_info_elements[0].text if len(match_info_elements) > 0 else None
    date_info = match_info_elements[1].text if len(match_info_elements) > 1 else None

    # Get the outcome (like "won" or "lost")
    outcome_class_list = container.get_attribute("class").split(" ")
    outcome = [outcome_class.split("__")[-1] for outcome_class in outcome_class_list if outcome_class.startswith("styles__won") or outcome_class.startswith("styles__lost")]
    outcome = outcome[0] if outcome else None  # Get the outcome or None if not found

    # Try to find the stat in the span element within div with class "styles__stat__PICCL"
    stat_elements = container.find_elements(By.CSS_SELECTOR, "div.styles__stat__PICCL span")
    player_stat = None
    if stat_elements:  # If there is at least one matching element
        player_stat = stat_elements[0].text  # Take the text of the first matching element

    # Add the data to the data list
    data_rival.append({
        "Sport Identifier": sport_identifier,
        "Match Info": match_info,
        "Outcome": outcome,
        "Player Stat": player_stat,
        "Date": date_info
    })


# Quit the driver
driver.quit()

# Create pandas DataFrames
df = pd.DataFrame(data)
df_rival = pd.DataFrame(data_rival)

# Print the DataFrames
print(df)
print(df_rival)


# In[ ]:


df.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Results/UD_results_highlow.csv")
df_rival.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Results/UD_results_rival.csv")


# In[ ]:


###############
#Testing
###############


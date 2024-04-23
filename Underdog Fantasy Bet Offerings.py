#!/usr/bin/env python
# coding: utf-8

# In[3]:


#This program scrapes all the odds offered on Underdog Fantasy


# In[4]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from selenium.webdriver.chrome.service import Service
import pandas as pd
import re


# Setup WebDriver with Service
service = Service('/Users/danielbrown/Desktop/chromedriver-mac-arm64/chromedriver')
driver = webdriver.Chrome(service=service)

# Specify the path to the ChromeDriver executable
#chromedriver_path = "/Users/danielbrown/Downloads/chromedriver_mac_arm64/chromedriver"

# Create a new instance of the Chrome web driver
#driver = webdriver.Chrome(chromedriver_path)

driver.set_window_size(1200, 800)

# Use the web driver to interact with the web page
driver.get("https://underdogfantasy.com/login")

# Find the username input field and fill it in with your login username
wait = WebDriverWait(driver, 60)
username_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[data-testid='email_input'][autocomplete='email']")))
username_field.send_keys("djbrown227@gmail.com")

password_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[data-testid='password_input'][autocomplete='current-password']")))
password_field.send_keys("SeanScott227!")

# Find the "Sign in" button and click on it to submit the login form
sign_in_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='sign-in-button']")))
sign_in_button.click()

# Find the "Pick'em" tab and wait for it to become clickable before clicking on it
pickem_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.styles__link__C_eQ8[href='/pick-em']")))
pickem_tab.click()

wait = WebDriverWait(driver, 10)
player_containers = wait.until(presence_of_all_elements_located((By.CSS_SELECTOR, "div.styles__overUnderCell__KgzNn[role='button'][tabindex='0']")))

data = []
for container in player_containers:
    name_element = container.find_element(By.CSS_SELECTOR, "div.styles__playerInfo__e6Lbk h1.styles__playerName__jW6mb")
    stat_elements = container.find_elements(By.CSS_SELECTOR, "p.styles__statLine__K1NYh")

    name = name_element.text
    stats = [stat_element.text for stat_element in stat_elements]

    for stat in stats:
        data.append({"Name": name, "Stat": stat})

df_higherlower = pd.DataFrame(data)
df_higherlower[['Line', 'Line_Category']] = df_higherlower['Stat'].str.extract(r'(\d*\.?\d+)\s*(.*)')
df_higherlower = df_higherlower.drop(columns=['Stat'])
df_higherlower['Implied Probability'] = 0.5512
df_higherlower['Fixed Odds Site'] = 'Underdog Fantasy'
print(df_higherlower)

# #Pickem Rivals
wait = WebDriverWait(driver, 10)
rivals_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.styles__navLink__JAbVL[href='/pick-em/rivals']")))
rivals_tab.click()

# Replace 'driver' with your webdriver instance
wait = WebDriverWait(driver, 10)

# Locate the parent containers
parent_containers = wait.until(presence_of_all_elements_located((By.CSS_SELECTOR, "div.styles__rivalLineCell__WQojL")))

# Iterate through the parent containers and extract the required information
data = []
for container in parent_containers:
    player_name_elements = container.find_elements(By.CSS_SELECTOR, "div.styles__playerName__VNfpb")
    points_element = container.find_element(By.CSS_SELECTOR, "div.styles__stat__Uf3SY span")
    adjustment_elements = container.find_elements(By.CSS_SELECTOR, "div.styles__spreadBox__Xb5VO p")

    player_names = [name_element.get_attribute("title") for name_element in player_name_elements]
    points = points_element.text

    # Extract the adjustment value or use the default value if the element doesn't exist
    adjustment = adjustment_elements[0].text if adjustment_elements else "0.0 Adjustment"

    data.append({"Player1": player_names[0], "Player2": player_names[1], "Stat_Category": points, "Adjustment": adjustment})

# Create a DataFrame from the data list
df_rival = pd.DataFrame(data)
df_rival['Adjustment'] = df_rival['Adjustment'].apply(lambda x: float(re.sub(r'[^\d.]', '', x)))
df_rival['Fixed Odds Site'] = 'Underdog Fantasy'
print(df_rival)

driver.quit()


# In[ ]:


df_higherlower.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Underdog HigherLower/df_higherlower.csv")
df_rival.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Underdog Rivals/df_rival.csv")


# In[ ]:





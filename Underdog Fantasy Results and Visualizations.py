#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import re


# In[2]:


df = pd.read_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Results/UD_results_highlow.csv")
print(df)


# In[3]:


import pandas as pd
from datetime import datetime

# Assuming df is your DataFrame
# 1. Drop 'Sport Identifier' and 'Result Stat' columns
df = df.drop(['Sport Identifier','Unnamed: 0'], axis=1)

# 2. Remove the scores from the 'Match Info' column
df['Match Info'] = df['Match Info'].apply(lambda x: x.split('-')[-1].strip())

# 3. Convert 'Match Info' to datetime
# Here I'm assuming if it's a time only string it will have the "PM" or "AM" at the end.
df['Match Info'] = df['Match Info'].apply(lambda x: pd.to_datetime(x) if ("PM" in x or "AM" in x) else pd.to_datetime(x, format="%m/%d/%y %I:%M%p"))

# If the date is missing, replace it with today's date
df['Match Info'] = df['Match Info'].apply(lambda x: pd.to_datetime(str(datetime.now().date()) + " " + x.strftime("%I:%M%p")) if pd.isnull(x.date()) else x)

# 4. Map 'Outcome' column
outcome_mapping = {float('nan'): 'Tie', 'o3o4E': 'Win', 'NT6cP': 'Lose'}
df['Outcome'] = df['Outcome'].map(outcome_mapping)

#print(df)


# In[4]:


# Mapping Outcome values to numbers
outcome_1_mapping = {'Tie': 2, 'Win': 1, 'Lose': 0}
df['Outcome_1'] = df['Outcome'].map(outcome_1_mapping)
#print(df)


# In[5]:


# Sort data by date
df.sort_values(by='Match Info', inplace=True)

# Calculate running averages
# Calculate running averages
df['Running Avg (Outcome_1 = 1)'] = (df['Outcome_1'] == 1).cumsum() / ((df['Outcome_1'] == 1) | (df['Outcome_1'] == 2) | (df['Outcome_1'] == 0)).cumsum()
df['Running Avg (Outcome_1 = 1 or 2)'] = ((df['Outcome_1'] == 1) | (df['Outcome_1'] == 2)).cumsum() / ((df['Outcome_1'] == 1) | (df['Outcome_1'] == 2) | (df['Outcome_1'] == 0)).cumsum()


#print(df)


# In[6]:


print(df.dtypes)


# In[7]:


def extract_sport(player_stat):
    # Split the string at the first number encountered
    splits = re.split(r'\d+\.\d+', player_stat)
    # If there's a part after the number, return it, else return None
    if len(splits) > 1:
        return splits[1].strip()
    else:
        return None

# Apply the function to the 'Player Stat' column and create the new 'Sport' column
df['Stat'] = df['Player Stat'].apply(extract_sport)

print(df)


# In[8]:


#Basketball Stat Mapping
#'Hits': 'Hockey' was excluded
basketball_mapping = {'Points': 'Basketball', 'Assists': 'Basketball','Rebounds':'Basketball','Blocks':'Basketball','Turnovers':'Basketball','3-Pointers Made':'Basketball','Points + Rebounds': 'Basketball','Points + Assists': 'Basketball',
                      'Pts + Rebs + Asts': 'Basketball','Rebounds + Assists': 'Basketball','Steals':'Basketball','Blocks + Steals':'Basketball',
                      'Singles': 'Baseball', 'Hits': 'Baseball','Total Bases': 'Baseball','Hits + Runs + RBIs': 'Baseball','Batter Walks': 'Baseball','Strikeouts': 'Baseball','Strikeouts': 'Baseball','Pitch Count': 'Baseball','Strikeouts': 'Baseball',
                      'Shots': 'Hockey','Saves': 'Hockey','Goals Against': 'Hockey','Assists': 'Hockey',
                      'Games lost':'Tennis','Games won':'Tennis',
                      'Shots Attempted': 'Soccer',
                      'Finishing Position':'Racing'
                     }


df['Sport'] = df['Stat'].map(basketball_mapping)
#
df = df[['Match Info','Running Avg (Outcome_1 = 1)','Running Avg (Outcome_1 = 1 or 2)','Stat','Sport','Outcome_1']]
print(df)


# In[9]:


#############
#Chart
###########


# In[ ]:





# In[10]:


# import pandas as pd

# # Suppose df is your DataFrame
# df['Match Info'] = pd.to_datetime(df['Match Info'])  # Ensuring 'Match Info' is in datetime format

# # Setting 'Match Info' to be the DataFrame index
# df.set_index('Match Info', inplace=True)

# # Grouping by sport and resampling by month end to get the last entry of each month for each sport
# df_grouped = df.groupby('Sport').resample('M').last()

# # Now df_grouped is a multi-index DataFrame with 'Sport' and 'Match Info' as indices, containing the last entry of each month for each sport
# # To get a table with 'Sport' as rows and 'Match Info' as columns, unstack the DataFrame:
# df_unstacked = df_grouped.unstack('Sport')

# # Now df_unstacked is a DataFrame with 'Match Info' as rows and 'Sport' as columns, showing the running average at the end of each month for each sport
# print(df_unstacked)


# In[11]:


import plotly.graph_objects as go

# Create a line plot for the running average of 1's in Outcome_1
fig1 = go.Figure(data=go.Scatter(x=df['Match Info'], y=df['Running Avg (Outcome_1 = 1)'], mode='lines+markers'))
fig1.update_layout(title='Running Average of 1\'s in Outcome_1 Over Time',
                   xaxis_title='Date',
                   yaxis_title='Running Average',
                   hovermode="x unified") # "x unified" ensures the tooltip appears in sync across all traces
fig1.show()

# Create a line plot for the running average of 1's and 2's in Outcome_1
fig2 = go.Figure(data=go.Scatter(x=df['Match Info'], y=df['Running Avg (Outcome_1 = 1 or 2)'], mode='lines+markers'))
fig2.update_layout(title='Running Average of 1\'s and 2\'s in Outcome_1 Over Time',
                   xaxis_title='Date',
                   yaxis_title='Running Average',
                   hovermode="x unified") # "x unified" ensures the tooltip appears in sync across all traces
fig2.show()


# In[12]:


################


# In[13]:


# import pandas as pd
# import numpy as np
# import plotly.graph_objects as go

# # Define a function for calculating running averages for Outcome_1 = 1
# def calculate_running_average_1(group):
#     return (group['Outcome_1'] == 1).cumsum() / ((group['Outcome_1'] == 1) | (group['Outcome_1'] == 2) | (group['Outcome_1'] == 0)).cumsum()

# # Define a function for calculating running averages for Outcome_1 = 1 or 2
# def calculate_running_average_1_or_2(group):
#     return ((group['Outcome_1'] == 1) | (group['Outcome_1'] == 2)).cumsum() / ((group['Outcome_1'] == 1) | (group['Outcome_1'] == 2) | (group['Outcome_1'] == 0)).cumsum()

# # Make sure 'Match Info' is datetime
# df['Match Info'] = pd.to_datetime(df['Match Info'])

# # Sort values by date to make sure averages are calculated correctly
# df = df.sort_values('Match Info')

# # Apply running average functions to each sport
# for sport in df['Sport'].unique():
#     sport_df = df[df['Sport'] == sport]
#     df.loc[df['Sport'] == sport, 'Running Avg (Outcome_1 = 1) Sportwise'] = calculate_running_average_1(sport_df)
#     df.loc[df['Sport'] == sport, 'Running Avg (Outcome_1 = 1 or 2) Sportwise'] = calculate_running_average_1_or_2(sport_df)

# # Initialize figures
# fig1 = go.Figure()
# fig2 = go.Figure()

# # Get the unique sports
# sports = df['Sport'].unique().tolist()

# # Add a trace for each sport
# for sport in sports:
#     sport_df = df[df['Sport'] == sport]
#     fig1.add_trace(go.Scatter(x=sport_df['Match Info'], y=sport_df['Running Avg (Outcome_1 = 1) Sportwise'], mode='lines+markers', name=sport))
#     fig2.add_trace(go.Scatter(x=sport_df['Match Info'], y=sport_df['Running Avg (Outcome_1 = 1 or 2) Sportwise'], mode='lines+markers', name=sport))

# # Create the dropdown menu
# dropdown = [{"label": "All Sports", "method": "update", "args": [{"visible": [True for _ in sports]}]}]
# for i, sport in enumerate(sports):
#     bool_list = [False for _ in sports]
#     bool_list[i] = True
#     dropdown.append({"label": sport, "method": "update", "args": [{"visible": bool_list}, {"title": sport}]})

# # Update the layout
# fig1.update_layout(title='Running Average of 1\'s in Outcome_1 Over Time',
#                    xaxis_title='Date',
#                    yaxis_title='Running Average',
#                    hovermode="x unified",
#                    updatemenus=[{"buttons": dropdown}])

# fig2.update_layout(title='Running Average of 1\'s and 2\'s in Outcome_1 Over Time',
#                    xaxis_title='Date',
#                    yaxis_title='Running Average',
#                    hovermode="x unified",
#                    updatemenus=[{"buttons": dropdown}])

# # Show the figures
# fig1.show()
# fig2.show()


# In[14]:


#################


# In[15]:


import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Define a function for calculating running averages for Outcome_1 = 1
def calculate_running_average_1(group):
    return (group['Outcome_1'] == 1).cumsum() / ((group['Outcome_1'] == 1) | (group['Outcome_1'] == 2) | (group['Outcome_1'] == 0)).cumsum()

# Define a function for calculating running averages for Outcome_1 = 1 or 2
def calculate_running_average_1_or_2(group):
    return ((group['Outcome_1'] == 1) | (group['Outcome_1'] == 2)).cumsum() / ((group['Outcome_1'] == 1) | (group['Outcome_1'] == 2) | (group['Outcome_1'] == 0)).cumsum()

# Make sure 'Match Info' is datetime
df['Match Info'] = pd.to_datetime(df['Match Info'])

# Sort values by date to make sure averages are calculated correctly
df = df.sort_values('Match Info')

# Apply running average functions to each sport
for sport in df['Sport'].unique():
    sport_df = df[df['Sport'] == sport]
    df.loc[df['Sport'] == sport, 'Running Avg (Outcome_1 = 1) Sportwise'] = calculate_running_average_1(sport_df)
    df.loc[df['Sport'] == sport, 'Running Avg (Outcome_1 = 1 or 2) Sportwise'] = calculate_running_average_1_or_2(sport_df)

# Initialize figures
fig1 = go.Figure()
fig2 = go.Figure()

# Get the unique sports
sports = df['Sport'].unique().tolist()

# Add a trace for each sport
for sport in sports:
    sport_df = df[df['Sport'] == sport]
    fig1.add_trace(go.Scatter(x=sport_df['Match Info'], y=sport_df['Running Avg (Outcome_1 = 1) Sportwise'], mode='lines+markers', name=sport))
    fig2.add_trace(go.Scatter(x=sport_df['Match Info'], y=sport_df['Running Avg (Outcome_1 = 1 or 2) Sportwise'], mode='lines+markers', name=sport))

# Create the dropdown menu
dropdown = [{"label": "All Sports", "method": "update", "args": [{"visible": [True for _ in sports]}]}]
for i, sport in enumerate(sports):
    bool_list = [False for _ in sports]
    bool_list[i] = True
    dropdown.append({"label": sport, "method": "update", "args": [{"visible": bool_list}, {"title": sport}]})

# Define a custom template for aesthetics
custom_template = go.layout.Template()
custom_template.layout = go.Layout(font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"))

# Update the layout
fig1.update_layout(title='Running Average of 1\'s in Outcome_1 Over Time',
                   xaxis_title='Date',
                   yaxis_title='Running Average',
                   hovermode="x unified",
                   updatemenus=[{"buttons": dropdown}],
                   template=custom_template)

fig2.update_layout(title='Running Average of 1\'s and 2\'s in Outcome_1 Over Time',
                   xaxis_title='Date',
                   yaxis_title='Running Average',
                   hovermode="x unified",
                   updatemenus=[{"buttons": dropdown}],
                   template=custom_template)

# Show the figures
fig1.show()
fig2.show()


# In[16]:


#################


# In[17]:


#Running Average Wins for Underdog Fantasy rival


# In[18]:


#/Users/danielbrown/Desktop/Underdog WebApp/Results/UD_results_rival.csv
df = pd.read_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Results/UD_results_rival.csv")


# In[19]:


# Assuming df is your DataFrame
# 1. Drop 'Sport Identifier' and 'Result Stat' columns
df = df.drop(['Sport Identifier', 'Match Info'], axis=1)

# 2. Remove the scores from the 'Match Info' column
#df['Match Info'] = df['Match Info'].apply(lambda x: x.split('-')[-1].strip())

# 3. Convert 'Match Info' to datetime
# Here I'm assuming if it's a time only string it will have the "PM" or "AM" at the end.
df['Date'] = df['Date'].apply(lambda x: pd.to_datetime(x) if ("PM" in x or "AM" in x) else pd.to_datetime(x, format="%m/%d/%y %I:%M%p"))

# If the date is missing, replace it with today's date
df['Date'] = df['Date'].apply(lambda x: pd.to_datetime(str(datetime.now().date()) + " " + x.strftime("%I:%M%p")) if pd.isnull(x.date()) else x)

# 4. Map 'Outcome' column
outcome_mapping = {float('nan'): 'Tie', 'ONP9m': 'Win', 'iPePg': 'Lose'}
df['Outcome'] = df['Outcome'].map(outcome_mapping)
df = df.rename(columns={'Date': 'Match Info'})

print(df)


# In[20]:


# Mapping Outcome values to numbers
outcome_1_mapping = {'Tie': 2, 'Win': 1, 'Lose': 0}
df['Outcome_1'] = df['Outcome'].map(outcome_1_mapping)
print(df)


# In[21]:


# Sort data by date
df.sort_values(by='Match Info', inplace=True)

# Calculate running averages
# Calculate running averages
df['Running Avg (Outcome_1 = 1)'] = (df['Outcome_1'] == 1).cumsum() / ((df['Outcome_1'] == 1) | (df['Outcome_1'] == 2) | (df['Outcome_1'] == 0)).cumsum()
df['Running Avg (Outcome_1 = 1 or 2)'] = ((df['Outcome_1'] == 1) | (df['Outcome_1'] == 2)).cumsum() / ((df['Outcome_1'] == 1) | (df['Outcome_1'] == 2) | (df['Outcome_1'] == 0)).cumsum()


print(df)


# In[22]:


#################


# In[23]:


#Basketball Stat Mapping
#'Hits': 'Hockey' was excluded
basketball_mapping = {'Points': 'Basketball', 'Assists': 'Basketball','Rebounds':'Basketball','Blocks':'Basketball','Turnovers':'Basketball','3-Pointers Made':'Basketball','Points + Rebounds': 'Basketball','Points + Assists': 'Basketball',
                      'Pts + Rebs + Asts': 'Basketball','Rebounds + Assists': 'Basketball','Steals':'Basketball','Blocks + Steals':'Basketball',
                      'Singles': 'Baseball', 'Hits': 'Baseball','Total Bases': 'Baseball','Hits + Runs + RBIs': 'Baseball','Batter Walks': 'Baseball','Strikeouts': 'Baseball','Strikeouts': 'Baseball','Pitch Count': 'Baseball','Strikeouts': 'Baseball',
                      'Shots': 'Hockey','Saves': 'Hockey','Goals Against': 'Hockey','Assists': 'Hockey',
                      'Games won':'Tennis',
                      'Shots Attempted': 'Soccer',
                      'Finishing Position':'Racing',
                      'Fewer Strokes':'Golf'
                     }


df['Sport'] = df['Player Stat'].map(basketball_mapping)
#
#df = df[['Match Info','Running Avg (Outcome_1 = 1)','Running Avg (Outcome_1 = 1 or 2)','Stat','Sport','Outcome_1']]
print(df)


# In[24]:


##################


# In[25]:


import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Define a function for calculating running averages for Outcome_1 = 1
def calculate_running_average_1(group):
    return (group['Outcome_1'] == 1).cumsum() / ((group['Outcome_1'] == 1) | (group['Outcome_1'] == 2) | (group['Outcome_1'] == 0)).cumsum()

# Define a function for calculating running averages for Outcome_1 = 1 or 2
def calculate_running_average_1_or_2(group):
    return ((group['Outcome_1'] == 1) | (group['Outcome_1'] == 2)).cumsum() / ((group['Outcome_1'] == 1) | (group['Outcome_1'] == 2) | (group['Outcome_1'] == 0)).cumsum()

# Make sure 'Match Info' is datetime
df['Match Info'] = pd.to_datetime(df['Match Info'])

# Sort values by date to make sure averages are calculated correctly
df = df.sort_values('Match Info')

# Apply running average functions to each sport
for sport in df['Sport'].unique():
    sport_df = df[df['Sport'] == sport]
    df.loc[df['Sport'] == sport, 'Running Avg (Outcome_1 = 1) Sportwise'] = calculate_running_average_1(sport_df)
    df.loc[df['Sport'] == sport, 'Running Avg (Outcome_1 = 1 or 2) Sportwise'] = calculate_running_average_1_or_2(sport_df)

# Initialize figures
fig1 = go.Figure()
fig2 = go.Figure()

# Get the unique sports
sports = df['Sport'].unique().tolist()

# Add a trace for each sport
for sport in sports:
    sport_df = df[df['Sport'] == sport]
    fig1.add_trace(go.Scatter(x=sport_df['Match Info'], y=sport_df['Running Avg (Outcome_1 = 1) Sportwise'], mode='lines+markers', name=sport))
    fig2.add_trace(go.Scatter(x=sport_df['Match Info'], y=sport_df['Running Avg (Outcome_1 = 1 or 2) Sportwise'], mode='lines+markers', name=sport))

# Create the dropdown menu
dropdown = [{"label": "All Sports", "method": "update", "args": [{"visible": [True for _ in sports]}]}]
for i, sport in enumerate(sports):
    bool_list = [False for _ in sports]
    bool_list[i] = True
    dropdown.append({"label": sport, "method": "update", "args": [{"visible": bool_list}, {"title": sport}]})

# Define a custom template for aesthetics
custom_template = go.layout.Template()
custom_template.layout = go.Layout(font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"))

# Update the layout
fig1.update_layout(title='Running Average of 1\'s in Outcome_1 Over Time',
                   xaxis_title='Date',
                   yaxis_title='Running Average',
                   hovermode="x unified",
                   updatemenus=[{"buttons": dropdown}],
                   template=custom_template)

fig2.update_layout(title='Running Average of 1\'s and 2\'s in Outcome_1 Over Time',
                   xaxis_title='Date',
                   yaxis_title='Running Average',
                   hovermode="x unified",
                   updatemenus=[{"buttons": dropdown}],
                   template=custom_template)

# Show the figures
fig1.show()
fig2.show()


# In[ ]:





# In[ ]:





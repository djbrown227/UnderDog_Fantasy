#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd


# In[4]:


#Import csvs that contain pinnacle odds and underdog lines
df_higher_lower = pd.read_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Underdog HigherLower/df_higherlower.csv")
df_rival = pd.read_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Underdog Rivals/df_rival.csv")
all_sports_odds = pd.read_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/all_sport_odds.csv")


# In[5]:


#Merge and find positive EV lines on df_higher_lower, when pinnacle lines match underdog fantasy lines
df_positive_EV = pd.merge(df_higher_lower, all_sports_odds, on=['Name', 'Line_Category', 'Line'])
#df_positive_EV.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/df_positive_EV.csv")

#all_sports_odds = pd.read_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/all_sport_odds.csv")
df_positive_EV = df_positive_EV[df_positive_EV['No_Vig_Probability'] > df_positive_EV['Implied Probability']][['Name', 'Line', 'Line_Category', 'Over_Under', 'No_Vig_Probability','Bookmaker']]
df_positive_EV.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/df_positive_EV.csv")
print(df_positive_EV)


# In[ ]:





# In[6]:


# #Merge and find line discrepancies df_higher_lower

# Merge and find line discrepancies df_higher_lower
df_line_discrep = pd.merge(df_higher_lower, all_sports_odds, on=['Name', 'Line_Category'])

#Find where Underdog Line(Line_x) does not equal Sportbook Lines(Line_y)
df_line_discrep = df_line_discrep[df_line_discrep['Line_x'] != df_line_discrep['Line_y']][['Name', 'Line_x', 'Line_Category','Over_Under', 'No_Vig_Probability','Line_y','Bookmaker']]

df_line_discrep.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/df_line_discrep_test.csv")

# Filter the DataFrame based on your conditions
condition1 = (df_line_discrep['Line_x'] <= df_line_discrep['Line_y']) & (df_line_discrep['Over_Under'] == 'Under') & (df_line_discrep['No_Vig_Probability'] >= 0.552)
condition2 = (df_line_discrep['Line_x'] <= df_line_discrep['Line_y']) & (df_line_discrep['Over_Under'] == 'Over') & (df_line_discrep['No_Vig_Probability'] <= 0.448)
condition3 = (df_line_discrep['Line_x'] >= df_line_discrep['Line_y']) & (df_line_discrep['Over_Under'] == 'Over') & (df_line_discrep['No_Vig_Probability'] >= 0.552)
condition4 = (df_line_discrep['Line_x'] >= df_line_discrep['Line_y']) & (df_line_discrep['Over_Under'] == 'Under') & (df_line_discrep['No_Vig_Probability'] <= 0.448)

df_line_discrep = df_line_discrep[~(condition1 | condition2 | condition3 | condition4)][['Name', 'Line_x', 'Line_Category', 'Over_Under', 'No_Vig_Probability', 'Line_y', 'Bookmaker']]

condition5 = (df_line_discrep['Line_x'] <= df_line_discrep['Line_y']) & (df_line_discrep['Over_Under'] == 'Over')
condition6 = (df_line_discrep['Line_x'] >= df_line_discrep['Line_y']) & (df_line_discrep['Over_Under'] == 'Under')

df_line_discrep = df_line_discrep[condition5 | condition6][['Name', 'Line_x', 'Line_Category', 'Over_Under', 'No_Vig_Probability', 'Line_y', 'Bookmaker']]

# Rename the columns
df_line_discrep.rename(columns={'Line_x': 'Line', 'Line_y': 'Bookmaker_Line'}, inplace=True)

# Write the DataFrame to a CSV file
df_line_discrep.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/df_line_discrep_final.csv")

# Print the DataFrame
print(df_line_discrep)


# In[ ]:





# In[7]:


#Rivals


# In[8]:


# create the first dataframe: merge df1 and df2 on Player1 and Line_Category, and add the Adjustment to the Line
df_player1_adj = pd.merge(df_rival, all_sports_odds, how='inner', left_on=['Player1', 'Stat_Category'], right_on=['Name', 'Line_Category'])
df_player1_adj['Line'] += df_player1_adj['Adjustment']
df_player1_adj = df_player1_adj.drop(['Name', 'Line_Category', 'Adjustment'], axis=1)

df_player1_adj.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Underdog Rivals/df_player1_adj.csv")


# create the second dataframe: merge df1 and df2 on Player2 and Line_Category, without adding the Adjustment
df_player2 = pd.merge(df_rival, all_sports_odds, how='inner', left_on=['Player2', 'Stat_Category'], right_on=['Name', 'Line_Category'])
df_player2 = df_player2.drop(['Name', 'Line_Category', 'Adjustment'], axis=1)
df_player2.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Underdog Rivals/df_player2_adj.csv")

#Neaten up the two dataframes
df_player1_adj = df_player1_adj[['Player1','Player2','Stat_Category','Line','Over_Under','League','No_Vig_Probability','Bookmaker']]
df_player1_adj = df_player1_adj.reset_index(drop=True)



df_player2 = df_player2[['Player1','Player2','Stat_Category','Line','Over_Under','League','No_Vig_Probability','Bookmaker']]
df_player2 = df_player2.reset_index(drop=True)


print(df_player1_adj.head(150))
print(df_player2.head(150))


# In[9]:


import numpy as np
# merge df1 and df2 on 'Player1', 'Player2', and 'Stat_Category'
merged_df = pd.merge(df_player1_adj, df_player2, on=['Player1', 'Player2', 'Stat_Category','Over_Under'], suffixes=('_df1', '_df2'))

#Only keep 'Over' odds
merged_df = merged_df[merged_df['Over_Under'] != 'Under']

#drop duplicates
merged_df = merged_df.drop_duplicates()

#Round Probabilities
merged_df['No_Vig_Probability_df1'] = merged_df['No_Vig_Probability_df1'].round(2)
merged_df['No_Vig_Probability_df2'] = merged_df['No_Vig_Probability_df2'].round(2)

# Remove rows with duplicate values in columns 'Player1', 'Player2', 'Stat_Category', 'Line_df2', 'Bookmaker_df2'
merged_df = merged_df.drop_duplicates(subset=['Player1', 'Player2', 'Stat_Category', 'Line_df2', 'Bookmaker_df2'])
merged_df = merged_df.drop_duplicates(subset=['Player1', 'Player2', 'Stat_Category', 'Line_df2'])

#Send merged_df to csv
merged_df.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Underdog Rivals/merged_df.csv")

#Groupby and Average the Lines and Probabilities
merged_df = merged_df.groupby(['Player1', 'Player2', 'Stat_Category', 'League_df1'])[['Line_df1', 'Line_df2', 'No_Vig_Probability_df1', 'No_Vig_Probability_df2']].mean().reset_index()

merged_df.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Underdog Rivals/merged_df_1.csv")

#Create Rival Choice column where values are nan
merged_df['Rival_Choice'] = np.nan

# # Condition 1 and 2
unequal_rows_1 = (merged_df['Line_df1'] > merged_df['Line_df2'])
merged_df.loc[unequal_rows_1 & (merged_df['No_Vig_Probability_df1'] >= merged_df['No_Vig_Probability_df2']), 'Rival_Choice'] = merged_df['Player1']

unequal_rows_2 = (merged_df['Line_df1'] < merged_df['Line_df2'])
merged_df.loc[unequal_rows_2 & (merged_df['No_Vig_Probability_df2'] >= merged_df['No_Vig_Probability_df1']), 'Rival_Choice'] = merged_df['Player2']

# # Condition 3 and 4
over_rows = (merged_df['Line_df1'] == merged_df['Line_df2'])
merged_df.loc[over_rows & (merged_df['No_Vig_Probability_df1'] > (merged_df['No_Vig_Probability_df2']+0.01)), 'Rival_Choice'] = merged_df['Player1']
merged_df.loc[over_rows & (merged_df['No_Vig_Probability_df2'] > (merged_df['No_Vig_Probability_df1']+0.01)), 'Rival_Choice'] = merged_df['Player2']

#Remove empty Rival Choice rows, this indicates that there was not a good choice
merged_df.dropna(subset=['Rival_Choice'], inplace=True)

print(merged_df)

merged_df.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/Underdog Rivals/merged_df_2.csv")


# In[ ]:





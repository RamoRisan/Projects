from re import L
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time


#this is the url i scraped from
table_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
#download the page, using the get method from request library
data = requests.get(table_url)
#print(data.text) --> gives me the html if i wanted to print it


#beatifulsoup will parse the HTML from the table_url
entry = BeautifulSoup(data.text, features="lxml")
#will select any table element from the table element
standing_table = entry.select('table.stats_table')[0]
#this is finding all the a tags
links = standing_table.find_all('a')
links = [l.get("href") for l in links]
#this will give us only the team links
#checks to see if squads is in the href
links = [l for l in links if '/squads/'in l]
#will use a format string to make the links needed for each team
team_urls = [f"https://fbref.com{l}" for l in links]




team_url = team_urls[0]
data = requests.get(team_url)
#import pandas so we can analyze data better


#go through all the tables till we get to scores and fixtures
matches = pd.read_html(data.text, match="Scores & Fixtures")
#print(matches[0])


soup = BeautifulSoup(data.text)
links = soup.find_all('a')
links = [l.get("href") for l in links]
#we will look for any links that have all_comps/shooting/ as that will be where
#we can get shooting data
links = [l for l in links if l and 'all_comps/shooting/' in l]
#will use a reference string and request to get/download the shooting html
data = requests.get(f"https://fbref.com{links[0]}")
#will read in the shooting data
shooting = pd.read_html(data.text, match="Shooting")[0]
shooting.columms = shooting.columns.droplevel()
#gives us first 5 rows on the stats instead of all of them
shooting.head()
#gets rid of the unnesary columns such as date, time, etc
shooting.columns = shooting.columns.droplevel()
#this will combine the two data frames
#date colums would be used to combine the matches and shooting in one
team_data = matches[0].merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
#creates a list for 2024 and 2023 years
years = list(range(2024,2022, -1))
#will contain the match long for each team
all_matches = []
standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
#will loop through each season

#loop through the list of years
for year in years:
   data = requests.get(standings_url)
   soup = BeautifulSoup(data.text)
   standings_table = soup.select('table.stats_table')[0]
   #requests the standingnt page, beautifulsoup will parse through html
   #gets the first table
   #extracts all the a tags, includes only those inf the squad page
   links = [l.get("href") for l in standings_table.find_all('a')]
   links = [l for l in links if '/squads/' in l]
   #builds the url
   team_urls = [f"https://fbref.com{l}" for l in links]
   #get the previous season link
   previous_season = soup.select("a.prev")[0].get("href")
   standings_url = f"https://fbref.com{previous_season}"
   #loops through each team's url
   for team_url in team_urls:
       #fetches the shooting data
       team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
       data = requests.get(team_url)
       matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
       soup = BeautifulSoup(data.text)
       links = [l.get("href") for l in soup.find_all('a')]
       links = [l for l in links if l and 'all_comps/shooting/' in l]
       data = requests.get(f"https://fbref.com{links[0]}")
       shooting = pd.read_html(data.text, match="Shooting")[0]
       shooting.columns = shooting.columns.droplevel()
       #merges the shooting and match data
       try:
           team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
       except ValueError:
           continue
       #filters to make sure we skip over any non premier league matches
       team_data = team_data[team_data["Comp"] == "Premier League"]
      
       team_data["Season"] = year
       team_data["Team"] = team_name
       all_matches.append(team_data)
       #to make sure we do not send too many requests at once
       time.sleep(1)








match_df = pd.concat(all_matches)
match_df.columns = [c.lower() for c in match_df.columns]
match_df.to_csv("matches.csv")

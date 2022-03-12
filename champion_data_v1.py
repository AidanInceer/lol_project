import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def champion_links():
    url = r"https://euw.op.gg/champions"

    user_agent = {'User-Agent': "Mozilla/5.0"}
    page = requests.get(url,headers= user_agent)
    soup = BeautifulSoup(page.text, "html.parser")
    champion_section = soup.find("nav", {"class":"css-pqbqz6 e1n0mtzi8"})
    link_base = "https://euw.op.gg/champions/"
    link_list = []
    for init_link in champion_section.find_all('a', href=True):
        for role_raw in init_link.find_all("i"):
            role = role_raw.text.strip().lower()
            if role == "middle":
                role = "mid"
            elif role == "bottom":
                role = "adc"
            str_link_raw = str(init_link['href'])
            str_link_stripped = str_link_raw.split("/")[2]
            link = (link_base + str_link_stripped + "/" + role + "/counters")
            link_list.append(link)
    return link_list
    
def matchup_data():
    
    user_agent = {'User-Agent': "Mozilla/5.0"}  
    champ_link_list = champion_links()

    df_list = []
    for champion_link in champ_link_list:
        champ_name = champion_link.split("/")[4].lower()
        champ_role = champion_link.split("/")[5].lower()

        url = champion_link
        page = requests.get(url,headers= user_agent)
        soup = BeautifulSoup(page.text, "html.parser")

        opp_name_list = []
        for opp_name_raw in soup.find_all("div", {"class":"name"}):
            opp_name = opp_name_raw.text.lower()
            opp_name_list.append(opp_name)

        opp_winrate_list = []
        for opp_winreate_raw in soup.find_all("span", {"class":"win"}):
            opp_winreate = opp_winreate_raw.text.replace("%","")
            opp_winrate_list.append(opp_winreate)
        
        matchup_df = pd.DataFrame({"opponent_name" : opp_name_list,
                                   f"champ_{champ_name}" : opp_winrate_list})
        
        matchup_df.to_csv(f"./champion_matchup_csvs/{champ_role}_{champ_name}.csv",index=False)

        df_list.append(matchup_df)
    return df_list
        

def format_data():
    role_list = ["adc","jungle","mid","support","top"]
    for role in role_list:
        matchup_data_list = []
        for filename in os.listdir("./champion_matchup_csvs"):
            if filename.startswith(role):
                matchup_data = pd.read_csv(f"./champion_matchup_csvs/{filename}")
                matchup_data_list.append(matchup_data)
        
    
        dfs = [df.set_index('opponent_name') for df in matchup_data_list]
        combined_df = pd.concat(dfs, axis=1)
        print(combined_df)
        combined_df = combined_df.sort_values("opponent_name")
        combined_df = combined_df.sort_index(axis=1)
        combined_df = combined_df.fillna(50.00)
        combined_df.columns = combined_df.columns.str.replace("champ_","")
        combined_df.to_csv(f"./role_matchup_data/{role}_matchups.csv")
            

format_data()


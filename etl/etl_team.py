import pandas as pd
from sqlalchemy import create_engine
import json

# Step 1: Read your JSON file
with open('vct-international/esports-data/teams.json') as f:
    teams_data = json.load(f)

# Step 2: Create a pandas DataFrame with selected fields
df = pd.DataFrame(teams_data)
selected_columns = ['id', 'acronym', "home_league_id", 'slug', 'name']
df = df[selected_columns]

# Step 3: Set up the PostgreSQL connection
db_username = 'postgres'
db_password = '5142'
db_host = 'localhost'
db_port = '5432'
db_name = 'vct'

# Create the connection string
connection_string = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(connection_string)

# Step 4: Upload the DataFrame to PostgreSQL
# 'team_data' is the name of the table you want to create/update in PostgreSQL
df.to_sql('team_data', engine, if_exists='replace', index=False)

print("Data uploaded successfully!")
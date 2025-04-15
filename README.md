# salesData
Group work using sql and sales data

We need to add conn = engine.connect() after creating the engine
Then the df.to_sql should have in the parenthesis ('name', conn, if_exists='replace', index = false)

Wrap queries in text()

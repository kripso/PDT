PDT Assignment 1

Algorithm:
Prerequisites - unique values are kept in a dictionary for a table that needs it in a format -> table[primary_key] = None. this approach gave the best performance over other tested approaches

1.  Populate context domains and entities in a separate Process
	1. They are separate in logic from other tables and are needed for context annotations
2. Populate authors in the main Process
3.  Populate conversations table (in my case I renamed it to tweets for better understandability)
4.  After the *tweets get populated all processes are executed in parallel
5.  One separate process to Populate Context annotations Table
	1. includes the whole read of conversations
6.  Another separate process to Populate Hashtags Table 
	1. includes the whole read of conversations
7.  Meanwhile on the main thread reading through the conversation once more and for every 1_000_000 (100_000 should yield better performance for my use case) rows create a new Process to populate the Annotations table, Links table, and Tweets table

Used Technology:
1.  Multiprocessing - wanted to try something new and with independent tables and logic should save quite a bit of runtime.
2.  Dictionaries - to store unique keys because of O(1) search for existing values
3.  Wrapper function - clean tracking of runtime

  

Used SQL
1.  psycopg2 - based on research should be the best library to interact with the Postgres database, 
2.   cursor.copy_from - copy_from yields the best performance for writing batches of rows into Postgres tables.
3.  GENERATED ALWAYS AS IDENTITY - to keep python code cleaner and faster let the database create an id where tweeter does not provide one
	1. this is not the case for hashtags where I created ids manually and assigned them to hashtags and tweet hashtags
4.  Unlogged tables were used for better performance even though they are considered less safe for data retention

Runntime: 
	58 minues and 34 seconds
	with smaller batches and some optimizations done over tha last runntime will decrease but that doesnt matter now.

Database:
there is an arror in my code because tweet references table is after import empty, may be because of multiprocesing and that UNIQUE_TWEETS is modified on main proces but im spawning the separate proces to pupulate references after main is done so this shoulnt be the case. Will investigate over the weekend. but im not ale to now

[image](./database.png)
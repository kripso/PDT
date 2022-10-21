# Assignment 1

## 1. Vyhľadajte v authors username s presnou hodnotou ‘mfa_russia’ a analyzujte daný select. Akú metódu vám vybral plánovač a prečo - odôvodnite prečo sa rozhodol tak ako sa rozhodol?

Query planer used Parallel Sequantion Scan. Select with where option can be parallelized. where the table is split into chunks of roughly same size for each available worker.

```sql
EXPLAIN ANALYZE SELECT * FROM authors WHERE username = 'mfa_russia';
```

![image](./assets/Pasted%20image%2020221019214200.png)

## 2. Koľko workerov pracovalo na danom selecte a na čo slúžia? Zdvihnite počet workerov a povedzte ako to ovplyvňuje čas. Je tam nejaký strop? Ak áno, prečo? Od čoho to závisí (napíšte a popíšte všetky parametre)?

workers used by default -> 4

* this was because in "postrgresql.conf" the PGTune set them to 4 by default
* the number of workers represents number of parallel processes that work on that query with (in this case) four different parts of authors table

```sql
SET max_parallel_workers_per_gather TO 5;
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM authors WHERE username = 'mfa_russia';
```

![image](./assets/Pasted%20image%2020221019225515.png)

with max_parallel_workers_per_gather set to 5 the execution time lowerd by 80ms.Which is almost 1/3 performance increase on this query.

```sql
SET max_parallel_workers_per_gather TO 6;
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM authors WHERE username = 'mfa_russia';
```

![image](./assets/Pasted%20image%2020221019230330.png)

```sql
SET max_parallel_workers_per_gather TO 7;
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM authors WHERE username = 'mfa_russia';
```

![image](./assets/Pasted%20image%2020221019230400.png)

as we can see increasing **max_parallel_workers_per_gather** to more that 5 on this query didnt affect the query optimizer even though that **max_parallel_workers** is 12.

## 3. Vytvorte btree index nad username a pozrite ako sa zmenil čas a porovnajte výstup oproti požiadavke bez indexu. Potrebuje plánovač v tejto požiadavke viac workerov? Čo ovplyvnilo zásadnú zmenu času?

```sql
CREATE INDEX index_authors_username ON authors using BTREE (username);
EXPLAIN ANALYZE SELECT * FROM authors WHERE username = 'mfa_russia';
```

![image](./assets/Pasted%20image%2020221020002402.png)
query on indexed table column took only a framction compared to unidexed table. 0.035 vs 253.474

from explain we see that only one workerwas used because on indexed column we dont need to search whole column sequentialy but only hashed b-tree with has logaritmic time complexity.

## 4. Vyberte používateľov, ktorý majú followers_count väčší, rovný ako 100 a zároveň menší, rovný 200. Potom zmeňte rozsah na väčší, rovný ako 100 a zároveň menší, rovný 120. Je tam rozdiel, ak áno prečo?

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM authors WHERE followers_count BETWEEN 100 AND 200;
```

![image](./assets/Pasted%20image%2020221020003313.png)

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM authors WHERE followers_count BETWEEN 100 AND 120;
```

![image](./assets/Pasted%20image%2020221020003423.png)

From explain we see that there is a differance in what type of scan the optimizer uses the narrower our contition becomes the more likely is the optimizer going to choose parallel scan instead of plain sequantial one. Same as our first query witch was very specific here where the differance was just 20 follower the optimizer chose parallel scan. The behavior really depands on how likely the where contition is to have results in multiple workers at the same time because if data would be split on more workers they will then need to comunicate with each other and merge the results to not have aditional duplicates and such.

## 5. Vytvorte index nad 4 úlohou  a v oboch podmienkach popíšte prácu s indexom. Čo je to Bitmap Index Scan a prečo je tam Bitmap Heap Scan? Prečo je tam recheck condition? Použil sa vždy index?

```sql
CREATE INDEX index_authors_followers_count ON authors (followers_count);
```

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM authors WHERE followers_count BETWEEN 100 AND 200;
```

![image](./assets/Pasted%20image%2020221021185207.png)

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM authors WHERE followers_count BETWEEN 100 AND 120;
```

![image](./assets/Pasted%20image%2020221021185147.png)

Index was always used. Bitmap Index Scan is used together with Bitmap Heap Scan. Bitmap Index Scan constructs a bitmap of potential row locations and Heap Scan than decite which data to extract from it.
Its kind of in the middle of sequential scan and index scan. Recheck cond was used because a lossy bitmap was used because work_mem was not big enough to contain a bitmap that contains one bit per table row.

## 7. Vytvorte ďalšie 3 btree indexy na name, followers_count, a description a insertnite si svojho používateľa (to je jedno aké dáta) do authors. Koľko to trvalo? Dropnite indexy a spravte to ešte raz. Prečo je tu rozdiel?

```sql
CREATE INDEX index_authors_name ON authors (name);
CREATE INDEX index_authors_description ON authors (description);
-- CREATE INDEX index_authors_followers_count ON authors (followers_count);
```

```sql
INSERT INTO authors VALUES (9999999, 'roland', 'kripso', 'your average Joe', 444, 333, 222, 111);
```

result: `Query returned successfully in 33 msec.`

```sql
DROP INDEX index_authors_name;
DROP INDEX index_followers_interval;
DROP INDEX index_authors_description;
DROP INDEX index_authors_followers_count;

DELETE FROM authors WHERE id=9999999;
```

```sql
INSERT INTO authors VALUES (9999999, 'roland', 'kripso', 'your average Joe', 444, 333, 222, 111);
```

result: `Query returned successfully in 76 msec.`

On multiple testings this behavior was not consistent but ill include only the initial test. Here we can see that inserting into a indexed table was slightly faster for which i dont have an explanation other than in such a fast insert times we can see some otliers here and there. From what it looks like my computres can recompute the indexes an insert values to authors table way too fast to find any difference.

## 8. Vytvorte btree index nad conversations pre retweet_count a pre content. Porovnajte ich dĺžku vytvárania. Prečo je tu taký rozdiel? Čím je ovplyvnená dĺžka vytvárania indexu a prečo?

```sql
CREATE INDEX index_tweet_content ON tweets (content);
```

result: `Query returned successfully in 1 min 31 secs.`

```sql
CREATE INDEX index_tweet_retweet_count ON tweets (retweet_count);
```

result: `Query returned successfully in 9 secs 6 msec.`

Creating a B-tree index over numeric values of 8 bytes is much faster than going through alphanumeric values of potentialy unlimited lenght. On text columns the b-tree algorithm has to go over the whole text to create the index and therefore is much slower.

## 9. Porovnajte indexy pre retweet_count, content, followers_count, name,... v čom sa líšia pre nasledovné parametre: počet root nódov, level stromu, a priemerná veľkosť itemu. Vysvetlite

```sql
CREATE extension pgstattuple;
CREATE extension pageinspect;
```

```sql
SELECT root, level FROM bt_metap('index_tweet_content');
SELECT avg_item_size FROM bt_page_stats('index_tweet_content',10000);
```

![image](./assets/Pasted%20image%2020221020204834.png)
![image](./assets/Pasted%20image%2020221020205250.png)

```sql
SELECT root, level FROM bt_metap('index_tweet_retweet_count');
SELECT avg_item_size FROM bt_page_stats('index_tweet_retweet_count',10000);
```

![image](./assets/Pasted%20image%2020221020205645.png)
![image](./assets/Pasted%20image%2020221020205739.png)

```sql
SELECT root, level FROM bt_metap('index_authors_name');
SELECT avg_item_size FROM bt_page_stats('index_authors_name',10000);
```

![image](./assets/Pasted%20image%2020221020205752.png)
![image](./assets/Pasted%20image%2020221020205812.png)

```sql
SELECT root, level FROM bt_metap('index_authors_followers_count');
SELECT avg_item_size FROM bt_page_stats('index_authors_followers_count',1000);
```

![image](./assets/Pasted%20image%2020221020205827.png)
![image](./assets/Pasted%20image%2020221020205906.png)

The root in content is the largest becuse it has the largest number of children than there is authors names. This would corespond with the number of levels but that wouldnt have to happen necessarily. Avg item size corespons to avg size of an item in 10 000 item sample that bt_page_stats took.

## 10. Vyhľadajte v conversations content meno „Gates“ na ľubovoľnom mieste a porovnajte výsledok po tom, ako content naindexujete pomocou btree. V čom je rozdiel a prečo?

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tweets WHERE "content" LIKE '%Gates%';
```

![image](./assets/Pasted%20image%2020221020210351.png)

```sql
CREATE INDEX index_tweets_content ON tweets (content);

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tweets WHERE "content" LIKE '%Gates%';
```

![image](./assets/Pasted%20image%2020221020210731.png)

There is no difference when using LIKE with prefix and sufix search b tree would be used if we search for equality.

## 11. Vyhľadajte tweet, ktorý začína “There are no excuses” a zároveň je obsah potenciálne senzitívny (possibly_sensitive). Použil sa index? Prečo? Ako query zefektívniť?

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tweets WHERE possibly_sensitive=true AND "content" LIKE 'There are no excuses%';
```

![image](./assets/Pasted%20image%2020221021151845.png)

```sql
CREATE INDEX index_tweets_content_prefix ON tweets USING btree (content varchar_pattern_ops);

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tweets WHERE possibly_sensitive=true AND "content" LIKE 'There are no excuses%';
```

![image](./assets/Pasted%20image%2020221021152016.png)

Index was not used for more or less same reason why it wasn't used in the last exercise. Although b-tree index searches on prefix basis we have to enable one parameter which would allow for partial equality meaning prefix search would work. And the parameter was used in the second portion "varchar_pattern_ops". From testing we can see the same query took only 0.090ms.

## 12. Vytvorte nový btree index, tak aby ste pomocou neho vedeli vyhľadať tweet, ktorý končí reťazcom „<https://t.co/pkFwLXZlEm>“ kde nezáleží na tom ako to napíšete. Popíšte čo jednotlivé funkcie robia

```sql
CREATE INDEX index_tweets_content_reverse_varchar_pattern_ops ON tweets (REVERSE(LOWER("content")) varchar_pattern_ops);

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tweets WHERE REVERSE(LOWER("content")) lIKE REVERSE(LOWER('%https://t.co/pkFwLXZlEm'));
```

![image](./assets/Pasted%20image%2020221021161740.png)

Almost the same approach that we took on excersise 11 can be used here with two differences.

1. we use reverse to reverse the content
2. we use lower to make the whole content be in lower case

First change is used to help with sufix search as this approarch is the easiest and fastest to perform. We basicaly do a prefix search but in reverse.

The second change converts the content to lower case because we want to have the freadom of writing the query imput without case sensitivity.

## 14. Nájdite conversations, ktoré majú reply_count väčší ako 150, retweet_count väčší rovný ako 5000 a výsledok zoraďte podľa quote_count. Následne spravte jednoduché indexy a popíšte ktoré má a ktoré nemá zmysel robiť a prečo. Popíšte a vysvetlite query plan, ktorý sa aplikuje v prípade použitia jednoduchých indexov

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tweets WHERE retweet_count >= 5000 AND reply_count > 150 ORDER BY quote_count DESC;
```

![image](./assets/Pasted%20image%2020221021233505.png)

```sql
CREATE INDEX index_tweets_retweet_count ON tweets (retweet_count);
CREATE INDEX index_tweets_quote_count ON tweets (quote_count);
CREATE INDEX index_tweets_reply_count ON tweets (reply_count);
```

![image](./assets/Pasted%20image%2020221021233345.png)

The only index that was meanigful based on query optimizer was index_tweets_retweet_count, as optimizer only used this one.

## 15. Na predošlú query spravte zložený index a porovnajte výsledok s tým, keď je sú indexy separátne. Výsledok zdôvodnite. Popíšte použitý query plan. Aký je v nich rozdiel?

```sql
CREATE INDEX index_tweets_reply_retweet_counts ON tweets (reply_count, retweet_count, quote_count);
```

![image](./assets/Pasted%20image%2020221021172436.png)

the optimizer prioritized the complex index because all the walues were used in search.

## 16. Napíšte dotaz tak, aby sa v obsahu konverzácie našlo slovo „Putin“ a zároveň spojenie „New World Order“, kde slová idú po sebe a zároveň obsah je senzitívny. Vyhľadávanie má byť indexe. Popíšte použitý query plan pre GiST aj pre GIN. Ktorý je efektívnejší?

```sql
ALTER TABLE tweets ADD COLUMN vector_content tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce("content",''))) STORED;

CREATE INDEX gin_index_tweets_content ON tweets USING gin(vector_content);

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tweets WHERE vector_content @@ to_tsquery('english', 'Putin & New <-> World <-> Order') AND possibly_sensitive=true;
```

![image](./assets/Pasted%20image%2020221021201111.png)

```sql
CREATE INDEX gist_index_tweets_content ON tweets USING gist(vector_content);

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tweets WHERE vector_content @@ to_tsquery('english', 'Putin & New <-> World <-> Order') AND possibly_sensitive=true;
```

Even though the Based on what GIST should do, where it should have better performance it in our case does not have. From our testing it has way worse performace for reason i cant explain. Whereas GIN which should be more precise and slower has better performace. The wanted behavior coresponds with why the optimizer used GIST over GIN but somehow the GIN had better performance.

![image](./assets/Pasted%20image%2020221021202518.png)

## 17. Vytvorte vhodný index pre vyhľadávanie v links.url tak aby ste našli kampane z ‘darujme.sk’. Ukážte dotaz a použitý query plan. Vysvetlite prečo sa použil tento index

```sql
CREATE EXTENSION pg_trgm; 
CREATE INDEX idx_urls_trgm ON links USING gin (url gin_trgm_ops);

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM links WHERE url LIKE '%darujme.sk%';
```

![image](./assets/Pasted%20image%2020221021203247.png)

Gin index over urls with help of trigrams is a clear choice here because we want to find contains in the url.

## 18. Vytvorte query pre slová "Володимир" a "Президент" pomocou FTS (tsvector a tsquery) v angličtine v stĺpcoch conversations.content, authors.decription a authors.username, kde slová sa môžu nachádzať v prvom, druhom ALEBO treťom stĺpci. Teda vyhovujúci záznam je ak aspoň jeden stĺpec má „match“. Výsledky zoradíte podľa retweet_count zostupne. Pre túto query vytvorte vhodné indexy tak, aby sa nepoužil ani raz sekvenčný scan (správna query dobehne rádovo v milisekundách, max sekundách na super starých PC). Zdôvodnite čo je problém s OR podmienkou a prečo AND je v poriadku pri joine

```sql
ALTER TABLE authors ADD COLUMN vector_description tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(description, ''))) STORED;
ALTER TABLE authors ADD COLUMN vector_username tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(username, ''))) STORED;

CREATE INDEX gin_index_authors_description ON authors USING gin(vector_description);
CREATE INDEX gin_index_authors_username ON authors USING gin(vector_username);
```

```sql
EXPLAIN (ANALYZE, BUFFERS)  
    SELECT
        tweets.id AS tweets_id, tweets.author_id AS tweets_author_id, tweets.content AS tweets_content, tweets.retweet_count as tweets_retweet_cout,
        authors.description AS authors_description, authors.id AS authors_id, authors.username AS authors_username, 
        tweets.vector_content, authors.vector_description, authors.vector_username
    FROM
        tweets
    LEFT JOIN 
        authors ON tweets.author_id = authors.id
    WHERE
        tweets.vector_content @@ to_tsquery('english', 'Володимир | Президент') 
    OR 
        authors.vector_description @@ to_tsquery('english', 'Володимир | Президент')
    OR
        authors.vector_username @@ to_tsquery('english', 'Володимир | Президент')
    ORDER BY 
        tweets.retweet_count desc;
```

![image](./assets/Pasted%20image%2020221021220419.png)

```sql
EXPLAIN (ANALYZE, BUFFERS)
    SELECT
        tweets.id, tweets.author_id, tweets.content, tweets.retweet_count,
        authors.description AS authors_description, authors.id AS authors_id, authors.username AS authors_username, 
        tweets.vector_content, authors.vector_description, authors.vector_username
    FROM
        tweets
    INNER JOIN 
        authors ON tweets.author_id = authors.id
    WHERE
        tweets.vector_content @@ to_tsquery('english', 'Володимир & Президент') 
UNION
    SELECT
        tweets.id, tweets.author_id, tweets.content, tweets.retweet_count,
        authors.description AS authors_description, authors.id AS authors_id, authors.username AS authors_username, 
        tweets.vector_content, authors.vector_description, authors.vector_username
    FROM
        tweets
    INNER JOIN 
        authors ON tweets.author_id = authors.id
    WHERE
        authors.vector_description @@ to_tsquery('english', 'Володимир & Президент')
UNION
    SELECT
        tweets.id, tweets.author_id, tweets.content, tweets.retweet_count,
        authors.description AS authors_description, authors.id AS authors_id, authors.username AS authors_username, 
        tweets.vector_content, authors.vector_description, authors.vector_username
    FROM
        tweets
    INNER JOIN 
        authors ON tweets.author_id = authors.id
    WHERE
        authors.vector_username @@ to_tsquery('english', 'Володимир & Президент')
ORDER BY
    retweet_count desc;
```

![image](./assets/Pasted%20image%2020221021222736.png)
![image](./assets/Pasted%20image%2020221021222753.png)

When using OR in the query the optimizer uses HASH JOIN which does not support the use of indexing. So when we want to use and in our query we can create separate queries for each or statement and then UNITE them to one table.

Here for some reason using tweets.retweet_count as tweet_retweet_count would break this query and it would do one segential scan, so i had to ommit it from the query.

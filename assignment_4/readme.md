Dôležité: všetky počty počítate na základe databázy a nepreberáte uložené čísla.  

### 1. Vytvorte volaním iba jednej query nového Autora s Vašim menom (vyplňte minimálne name a username) a tým istým volaním vytvorte tweet ktorý bude obsahovať aspoň jeden vami vybraný Hashtag (vzťah :HAS) a ktorý bude retweetovať najretweetovanejší tweet Vladimíra Zelenského{username:"ZelenskyyUa"}. 

```cypher
MATCH (:Author {username:"ZelenskyyUa"})-[:TWEETED]->(zel_tweet:Conversation)
WITH zel_tweet
ORDER BY zel_tweet.retweet_count DESC LIMIT 1
MATCH (h:Hashtag {tag: 'StandWithUkraine'})
CREATE (a:Author {name:'roland', username:'kripso'})-[:TWEETED]->(c:Conversation {content:'content with hashtag #StandWithUkraine'})-[has:HAS]->(h), (c)-[ret:RETWEETED]->(zel_tweet)
RETURN a,c,h,has,ret,zel_tweet;
```

### 2. Vyhľadajte zlyhania influencerov. Vyhľadajte 20 najmenej retweetovanych tweetov od Accountov, ktoré sú na prvých 10 miestach v celkovom počte retweetov. Aj keď taký príkld v datasete nie je, počítajte aj s prípadom, ak by niektorý tweet bol retweetnutý 0 krát. 

```cypher
MATCH (a:Author)-[:TWEETED]->(t:Conversation)
call {
    with a
    Match (a)-[:TWEETED]->(t:Conversation)
    with  t, sum(t.retweet_count) as tw_
    order by tw_a asc limit 20
    RETURN collect(t) as tweets
}
with a, tweets, sum(t.retweet_count) as tw_d
return a, tweets
order by tw_d desc limit 10
```

```cypher
MATCH (a:Author)-[:TWEETED]->(t:Conversation)
with a, sum(t.retweet_count) as tweets_sum
call {
    with a, tweets_sum
    match (a)-[:TWEETED]->(t)
    with a, t, tweets_sum
    order by tweets_sum asc limit 20
    RETURN collect(t) as tweets
}
with a, tweets, tweets_sum
return a, tweets
order by tweets_sum desc limit 10
```
### 3. Odporučte používateľovi (username: Marios59885699) followovanie ďalších autorov na základe zhody v retweetovaní rovnakých tweetov: Vyhľadajte 10 autorov, ktorí retweetli najviac tweetov rovnakych, ako používateľ Marios59885699. Počítajú sa aj retweety tweetov, ktoré retweetujú rovnaký tweet. 

### 4. Nájdite najkratšie cesty medzi Ukrajinským parlamentom (username: “ua_parliament”) a NextaTV (username: “nexta_tv”) cez vzťahy TWEETED, RETWEETED, REPLIED_TO a QUOTED. Hľadajte do hĺbky maximálne 10. (hint: allShortestPaths) 

### 5. Upravte query z predchádzajúcej úlohy, aby vrátila iba nájdenú najkratšiu cestu a jednotlivé uzly typu Conversation v nej aj spolu z autorom, ktorý ich tweetol. (hint: UNWIND) 

### 6. Vypíšte 10 najpoužívanejších hashtagov v datasete aj s celkovým počtom použití a autorom, ktorý daný hashtag najviac krát použil. (hint: collect)
```cypher
MATCH (c:Conversation)-[has:HAS]->(h:Hashtag)
return h, count(has) as h_count
order by h_count desc limit 10
```


```cypher
MATCH (:Conversation)-[has:HAS]->(h:Hashtag)
with h, count(has) as h_count
order by h_count desc limit 10
MATCH (a:Author)-[t:TWEETED]->(:Conversation)-[:HAS]->(h)
WITH a, h, count(t) as per_user, h_count
ORDER BY per_user DESC
RETURN h.tag as hashtag, head(collect(a.username)) as most_used_by, h_count as total_times_used
```

version 2
```cypher
MATCH (:Conversation)-[has:HAS]->(h:Hashtag)
with h, count(has) as h_count
order by h_count desc limit 10
call
{
    with h, h_count
    MATCH (a:Author)-[t:TWEETED]->(:Conversation)-[:HAS]->(h)
    return a, count(t) as per_user
    ORDER BY per_user DESC
    limit 1
}
RETURN h.tag as hashtag, a.username as most_used_by, h_count as total_times_used
```
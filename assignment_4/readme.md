# Assignment_4

### 1. Vytvorte volaním iba jednej query nového Autora s Vašim menom (vyplňte minimálne name a username) a tým istým volaním vytvorte tweet ktorý bude obsahovať aspoň jeden vami vybraný Hashtag (vzťah :HAS) a ktorý bude retweetovať najreplyovejsi tweet Vladimíra Zelenského{username:"ZelenskyyUa"}

```sql
MATCH (za:Author {username: 'ZelenskyyUa'})-[:TWEETED]->(zel_tweet:Conversation)<-[rp:REPLIED_TO]-(:Conversation)
with zel_tweet, count(rp) as rp_count
ORDER BY rp_count DESC LIMIT 1
MATCH (h:Hashtag {tag: 'StandWithUkraine'})
CREATE (a:Author {name:'roland', username:'kripso'})-[:TWEETED]->(c:Conversation {content:'content with hashtag #StandWithUkraine'})-[has:HAS]->(h), (c)-[ret:RETWEETED]->(zel_tweet)
RETURN a,c,h,has,ret,zel_tweet;
```

### 2. Vyhľadajte zlyhania influencerov. Vyhľadajte 20 najmenej retweetovanych tweetov od Accountov, ktoré sú na prvých 10 miestach v celkovom počte retweetov. Aj keď taký príkld v datasete nie je, počítajte aj s prípadom, ak by niektorý tweet bol retweetnutý 0 krát

```sql
MATCH (a:Author)-[:TWEETED]->(:Conversation)<-[rt:RETWEETED]-(:Conversation)
with a, count(rt) as rt_count
order by rt_count desc limit 10
call {
    with a
    match (a)-[:TWEETED]->(t:Conversation)<-[rt2:RETWEETED]-(:Conversation)
    return t, count(rt2) as tweets_sum
    order by tweets_sum asc limit 20
}
return a.username, tweets_sum, t.id, t.content
order by tweets_sum asc limit 20
```

### 3. Odporučte používateľovi (username: Marios59885699) followovanie ďalších autorov na základe zhody v retweetovaní rovnakých tweetov: Vyhľadajte 10 autorov, ktorí retweetli najviac tweetov rovnakych, ako používateľ Marios59885699. Počítajú sa aj retweety tweetov, ktoré retweetujú rovnaký tweet

```sql
match (m:Author {username:'Marios59885699'})-[:TWEETED]->(:Conversation)-[:RETWEETED]->(rt:Conversation)
match (a:Author)-[t:TWEETED]->(:Conversation)-[ret:RETWEETED*..2]->(rt)
where m <> a
with a, count(ret) as retweet_count
order by retweet_count desc
return a.username, retweet_count
limit 10
```

### 4. Nájdite najkratšie cesty medzi Ukrajinským parlamentom (username: “ua_parliament”) a NextaTV (username: “nexta_tv”) cez vzťahy TWEETED, RETWEETED, REPLIED_TO a QUOTED. Hľadajte do hĺbky maximálne 10. (hint: allShortestPaths)

```sql
MATCH (par:Author {username: 'ua_parliament'})
MATCH (nex:Author {username: 'nexta_tv'})
return allShortestPaths((par)-[:TWEETED|RETWEETED|REPLIED_TO|QUOTED*..10]-(nex))
```

### 5. Upravte query z predchádzajúcej úlohy, aby vrátila iba nájdenú najkratšiu cestu a jednotlivé uzly typu Conversation v nej aj spolu z autorom, ktorý ich tweetol. (hint: UNWIND)

```sql
MATCH (par:Author {username: 'ua_parliament'})
MATCH (nex:Author {username: 'nexta_tv'})
UNWIND allShortestPaths((par)-[:TWEETED|RETWEETED|REPLIED_TO|QUOTED*..10]-(nex)) as route
UNWIND nodes(route) as sh_path_nodes
call
{
    with sh_path_nodes
    Match (a:Author)-[:TWEETED]->(sh_path_nodes)
    return a
}
return a, sh_path_nodes
```

### 6. Vypíšte 10 najpoužívanejších hashtagov v datasete aj s celkovým počtom použití a autorom, ktorý daný hashtag najviac krát použil. (hint: collect)

```sql
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

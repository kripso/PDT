# Assignment_4

### 1. Vytvorte volaním iba jednej query nového Autora s Vašim menom (vyplňte minimálne name a username) a tým istým volaním vytvorte tweet ktorý bude obsahovať aspoň jeden vami vybraný Hashtag (vzťah :HAS) a ktorý bude retweetovať najreplyovejsi tweet Vladimíra Zelenského{username:"ZelenskyyUa"}

ako prve som si spravil MATCH ktory mi vratil prezitenta zelenskeho, presiel jeho tweetami a spocital mnozstvo reply kazdeho jeho tweetu, nakoniec tam je pridany order a limit aby som vybral len najviac replienuty.

druhy match my selectne hashtag ktory pouzivam v tweete ktory budem vytvarat

nakoniec uz vytvaram samotny zaznam v ktorom vyuzivam predchadzajuce nody a takties priamo zakodovam moje osobne informacie s tweetom.

```sql
MATCH (za:Author {username: 'ZelenskyyUa'})-[:TWEETED]->(zel_tweet:Conversation)<-[rp:REPLIED_TO]-(:Conversation)
with zel_tweet, count(rp) as rp_count
ORDER BY rp_count DESC LIMIT 1
MATCH (h:Hashtag {tag: 'StandWithUkraine'})
CREATE (a:Author {name:'roland', username:'kripso'})-[:TWEETED]->(c:Conversation {content:'content with hashtag #StandWithUkraine'})-[has:HAS]->(h), (c)-[ret:RETWEETED]->(zel_tweet)
RETURN a,c,h,has,ret,zel_tweet;
```

![image](./assets/Pasted%20image%2020221123193146.png)

### 2. Vyhľadajte zlyhania influencerov. Vyhľadajte 20 najmenej retweetovanych tweetov od Accountov, ktoré sú na prvých 10 miestach v celkovom počte retweetov. Aj keď taký príkld v datasete nie je, počítajte aj s prípadom, ak by niektorý tweet bol retweetnutý 0 krát

Prvym matchom si vyhladam najuspesnejsie ucty a za pouziti call funkcie pre kazdy z tychto uctov zozbieram ich 20 najmenej uspesne tweetow(teoreticky sa mohlo stat ze vsetky najneuspesnejsie tweety by boli od jedneho pouzivatela) ktore na konci zoradim a vratim len prvych 20

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
return a, tweets_sum, t
order by tweets_sum asc limit 20
```

![image](./assets/Pasted%20image%2020221123193319.png)

### 3. Odporučte používateľovi (username: Marios59885699) followovanie ďalších autorov na základe zhody v retweetovaní rovnakých tweetov: Vyhľadajte 10 autorov, ktorí retweetli najviac tweetov rovnakych, ako používateľ Marios59885699. Počítajú sa aj retweety tweetov, ktoré retweetujú rovnaký tweet

Vysledna query sa stavia z dvoch match funkcii kde prva mi nachadza zvoleneho pouzivatela a konverzacie ktore retweetoval a v druhom tieto retweety vyhladavam do hlbky 2 aby sme vyhladali aj retweety retweetov

```sql
match (m:Author {username:'Marios59885699'})-[:TWEETED]->(:Conversation)-[:RETWEETED]->(rt:Conversation)
match (a:Author)-[t:TWEETED]->(:Conversation)-[ret:RETWEETED*..2]->(rt)
where m <> a
with a, count(ret) as retweet_count
order by retweet_count desc
return a.username, retweet_count
limit 10
```

![image](./assets/Pasted%20image%2020221123193520.png)

### 4. Nájdite najkratšie cesty medzi Ukrajinským parlamentom (username: “ua_parliament”) a NextaTV (username: “nexta_tv”) cez vzťahy TWEETED, RETWEETED, REPLIED_TO a QUOTED. Hľadajte do hĺbky maximálne 10. (hint: allShortestPaths)

Pomocou hintu na najdenie najmensie cesty bolo nutne uz len matchnut nasich dvoch autorov a prehladavat do hlbky 10 pomocou *..10

```sql
MATCH (par:Author {username: 'ua_parliament'})
MATCH (nex:Author {username: 'nexta_tv'})
return allShortestPaths((par)-[:TWEETED|RETWEETED|REPLIED_TO|QUOTED*..10]-(nex))
```

![image](./assets/Pasted%20image%2020221123193548.png)

### 5. Upravte query z predchádzajúcej úlohy, aby vrátila iba nájdenú najkratšiu cestu a jednotlivé uzly typu Conversation v nej aj spolu z autorom, ktorý ich tweetol. (hint: UNWIND)

nato aby som sa vedel dostat az k autorovmu nodu pomocou unwind som musel pouzit danu funkciu 2 krat raz na paths a potom na nodes(routes)-kde nodes rovno zakoduje path na node aby som ho vedel vyuzit v call funkcii ktora vyhladava autora tweetu

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

![image](./assets/Pasted%20image%2020221123193622.png)

### 6. Vypíšte 10 najpoužívanejších hashtagov v datasete aj s celkovým počtom použití a autorom, ktorý daný hashtag najviac krát použil. (hint: collect)

Na vyhladanie najpouzivanejsich hastagov staci jednoduchy match a count(tweetov) kde nakoniec prejdem kazdym hastagom kde pre kazdy vyhladam tweety ktore ich pouzivaju a od ktorych autorov.

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

![image](./assets/Pasted%20image%2020221123193718.png)

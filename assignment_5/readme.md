# Assignment 5

v src sa nachadza:
1. dump z insomnie ktory obsahuje vsetky requesty na elastic
2. denormalisation.sql -> query na postgre ktory vytvori denormalizovanu tabulku
3. mappings.json -> index pre elastic
4. main.py -> python import kod do elasticu z postgre

v hlavnom repoziraty je:
1. requirements.txt
2. pouzity docker-compose na rozbehanie clustera

### Rozbehajte si 3 inštancie Elasticsearch-u  
```yaml
version: '2.2'
services:
  ES01:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.2
    container_name: ES01
    environment:
      - node.name=ES01
      - xpack.security.enabled=false
      - xpack.monitoring.collection.enabled=true
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=ES02,ES03
      - cluster.initial_master_nodes=ES01,ES02,ES03
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - data_volume:/data
    ports:
      - 9200:9200
    networks:
      - elastic

  ES02:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.2
    container_name: ES02
    environment:
      - node.name=ES02
      - xpack.security.enabled=false
      - xpack.monitoring.collection.enabled=true
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=ES01,ES03
      - cluster.initial_master_nodes=ES01,ES02,ES03
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - data_volume:/data
    ports:
      - 9201:9200
    networks:
      - elastic

  ES03:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.2
    container_name: ES03
    environment:
      - node.name=ES03
      - xpack.security.enabled=false
      - xpack.monitoring.collection.enabled=true
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=ES01,ES02
      - cluster.initial_master_nodes=ES01,ES02,ES03
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - data_volume:/data
    ports:
      - 9202:9200
    networks:
      - elastic

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.2
    container_name: kibana
    depends_on:
      - ES01
      - ES02
      - ES03
    ports:
      - 5601:5601
    networks:
      - elastic
    environment:
      ELASTICSEARCH_URL: http://localhost:9200
      ELASTICSEARCH_HOSTS: '["http://ES01:9200","http://ES02:9200","http://ES03:9200"]'

networks:
  elastic:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.enable_icc: "true"

volumes:
  data_volume:
    driver: local
    driver_opts:
      type: 'none'
      o: 'bind'
      device: full_path

```
Na rozbehanie clustra som so vytvoril tento docker-compose podla dokumentacii a predchadzajucisch skusenosti. dolezite informacie z neho su ze kazdy ES si exposuzem v pripade vypadku aby som sa vedel z vonka pripojit aspon na jeden beziaci node. 

Dalo by sa to ohandlovat aj pomocou proxy a tak ale to uz sa mi nechcelo. Kibana to handluje uz sama a vieme sa z vonka cez kibanu pytat na elastic nody napriklad takto http://localhost:5601/api/console/proxy?path=_cat%2Findices%3Fv&method=GET ale toto som nevyuzival.

![image](./assets/Pasted%20image%2020221224110031.png)

### Vytvorte index pre Tweety, ktorý bude mať “optimálny“ počet shardov a replík pre 3 nódy (aby tam bola distribúcia dotazov vo vyhľadávaní, aj distribúcia uložených dát)  
```json
"index": {
	"number_of_shards": 3,
	"number_of_replicas": 2
},
```
Ako optimalny pocet shardov sme zvolili na zaciatku tri lebo vela dokumentacii odporucalo plus minus 1 shard na 20gb alebo ako druha moznost 1 shard na CPU core. Nakolko mam 12 jadier skusil som verziu aj 12 shardov kde import time vsetkych tweetov sa znizil z 80 min na 58.

### Vytvorte mapping pre normalizované dáta z Postgresu (denormalizujte ich) – Každý  
```json
"author": {
	"properties": {
		"id": {
			"type": "long"
		},
		"name": {
			"type": "keyword",
			"fields": {
				"name_shingle": {
					"type": "text",
					"analyzer": "custom_shingles"
				},
				"name_ngram": {
					"type": "text",
					"analyzer": "custom_ngram"
				}
			}
		},
		"username": {
			"type": "keyword",
			"fields": {
				"username_ngram": {
					"type": "text",
					"analyzer": "custom_ngram"
				}
			}
		},
		"description": {
			"type": "text",
			"analyzer": "englando",
			"fields": {
				"description_shingle": {
					"type": "text",
					"analyzer": "custom_shingles"
				}
			}
		},
		"followers_count": {
			"type": "integer"
		},
		"following_count": {
			"type": "integer"
		},
		"tweet_count": {
			"type": "integer"
		},
		"listed_count": {
			"type": "integer"
		}
	}
},
```

```json
"annotations": {
	"type": "nested",
	"properties": {
		"id": {
			"type": "long"
		},
		"value": {
			"type": "keyword"
		},
		"type": {
			"type": "keyword"
		},
		"probability": {
			"type": "half_float"
		}
	}
},
"domains": {
	"type": "nested",
	"properties": {
		"id": {
			"type": "long"
		},
		"name": {
			"type": "text"
		},
		"desc": {
			"type": "text"
		}
	}
},
"entities": {
	"type": "nested",
	"properties": {
		"id": {
			"type": "long"
		},
		"name": {
			"type": "text"
		},
		"desc": {
			"type": "text"
		}
	}
},
"hashtags": {
	"type": "nested",
	"properties": {
		"id": {
			"type": "long"
		},
		"tag": {
			"type": "keyword"
		}
	}
},
"links": {
	"type": "nested",
	"properties": {
		"id": {
			"type": "long"
		},
		"url": {
			"type": "keyword"
		},
		"title": {
			"type": "keyword"
		},
		"description": {
			"type": "keyword"
		}
	}
},
```
Mapping skoro vsetkych fieldov je logicky rovnaky ako sme mali v postgre tabulky s tym ze jeden doc obsahuje vsetky udaje o tweete a jeho metadatach. jedine co sa podstatnejsie zmenilo je ze v ramci "meta" cize udaje o tveete mam uchovany objekt tweetu s jeho typom.

Referencie na tweet su pod fieldom "referenced" kde som ulozil len:
parent_id -> id parent tweetu
referenced_content -> content parent tweetu
referenced_author_id -> author id parent tweetu
referenced_author_name -> author name parent tweetu
referenced_author_username -> author username parent tweetu
referenced_hashtags -> hashtagy parent tweetu
```json
"meta": {
	"properties": {
		"id": {
			"type": "long"
		},
		"type": {
			"type": "keyword"
		},
		"content": {
			"type": "text",
			"analyzer": "englando"
		},
		"possibly_sensitive": {
			"type": "boolean"
		},
		"language": {
			"type": "keyword"
		},
		"source": {
			"type": "keyword"
		},
		"retweet_count": {
			"type": "integer"
		},
		"reply_count": {
			"type": "integer"
		},
		"like_count": {
			"type": "integer"
		},
		"quote_count": {
			"type": "integer"
		},
		"created_at": {
			"type": "date"
		}
	}
},
```

```json
"referenced": {
	"properties": {
		"parent_id": {
			"type": "long"
		},
		"referenced_content": {
			"type": "text",
			"analyzer": "englando"
		},
		"referenced_author_id": {
			"type": "long"
		},
		"referenced_author_name": {
			"type": "keyword"
		},
		"referenced_author_username": {
			"type": "keyword"
		},
		"referenced_hashtags": {
			"type": "nested",
			"properties": {
				"id": {
					"type": "long"
				},
				"tag": {
					"type": "keyword"
				}
			}
		}
	}
}
```

### Pre index tweets vytvorte 3 vlastné analyzéry (v settings) nasledovne:  
```json
"analysis": {
	"analyzer": {
		"englando": {
			"type": "custom",
			"char_filter": [
				"html_strip"
			],
			"tokenizer": "standard",
			"filter": [
				"english_possessive_stemmer",
				"lowercase",
				"english_stop",
				"english_stemmer"
			]
		},
		"custom_shingles": {
			"type": "custom",
			"char_filter": [
				"html_strip"
			],
			"tokenizer": "standard",
			"filter": [
				"lowercase",
				"asciifolding",
				"filter_shingles"
			]
		},
		"custom_ngram": {
			"type": "custom",
			"char_filter": [
				"html_strip"
			],
			"tokenizer": "standard",
			"filter": [
				"lowercase",
				"asciifolding",
				"filter_ngrams"
			]
		},
		"just_lowercase": {
			"type": "custom",
			"tokenizer": "standard",
			"filter": [
				"lowercase"
			]
		}
	},
	"filter": {
		"english_possessive_stemmer": {
			"type": "stemmer",
			"stem_english_possessives": true
		},
		"english_stop": {
			"type": "stop",
			"stopwords": "_english_"
		},
		"english_stemmer": {
			"type": "stemmer",
			"language": "english"
		},
		"filter_ngrams": {
			"type": "ngram",
			"min_gram": 1,
			"max_gram": 10
		},
		"filter_shingles": {
			"type": "shingle",
			"token_separator": " "
		}
	}
}
```

### Vytvorte denormalizované Tweety.  
```sql
create table
	tweets_merged as (
		Select
			*
		from
			tweets
			left join (
				select
					au.id as author_id,
					au.name as author_name,
					au.username as author_username,
					au.description as author_description,
					au.followers_count,
					au.following_count,
					au.tweet_count,
					au.listed_count
				from
					authors as au
			) authors USING (author_id)
			left join (
				select
					tr.parent_id,
					tr.type,
					tr.tweet_id as "id"
				from
					tweet_references as tr
			) tweet_references USING ("id")
			left join (
				Select
					an.tweet_id as "id",
					array_agg (an.id) as annotations_ids,
					array_agg (an."value") as annotation_values,
					array_agg (an."type") as annotation_types,
					array_agg (an.probability) as annotation_probabilities
				from
					annotations as an
				GROUP BY
					an.tweet_id
			) annotations USING ("id")
			left join (
				Select
					li.tweet_id as "id",
					array_agg (li.id) as link_ids,
					array_agg (li.title) as link_titles,
					array_agg (li.url) as link_urls,
					array_agg (li.description) as link_descriptions
				from
					links as li
				GROUP BY
					li.tweet_id
			) links USING ("id")
			left join (
				SELECT
					th.tweet_id as "id",
					array_agg (H.id) as hashtag_ids,
					array_agg (H.tag) as hashtag_tags
				From
					tweet_hashtags as th
					LEFT JOIN hashtags as H ON H.id = th.hashtag_id
				GROUP BY
					th.tweet_id
			) hashtags USING ("id")
			left join (
				SELECT
					ca.tweet_id as "id",
					array_agg (cd.id) as domain_ids,
					array_agg (cd.name) as domain_names,
					array_agg (cd.description) as domain_descriptions,
					array_agg (ce.id) as entity_ids,
					array_agg (ce.name) as entity_names,
					array_agg (ce.description) as entity_descriptions
				from
					context_annotations as ca
					left join context_domains as cd ON cd.id = ca.context_domain_id
					left join context_entities as ce ON ce.id = ca.context_entity_id
				GROUP by
					ca.tweet_id
			) context_annotations USING ("id")
	);

CREATE INDEX idx_tweets_merged_id ON tweets_merged ("id");
CREATE INDEX idx_tweet_parent_id ON tweets_merged (parent_id);

create table
	tweet_docs as (
		Select
			*
		from
			tweets_merged as doc_a
			left join (
				SELECT
					doc_b.id as parent_id,
					doc_b.content as referenced_content,
					doc_b.author_id as referenced_author_id,
					doc_b.author_name as referenced_author_name,
					doc_b.author_username as referenced_author_username,
					doc_b.hashtag_ids as referenced_hashtag_ids,
					doc_b.hashtag_tags as referenced_hashtag_tags
				from
					tweets_merged as doc_b
			) doc_b using (parent_id)
	);

CREATE INDEX idx_tweet_docs_id ON tweet_docs ("id");

create table
	tweet_docs_with_pid as (
		select
			ntile (1024) over (
				ORDER BY
					"id"
			),
			*
		from
			tweet_docs
	);

CREATE INDEX idx_tweet_docs_with_pid_id ON tweet_docs_with_pid ("id");
CREATE INDEX idx_tweet_docs_with_pid_ntile ON tweet_docs_with_pid ("ntile");

DROP TABLE "tweet_docs";
DROP TABLE "tweets_merged";
```
na vytvorenie denormalizovanej tweet tabulky som pouzil tuto sekvenciu sql prikazov ako su.. Ked som to skombinoval do jedneho prikazu s with doc (select) left join doc as doc_b... tak to robilo nejake srandy.

Prve query spravi tabulku `tweets_merged` ktora obsahuje joinute vsetky tabulky do jednej velkej ktora ale neobsahuje referenced polia.

Potom pomocou `parent_id` joinem `tweets_merged` so samou sebou aby som pridal potrebne refenced polia a vznikne `tweet_docs`

k `tweet_docs` este pridam jeden stlpec ktory vyuzivam v importe na rychlejsie paralelizovanie readu. `ntile(1024)` mi rozdeli dataset na 1024 rovnako velkych casti.

denormalizacia trvala ~45 minut.
![image](./assets/Pasted%20image%2020221224120640.png)

### Importujete dáta do Elasticsearchu prvych 5000 tweetov  
```python
TABLE_NAME = 'tweet_docs_with_pid'

LIMIT = 500
PARALEL = 10
INDEX_NAME = 'pdt_cluster'
...
with conn.cursor(name="named", cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
	cursor.itersize = 4_000
	cursor.execute(
		f'select * from {TABLE_NAME} where MOD("ntile", {PARALEL})={paralel_id} {f"limit {LIMIT}" if LIMIT != None else ""} '
	)

	docs = []
	for index, row in enumerate(cursor):
		doc = {
			"_index": INDEX_NAME,
			"_id": row.get("id"),
			"author": {},
			"annotations": [],
			"domains": [],
			"entities": [],
			"hashtags": [],
			"links": [],
			"meta": {},
			"referenced": {},
		}
		...
		deque(helpers.parallel_bulk(es, docs, request_timeout=60))
...
```
![image](./assets/Pasted%20image%2020221224105953.png)
Na import do elasticu som pouzil python. ThreadpoolExecutor logiku na paralelizovanie tasku, named cursor na postupne nacitavanie query a RealDictCursor engine nato aby sa precitane riadky spravali ako dictionary a nie polia. 

Query na postgre obsahuje okrem selectu na tabulku aj dve logicke casti:
1. jedna je limit -> pre bulk import 5000 dat alebo akehokolvek ineho arbitrary mnozstva.
2. `MOD("ntile", {PARALEL})={paralel_id}` ktoru si paralelizujem query. Nakolko chcem vyuzit na read 24 logickych jadier (pri 5000 import som vyuzil 10 a limit 500)
Celkova logika importu:
1. zavolaj funkciu pre import s `threadpoolexecutor(max_workers=PARALEL)`
2. selectni table a riadky podla mod paralel_id
3. pre kazdy riadok `row.get('column_name')` osetri None values. pri nested udajoch itereruj listom ako napriklad pri `hashtagoch`
4. po sparsovani 2_000 riadkov zavolaj `parallel_bulk` ktory pusne data do elasticu

### Experimentujte s nódami, a zistite koľko nódov musí bežať (a ktoré) aby vám  Elasticsearch vedel pridávať dokumenty, mazať dokumenty, prezerať dokumenty a vyhľadávať nad nimi? Dá sa nastaviť Elastic tak, aby mu stačil jeden nód? Čo je dôvodom toho že existuje nejaké kvórum? 

#### 3 Nodes
Query: 
http://localhost:9200/pdt_cluster/_doc/1496763787411664902
response: 
```json
{
	"_index": "pdt_cluster",
	"_id": "1496763787411664902",
	"_version": 1,
	"_seq_no": 511,
	"_primary_term": 1,
	"found": true,
	"_source": {...document...}
}
```
#### 2 Nodes
![image](./assets/Pasted%20image%2020221224131346.png)
pri vyhladavani nad indexom bez replik (cely dataset tweetov)
![image](./assets/Pasted%20image%2020221224132009.png)

Query na cluster index: 
http://localhost:9200/pdt_cluster/_doc/1496763787411664902
response: 
```json
{
	"_index": "pdt_cluster",
	"_id": "1496763787411664902",
	"_version": 1,
	"_seq_no": 511,
	"_primary_term": 1,
	"found": true,
	"_source": {...document...}
}
```
#### 1 Nodes
pri jednom node kibana prestala ukazovat cluster overview ale requesty na exposnuty port a node fungovali stale
pri vyhladavani nad indexom bez replik (cely dataset tweetov):
![image](./assets/Pasted%20image%2020221224131617.png)
![image](./assets/Pasted%20image%2020221224131801.png)

Query na cluster index: 
http://localhost:9200/pdt_cluster/_doc/1496763787411664902
response: 
```json
{
	"_index": "pdt_cluster",
	"_id": "1496763787411664902",
	"_version": 1,
	"_seq_no": 511,
	"_primary_term": 1,
	"found": true,
	"_source": {...document...}
}
```

Nad clustrom sa dalo vyhladavat aj pri 2 aj pri 1dnom. Dolezite bolo aby bezal master node. A dalsia vec je podla nastaveni ak mame exposnuty ibe node 1 nemoze vypadnut lebo sa uz z pocitaca nebudeme vediet spytat nic lebo jediny exposnuty padol. Pokial neberieme teda kibanu do uvahy ako som uz spomenul requesty na cluster sa daju robit aj v kibane ale aj cez kibanu.. Staci spravit pos request na proxy kibany. takto by sme vedeli robit request na jeden endpoint po cely cas. inak si musime dat pozor ktore nody idu a aky je ich exposnuty port

pri cluster mode mame zarucene ze integrita dat ostane nedotknute pri behu aspon 2 nodov z troch to koli replikacii. Pokial ale spadnu dva nody integrita uz je zasiahnuta a je mozne ze nedostaneme vysledky pre nas dopyt.

Nad dvomi nodami nevieme aj pridavat aj uberat zaznamy aj pridavat ich.

Za to moze quorum ktore sme nastaili na dva pri tvorbe indexu: `number_of_replicas`
cize potrebujeme aspon dva nody


### Upravujte počet retweetov pre vami vybraný tweet pomocou vašeho jednoduchého  scriptu (v rámci Elasticsearchu) a sledujte ako sa mení `_seq_no` a `_primary_term` pri tom ako zabíjate a spúšťate nódy.
#### 3 Nodes
![image](./assets/Pasted%20image%2020221224134554.png)
![image](./assets/Pasted%20image%2020221224134609.png)
#### 2 Nodes
![image](./assets/Pasted%20image%2020221224134705.png)
![image](./assets/Pasted%20image%2020221224134725.png)
#### 1 Node
neda sa updatovat zaznam

`_seq_no` sa vzdy po update zvacsilo o 1.
`_primary_term` ostalo rovnake

### Zrušte repliky a importujete všetky tweety 
```python
LIMIT = None
PARALEL = 24
INDEX_NAME = 'pdt_single'
```
vyuzivam ten isty kod len sa zmenia 3 globalne premenne:
LIMIT -> nakolko uz chceme vsetky tweety
PARALEL -> ProccesPoolExecutor bude vyuzivat uz 24 logickych jadier
INDEX_NAME -> zmenime na signle aby sa nam nevytvarali repliky

skusil som nastavenie s 3 shardami a 12timi 
pri 3 shardoch trval import 80 min a store.size bol 65gb
pri 12 shardoch trval import 58 min a store.size bol 83.4gb

![image](./assets/Pasted%20image%2020221224114007.png)

### Vyhľadajte vo vašich tweetoch, kde použite function_score pre jednotlivé  medzikroky nasledovne:  
```json
{
	"query": {
		"function_score": {
			"query": {
				"bool": {
					"must": [
							{
								"nested": {
										"path": "hashtags",
										"query": {
												"match": {
														"hashtags.tag": "Ukraine"
												}
										}
								}
							},
							{
							"multi_match": {
											"query": "put1n chr1stian fake jew",
											"fields": [
													"author.description.description_shingle^10",
													"metadata.content^6"
											],
											"fuzziness": "AUTO"
									}
							},
							{
							"match": {
									"referenced.referenced_content": {
											"query": "nazi"
									}
							}
						}
					]
				}
			}
		}
	}
}
```
![image](./assets/Pasted%20image%2020221224142908.png)
```json
{
	"query": {
		"function_score": {
			"query": {
				"bool": {
					"filter": [
						{
							"range": {
								"author.following_count": {
									"gt": 100
								}
							}
						},
						{
							"range": {
								"author.followers_count": {
									"gt": 100
								}
							}
						},
						{
							"nested": {
								"path": "links",
								"query": {
									"bool": {
										"must": {
											"exists": {
												"field": "links.url"
											}
										},
										"must_not": {
											"term": {
												"links.url": "\\N"
											}
										}
									}
								}
							}
						}
					]
				}
			}
		}
	}
}
```
`\\N` som mohol v python kode handlovat.. uz je neskoro :)
![image](./assets/Pasted%20image%2020221224142922.png)

```json
{
	"query": {
		"function_score": {
			"functions": [
				{
					"weight": 5,
					"filter": {
						"bool": {
							"should": {
								"nested": {
									"path": "domains",
									"query": {
										"match": {
											"domains.name": {
												"query": "Person"
											}
										}
									}
								}
							}
						}
					}
				},
				{
					"weight": 10,
					"filter": {
						"bool": {
							"should": {
								"nested": {
									"path": "entities",
									"query": {
										"match": {
											"entities.name": {
												"query": "Soros"
											}
										}
									}
								}
							}
						}
					}
				},
				{
					"weight": 5,
					"filter": {
						"bool": {
							"should": {
								"match_phrase": {
									"author.description.description_shingle": {
										"query": "put1n chr1stian fake jew",
										"slop": 1
									}
								}
							}
						}
					}
				}
			]
		}
	}
}
```
![image](./assets/Pasted%20image%2020221224144337.png)
```json
{
	"aggs": {
		"tags_bucket": {
			"nested": {
				"path": "hashtags"
			},
			"aggs": {
				"filtered_tags": {
					"filter": {
						"bool": {
							"must": [
								{
									"terms": {
										"hashtags.tag": [
											"istandwithputin",
											"racism",
											"1trillion",
											"istandwithrussia",
											"isupportrussia",
											"blacklivesmatter",
											"racism",
											"racistukraine",
											"africansinukraine",
											"palestine",
											"israel",
											"freepalestine",
											"istandwithpalestine",
											"racisteu",
											"putin"
										]
									}
								}
							]
						}
					},
					"aggs": {
						"tags": {
							"terms": {
								"field": "hashtags.tag"
							}
						}
					}
				}
			}
		}
	}
}
```
![image](./assets/Pasted%20image%2020221224153117.png)


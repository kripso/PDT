create table tweets_with_author as(
	Select 
		ntile(1024) over (ORDER BY id), * 
	from 
		tweets 
		left join ( 
			select au.id as author_id, au.name as author_name, au.username as author_username,  au.description as author_description,au.followers_count,au.following_count, au.tweet_count, au.listed_count from authors as au
		) authors USING(author_id)
		left join (
			select tr.id as tweet_reference_id, tr.parent_id, tr.type, tr.tweet_id as "id" from tweet_references as tr
		) tweet_references USING("id")
		left join (
			Select an.tweet_id as "id", array_agg(an.id) as annotations_ids, array_agg(an."value") as "annotation_values", array_agg(an."type") as "annotation_types", array_agg(an.probability) as annotation_probabilities from annotations as an
			GROUP BY an.tweet_id
		) annotations USING("id")
		left join (
			Select li.tweet_id as "id", array_agg(li.id) as link_ids, array_agg(li.title) as link_titles, array_agg(li.url) as link_urls, array_agg(li.description) as link_descriptions from links as li
			GROUP BY li.tweet_id
		) links USING("id")
		left join (
			SELECT th.tweet_id as "id", array_agg(H.id) as hashtag_ids, array_agg(H.tag) as hashtag_tags From tweet_hashtags as th
			LEFT JOIN hashtags as H ON H.id = th.hashtag_id
			GROUP BY th.tweet_id
		) hashtags USING("id")
		left join (
			SELECT ca.tweet_id as "id", array_agg(cd.id) as domain_ids, array_agg(cd.name) as "domain_names", array_agg(cd.description) as domain_descriptions, array_agg(ce.id) as entity_ids, array_agg(ce.name) as "entity_names", array_agg(ce.description) as entity_descriptions from context_annotations as ca
				left join context_domains as cd ON cd.id = ca.context_domain_id
				left join context_entities as ce ON ce.id = ca.context_entity_id
			GROUP by ca.tweet_id
		) context_annotations USING("id")
)

create table tweets_with_pid as (
	select ntile(1024) over (ORDER BY id), * from tweets_with_author
)
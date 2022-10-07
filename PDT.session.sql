
SELECT COUNT(*) FROM authors; -- 5 895 176
SELECT COUNT(*) FROM tweets; -- 32 347 011
SELECT COUNT(*) FROM annotations; -- 194 80 545
SELECT COUNT(*) FROM context_annotations; -- 134 444 727
SELECT COUNT(*) FROM context_domains; -- 88
SELECT COUNT(*) FROM context_entities; -- 29 438
SELECT COUNT(*) FROM tweet_hashtags; -- 773 865
SELECT COUNT(*) FROM tweet_references; -- 0
SELECT COUNT(*) FROM links; -- 11 552 641
SELECT COUNT(*) FROM hashtags; -- 773 865

SELECT pg_size_pretty(pg_total_relation_size('authors')); -- 1071 MB
SELECT pg_size_pretty(pg_total_relation_size('tweets')); -- 8659 MB
SELECT pg_size_pretty(pg_total_relation_size('annotations')); -- 1725 MB
SELECT pg_size_pretty(pg_total_relation_size('context_annotations')); -- 10 GB
SELECT pg_size_pretty(pg_total_relation_size('context_domains')); -- 80 kB
SELECT pg_size_pretty(pg_total_relation_size('context_entities')); -- 4232 kB
SELECT pg_size_pretty(pg_total_relation_size('tweet_hashtags')); -- 55 MB
SELECT pg_size_pretty(pg_total_relation_size('tweet_references')); -- 16 kb
SELECT pg_size_pretty(pg_total_relation_size('links')); -- 2084 MB
SELECT pg_size_pretty(pg_total_relation_size('hashtags')); -- 88 MB
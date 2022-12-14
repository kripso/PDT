link na github: https://github.com/kripso/PDT/tree/master/assignment_3

## 1. stiahnite a importujte si dataset pre Open Street mapy z https://download.geofabrik.de/europe/slovakia.html do novej DB  

Na importovanie osm suboru som pouzil `osm2pgsql` nakolko to bol jeden z odporucanych toolov.

```zsh
osm2pgsql.exe -S ./default.style -U postgres -W -d postgis_33_sample -H localhost -C 1000 --number-processes 4  C:\Users\Krips\Downloads\slovakia-latest.osm.pbf
```

```zsh
2022-11-03 20:39:21  osm2pgsql version 1.7.1
Password:
2022-11-03 20:39:24  Database version: 14.5
2022-11-03 20:39:24  PostGIS version: 3.3
2022-11-03 20:39:24  Setting up table 'planet_osm_point'
2022-11-03 20:39:24  Setting up table 'planet_osm_line'
2022-11-03 20:39:24  Setting up table 'planet_osm_polygon'
2022-11-03 20:39:24  Setting up table 'planet_osm_roads'
2022-11-03 20:40:24  Reading input files done in 60s (1m 0s).
2022-11-03 20:40:24    Processed 27410100 nodes in 3s - 9137k/s
2022-11-03 20:40:24    Processed 3575437 ways in 42s - 85k/s
2022-11-03 20:40:24    Processed 45957 relations in 15s - 3k/s
2022-11-03 20:40:26  Clustering table 'planet_osm_roads' by geometry...
2022-11-03 20:40:26  Clustering table 'planet_osm_point' by geometry...
2022-11-03 20:40:26  Clustering table 'planet_osm_polygon' by geometry...
2022-11-03 20:40:26  Clustering table 'planet_osm_line' by geometry...
2022-11-03 20:40:32  Creating geometry index on table 'planet_osm_roads'...
2022-11-03 20:40:32  Creating geometry index on table 'planet_osm_point'...
2022-11-03 20:40:32  Analyzing table 'planet_osm_roads'...
2022-11-03 20:40:38  Analyzing table 'planet_osm_point'...
2022-11-03 20:40:39  All postprocessing on table 'planet_osm_point' done in 12s.
2022-11-03 20:40:40  Creating geometry index on table 'planet_osm_line'...
2022-11-03 20:40:45  Creating geometry index on table 'planet_osm_polygon'...
2022-11-03 20:40:45  Analyzing table 'planet_osm_line'...
2022-11-03 20:40:46  All postprocessing on table 'planet_osm_line' done in 19s.
2022-11-03 20:41:00  Analyzing table 'planet_osm_polygon'...
2022-11-03 20:41:01  All postprocessing on table 'planet_osm_polygon' done in 34s.
2022-11-03 20:41:01  All postprocessing on table 'planet_osm_roads' done in 6s.
2022-11-03 20:41:01  osm2pgsql took 97s (1m 37s) overall.
```

## 2. zistite ak?? kraje s?? na Slovensku (planet_osm_polygon, admin_level = ???4???) a vyp????te ich s??radnice ako text s longitude a latitude
Na vypisanie krajov som vyuzil hint zo zadanie a kedze sme chceli `longitude a latitude` tak som este musel way pretransformovat z defaultneho `3857` na `4326`.

```sql
SELECT 
	"name", way, ST_AsText(ST_Transform(way, 4326))
FROM
    planet_osm_polygon
WHERE
    admin_level='4';
```

![image](./assets/Pasted%20image%2020221104195620.png)

## 3. zora??te kraje pod??a ich ve??kosti (st_area). Ve??kos?? vypo????tajte pomocou vhodnej funkcie a zobrazte v km^2 v SRID 4326
na vypocet povrch som pouzil st_area ako bolo v zadani a taktiez som koli presnosti pretransformoval way na `4326` pomocou `ST_Transform`.

dalej som vysledok zaokruhlil na dve desatinne miesta nakolko aj prednaske bolo spomenute ze nechat tam vela desatinnych miest je zavadzajuce koli presnosti merania ako takej.

Nakoniec som zo zvedavosti spocital areu slovenska ktore vychadza plus minus rovnako ako nam vravi vsevedna wikipedia

```sql
SELECT
	"name",
	ROUND((ST_Area(ST_Transform(way, 4326)::geography) / 1000000)::numeric, 2) as st_area
FROM
	planet_osm_polygon
WHERE
	admin_level='4'
ORDER BY
	st_area;
```

```sql
SELECT 
	sum(st_area) AS SK_Area 
FROM ( 
	SELECT
		"name",
		ROUND((ST_Area(ST_Transform(way, 4326)::geography) / 1000000)::numeric, 2) AS st_area
	FROM
		planet_osm_polygon
	WHERE
		admin_level='4'
	ORDER BY
		st_area
) tmp;
```

![image](./assets/Pasted%20image%2020221104195706.png)
![image](./assets/Pasted%20image%2020221104195757.png)

## 4. pridajte si dom, kde b??vate ako polyg??n (n??jdite si s??radnice napr. cez google maps) do planet_osm_polygon (znova pozor na s??radnicov?? syst??m). V??sledok zobrazte na mape
Tu som spravil simple insert polygonu kde som jednotlive body ziskal podla stranky https://www.openstreetmap.org/ a pomenoval som si ho `My_Home`

pri selecte som pridal `or admin_level=4` pre lepsiu vizualizaciu.

```sql
INSERT INTO
    planet_osm_polygon ("name", way)
VALUES
    (
        'My_Home',
		ST_Transform(
			ST_GeometryFromText (
				'POLYGON ((
					18.2777525 48.1886538, 
					18.2776122 48.1886695, 
					18.2776154 48.1886832, 
					18.2775310 48.1886930, 
					18.2775497 48.1887652, 
					18.2777743 48.1887397, 
					18.2777525 48.1886538
				))', 4326
			), 3857
		)
    );
SELECT "name", way FROM planet_osm_polygon where name='My_Home' or admin_level='4';
```

![image](./assets/Pasted%20image%2020221104195924.png)
![image](./assets/Pasted%20image%2020221104195945.png)

## 5. zistite v akom kraji je v???? dom
Pre zistenie v ako kraji sa nachadza moj dom som vyuzil funkciu `ST_Contains(way1,way2)` ktora pozire ci `way2` sa nachadza vo `way1`

to mi vratilo ze sa nachadza v nitrianskom kraji co je spravne aj podla predchadzajucej vyzualizacie

```sql
SELECT 
	"name", way 
FROM 
	planet_osm_polygon 
WHERE 
	admin_level='4' 
AND 
	ST_Contains(way, (SELECT way FROM planet_osm_polygon WHERE "name"='My_Home'));
```

![image](./assets/Pasted%20image%2020221104200047.png)

## 6. pridajte si do planet_osm_point va??u aktu??lnu polohu (pozor na s??radnicov??syst??m). V??sledok zobrazte na mape
na pridanie bodu som pouzi rovnaku strategiu ako na pridanie domu do `planet_osm_polygon` len teraz sa pridaval `POINT` a nie `POLYGON` do `planet_osm_point`

Na konci som zobralil moju aktualnu polohu ktora sa nenachadza ale v mojom dome ale v bratislave co je spravne.
```sql
INSERT INTO
    planet_osm_point ("name", way)
VALUES
    (
        'Me_There',
		ST_Transform(
			ST_GeometryFromText (
				'POINT (
					17.10114 48.13020
				)', 4326
			), 3857
		)
    );
SELECT "name", way FROM planet_osm_point WHERE "name"='Me_There'
UNION
SELECT "name", way FROM planet_osm_polygon WHERE "name"='My_Home' or admin_level='4';
```

![image](./assets/Pasted%20image%2020221104200207.png)
![image](./assets/Pasted%20image%2020221104200148.png)

## 7. zistite ??i ste doma - ??i je va??a poloha v r??mci v????ho b??vania.  
V ramci tejto ulohy som pridal dalsie `POLYGON` do `planet_osm_polygon` ktory reprezentoval budovu v ktorej som sa nachadzal aby sme vedeli spravne otestovat logiku programu.

na zistenie ci sa nachadzam v budove som vyuzil podobnu logiku ako pri hladani v ktorom kraji sa nachadzam a to teda pomocou `ST_Contains` ktore spravne vratilo ze sa nachadzam v `Nobelovo namestie 10`

```sql
INSERT INTO
    planet_osm_polygon (name, way)
VALUES
    (
        'Nobelovo namestie 10',
		ST_Transform(
			ST_GeometryFromText (
				'POLYGON ((
					17.1011156 48.1303161,
					17.1010457 48.1293621,
					17.1012453 48.1293550,
					17.1013165 48.1303104,
					17.1011156 48.1303161
				))', 4326
			), 3857
		)
    );
```

```sql
SELECT "name", way FROM planet_osm_point WHERE "name"='Me_There'
UNION
SELECT 
	"name", way
FROM 
	planet_osm_polygon
WHERE 
	"name" IN ('Nobelovo namestie 10', 'My_Home')
AND
	ST_Contains(
	    way, 
		(SELECT way FROM planet_osm_point WHERE "name"='Me_There')
	)
```

![image](./assets/Pasted%20image%2020221104200416.png)
![image](./assets/Pasted%20image%2020221104200434.png)

## 8. zistite ako ??aleko sa nach??dzate od FIIT (name = 'Fakulta informatiky a informa??n??ch technol??gi?? STU'). Pozor na spr??vny s??radnicov?? syst??m ??? vzdialenos?? mus?? by?? skuto??n??

na meranie vzdialenosti som pouzil `ST_Distance` suradnicovy system `4326` ktory mi daval presnejsie vysledky, ktore som na konci prepocital na km.

porovnal som vysledok s google mapami kde rozdiel medzi vysledkami je 6 metrov co moze byt aj margin of error lebo som nehladal presny bod ktory vrati `"name"='Fakulta informatiky a informa??n??ch technol??gi?? STU'`
```sql
SELECT 
    ROUND((
        ST_Distance(
            (
                SELECT 
                    ST_Transform(way, 4326)::geography AS st_way 
                FROM 
                    planet_osm_polygon 
                    WHERE "name"='Fakulta informatiky a informa??n??ch technol??gi?? STU'
			),
            (
                SELECT 
                    ST_Transform(way, 4326)::geography AS st_way 
                FROM 
                    planet_osm_point 
                    WHERE "name"='Me_There'
            )
    ) / 1000)::numeric, 2)  st_distance;
```

![image](./assets/Pasted%20image%2020221104200626.png)
![image](./assets/Pasted%20image%2020221104104721.png)

## 9. Stiahnite si QGIS a vyplotujte kraje a v???? dom z ??lohy 2 na mape - napr. ??ervenou ??iarou.  

![image](./assets/Pasted%20image%2020221104144537.png)
![image](./assets/Pasted%20image%2020221104144444.png)

## 10. Zistite s??radnice centroidu (??a??iska) plo??ne najmen??ieho okresu (vo v??sledku nezabudnite uvies?? aj EPSG k??d s??radnicov??ho syst??mu).  
na vypocitanie centroidu som vyuzil funkciu `ST_Centroid` ktory som vypocital aj v `4326` (na ziskanie `latitude a longitude` hodnot) a v `3857` pre vizualizaciu v `qgise`

vybratie najmensieho kraju bolo iba lahke re-usenutie predchadzajuceho kodu z prvych uloch a pridanie LIMIT 1.
```sql
SELECT
    name,
    ROUND((ST_Area(ST_Transform(way, 2065)) / 1000000)::numeric, 2) as st_area,
	ST_AsText(ST_Centroid(ST_Transform(way, 4326))) as st_degrees,
	ST_AsText(ST_Centroid(ST_Transform(way, 3857))) as st_metres
FROM
    planet_osm_polygon
WHERE
    admin_level='4'
ORDER BY
    st_area
LIMIT 1
```

![image](./assets/Pasted%20image%2020221104200928.png)
![image](./assets/Pasted%20image%2020221104151757.png)

## 11. Vytvorte priestorov?? tabu??ku v??etk??ch ??sekov ciest, ktor??ch vzdialenos?? od vz??jomnej hranice okresov Malacky a Pezinok je men??ia ako 10 km
dolezite funkcie boli `ST_Buffer`(vytvorenie bubliny zo vzdialenostou 10_000 metrov) a `ST_Intersection` (najdenie spolocnych bodov dvoch polygonov)

filtrovanie malaciek a pezinka bolo lahke cez vyuzitie `name`
a nakoniec som pridal filter na cesty urcene pre motorove vozidla.

v `qgise` som vyzualizoval 3 query:
1. ktora vratila len spolocny poligon pre okresy
2. ktora vratila bublinu s velkostou 10km okolo daneho polygonu
3. ktora reprezentala samotne cesty

```sql
CREATE TABLE tmp_table AS
SELECT
	ST_Intersection
	(
		way,
		(
			SELECT 
				ST_Buffer(
					ST_Intersection(
						(
							SELECT 
								way
							FROM
								planet_osm_polygon
							WHERE
								admin_level='8'
							AND 
								"name"='okres Malacky'
						),
						(
							SELECT 
								way
							FROM
								planet_osm_polygon
							WHERE
								admin_level='8'
							AND 
								"name" ='okres Pezinok'
						)
				), 10000)  st_buffer
		)
	)
FROM
	planet_osm_roads
WHERE
    highway IN (
        'motorway',
        'trunk',
        'primary',
        'secondary',
        'tertiary'
    )

```

![image](./assets/Pasted%20image%2020221104161539.png)

## 12. Jedn??m dopytom zistite ????slo a n??zov katastr??lneho ??zemia (z d??t ZBGIS, https://www.geoportal.sk/sk/zbgis_smd/na-stiahnutie/), v ktorom sa nach??dza najdlh???? ??sek cesty (z d??t OSM) v okrese, v ktorom b??vate.
nerozumiem zadaniu.

## 13. Vytvorte oblas?? Okolie_Bratislavy, ktor?? bude zah????a?? z??nu do 20 km od Bratislavy, ale nebude zah????a?? oblas?? Bratislavy (Bratislava I a?? Bratislava V) a bude len na ??zem?? Slovenska. Zistite jej v??meru
prva z uvedenych query je vyuzita na sa vyzualizaciu vyslednej plochy ktora sa bude pocitat v druhej query.

boli vyuzite doteraz vsetky uz aspon raz pouzite funkcie plus `ST_Union` ktora mi zjednotila vsetky kraje slovenska na jedno ucelene slovensko.

```SQL
SELECT
	ST_Intersection (
		(
			ST_Transform (
				ST_Difference (ST_Buffer (bratislava, 20000), bratislava),
				3857
			)
		),
		(
			SELECT
				ST_Union (way)
			FROM
				planet_osm_polygon
			WHERE
				admin_level = '4'
		)
	)
FROM
	ST_Transform (
		(
			SELECT
				way
			FROM
				planet_osm_polygon
			WHERE
				admin_level = '6'
				AND "name" = 'Bratislava'
		),
		2065
	) as bratislava
```

![image](./assets/Pasted%20image%2020221104185256.png)

na vypocitanie povrchu tejto plochy som znovy vyuzil `ST_Area` kde som dal `Okolie_Bratislavy` ako vsup ktory je v `2065` systeme.
pri vypocte vysledku som si po konzultaciu s kamaratom vsimol ze sa nase vysledky nezhodovali ale obaja sme vyuzivali tie iste jednotky len inu logiku programu. 
Nakoniec sme zistili ze problem bol v nasich datasetoch ked on sposti moj kod na jeho pc tak mu vyde rovnaky vysledok ako s jeho query a naopak. Takze je dost mozne ze medzy tym ked som ja stahoval dataset a on sa nieco zmenilo co zapricinilo 8 metrov stvorcovych rozdiel vo vysledku

```sql
SELECT
	ROUND((ST_Area(Okolie_Bratislavy) / 1000000)::numeric, 2)
FROM
	(
		SELECT
			ST_Intersection (
				(
					ST_Transform (
						ST_Difference (ST_Buffer (bratislava, 20000), bratislava),
						3857
					)
				),
				(
					SELECT
						ST_Union (way)
					FROM
						planet_osm_polygon
					WHERE
						admin_level = '4'
				)
			) as Okolie_Bratislavy
		FROM
			ST_Transform (
				(
					SELECT
						way
					FROM
						planet_osm_polygon
					WHERE
						admin_level = '6'
						AND "name" = 'Bratislava'
				),
				2065
			) as bratislava
	) query
```

![image](./assets/Pasted%20image%2020221104193449.png)

Na kamaratovom pocitaci ta ista query

![image](./assets/Pasted%20image%2020221104193408.png)
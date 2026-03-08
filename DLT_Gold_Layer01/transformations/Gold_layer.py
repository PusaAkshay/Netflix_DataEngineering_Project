from pyspark import pipelines as dp
from pyspark.sql.functions import *
from pyspark.sql.types import *


rules = {
    "rule_1": "showid is NOT NULL"
}

director_rules = {
    "rule_1": "director is NOT NULL"
}

cast_rules = {
    "rule_1": "cast is NOT NULL"
}

country_rules = {
    "rule_1": "country is NOT NULL"
}

category_rules = {
    "rule_1": "listed_in is NOT NULL"
}

title_rules = {
    "rule_1": "show_id is NOT NULL"  
}
@dp.table(name="gold_netflixdirectors")
@dp.expect_all_or_drop(director_rules)
def gold_netflixdirectors():
    df = spark.readStream.format("delta").load("abfss://silver@netflixproject28.dfs.core.windows.net/netflix_directors")
    return df

@dp.table(name="gold_netflixcast")
@dp.expect_all_or_drop(cast_rules)
def gold_netflixcast():
    df = spark.readStream.format("delta").load("abfss://silver@netflixproject28.dfs.core.windows.net/netflix_cast")
    return df

@dp.table(name="gold_netflixcountries")
@dp.expect_all_or_drop(country_rules)
def gold_netflixcountries():
    df = spark.readStream.format("delta").load("abfss://silver@netflixproject28.dfs.core.windows.net/netflix_countries")
    return df

@dp.table(name="gold_netflixcategory")
@dp.expect_all_or_drop(category_rules)
def gold_netflixcategory():
    df = spark.readStream.format("delta").load("abfss://silver@netflixproject28.dfs.core.windows.net/netflix_category")
    return df

@dp.table(name="gold_stg_netflixtitles")
@dp.expect_all_or_drop(title_rules)
def gold_stg_netflixtitles():
    df = spark.readStream.format("delta").load("abfss://silver@netflixproject28.dfs.core.windows.net/netflix_titles")
    return df

@dp.view()
def gold_trans_netflixtitles():
    df = dp.read("gold_stg_netflixtitles")
    df = df.withColumn("newFlag", lit(1))
    return df

@dp.table(name="gold_netflixtitles")
@dp.expect_all_or_drop(title_rules)
def gold_netflixtitles():
    df = dp.read("gold_trans_netflixtitles") 
    return df
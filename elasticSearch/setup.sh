# A tutorial on how to use elasticsearch for instant search:    https://marcobonzanini.com/2015/08/10/building-a-search-as-you-type-feature-with-elasticsearch-angularjs-and-flask/
# there are some difference in elasticsearch api because of difference in elasticsearch version
# Download and run the elastic search from its website
# run bible_to_json_convertor.py to convert your bible files to indexable json files
# point corpus_location field in this file to the location of your json files


corpus_location="/mounts/work/ayyoob/alignment/elastic/"

curl -XDELETE http://localhost:9200/bible_index; echo;
curl -H "Content-Type: application/json" -XPUT http://localhost:9200/bible_index -d @mapping.json; echo; # check type of the verse_id field in mapping part! all bible verse numbers fit in integer
curl -H "Content-Type: application/json" -XPUT http://localhost:9200/bible_index_noedge -d @mapping_noedge.json; echo; # check type of the verse_id field in mapping part! all bible verse numbers fit in integer

files=`ls $corpus_location`
for file in $files
do 
    curl -H "Content-Type: application/json" -XPOST "localhost:9200/bible_index/_bulk?pretty&refresh" --data-binary "@$corpus_location$file";
    curl -H "Content-Type: application/json" -XPOST "localhost:9200/bible_index_noedge/_bulk?pretty&refresh" --data-binary "@$corpus_location$file";
done

#see number of indexed verses(documents)
curl  -XGET "localhost:9200/bible_index/_stats/docs"
curl  -XGET "localhost:9200/bible_index_noedge/_stats/docs"

# create another index, in this one use exact match for langauges (instead of n-gram)
# curl -H "Content-Type: application/json" -XPUT http://localhost:9200/bible_index -d @mapping_langauge.json; echo;
# curl -XPOST localhost:9200/_reindex -H 'Content-Type: application/json' -d '
# {
#   "source": {
#     "index": "bible_index"
#   },
#   "dest": {
#     "index": "bible_index_v1"
#   }
# }'

# run the app for development
# cd app
conda activate alignment
export FLASK_ENV=development
export CAPTCHA_SITE_KEY='createonline'
export CAPTCHA_SECRET_KEY='createonline'
export FLASK_SECRET_KEY="ddddddddddddddddd"
export FLASK_APP=align.py
FLASK_ENV=development flask run
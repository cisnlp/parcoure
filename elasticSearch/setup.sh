# A tutorial on how to use elasticsearch for instant search:    https://marcobonzanini.com/2015/08/10/building-a-search-as-you-type-feature-with-elasticsearch-angularjs-and-flask/
# there are some difference in elasticsearch api because of difference in elasticsearch version
# Download and run the elastic search from its website
# run bible_to_json_convertor.py to convert your bible files to indexable json files
# point corpus_location field in this file to the location of your json files

if [ "$#" -ne 1 ]; then
    echo "Please provide the elasticsearch json files location as input"
    exit -1
fi

corpus_location="$1"

printf "delete index if exists"
curl -XDELETE http://localhost:9200/parcoure_index; echo;
curl -XDELETE http://localhost:9200/parcoure_index_noedge; echo;

printf "\n\n\ncreate index"
curl -H "Content-Type: application/json" -XPUT http://localhost:9200/parcoure_index -d @mapping.json; echo; # check type of the verse_id field in mapping part! all bible verse numbers fit in integer
curl -H "Content-Type: application/json" -XPUT http://localhost:9200/parcoure_index_noedge -d @mapping_noedge.json; echo; # check type of the verse_id field in mapping part! all bible verse numbers fit in integer

printf "\n\n\nfeed the corpora to elasticsearch"
files=`ls $corpus_location`
for file in $files
do 
    curl -H "Content-Type: application/json" -XPOST "localhost:9200/parcoure_index/_bulk?pretty" --data-binary "@$corpus_location$file"; echo;
    curl -H "Content-Type: application/json" -XPOST "localhost:9200/parcoure_index_noedge/_bulk?pretty" --data-binary "@$corpus_location$file"; echo;
done


printf "\n\n\ncheck the result"
#see number of indexed verses(documents)
curl  -XGET "localhost:9200/parcoure_index/_stats/docs"; echo; echo;
curl  -XGET "localhost:9200/parcoure_index_noedge/_stats/docs"

# create another index, in this one use exact match for langauges (instead of n-gram)
# curl -H "Content-Type: application/json" -XPUT http://localhost:9200/parcoure_index -d @mapping_langauge.json; echo;
# curl -XPOST localhost:9200/_reindex -H 'Content-Type: application/json' -d '
# {
#   "source": {
#     "index": "parcoure_index"
#   },
#   "dest": {
#     "index": "parcoure_index_v1"
#   }
# }'

# run the app for development
# cd app

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
index_name="$2"
index_noedge="$3"

printf "delete index if exists\n"
printf "______________________________________\n"
curl -XDELETE http://localhost:9200/"$index_name"; echo;
curl -XDELETE http://localhost:9200/"$index_noedge"; echo;

printf "\n\n\ncreate index\n"
printf "______________________________________\n"
curl -H "Content-Type: application/json" -XPUT http://localhost:9200/"$index_name" -d @mapping.json; echo; # check type of the verse_id field in mapping part! all bible verse numbers fit in integer
curl -H "Content-Type: application/json" -XPUT http://localhost:9200/"$index_noedge" -d @mapping_noedge.json; echo; # check type of the verse_id field in mapping part! all bible verse numbers fit in integer

printf "\n\n\nfeed the corpora to elasticsearch\n"
printf "______________________________________\n"
counter=0
files=`ls $corpus_location`
for file in $files
do 
    if [ $(($counter % 500)) -eq 0]; then
        curl -H "Content-Type: application/json" -XPOST "localhost:9200/"$index_name"/_bulk?pretty" --data-binary "@$corpus_location$file" 2>&1  > indexing.log; echo;
        curl -H "Content-Type: application/json" -XPOST "localhost:9200/"$index_noedge"/_bulk?pretty" --data-binary "@$corpus_location$file" 2>&1 > indexing.log ; echo;
    else 
        curl -H "Content-Type: application/json" -XPOST "localhost:9200/"$index_name"/_bulk?pretty" --data-binary "@$corpus_location$file" 2>&1 > indexing.log ; echo;
        curl -H "Content-Type: application/json" -XPOST "localhost:9200/"$index_noedge"/_bulk?pretty" --data-binary "@$corpus_location$file" 2>&1 > indexing.log ; echo;
    fi
done


printf "\n\n\ncheck the result\n"
printf "______________________________________\n"
#see number of indexed verses(documents)
curl  -XGET "localhost:9200/"$index_name"/_stats/docs"; echo; echo;
curl  -XGET "localhost:9200/"$index_noedge"/_stats/docs"; echo; echo;

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

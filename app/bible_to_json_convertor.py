import json
from align_reader import AlignReader

elastic_search_index_files_path = "/mounts/work/ayyoob/alignment/elastic/"



def convert_text_to_index_json( text, lang, res_path):
    file_json_string = ""
    index_object = {"index":{}}

    for pair in text.items():
        index_data_entry = {
            "language" : lang,
            "content" : pair[1],
            "verse_id" : pair[0]
        }

        index_object["index"]["_id"] =  pair[0] + "@" + lang

        file_json_string += json.dumps(index_object) + "\n"
        file_json_string += json.dumps(index_data_entry) + "\n"
    
    with open(res_path + lang + "index_json.txt", 'w') as res_file:
        res_file.write(file_json_string)

align_reader = AlignReader()
for lang in align_reader.all_langs:
    print("creating json file for: ", lang)
    text = align_reader.get_text_for_lang(lang)
    convert_text_to_index_json(text, lang, elastic_search_index_files_path)



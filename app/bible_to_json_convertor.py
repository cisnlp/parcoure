import json
from app.general_align_reader import GeneralAlignReader
import argparse
from app.utils import read_files

align_reader = GeneralAlignReader()

elastic_search_index_files_path = "/mounts/work/ayyoob/alignment/elastic/"
elastic_search_index_files_path_non_bert = "/mounts/work/ayyoob/alignment/elastic/non_bert_editions/"

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

def create_json_file_for_edition(edition, path):
    print("creating json file for: ", edition)
    text = read_files([edition])[edition]
    print("read %d sentences" % len(text))
    convert_text_to_index_json(text, edition, path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="create json objects proper to feed to elasticSearch index, -b:only parse bert supported files, -n:only parse non-bert supported files -e edition_name do it for one edition.", 
	epilog="example: python bible_to_json_convertor.py -n")

    parser.add_argument("-b", action="store_true")
    parser.add_argument("-n", action="store_true")
    parser.add_argument("-e", default="")
    parser.add_argument("-a", action="store_true")

    args = parser.parse_args()
    
    if args.b:
        for edition in align_reader.bert_langs:
            create_json_file_for_edition(edition, elastic_search_index_files_path)
    elif args.n:
        for lang in align_reader.all_langs:
            for edition in align_reader.lang_files[lang]:
                if edition not in align_reader.bert_langs:
                    create_json_file_for_edition(edition, elastic_search_index_files_path_non_bert)
    elif args.e != "":
        edition = args.e
        if edition in align_reader.bert_langs:
            create_json_file_for_edition(edition, elastic_search_index_files_path)
        else:
            create_json_file_for_edition(edition, elastic_search_index_files_path_non_bert)
    elif args.a:
        for lang in align_reader.all_langs:
            for edition in align_reader.lang_files[lang]:
                create_json_file_for_edition(edition, elastic_search_index_files_path)
    else:
        print("please provide correct arguments")
        print(parser.description)
        print(parser.epilog)
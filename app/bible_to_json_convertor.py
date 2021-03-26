import json
from app.general_align_reader import GeneralAlignReader
import argparse
from app import utils
import configparser

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
    text = utils.read_files([edition])[edition]
    print("read %d sentences" % len(text))
    convert_text_to_index_json(text, edition, path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="create json objects proper to feed to elasticSearch index.\n -b:only parse bert supported files, "\
        "-n:only parse non-bert supported files, -e edition_name do it for one edition, and -a all editions. "\
        "If you don't know the difference, just use -a\n"\
        "-c path to config.ini file \n"\
        "You have to set the location to save the results in config.ini file under elastic_dir if it is not there!", 
	epilog="example: python bible_to_json_convertor.py -n")

    parser.add_argument("-b", action="store_true")
    parser.add_argument("-n", action="store_true")
    parser.add_argument("-e", default="")
    parser.add_argument("-a", action="store_true")
    parser.add_argument("-c", default="config.ini")
    

    args = parser.parse_args()
    
    cparser = configparser.ConfigParser()
    cparser.read(args.c)
    elastic_search_index_files_path = cparser['section']['elastic_dir']
    
    print(1)
    utils.setup(args.c)
    print(2)
    align_reader = GeneralAlignReader()
    
    if args.b:
        for edition in align_reader.bert_files:
            create_json_file_for_edition(edition, elastic_search_index_files_path)
    elif args.n:
        for lang in align_reader.all_langs:
            for edition in align_reader.lang_files[lang]:
                if edition not in align_reader.bert_files:
                    create_json_file_for_edition(edition, elastic_search_index_files_path)
    elif args.e != "":
        edition = args.e
        if edition in align_reader.bert_files:
            create_json_file_for_edition(edition, elastic_search_index_files_path)
        else:
            create_json_file_for_edition(edition, elastic_search_index_files_path)
    elif args.a:
        for lang in align_reader.all_langs:
            for edition in align_reader.lang_files[lang]:
                create_json_file_for_edition(edition, elastic_search_index_files_path)
    else:
        print("please provide correct arguments")
        print(parser.description)
        print(parser.epilog)
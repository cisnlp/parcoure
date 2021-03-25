import configparser
import os
import xml.dom.minidom
from app.utils import setup_dict_entry, read_files, setup
from app.utils import Cache
import codecs
import argparse



def read_config(f):
    global CES_alignment_files
    global CES_corpus_dir
    global parser
    global ParCourE_data_dir


    parser = configparser.ConfigParser()
    parser.read(f)

    
    CES_corpus_dir = parser['section']['CES_corpus_dir']
    CES_alignment_files = parser['section']['CES_alignment_files'].split(',')[:]
    ParCourE_data_dir = parser['section']['ParCourE_data_dir']
    ParCourE_data_dir += "/parCourE"


def save_config(f):
    with open(f, 'w') as cfile:
        parser.write(cfile)

def create_dirs():
    global corpora_dir
    global config_dir
    
    config_dir = ParCourE_data_dir + "/config/"
    data_dir = ParCourE_data_dir + "/data/"
    corpora_dir = ParCourE_data_dir + "/data/corpora/"
    alignments_dir = ParCourE_data_dir + "/data/alignments/"
    aligns_index_dir = ParCourE_data_dir + "/data/align_index/"
    lexicon_dir = ParCourE_data_dir + "/data/lexicon/"
    elastic_dir = ParCourE_data_dir + "/data/elastic/"

    if not os.path.exists(ParCourE_data_dir):
        os.makedirs(ParCourE_data_dir)
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if not os.path.exists(corpora_dir):
        os.mkdir(corpora_dir)
    if not os.path.exists(alignments_dir):
        os.mkdir(alignments_dir)
    if not os.path.exists(lexicon_dir):
        os.mkdir(lexicon_dir)
    if not os.path.exists(elastic_dir):
        os.mkdir(elastic_dir)
    if not os.path.exists(aligns_index_dir):
        os.mkdir(aligns_index_dir)

    parser['section']['config_dir'] = config_dir
    parser['section']['corpora_dir'] = corpora_dir
    parser['section']['alignments_dir'] = alignments_dir
    parser['section']['aligns_index_dir'] = aligns_index_dir
    parser['section']['lexicon_dir'] = lexicon_dir
    parser['section']['elastic_dir'] = elastic_dir


def get_sentence_id(s_file, t_file, rel_string):
    global last_sentense_id
    global file_id_mapping

    s_side = rel_string.split(";")[0].strip()
    t_side = rel_string.split(";")[1].strip()

    setup_dict_entry(file_id_mapping, s_file, {})
    setup_dict_entry(file_id_mapping, t_file, {})

    if s_side in file_id_mapping[s_file]:
        id = file_id_mapping[s_file][s_side]
        setup_dict_entry(file_id_mapping[t_file], t_side, id)
    elif t_side in file_id_mapping[t_file]:
        id = file_id_mapping[t_file][t_side]
        setup_dict_entry(file_id_mapping[s_file], s_side, id)
    else:
        id = str(last_sentense_id)
        last_sentense_id += 1
        setup_dict_entry(file_id_mapping[t_file], t_side, id)
        setup_dict_entry(file_id_mapping[s_file], s_side, id)
    
    return id


def process_alignment_file(file):
    doc = xml.dom.minidom.parse(CES_corpus_dir + "/" + file)
    align_grps = doc.getElementsByTagName("linkGrp")

    for align_grp in align_grps:
        s_lang = align_grp.getAttribute("fromDoc").split("/")[0]
        s_file = align_grp.getAttribute("fromDoc").split("/")[1]
        if s_file[-3:] == ".gz":
            s_file = s_file[:-3]

        t_lang = align_grp.getAttribute("toDoc").split("/")[0]
        t_file = align_grp.getAttribute("toDoc").split("/")[1]
        if t_file[-3:] == ".gz":
            t_file = t_file[:-3]

        aligns = align_grp.getElementsByTagName("link")

        extract_sentence_alignments(s_lang, s_file, t_lang, t_file, aligns)

def fix_file_name(file):
    if file[-4] == '.':
        return file[:-4]
    else:
        return file

def get_CES_text(node):
    res = ''

    if node.nodeType == node.TEXT_NODE:
        res = node.data
    else:
        
        for ch_node in node.childNodes:
            text = get_CES_text(ch_node)
            if text != '':
                res += text + ' '

    return res.strip()

def compose_text(CES_ids, CES_file):
    res = ''
    for CES_id in CES_ids:
        res += CES_file[CES_id]
        res += ' '

    res = res.strip()
    return  res

def create_res_sentences(PC_s_file, PC_t_file, sentence_id, CES_s_file, CES_t_file, rel_string):
    s_CES_ids = rel_string.split(";")[0].strip().split()
    t_CES_ids = rel_string.split(";")[1].strip().split()

    if not sentence_id in PC_s_file:
        text = compose_text(s_CES_ids, CES_s_file)
        PC_s_file[sentence_id] = text

    if not sentence_id in PC_t_file:
        text = compose_text(t_CES_ids, CES_t_file)
        PC_t_file[sentence_id] = text
            
def read_CES_senteces_file(file):
    print(f"reading CES file: {file}")
    res = {}
    nodes = xml.dom.minidom.parse(file).getElementsByTagName("s")
    for node in nodes:
        id = node.getAttribute("id")
        text = get_CES_text(node)
        if text[-2:] == ' .':
            text = text[:-2]+'.'
        res [id] = text

    return res
        
def write_PC_format(file, content):
    with codecs.open(corpora_dir + '/' + file + ".txt", "w", "utf-8") as fo:
        for id in content:
            fo.write(f"{id}\t{content[id]}\n")

def valid_alignment(align_string):
    splitted = align_string.split(";")
    if len(splitted) != 2 or splitted[0] == '' or splitted[1] == '':
        return False
    
    return True

def save_PC_config_files():
    global config_dir
    global lang_files
    global langs_order
    global file_edition_mapping
    global bert_100
    global prefixes

    with open(config_dir + "/lang_files.txt", 'w') as of:
        for item in lang_files:
            of.write(f"{item} {lang_files[item]}\n")
    
    with open(config_dir + "/languages_order_file.txt", 'w') as of:
        for item in langs_order:
            of.write(f"{item}\n")
    
    with open(config_dir + "/edition_file_mapping.txt", 'w') as of1, open(config_dir + "/file_edition_mapping.txt", 'w') as of2:
        for item in file_edition_mapping:
            of1.write(f"{file_edition_mapping[item]}\t{item}\n")
            of2.write(f"{item}\t{file_edition_mapping[item]}\n")
    
    with open(config_dir + "/bert_100.txt", 'w') as of:
        for item in bert_100:
            of.write(f"{item}\n")

    with open(config_dir + "/prefixes.txt", 'w') as of:
        for item in prefixes:
            of.write(f"{item} {prefixes[item]}\n")

def add_to_PC_config_files(s_lang, s_edition, t_lang, t_edition):
    global lang_files
    global langs_order
    global file_edition_mapping
    global bert_100
    global prefixes

    lang_files[s_edition] = s_lang
    lang_files[t_edition] = t_lang

    langs_order.append(f"{s_lang},{t_lang}")

    file_edition_mapping[s_edition] = s_edition
    file_edition_mapping[t_edition] = t_edition


def extract_sentence_alignments(s_lang, s_file, t_lang, t_file, aligns):
    global ces_cache
    s_edition = fix_file_name(s_file)
    t_edition = fix_file_name(t_file)

    # for CES format corpora we use the same name for edition and file !
    PC_files = read_files([s_edition, t_edition])
    PC_s_file = PC_files[s_edition]
    PC_t_file = PC_files[t_edition]

    CES_s_file = ces_cache.get(CES_corpus_dir + "/" + s_file)
    CES_t_file = ces_cache.get(CES_corpus_dir + "/" + t_file)
    
    for align in aligns:
        align_string = align.getAttribute("xtargets")
        if valid_alignment(align_string):
            sentence_id = get_sentence_id(s_file, t_file, align_string)
            create_res_sentences(PC_s_file, PC_t_file, sentence_id, CES_s_file, CES_t_file, align_string)
    
    write_PC_format(s_edition, PC_s_file)
    write_PC_format(t_edition, PC_t_file)

    add_to_PC_config_files(s_lang, s_edition, t_lang, t_edition)


file_id_mapping = {}
last_sentense_id = 1
ces_cache = Cache(read_CES_senteces_file)     
lang_files = {}
langs_order = []
file_edition_mapping = {}
bert_100 = []
prefixes = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create ParCourE format corpora from CES format.", 
	epilog="example: python -m convert_corpus_from_CES_format -c config.ini")

    parser.add_argument("-c", default="")


	
    args = parser.parse_args()
    if args.c == "":
        print("please specify config file")
        exit()

    read_config(args.c)
    create_dirs()
    save_config(args.c)
    setup(args.c)


    for file in CES_alignment_files:
        process_alignment_file(file)
    
    save_PC_config_files()
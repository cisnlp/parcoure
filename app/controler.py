import codecs
import sys
from app import stats, utils
from app.general_align_reader import GeneralAlignReader

align_reader = GeneralAlignReader()



def create_bins(min, max, count):
    res = []

    step = (max - min) / count
    for i in range(count):
        res.append((min + step * i, min + step * (i+1)))

    return res

def find_bin(bins, value):
    for bin in bins:
        if value >= bin[0] and value <= bin[1]:
            return bin

def bin_to_str(bin):
    return "%.1f-%.1f" % (bin[0], bin[1])

def divide_dict_by_dict(numerator, denominator):
    res = {}
    min = sys.maxsize
    max = -min -1

    for item in numerator:
        res[item] = numerator[item] / denominator[item]
        if res[item] < min:
            min = res[item]
        if res[item] > max:
            max = res[item]

    return (res, min, max)

def divide_dict_by_bal(numerator, denominator):
    res = {}
    min = sys.maxsize
    max = -min -1

    for item in numerator:
        res[item] = numerator[item] / denominator
        if res[item] < min:
            min = res[item]
        if res[item] > max:
            max = res[item]

    return (res, min, max)

def handle_verse_division(stat_type, lang1, lang2, lang_file1, lang_file2, file_data):
    if stats.is_mutualverse(stat_type):
        if stats.is_edition(stat_type):
            verse_data, verse_min, verse_max = stats.files_cache.get(utils.stats_directory + 'edition_pair_verse_stats.txt')
        else:
            verse_data, verse_min, verse_max = stats.files_cache.get(utils.stats_directory + 'lang_pair_verse_stats.txt')
    else:
        if stats.is_edition(stat_type):
            verse_data, verse_min, verse_max = stats.files_cache.get(utils.stats_directory + 'edition_verse_stats.txt')
        else:
            verse_data, verse_min, verse_max = stats.files_cache.get(utils.stats_directory + 'lang_verse_stats.txt')

    if stat_type in stats.no_lang_stat_vals:
        file_data, data_min, data_max = divide_dict_by_dict(file_data, verse_data)
    elif stat_type in stats.one_edition_stat_vals:
        file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[lang_file1])
    elif stat_type in stats.one_lang_stat_vals:
        file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[lang1])
    elif stat_type in stats.two_edition_stat_vals:
        if lang_file1 + "_" + lang_file2 in verse_data:
            file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[lang_file1 + "_" + lang_file2])
        else:
            file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[lang_file2 + "_" + lang_file1])
    elif stat_type in stats.two_langs_stat_vals:
        if lang1 + "_" + lang2 in verse_data:
            file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[lang1 + "_" + lang2])
        else:
            file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[lang2 + "_" + lang1])
    
    return file_data, data_min, data_max

def extract_data_from_file(stat_type, lang1, lang2, lang_file1, lang_file2, bin_size, min, max):
    if stat_type in stats.no_lang_stat_vals:
        if stats.is_perverse(stat_type):
            f_path = utils.stats_directory + stats.get_perverse_original_file(stat_type) + ".txt"
        else:
            f_path = utils.stats_directory + stat_type + ".txt"
    elif stat_type in stats.one_edition_stat_vals:
        f_path = utils.stats_directory + 'edition_stats/' + lang_file1 + "_tokens_stat.txt"
    elif stat_type in stats.one_lang_stat_vals:
        f_path = utils.stats_directory + 'lang_stats/' + lang1 + "_tokens_stat.txt"
    elif stat_type in stats.two_edition_stat_vals:
        _, _, s_edit, t_edit = align_reader.get_ordered_editions(align_reader.file_edition_mapping[lang_file1], align_reader.file_edition_mapping[lang_file2])
        f_path = utils.stats_directory + 'edition_pair_stats/' + align_reader.edition_file_mapping[s_edit] + "_" + align_reader.edition_file_mapping[t_edit] + "_tokens_stat.txt"
    elif stat_type in stats.two_langs_stat_vals:
        s_lang, t_lang = align_reader.get_ordered_langs(lang1, lang2)
        f_path = utils.stats_directory + 'lang_pair_stats/' + s_lang + "_" + t_lang + "_tokens_stat.txt"

    file_data, data_min, data_max = stats.files_cache.get(f_path)

    if stats.is_perverse(stat_type):
        file_data, data_min, data_max = handle_verse_division(stat_type, lang1, lang2, lang_file1, lang_file2, file_data)

    
    res = {"items":{}, "counts":[]}
    counts = {}
    

    min = data_min if min == None else min
    max = data_max if max == None else max
    bins = create_bins(min, max, bin_size)

    for bin in bins:
        counts[bin_to_str(bin)] = 0
        res["items"][bin_to_str(bin)] = {}

    for item in file_data.items():
        val = item[1]
        nam = item[0]
        if val >= min and val <= max:
            bin = find_bin(bins, val)
            counts[bin_to_str(bin)] += 1
            res["items"][bin_to_str(bin)][nam] = val
    
    for item in counts:
        res["counts"].append({"name": item, "value":counts[item]})

    return res
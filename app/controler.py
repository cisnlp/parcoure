import codecs
import sys
import app.stats as stats


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

def handle_verse_division(stat_type, lang1, lang2, edition1, edition2, file_data):
    if stats.is_mutualverse(stat_type):
        if stats.is_edition(stat_type):
            verse_data, verse_min, verse_max = stats.files_cache.get(stats.eflomal_stats_directory + 'edition_pair_verse_stats.txt')
        else:
            verse_data, verse_min, verse_max = stats.files_cache.get(stats.eflomal_stats_directory + 'lang_pair_verse_stats.txt')
    else:
        if stats.is_edition(stat_type):
            verse_data, verse_min, verse_max = stats.files_cache.get(stats.eflomal_stats_directory + 'edition_verse_stats.txt')
        else:
            verse_data, verse_min, verse_max = stats.files_cache.get(stats.eflomal_stats_directory + 'lang_verse_stats.txt')

    if stat_type in stats.no_lang_stat_vals:
        file_data, data_min, data_max = divide_dict_by_dict(file_data, verse_data)
    elif stat_type in stats.one_edition_stat_vals:
        file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[edition1])
    elif stat_type in stats.one_lang_stat_vals:
        file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[lang1])
    elif stat_type in stats.two_edition_stat_vals:
        if edition1 + "_" + edition2 in verse_data:
            file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[edition1 + "_" + edition2])
        else:
            file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[edition2 + "_" + edition1])
    elif stat_type in stats.two_langs_stat_vals:
        if lang1 + "_" + lang2 in verse_data:
            file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[lang1 + "_" + lang2])
        else:
            file_data, data_min, data_max = divide_dict_by_bal(file_data, verse_data[lang2 + "_" + lang1])
    
    return file_data, data_min, data_max

def extract_data_from_file(stat_type, lang1, lang2, edition1, edition2, bin_size, min, max):
    if stat_type in stats.no_lang_stat_vals:
        if stats.is_perverse(stat_type):
            f_path = stats.eflomal_stats_directory + stats.get_perverse_original_file(stat_type) + ".txt"
        else:
            f_path = stats.eflomal_stats_directory + stat_type + ".txt"
    elif stat_type in stats.one_edition_stat_vals:
        f_path = stats.eflomal_stats_directory + 'edition_stats/' + edition1 + "_tokens_stat.txt"
    elif stat_type in stats.one_lang_stat_vals:
        f_path = stats.eflomal_stats_directory + 'lang_stats/' + lang1 + "_tokens_stat.txt"
    elif stat_type in stats.two_edition_stat_vals:
        f_path = stats.eflomal_stats_directory + 'edition_pair_stats/' + edition1 + "_" + edition2 + "_tokens_stat.txt"
    elif stat_type in stats.two_langs_stat_vals:
        f_path = stats.eflomal_stats_directory + 'lang_pair_stats/' + lang1 + "_" + lang2 + "_tokens_stat.txt"

    file_data, data_min, data_max = stats.files_cache.get(f_path)

    if stats.is_perverse(stat_type):
        file_data, data_min, data_max = handle_verse_division(stat_type, lang1, lang2, edition1, edition2, file_data)

    
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
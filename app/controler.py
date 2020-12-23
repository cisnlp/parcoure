import codecs
import sys

def read_dict_file_data(f_path):
    res = []
    min = sys.maxsize
    max = -min -1
    with codecs.open(f_path, 'r', "utf-8") as f:
        for line in f:
            parts = line.split('\t')
            if len(parts) == 2 or len(parts) == 3:
                if len(parts) == 2:
                    val = int(parts[1])
                    key = parts[0]
                else:
                    val = int(parts[2])
                    key = parts[0] + "  " + parts[1]
                res.append({"name": key, "value":val})
                if val > max:
                    max = val
                if val < min:
                    min = val

    return (res, min, max)

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
    return "%.3f-%.3f" % (bin[0], bin[1])

def extract_data_from_file(f_path, bin_size, min, max):
    res = {"items":{}, "counts":[]}
    counts = {}
    file_data, data_min, data_max = read_dict_file_data(f_path)

    min = data_min if min == None else min
    max = data_max if max == None else max
    bins = create_bins(min, max, bin_size)

    for bin in bins:
        counts[bin_to_str(bin)] = 0
        res["items"][bin_to_str(bin)] = {}

    for item in file_data:
        if item['value'] >= min and item['value'] <= max:
            bin = find_bin(bins, item["value"])
            counts[bin_to_str(bin)] += 1
            res["items"][bin_to_str(bin)][item["name"]] = item["value"]
    
    for item in counts:
        res["counts"].append({"name": item, "value":counts[item]})

    return res
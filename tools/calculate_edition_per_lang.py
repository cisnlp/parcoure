from app.general_align_reader import GeneralAlignReader

align_reader = GeneralAlignReader()

edition_count_per_lang = {k: len(v) for k,v in align_reader.lang_files.items()}
#print(sorted(edition_count_per_lang.items(), key= lambda x: x[1]))

more_than_1 = []
more_than_10 = []
more_than_4_less_11 = []
for x in edition_count_per_lang:
    if edition_count_per_lang[x] > 1:
        more_than_1.append(x)
    if edition_count_per_lang[x] > 4 and edition_count_per_lang[x] < 11:
        more_than_4_less_11.append(x)

    if edition_count_per_lang[x] > 10:
        more_than_10.append(x)

for i, x in enumerate(more_than_10):
    for y in more_than_10[i+1:]:
        print("{},{}".format(x,y))

for x in more_than_10:
    for y in more_than_1:
        if y not in more_than_10:
            print("{},{}".format(x,y))

for i,x in enumerate(more_than_4_less_11):
    for y in more_than_4_less_11[i+1:]:
        print("{},{}".format(x,y))


prefix_file = "/mounts/work/mjalili/projects/pbc_simalign/configs/prefixes.txt"
output_file = "/mounts/work/ayyoob/alignment/config/"

with open(prefix_file, "r") as prf_file, open(output_file + "file_language_name_mapping.txt", "w") as flm_f, open(output_file + "language_name_file_mapping.txt", "w") as lfm_f:
    for prf_l in prf_file:
        prf_l = prf_l.strip().split()
        file_name = prf_l[0].strip()
        if len(file_name.split('-')) > 3:
            lang_name = file_name.split('-')[0] + "-" + file_name.split('-')[3]
        else:
            lang_name = file_name.split('-')[0] 
        
        flm_f.write(file_name + "\t" + lang_name + "\n")
        lfm_f.write(lang_name+ "\t" + file_name + "\n")
    



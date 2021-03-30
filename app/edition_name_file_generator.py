#this should be configure file

# to be created:
# - lang order file
import app.utils


config_path = app.utils.config_dir
lang_file_mapping_path = config_path + "lang_files.txt"

with open(lang_file_mapping_path, "r") as prf_file, open(config_path + "file_edition_mapping.txt", "w") as flm_f, open(config_path + "edition_file_mapping.txt", "w") as lfm_f:
    for prf_l in prf_file:
        prf_l = prf_l.strip().split()
        file_name = prf_l[0].strip()
        if len(file_name.split('-')) > 3:
            lang_name = file_name.split('-')[0] + "-" + file_name.split('-')[3]
        else:
            lang_name = file_name.split('-')[0] 
        
        flm_f.write(file_name + "\t" + lang_name + "\n")
        lfm_f.write(lang_name+ "\t" + file_name + "\n")
    



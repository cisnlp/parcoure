
import app.utils as utils
import argparse, configparser, os


if __name__ == "__main__":
    
    config_file = os.environ['CONFIG_PATH']
    
    print("###################         converting corpus format     #####################")
    utils.run_command(f"python -u -m tools.convert_corpus_from_CES_format -c {config_file}")



    print("\n\n###################   creating elasticsearch files   #####################")
    utils.run_command(f"python -u -m app.bible_to_json_convertor -a -c {config_file}")



    parser = configparser.ConfigParser()
    parser.read(config_file)
    print("\n\n################### feeding corpora to elasticsearch #####################")
    utils.run_command(f"cd elasticSearch; chmod +x setup.sh; ./setup.sh {parser['section']['elastic_dir']}")



    print("\n\n###################    generating word alignments    #####################")
    aligner = "fast_align"
    if 'extra_aligner_path' in parser['section'] and parser['section']['extra_aligner_path'] != "":
        aligner = "other"
    print(f"\n using {aligner} as aligner")
    utils.run_command(f"python -u -m tools.parallel_align_maker -a {aligner} -i {parser['section']['aligns_index_dir']} -o {parser['section']['alignments_dir']} -w {parser['section']['worker_count']}")



    print("\n\n###################     calculating corpus stat      #####################")
    utils.run_command(f"python -u -m tools.alignment_static_calculator -w {parser['section']['worker_count']}")
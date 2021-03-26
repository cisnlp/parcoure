from app.utils import Cache, read_dict_file_data

verse_stat_types = [('edition_verse_stats', 'editions verse count'), ('lang_verse_stats', 'languages verse count'), ('edition_pair_verse_stats', 'edition pair mutual verse count'), ('lang_pair_verse_stats', 'language pair mutual verse count')]

corpus_stat_types = [('edition_pair_token_totcount_stats', 'edition pair total alignments'), ('lang_pair_token_totcount_stats', 'language pair total alignments')]
corpus_perverse_stat_types = [('edition_permutualverse_alignment_stats', 'edition pair alignments per verse'), ('lang_permutualverse_alignment_stats', 'language pair alignments per verse')]

vocab_stat_types = [('edition_token_stats', 'edition vocab size'), ('lang_token_stats', 'language vocab size'), ('edition_pair_token_count_stats', 'edition tranlation pair count'), ('lang_pair_token_count_stats', 'language translation pair count')]
vocab_per_verse_stat_types = [('edition_perverse_single_vocab', 'edition vocab size per verse'), ('language_perverse_single_vocab', 'language vocab size per verse'), ('language_permutualverse_vocab', 'language new translations per verse count'), ('edition_permutualverse_vocab', 'edition new translations per verse count')]

token_repetion_stat_types = [('lang_token_count', 'language\'s tokens count'), ('edition_token_count', 'edition\'s tokens count'), ('lang_token_count_pair', 'language\'s translation pair counts'), ('edition_token_count_pair', 'edition\'s translation pair counts')]
token_repetition_perverse_stat_types = [('lang_perverse_token', 'language\'s tokens count per verse'), ('edition_persverse_token', 'edition\'s tokens count perverse'), ('lang_permutualverse_token_pair', 'language\'s translation pair counts per verse'), ('edition_permutualverse_token_pair', 'edition\'s translation pair counts per verse')]

stat_types = []
stat_types.extend(verse_stat_types)
stat_types.extend(corpus_stat_types)
stat_types.extend(corpus_perverse_stat_types)
stat_types.extend(vocab_stat_types)
stat_types.extend(vocab_per_verse_stat_types)
stat_types.extend(token_repetion_stat_types)
stat_types.extend(token_repetition_perverse_stat_types)


verse_stat_vals = [x[0] for x in verse_stat_types]
corpus_stat_vals = [x[0] for x in corpus_stat_types]
corpus_perverse_stat_vals = [x[0] for x in corpus_perverse_stat_types]
vocab_stat_vals = [x[0] for x in vocab_stat_types]
vocab_per_verse_stat_vals = [x[0] for x in vocab_per_verse_stat_types]
token_repetion_stat_vals = [x[0] for x in token_repetion_stat_types]
token_repetition_perverse_stat_vals = [x[0] for x in token_repetition_perverse_stat_types]

stat_vals = []
stat_vals.extend(verse_stat_vals)
stat_vals.extend(corpus_stat_vals)
stat_vals.extend(corpus_perverse_stat_vals)
stat_vals.extend(vocab_stat_vals)
stat_vals.extend(vocab_per_verse_stat_vals)
stat_vals.extend(token_repetion_stat_vals)
stat_vals.extend(token_repetition_perverse_stat_vals)

one_lang_stat_vals = ['lang_token_count', 'lang_perverse_token']
two_langs_stat_vals = ['lang_token_count_pair', 'lang_permutualverse_token_pair']
one_edition_stat_vals = ['edition_token_count', 'edition_persverse_token']
two_edition_stat_vals = ['edition_token_count_pair', 'edition_permutualverse_token_pair']
no_lang_stat_vals= []
no_lang_stat_vals.extend(verse_stat_vals)
no_lang_stat_vals.extend(corpus_stat_vals)
no_lang_stat_vals.extend(corpus_perverse_stat_vals)
no_lang_stat_vals.extend(vocab_stat_vals)
no_lang_stat_vals.extend(vocab_per_verse_stat_vals)


files_cache = Cache(read_dict_file_data)

def is_perverse(stat_type):
    if stat_type in vocab_per_verse_stat_vals or stat_type in token_repetition_perverse_stat_vals or stat_type in corpus_perverse_stat_vals:
        return True
    return False

def is_edition(stat_type):
    if stat_type.startswith('edition'):
        return True
    return False

def is_mutualverse(stat_type):
    if stat_type.split('_')[1] == 'permutualverse':
        return True
    return False

perverse_original_file = {'edition_perverse_single_vocab': 'edition_token_stats', 'language_perverse_single_vocab': 'lang_token_stats', 'language_permutualverse_vocab': 'lang_pair_token_count_stats', 'edition_permutualverse_vocab': 'edition_pair_token_count_stats', 'edition_permutualverse_alignment_stats': 'edition_pair_token_totcount_stats', 'lang_permutualverse_alignment_stats': 'lang_pair_token_totcount_stats'}
def get_perverse_original_file(stat_type):
    return perverse_original_file[stat_type]

perverse_coefficient = {'edition_perverse_single_vocab': 1000, 'language_perverse_single_vocab': 1000, 'language_permutualverse_vocab': 1000, 'edition_permutualverse_vocab': 1000}
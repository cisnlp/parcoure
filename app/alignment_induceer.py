from surprise import Dataset
from surprise import Reader
import pandas as pd
from surprise import SVD, NMF, KNNBasic
from app.utils import setup_dict_entry
from random import  randrange
from app.document_retrieval import DocumentRetriever


doc_retriever = DocumentRetriever()


def get_row_col_editions2(source_edition, target_edition, align_reader):
    source_lang = source_edition[:3]
    target_lang = target_edition[:3]

    column_langs = align_reader.all_langs[:30]
    row_editions = [source_edition, target_edition]
    col_editions = []

    if source_lang in column_langs:
        column_langs.remove(source_lang)
    if target_lang in column_langs:
        column_langs.remove(target_lang)

    for lang in column_langs:
        col_editions.append(align_reader.lang_files[lang][0])

    return row_editions, col_editions

def get_row_col_editions(source_edition, target_edition, align_reader):
    source_lang = source_edition[:3]
    target_lang = target_edition[:3]

    row_langs = align_reader.all_langs[100:400] #TODO check different numbers
    column_langs = align_reader.all_langs[:40]
    row_editions = []
    col_editions = []

    if source_lang in row_langs:
        row_langs.remove(source_lang)
    if source_lang in column_langs:
        column_langs.remove(source_lang)

    if target_lang in row_langs:
        row_langs.remove(target_lang)
    if target_lang in column_langs:
        column_langs.remove(target_lang)


    if 'chv' in row_langs:
        row_langs.remove('chv')
    if 'chv' in column_langs:
        column_langs.remove('chv')
    
    if 'aaz' in row_langs:
        row_langs.remove('aaz')
    if 'aaz' in column_langs:
        column_langs.remove('aaz')

    for lang in row_langs:
        row_editions.append(align_reader.lang_files[lang][0])
    for lang in column_langs:
        col_editions.append(align_reader.lang_files[lang][0])

    row_editions.append(source_edition)
    col_editions.append(target_edition)

    return row_editions, col_editions

def get_alignments_df(row_editions, col_editions, source_edition, target_edition, verse_id, align_reader): #TODO can be improved a lot
    token_counts = {}
    existing_items = {}
    lang_pair_counts = {}


    aligns_dict = {'itemID': [], 'userID': [], 'rating': []}
    for re in row_editions:
        token_counts[re] = 0
        existing_items[re] = {}
        lang_pair_counts[re] = {}
        for ce in col_editions:
            setup_dict_entry(token_counts, ce, 0)
            existing_items[re][ce] = []
            
            #if re == source_edition and ce == target_edition:
            #    continue
            
            aligns = align_reader.get_verse_alignment([verse_id], re, ce)
            
            s_tokens = doc_retriever.retrieve_document(verse_id + "@" + re).split() # TODO remove me
            t_tokens = doc_retriever.retrieve_document(verse_id + "@" + ce).split()

            if verse_id in aligns:
                lang_pair_counts[re][ce] = len(aligns[verse_id])
                for align in aligns[verse_id]:
                    aligns_dict['itemID'].append(re + str(align[0]))
                    aligns_dict['userID'].append(ce + str(align[1]))
                    aligns_dict['rating'].append(2)

                    if align[0] > token_counts[re]:
                        token_counts[re] = align[0]
                    if align[1] > token_counts[ce]:
                        token_counts[ce] = align[1]
                    
                    existing_items[re][ce].append(f"{align[0]},{align[1]}")

                    #if re == source_edition and ce == target_edition:
                    print("aligned: ", s_tokens[align[0]], t_tokens[align[1]])

            else:
                lang_pair_counts[re][ce] = 0
                    
    for re in row_editions:
        for ce in col_editions:
            #if re == source_edition and ce == target_edition:
            #    continue
            for i in range(token_counts[re]):
                for j in range(token_counts[ce]):
                    if f"{i},{j}" not in existing_items[re][ce]:
                        aligns_dict['itemID'].append(re + str(i))
                        aligns_dict['userID'].append(ce + str(j))
                        aligns_dict['rating'].append(1)


     

    #for re in row_editions:
    #    for ce in col_editions:
    #        #if re == source_edition and ce == target_edition:
    #        #    continue
            
    #        for x in range(lang_pair_counts[re][ce] * 4): # TODO parametr
    #            while True:
    #                i = randrange(0, token_counts[re])
    #                j = randrange(0, token_counts[ce])
    #                if f"{i},{j}" not in existing_items[re][ce]:
    #                    aligns_dict['itemID'].append(re + str(i))
    #                    aligns_dict['userID'].append(ce + str(j))
    #                    aligns_dict['rating'].append(0)

    #                    if re == source_edition and ce == target_edition:
    #                        print("nono: ", s_tokens[i], t_tokens[j])
    #                    break
    #print(aligns_dict)

    return pd.DataFrame(aligns_dict), token_counts[source_edition], token_counts[target_edition]

def predict_alignments2(algo, source_edition, target_edition, s_tok_count, t_tok_count, verse_id):
    aligns = []
    source_predictions = {}
    target_predictions = {}

    algo.sim
    for i in range(s_tok_count):
        for j in range(t_tok_count):
            #res = algo.predict(target_edition + str(j), source_edition + str(i))
            #algo.

            setup_dict_entry(source_predictions, i, (j, res.est))
            setup_dict_entry(target_predictions, j, (i, res.est))

            if source_predictions[i][1] < res.est:
                source_predictions[i] = (j, res.est)
            if target_predictions[j][1] < res.est:
                target_predictions[j] = (i, res.est)
            

            #print(s_tokens[i], t_tokens[j], res.est)
            #if res.est >= 0.5:
            #    aligns.append((i,j))

    for i in range(s_tok_count):
        for j in range(t_tok_count):
            if source_predictions[i][0] == j and target_predictions[j][0] == i:
                aligns.append((i,j))

    #for i in range(s_tok_count):
    #    aligns.append((i,source_predictions[i][0]))

    #for j in range(t_tok_count):
    #    if (target_predictions[j][0], j) not in aligns:
    #        aligns.append((target_predictions[j][0], j))
    return aligns

def remove_aligned_words(source_predictions, target_predictions, i , j):
    print(f"remove aligned word, {i}, {j}")
    for item in source_predictions:
        tmp = []
        for score_tuple in source_predictions[item]:
            if score_tuple[0] != j:
                tmp.append(score_tuple)
            else:
                print( f"removing{score_tuple} from source {item}")
        source_predictions[item] = tmp
    
    for item in target_predictions:
        tmp = []
        for score_tuple in target_predictions[item]:
            if score_tuple[0] != i:
                tmp.append(score_tuple)
            else:
                print( f"removing{score_tuple} from target {item}")
        source_predictions[item] = tmp
    
    
            

def predict_alignments(algo, source_edition, target_edition, s_tok_count, t_tok_count, verse_id):
    aligns = []
    source_predictions = {}
    target_predictions = {}

    s_tokens = doc_retriever.retrieve_document(verse_id + "@" + source_edition).split() # TODO remove me
    t_tokens = doc_retriever.retrieve_document(verse_id + "@" + target_edition).split()

    for i in range(s_tok_count):
        for j in range(t_tok_count):
            res = algo.predict(target_edition + str(j), source_edition + str(i))

            setup_dict_entry(source_predictions, i, [])
            setup_dict_entry(target_predictions, j, [])

            source_predictions[i].append((j, res.est))
            target_predictions[j].append((i, res.est))
            print(s_tokens[i], t_tokens[j], res.est)

            #print(s_tokens[i], t_tokens[j], res.est)
            #if res.est >= 0.5:
            #    aligns.append((i,j))

    #for j in range(t_tok_count):
    #    aligns.append((target_predictions[j][0], j))

    for i in range(s_tok_count):
        source_predictions[i].sort(key=lambda tup: tup[1], reverse=True)
    for i in range(t_tok_count):
        target_predictions[i].sort(key=lambda tup: tup[1], reverse=True)

    for i in range(1): # intermax param
        for i in range(s_tok_count):
            for j in range(t_tok_count):
                
                if source_predictions[i][0][0] == j and target_predictions[j][0][0] == i:
                    aligns.append((i,j))

                    #remove_aligned_words(source_predictions, target_predictions, i , j)
                    #source_predictions[i] = source_predictions[i][1:]
                    #target_predictions[j] = target_predictions[j][1:]

                    #break

    #for i in range(s_tok_count):
    #    aligns.append((i,source_predictions[i][0]))

    #for j in range(t_tok_count):
    #    if (target_predictions[j][0], j) not in aligns:
    #        aligns.append((target_predictions[j][0], j))
    return aligns

def get_induced_alignments(source_edition, target_edition, verse_id, align_reader):
    print(source_edition)
    print(target_edition)
    #algo = SVD()
    #algo = NMF()
    algo = KNNBasic(sim_options={'user_based':False})
    reader = Reader(rating_scale=(1, 3))

    ### itemid -> row, user -> col, source -> row, target-> col###
    row_editions, col_editions = get_row_col_editions(source_edition, target_edition, align_reader)

    df, s_tok_count, t_tok_count = get_alignments_df(row_editions, col_editions, source_edition, target_edition, verse_id, align_reader)
    
    data = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], reader)
    trainset = data.build_full_trainset()
    algo.fit(trainset)

    res = predict_alignments(algo, source_edition, target_edition, s_tok_count, t_tok_count, verse_id)

    return res
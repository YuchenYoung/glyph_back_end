from . import clip_explainability
from . import semantic_similarity
from . import MCTS
from . import KM
import math


def fill_in_nan(matrix):
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if math.isnan(matrix[i][j]):
                matrix[i][j] = 0.0
    return matrix


def format_mapping(props, matches, similarity, rel_mat):
    print(matches)
    mapping_res = []
    for i in range(len(props)):
        if matches[i] >= rel_mat.shape[0]:
            return []
        mapping_res.append({
            "prop": props[i],
            "element": matches[i],
            "similarity": similarity[i],
            "relevance": rel_mat[matches[i]][i]
        })
    print(mapping_res)
    return mapping_res


def data_mapping_km(theme, props, types, svgs):
    rel_matrix = fill_in_nan(clip_explainability.get_rel_props_elements(theme, props, svgs))
    similarity = semantic_similarity.get_theme_props_similarity(theme, props)
    print('======== in data mapping km =======')
    print(props)
    print(similarity)
    print(rel_matrix)
    # return map_data(props, svg_part + 1, rel_matrix)
    edges = rel_matrix.T
    for i in range(edges.shape[0]):
        for j in range(edges.shape[1]):
            edges[i][j] *= similarity[i]
    print(edges)
    match_arr = KM.km_algo(edges)
    map_res = {}
    for i in range(len(props)):
        map_res[props[i]] = int(match_arr[i])
    print(map_res)
    return map_res
    

def data_mapping_main(theme, props, types, svgs):
    rel_matrix = fill_in_nan(clip_explainability.get_rel_props_elements(theme, props, svgs))
    similarity = semantic_similarity.get_theme_props_similarity(theme, props)
    print('======== in data mapping main =======')
    print(props)
    print(similarity)
    print(rel_matrix)
    match_eles, score = MCTS.mcts_search(similarity, rel_matrix)
    mapping_res = {}
    for i in range(len(props)):
        mapping_res[props[i]] = match_eles[i]
    print(mapping_res)
    return mapping_res


def data_mapping_multi(theme, props, types, svgs_list):
    similarity = semantic_similarity.get_theme_props_similarity(theme, props)
    print('======== in data mapping multi =======')
    print(props)
    print(similarity)
    max_score = -1000
    max_svgs = -1
    # max_ops = []
    best_mapping = []
    for i in range(len(svgs_list)):
        print(f"now is image {i}")
        rel_matrix = fill_in_nan(clip_explainability.get_rel_props_elements(theme, props, svgs_list[i]))
        print(rel_matrix)
        match_eles, score = MCTS.mcts_search(similarity, rel_matrix)
        print(f'{i} {score}')
        cur_mapping = format_mapping(props, match_eles, similarity, rel_matrix)
        if max_score < score and len(cur_mapping) > 0:
            # max_ops = match_eles
            max_svgs = i
            max_score = score
            best_mapping = cur_mapping
        print(f"now finish {i}")
    return max_svgs, max_score, best_mapping

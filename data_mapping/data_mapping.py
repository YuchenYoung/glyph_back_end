from . import clip_explainability
from . import semantic_similarity
from . import MCTS
from . import KM
import math
import time


def fill_in_nan(matrix):
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if math.isnan(matrix[i][j]):
                matrix[i][j] = 0.0
    return matrix


def format_mapping(props, matches, similarity, rel_mat):
    print(matches)
    mapping_res = []
    for i in range(len(matches)):
        if matches[i] >= rel_mat.shape[0]:
            continue
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
    similarity, props = semantic_similarity.get_theme_props_similarity(theme, props)
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
    similarity, props = semantic_similarity.get_theme_props_similarity(theme, props)
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
    print('====== now calculate similarity =======')
    t_semantic_before = time.perf_counter()
    similarity, props = semantic_similarity.get_theme_props_similarity(theme, props)
    t_semantic_after = time.perf_counter()
    print('======== in data mapping multi =======')
    print(props)
    print(similarity)
    max_score = -1000
    max_svgs = -1
    # max_ops = []
    all_mapping = []
    all_score = []
    best_mapping = []
    semantic_time = t_semantic_after - t_semantic_before
    cal_time = []
    for i in range(len(svgs_list)):
        print(f"now is image {i}")
        cur_similarity = similarity[:int(len(svgs_list[i])*1.2)]
        cur_props = props[:int(len(svgs_list[i])*1.2)]
        t_matrix_before = time.perf_counter()
        rel_matrix = fill_in_nan(clip_explainability.get_rel_props_elements(theme, cur_props, svgs_list[i]))
        t_matrix_after = time.perf_counter()
        print(rel_matrix)
        t_match_before = time.perf_counter()
        match_eles, score = MCTS.mcts_search(cur_similarity, rel_matrix)
        t_match_after = time.perf_counter()
        print(f'{i} {score}')
        cur_mapping = format_mapping(cur_props, match_eles, cur_similarity, rel_matrix)
        all_mapping.append(cur_mapping)
        all_score.append(score)
        if max_score < score and len(cur_mapping) > 0:
            # max_ops = match_eles
            max_svgs = i
            max_score = score
            best_mapping = cur_mapping
        print(f"now finish {i}")
        cal_time.append([semantic_time, t_matrix_after - t_matrix_before, t_match_after - t_match_before])
        semantic_time = 0
    return max_svgs, max_score, best_mapping, all_score, all_mapping, cal_time

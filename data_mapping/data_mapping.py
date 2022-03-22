from tokenize import group
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


def get_similarity(theme, props, groups, types):
    similarity, props = semantic_similarity.get_theme_props_similarity(theme, props, types)
    print(props)
    print(similarity)
    dic_similarity = {}
    for i in range(len(props)):
        dic_similarity[props[i]] = similarity[i]
    for i in range(len(groups)):
        val = 0
        for it in groups[i]:
            pos = props.index(it)
            val += similarity[pos]
        val /= len(groups[i])
        dic_similarity[f'group{i}'] = val
    return props, similarity, dic_similarity


def format_mapping(props, groups, matches, similarity, rel_mat):
    print(matches)
    single_props = []
    group_props = []
    for i in range(len(groups)):
        group_props += groups[i]
        single_props.append('')
    # print(group_props)
    single_props += list(filter(lambda d: d not in group_props, props))
    # print(single_props)
    mapping_res = []
    for i in range(len(matches)):
        if matches[i] >= rel_mat.shape[0]:
            continue
        cur_map = {
            "element": matches[i],
            "similarity": similarity[i],
            "relevance": rel_mat[matches[i]][i]
        }
        if i < len(groups):
            cur_map['is_group'] = True
            cur_map['group'] = groups[i]
            cur_map['prop'] = f'group{i}'
        else:
            cur_map['is_group'] = False
            cur_map['prop'] = single_props[i]
        mapping_res.append(cur_map)
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


def data_mapping_multi(theme, props, similarity, group_props, types, svgs_list, mapped):
    print('====== now calculate similarity =======')
    # t_semantic_before = time.perf_counter()
    # similarity, props = semantic_similarity.get_theme_props_similarity(theme, props, types)
    # t_semantic_after = time.perf_counter()
    groups = []
    for lst in group_props:
        cur_group = []
        for it in lst:
            cur_group.append(props.index(it))
        groups.append(cur_group)
    print('======== in data mapping multi =======')
    print(props)
    print(similarity)
    max_score = -1000
    max_svgs = -1
    # max_ops = []
    all_mapping = []
    all_score = []
    best_mapping = []
    semantic_time = 0
    cal_time = []
    mapped_idx = []
    for it in mapped:
        if it['is_group'] == True:
            mapped_idx.append({"level": int(it['prop']), "ele": int(it['ele']), "is_group": True})
        else:
            mapped_idx.append({"level": props.index(it['prop']), "ele": int(it['ele']), "is_group": False})

    for i in range(len(svgs_list)):
        print(f"now is image {i}")
        # cur_similarity = similarity[:int(len(svgs_list[i])*1.2)]
        # cur_props = props[:int(len(svgs_list[i])*1.2)]
        cur_similarity = similarity
        cur_props = props
        t_matrix_before = time.perf_counter()
        rel_matrix = fill_in_nan(clip_explainability.get_rel_props_elements(theme, cur_props, svgs_list[i]))
        for j in range(len(props)):
            if types[props[j]] == 'time' or types[props[j]] == 'geography':
                rel_matrix[0][j] = 1.0
            elif "Item" in props[j] or "Object" in props[j]:
                rel_matrix[0][j] = 1.0
            else:
                rel_matrix[0][j] = 0.00
        t_matrix_after = time.perf_counter()
        print(rel_matrix)
        t_match_before = time.perf_counter()
        # print(groups)
        # print(mapped_idx)
        match_eles, score = MCTS.mcts_search(cur_similarity, rel_matrix, groups, mapped_idx)
        t_match_after = time.perf_counter()
        print(f'{i} {score}')
        cur_mapping = format_mapping(cur_props, group_props, match_eles, cur_similarity, rel_matrix)
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

# def data_mapping_multi(theme, props, types, svgs_list):
#     return 'max_svgs', 'max_score', 'best_mapping', 'all_score', 'all_mapping', 'cal_time'

from . import clip_explainability
from . import semantic_similarity
from . import MCTS
from . import KM


def data_mapping_km(theme, props, types, svgs):
    rel_matrix =  clip_explainability.get_rel_props_elements(theme, props, svgs)
    similarity = semantic_similarity.get_theme_props_similaruty(theme, props)
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
    rel_matrix =  clip_explainability.get_rel_props_elements(theme, props, svgs)
    similarity = semantic_similarity.get_theme_props_similaruty(theme, props)
    print('======== in data mapping main =======')
    print(props)
    print(similarity)
    print(rel_matrix)
    match_eles = MCTS.mcts_search(similarity, rel_matrix)
    mapping_res = {}
    for i in range(len(props)):
        mapping_res[props[i]] = match_eles[i]
    print(mapping_res)
    return mapping_res
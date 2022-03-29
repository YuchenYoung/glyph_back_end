import os
from sentence_transformers import SentenceTransformer, util

# model = SentenceTransformer('all-MiniLM-L6-v2')
model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'all-MiniLM-L6-v2')
model = SentenceTransformer(model_dir)

def normalize_and_sort(lst, props, types):
    min_val = -1
    max_val = 1
    new_list = []
    for i in range(len(lst)):
        # print(props[i])
        val = (lst[i] - min_val) / (max_val - min_val)
        if types[props[i]] == 'time' or types[props[i]] == 'geography':
            val = 1
        if "Item" in props[i] or "Object" in props[i]:
            val = 1
        new_list.append({"prop": props[i], "val": val})
    new_list.sort(key=(lambda d: d["val"]), reverse=True)
    for i in range(len(lst)):
        lst[i] = new_list[i]["val"]
        props[i] = new_list[i]["prop"]
    return lst, props


def get_theme_props_similarity(theme, props, types):
    # Two lists of sentences
    sentences1 = props

    sentences2 = [theme]

    # Compute embedding for both lists
    embeddings1 = model.encode(sentences1, convert_to_tensor=True)
    embeddings2 = model.encode(sentences2, convert_to_tensor=True)

    # Compute cosine-similarits
    cosine_scores = util.cos_sim(embeddings1, embeddings2)

    similarity = []
    # Output the pairs with their score
    for i in range(len(sentences1)):
        similarity.append(cosine_scores[i][0].item())
    print(similarity)

    return normalize_and_sort(similarity, props, types)
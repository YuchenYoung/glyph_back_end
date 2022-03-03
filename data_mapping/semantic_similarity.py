from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')


def get_theme_props_similarity(theme, props):
    # Two lists of sentences
    sentences1 = props

    sentences2 = [theme]

    #Compute embedding for both lists
    embeddings1 = model.encode(sentences1, convert_to_tensor=True)
    embeddings2 = model.encode(sentences2, convert_to_tensor=True)

    #Compute cosine-similarits
    cosine_scores = util.cos_sim(embeddings1, embeddings2)

    similarity = []
    #Output the pairs with their score
    for i in range(len(sentences1)):
        similarity.append(cosine_scores[i][0].item())

    return similarity
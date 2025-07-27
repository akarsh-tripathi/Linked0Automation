from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class PostScorer:
    def __init__(self, prompt):
        self.prompt = prompt
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def score_posts(self, posts):
        texts = [self.prompt] + posts
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        prompt_vec = tfidf_matrix[0]
        post_vecs = tfidf_matrix[1:]
        scores = cosine_similarity(prompt_vec, post_vecs)[0]
        return scores

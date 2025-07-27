from bot.probability_model import PostScorer
THRESHOLD = 0.75


class DecisionEngine:
    def __init__(self, prompt):
        self.model = PostScorer(prompt)

    def get_relevant_posts(self, post_texts, threshold=0.75):
        scores = self.model.score_posts(post_texts)
        result = []
        for i, score in enumerate(scores):
            result.append(
                {
                    "text": post_texts[i],
                    "score": round(score, 3),
                    "should_connect": score >= threshold,
                }
            )
        return result
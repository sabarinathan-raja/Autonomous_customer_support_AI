
import re
from time import perf_counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def tokenize(text: str):
    """Convert text into normalized word tokens."""

    return set(
        re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    )


def calculate_answer_relevance(
    customer_question: str,
    generated_answer: str
):
    """Calculate baseline TF-IDF similarity between question and answer."""

    if not customer_question.strip() or not generated_answer.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer()

        vectors = vectorizer.fit_transform([
            customer_question,
            generated_answer
        ])

        score = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        return round(float(score), 4)

    except ValueError:
        return 0.0


def calculate_faithfulness(
    policy_context: str,
    generated_answer: str
):
    """Calculate word-overlap baseline against policy context."""

    context_words = tokenize(policy_context)
    answer_words = tokenize(generated_answer)

    if not answer_words:
        return 0.0

    overlap = context_words.intersection(answer_words)

    return round(
        len(overlap) / len(answer_words),
        4
    )


def calculate_context_precision(
    retrieved_contexts: list,
    relevant_keywords: list
):
    """Calculate the fraction of retrieved chunks matching keywords."""

    if not retrieved_contexts or not relevant_keywords:
        return 0.0

    keywords = [
        keyword.lower().strip()
        for keyword in relevant_keywords
        if keyword.strip()
    ]

    if not keywords:
        return 0.0

    relevant_count = 0

    for context in retrieved_contexts:

        text = str(context).lower()

        if any(keyword in text for keyword in keywords):
            relevant_count += 1

    return round(
        relevant_count / len(retrieved_contexts),
        4
    )


def calculate_context_recall(
    retrieved_contexts: list,
    expected_keywords: list
):
    """Estimate keyword coverage in retrieved contexts."""

    if not expected_keywords:
        return 0.0

    retrieved_text = " ".join(
        str(context).lower()
        for context in retrieved_contexts
    )

    keywords = [
        keyword.lower().strip()
        for keyword in expected_keywords
        if keyword.strip()
    ]

    if not keywords:
        return 0.0

    matched_keywords = sum(
        1
        for keyword in keywords
        if keyword in retrieved_text
    )

    return round(
        matched_keywords / len(keywords),
        4
    )


def calculate_overall_score(
    answer_relevance: float,
    faithfulness: float,
    context_precision: float,
    context_recall: float
):
    """Calculate a simple average of quality metrics."""

    scores = [
        answer_relevance,
        faithfulness,
        context_precision,
        context_recall
    ]

    return round(
        sum(scores) / len(scores),
        4
    )


def calculate_response_time(start_time: float):
    """Calculate elapsed time in seconds."""

    return round(
        perf_counter() - start_time,
        4
    )

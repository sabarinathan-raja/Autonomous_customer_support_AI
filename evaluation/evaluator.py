
from evaluation.metrics import (
    calculate_answer_relevance,
    calculate_faithfulness,
    calculate_context_precision,
    calculate_context_recall,
    calculate_overall_score,
    calculate_response_time
)


def evaluate_response(
    customer_question,
    generated_answer,
    policy_context,
    retrieved_contexts,
    relevant_keywords,
    start_time,
    expected_keywords=None
):

    answer_relevance = calculate_answer_relevance(
        customer_question,
        generated_answer
    )

    faithfulness = calculate_faithfulness(
        policy_context,
        generated_answer
    )

    context_precision = calculate_context_precision(
        retrieved_contexts,
        relevant_keywords
    )

    context_recall = calculate_context_recall(
        retrieved_contexts,
        expected_keywords or []
    )

    overall_score = calculate_overall_score(
        answer_relevance,
        faithfulness,
        context_precision,
        context_recall
    )

    response_time = calculate_response_time(
        start_time
    )

    return {
        "answer_relevance": answer_relevance,
        "faithfulness": faithfulness,
        "context_precision": context_precision,
        "context_recall": context_recall,
        "overall_score": overall_score,
        "response_time_seconds": response_time
    }

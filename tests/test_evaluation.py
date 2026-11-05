
from time import perf_counter

from evaluation.evaluator import evaluate_response


def test_evaluation():

    question = "What is the refund policy?"

    answer = (
        "Customers can request a refund "
        "according to refund conditions."
    )

    context = (
        "Customers can request a refund "
        "according to refund conditions."
    )

    start_time = perf_counter()

    results = evaluate_response(
        customer_question=question,
        generated_answer=answer,
        policy_context=context,
        retrieved_contexts=[context],
        relevant_keywords=["refund", "customers"],
        expected_keywords=["refund", "conditions"],
        start_time=start_time
    )

    for metric, score in results.items():
        print(f"{metric}: {score}")

    assert 0 <= results["answer_relevance"] <= 1
    assert 0 <= results["faithfulness"] <= 1
    assert 0 <= results["context_precision"] <= 1
    assert 0 <= results["context_recall"] <= 1
    assert 0 <= results["overall_score"] <= 1


if __name__ == "__main__":
    test_evaluation()

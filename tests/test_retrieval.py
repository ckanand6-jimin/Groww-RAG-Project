from src.retrieve import retrieve


def test_expense_ratio_retrieval():
    result = retrieve(
        "What is the expense ratio of HDFC Mid Cap Fund?",
        top_k=3
    )

    assert len(result["hits"]) > 0
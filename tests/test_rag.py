from src.rag import answer_query

def test_benchmark_answer():
    result = answer_query(
        "What is the benchmark of HDFC Mid Cap Fund?"
    )

    assert "NIFTY" in result["answer"]
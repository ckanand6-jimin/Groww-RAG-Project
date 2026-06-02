from src.query_classifier import QueryType, build_refusal_response, classify_query


def test_classify_factual_query():
    query = "What is the expense ratio of HDFC Mid Cap Fund?"
    query_type, triggers = classify_query(query)
    assert query_type == QueryType.FACTUAL
    assert triggers == []


def test_classify_advisory_query():
    query = "Should I invest in HDFC Mid Cap Fund?"
    query_type, triggers = classify_query(query)
    assert query_type == QueryType.ADVISORY
    assert "should i" in triggers or "invest in" in triggers


def test_classify_ambiguous_query():
    query = "What do you think about HDFC equity fund?"
    query_type, triggers = classify_query(query)
    assert query_type == QueryType.AMBIGUOUS
    assert triggers


def test_build_refusal_response():
    response = build_refusal_response("Should I invest?", QueryType.ADVISORY)
    assert response["response_type"] == "REFUSAL"
    assert "financial advisor" in response["answer"].lower()
    assert response["citation"] == "https://www.amfiindia.com/investor"


def test_answer_query_refuses_advisory_questions():
    from src.rag import answer_query

    response = answer_query("Should I invest in HDFC Mid Cap Fund?")
    assert response["response_type"] == "REFUSAL"
    assert response["provider"] == "refusal"
    assert "financial advisor" in response["answer"].lower()

import sys
sys.path.insert(0, '.')
from email_processor import classify_email


def test_classifies_inquiry():
    result = classify_email("Question about parking", "Hi, how do I reserve a spot?")
    assert result["category"] == "inquiry"


def test_classifies_complaint():
    result = classify_email("Problem", "This parking gate is broken, fix it asap")
    assert result["category"] == "complaint"


def test_classifies_order():
    result = classify_email("Order", "I want to book parking tomorrow")
    assert result["category"] == "order"


def test_extracts_phone():
    result = classify_email("Question", "My phone is 061 123 456, call me")
    assert "phone" in result["entities"]
    assert result["entities"]["phone"] == "061 123 456"
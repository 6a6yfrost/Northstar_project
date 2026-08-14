from northstar_chatbot import NorthstarSupportBot


def test_order_query_without_exact_status_phrase_still_routes_to_order_status():
    bot = NorthstarSupportBot(data_dir='data')
    intent, confidence = bot.classify_intent('I want to check my order')
    assert intent == 'order_status', (intent, confidence)
    assert confidence > 0


def test_order_number_in_message_routes_to_order_status():
    bot = NorthstarSupportBot(data_dir='data')
    intent, confidence = bot.classify_intent('Where is ORD-2024-001')
    assert intent == 'order_status', (intent, confidence)
    assert confidence > 0

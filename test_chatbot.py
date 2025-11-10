from chatbot_core import Chatbot

def test_chatbot():
    """Run comprehensive tests on chatbot"""
    
    print("CHATBOT TESTING SUITE")
    print("=" * 70)
    
    chatbot = Chatbot()
    
    if not chatbot.initialize():
        print("❌ Failed to initialize chatbot")
        return False
    
    print("✓ Chatbot initialized successfully")
    
    # Test queries
    test_queries = [
        "Show me all employees",
        "List products with price less than 500",
        "How many employees",
        "What is the salary of John Doe"
    ]
    
    passed = 0
    failed = 0
    
    for query in test_queries:
        print(f"\nTest: {query}")
        response = chatbot.process_message(query)
        
        if response.get('success'):
            print(f"✓ SUCCESS - SQL: {response.get('sql')}")
            passed += 1
        else:
            print(f"❌ FAILED - {response.get('message')}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Passed: {passed}/{len(test_queries)}")
    print(f"❌ Failed: {failed}")
    
    chatbot.close()
    
    return failed == 0


if __name__ == "__main__":
    test_chatbot()

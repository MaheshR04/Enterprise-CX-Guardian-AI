"""
Chat Conversation Prompt Templates for Enterprise CX Guardian AI.
"""

CHAT_USER_TEMPLATE = """
Customer Query: {message}
"""

CHAT_CONTEXT_TEMPLATE = """
Conversation History:
{history}

Customer Query: {message}
"""

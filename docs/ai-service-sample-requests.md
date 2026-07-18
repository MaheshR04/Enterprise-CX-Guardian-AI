# AI Service MongoDB Conversation Test Requests

Base URL:

```bash
BASE_URL=http://localhost:8000/api/v1
```

## 1. Create Conversation

```bash
curl -X POST "$BASE_URL/conversations" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "conv_enterprise_demo_001",
    "metadata": {
      "channel": "web",
      "customer_id": "cust_1001",
      "tenant": "enterprise"
    }
  }'
```

Expected result: `201 Created` with `data.conversation_id`.

## 2. Continue Conversation

```bash
curl -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "conv_enterprise_demo_001",
    "message": "Hello, I need help with an enterprise subscription refund."
  }'
```

Expected result: user message, assistant message, prompt log, and token usage are persisted to MongoDB.

## 3. Continue Again

```bash
curl -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "conv_enterprise_demo_001",
    "message": "Can you summarize the policy and next best action?"
  }'
```

Expected result: the existing conversation is reused and history is loaded from MongoDB.

## 4. List Conversations

```bash
curl "$BASE_URL/conversations?limit=10&page=1&sort=desc"
```

Expected result: paginated conversation summaries with `message_count`.

## 5. Search Conversations

```bash
curl "$BASE_URL/conversations/search?conversationId=enterprise_demo&status=active&limit=10&page=1"
```

Expected result: filtered, paginated search results.

## 6. Load Conversation

```bash
curl "$BASE_URL/conversations/conv_enterprise_demo_001"
```

Expected result: conversation header, messages, prompt stats, latest prompt, latest usage, and token summary.

## 7. Soft Delete Conversation

```bash
curl -X DELETE "$BASE_URL/conversations/conv_enterprise_demo_001"
```

Expected result: status becomes `deleted`; document remains in MongoDB and is excluded from normal list results.

## 8. Verify Deleted Conversation Is Searchable Explicitly

```bash
curl "$BASE_URL/conversations/search?status=deleted&conversationId=enterprise_demo"
```

Expected result: soft-deleted conversation appears only when `status=deleted` is requested.

## 9. Restore Conversation

```bash
curl -X PATCH "$BASE_URL/conversations/conv_enterprise_demo_001/restore"
```

Expected result: status returns to `active`.

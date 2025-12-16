#!/bin/bash

# Test script for authentication middleware
# Usage: ./test_auth.sh

echo "🔐 Testing Authentication Middleware"
echo "===================================="
echo ""

# Set your AUTH_TOKEN here or load from environment
if [ -z "$AUTH_TOKEN" ]; then
    echo "⚠️  AUTH_TOKEN not set. Using default test token."
    AUTH_TOKEN="test-token-12345"
fi

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "Base URL: $BASE_URL"
echo "Token: ${AUTH_TOKEN:0:10}..." # Show only first 10 chars
echo ""

# Test 1: Public endpoint (health check)
echo "📝 Test 1: Public endpoint (no auth required)"
echo "GET $BASE_URL/health"
curl -s $BASE_URL/health | jq '.'
echo ""
echo ""

# Test 2: Public endpoint (root)
echo "📝 Test 2: Root endpoint (no auth required)"
echo "GET $BASE_URL/"
curl -s $BASE_URL/ | jq '.'
echo ""
echo ""

# Test 3: Protected endpoint without token
echo "📝 Test 3: Protected endpoint WITHOUT token (should fail)"
echo "POST $BASE_URL/faqs/ask"
curl -s -X POST $BASE_URL/faqs/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "contract_type": "contractor", "user_id": "test"}' | jq '.'
echo ""
echo ""

# Test 4: Protected endpoint with invalid token
echo "📝 Test 4: Protected endpoint with INVALID token (should fail)"
echo "POST $BASE_URL/faqs/ask"
curl -s -X POST $BASE_URL/faqs/ask \
  -H "Authorization-X: invalid-token-12345" \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "contract_type": "contractor", "user_id": "test"}' | jq '.'
echo ""
echo ""

# Test 5: Protected endpoint with valid token (Authorization-X format)
echo "📝 Test 5: Protected endpoint with VALID token (Authorization-X format)"
echo "POST $BASE_URL/faqs/ask"
curl -s -X POST $BASE_URL/faqs/ask \
  -H "Authorization-X: $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How can I participate in English classes?",
    "contract_type": "contractor",
    "user_id": "test_user"
  }' | jq '.'
echo ""
echo ""

echo "✅ Authentication tests completed!"
echo ""
echo "Summary:"
echo "- Test 1-2: Should succeed (public endpoints)"
echo "- Test 3-4: Should return 401 (missing/invalid token)"
echo "- Test 5: Should succeed (valid token with Authorization-X header)"


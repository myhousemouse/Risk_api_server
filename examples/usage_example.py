"""
간단한 사용 예제
"""

# 1단계: 초기 사업 정보 입력
initial_data = {
    "business_name": "스마트 카페",
    "business_description": "AI 바리스타와 무인 결제 시스템을 갖춘 프랜차이즈 카페를 오픈하려고 합니다.",
    "investment_amount": 100000000
}

# POST /api/v1/analyze/initial
# Response: { "session_id": "...", "matched_categories": [...], ... }

# =========================================

# 3단계: 질문 생성
question_request = {
    "session_id": "받은_세션_ID"
}

# POST /api/v1/analyze/questions
# Response: { "questions": [...], "total_questions": 15 }

# =========================================

# 5단계: 답변 제출 및 보고서 생성
answer_data = {
    "session_id": "받은_세션_ID",
    "answers": [
        {
            "question_id": "method1_q1",
            "answer": "30대 직장인"
        },
        {
            "question_id": "method1_q2",
            "answer": "강남역, 판교역 인근"
        }
        # ... 나머지 답변들
    ]
}

# POST /api/v1/analyze/report
# Response: { "overall_risk_score": 55, "method_results": [...], ... }

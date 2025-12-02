"""
Risk Manager API 테스트 스크립트

이 스크립트는 API의 전체 워크플로우를 테스트합니다.
"""
import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """섹션 구분선 출력"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_health_check():
    """헬스체크 테스트"""
    print_section("헬스체크")
    
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    return response.status_code == 200


def test_initial_analysis() -> Dict[str, Any]:
    """1단계: 초기 사업 정보 분석 테스트"""
    print_section("1단계: 초기 사업 정보 분석")
    
    data = {
        "business_name": "AI 학습 플랫폼",
        "business_description": "초등학생을 위한 AI 기반 맞춤형 수학 학습 앱을 개발하려고 합니다. "
                               "학생의 수준에 맞춰 문제를 제공하고, 취약점을 분석하여 개인화된 학습 경로를 제시합니다. "
                               "모바일 앱과 웹 플랫폼으로 제공할 예정입니다.",
        "investment_amount": 50000000
    }
    
    print("요청 데이터:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    response = requests.post(f"{BASE_URL}/api/v1/analyze/initial", json=data)
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result


def test_question_generation(session_id: str) -> Dict[str, Any]:
    """3단계: 질문 생성 테스트"""
    print_section("3단계: 맞춤형 질문 생성")
    
    data = {
        "session_id": session_id
    }
    
    print(f"세션 ID: {session_id}")
    
    response = requests.post(f"{BASE_URL}/api/v1/analyze/questions", json=data)
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    print(f"총 질문 수: {result['total_questions']}")
    
    print("\n생성된 질문들:")
    for i, q in enumerate(result['questions'][:5], 1):  # 처음 5개만 출력
        print(f"{i}. [{q['method']}] {q['question_text']}")
        print(f"   답변 유형: {q['question_type']}")
    
    if result['total_questions'] > 5:
        print(f"... 외 {result['total_questions'] - 5}개 질문")
    
    return result


def test_final_report(session_id: str, questions: list) -> Dict[str, Any]:
    """5단계: 최종 보고서 생성 테스트"""
    print_section("5단계: 최종 리스크 보고서 생성")
    
    # 샘플 답변 생성 (실제로는 사용자가 입력)
    answers = []
    for q in questions:
        if q['question_type'] == 'number':
            answer = "1000000"
        elif q['question_type'] == 'choice' and q.get('choices'):
            answer = q['choices'][0]
        else:
            answer = "테스트 답변입니다. 사업의 핵심은 AI 기술과 교육 컨텐츠의 결합입니다."
        
        answers.append({
            "question_id": q['question_id'],
            "answer": answer
        })
    
    data = {
        "session_id": session_id,
        "answers": answers
    }
    
    print(f"세션 ID: {session_id}")
    print(f"답변 수: {len(answers)}")
    
    response = requests.post(f"{BASE_URL}/api/v1/analyze/report", json=data)
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    
    print(f"\n📊 종합 리스크 점수: {result['overall_risk_score']}/100")
    print(f"📈 위험 수준: {result['overall_risk_level']}")
    
    print(f"\n📝 경영진 요약:")
    print(result['executive_summary'])
    
    print(f"\n⚠️  주요 리스크:")
    for risk in result['key_risks']:
        print(f"  - {risk}")
    
    print(f"\n💡 핵심 권장사항:")
    for rec in result['critical_recommendations']:
        print(f"  - {rec}")
    
    return result


def main():
    """전체 워크플로우 테스트"""
    print("\n" + "🚀 Risk Manager API 테스트 시작 🚀".center(60))
    
    try:
        # 1. 헬스체크
        if not test_health_check():
            print("❌ 헬스체크 실패")
            return
        
        # 2. 초기 분석
        initial_result = test_initial_analysis()
        session_id = initial_result['session_id']
        
        # 3. 질문 생성
        question_result = test_question_generation(session_id)
        questions = question_result['questions']
        
        # 4. 최종 보고서 생성
        final_result = test_final_report(session_id, questions)
        
        print_section("✅ 테스트 완료")
        print("모든 API 엔드포인트가 정상적으로 동작합니다!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 서버에 연결할 수 없습니다.")
        print("먼저 서버를 실행해주세요: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

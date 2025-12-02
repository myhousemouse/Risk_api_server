from typing import Dict, List
from datetime import datetime
import uuid
from .models import (
    InitialBusinessInput,
    InitialAnalysisResponse,
    QuestionGenerationResponse,
    Question,
    AnswerSubmissionRequest,
    FinalRiskReport,
    MethodAnalysisResult,
    OSDScore,
    CashLossAnalysis,
    CostBreakdown,
    AIRecommendation,
    IndustryCategory
)
from .classifier import IndustryClassifier
from .gpt_service import GPTService
from .risk_engine import OSDRiskEngine, CostAnalysisEngine


class SessionStore:
    """간단한 인메모리 세션 저장소 (실제로는 Redis나 DB 사용 권장)"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self, session_data: Dict) -> str:
        """새 세션 생성"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            **session_data,
            "created_at": datetime.now().isoformat()
        }
        return session_id
    
    def get_session(self, session_id: str) -> Dict:
        """세션 조회"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict):
        """세션 업데이트"""
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)
    
    def delete_session(self, session_id: str):
        """세션 삭제"""
        if session_id in self.sessions:
            del self.sessions[session_id]


class RiskAnalysisService:
    """리스크 분석 비즈니스 로직"""
    
    def __init__(self, gpt_service: GPTService, session_store: SessionStore):
        self.gpt_service = gpt_service
        self.session_store = session_store
        self.classifier = IndustryClassifier()
    
    def analyze_initial_business(
        self, 
        business_input: InitialBusinessInput
    ) -> InitialAnalysisResponse:
        """
        1단계: 초기 사업 정보 분석
        - 입력 검증
        - 업종 분류
        - 분석 기법 선택
        """
        # 1차 입력 검증: 비즈니스 아이디어인지 확인
        validation_result = self.gpt_service.validate_business_input(
            business_input.business_description
        )
        
        if not validation_result["is_valid"]:
            # 검증 실패 시 예외 발생
            error_message = validation_result["message"]
            if validation_result["suggestion"]:
                error_message += f"\n\n{validation_result['suggestion']}"
            raise ValueError(error_message)
        
        # 업종 분류
        categories = self.classifier.classify_business(
            business_input.business_description
        )
        
        # 분석 기법 선택
        methods = self.classifier.select_analysis_methods(categories)
        
        # 분류 근거 생성
        reasoning = self.classifier.generate_classification_reasoning(
            business_input.business_description,
            categories,
            methods
        )
        
        # 세션 생성
        session_data = {
            "business_name": business_input.business_name,
            "business_description": business_input.business_description,
            "investment_amount": business_input.investment_amount,
            "categories": [cat.dict() for cat in categories],
            "methods": [method.value for method in methods],
            "stage": "initial_analyzed"
        }
        session_id = self.session_store.create_session(session_data)
        
        return InitialAnalysisResponse(
            session_id=session_id,
            matched_categories=categories,
            selected_methods=methods,
            reasoning=reasoning
        )
    
    def generate_questions(
        self, 
        session_id: str
    ) -> QuestionGenerationResponse:
        """
        3단계: 맞춤형 질문 생성
        """
        session = self.session_store.get_session(session_id)
        if not session:
            raise ValueError("유효하지 않은 세션 ID입니다.")
        
        # 세션에서 정보 추출
        business_name = session["business_name"]
        business_description = session["business_description"]
        investment_amount = session["investment_amount"]
        
        # 문자열을 AnalysisMethod enum으로 변환
        from .models import AnalysisMethod
        methods = [AnalysisMethod(m) for m in session["methods"]]
        
        # GPT로 질문 생성
        questions = self.gpt_service.generate_questions(
            business_name,
            business_description,
            investment_amount,
            methods
        )
        
        # 세션 업데이트
        self.session_store.update_session(session_id, {
            "questions": [q.dict() for q in questions],
            "stage": "questions_generated"
        })
        
        return QuestionGenerationResponse(
            session_id=session_id,
            questions=questions,
            total_questions=len(questions)
        )
    
    def generate_final_report(
        self, 
        answer_request: AnswerSubmissionRequest
    ) -> FinalRiskReport:
        """
        5단계: OSD 기반 최종 리스크 보고서 생성
        """
        session_id = answer_request.session_id
        session = self.session_store.get_session(session_id)
        if not session:
            raise ValueError("유효하지 않은 세션 ID입니다.")
        
        # 세션에서 정보 추출
        business_name = session["business_name"]
        business_description = session["business_description"]
        investment_amount = session["investment_amount"]
        
        # 업종 카테고리 추출
        categories_data = session.get("categories", [])
        industry_category = IndustryCategory(categories_data[0]["category_id"]) if categories_data else IndustryCategory.GENERAL_BUSINESS
        
        # 문자열을 객체로 복원
        from .models import AnalysisMethod
        methods = [AnalysisMethod(m) for m in session["methods"]]
        questions = [Question(**q) for q in session["questions"]]
        
        # GPT로 OSD 기반 리스크 보고서 생성
        gpt_report = self.gpt_service.generate_risk_report(
            business_name,
            business_description,
            investment_amount,
            methods,
            questions,
            answer_request.answers,
            industry_category
        )
        
        # 1. 분석 기법별 OSD 리스크 구조화
        method_results = []
        all_osd_scores = []
        
        for result in gpt_report["method_results"]:
            osd_risks = [OSDScore(**osd) for osd in result["osd_risks"]]
            all_osd_scores.extend(osd_risks)
            
            method_results.append(MethodAnalysisResult(
                method=result["method"],
                osd_risks=osd_risks,
                key_findings=result["key_findings"],
                method_specific_insights=result["method_specific_insights"]
            ))
        
        # 2. 종합 리스크 점수 계산 (OSD 엔진 사용)
        overall_risk_score, overall_risk_level, risk_grade = OSDRiskEngine.calculate_overall_risk(all_osd_scores)
        
        # 3. 현금 손실액 분석 (비용 분석 엔진 사용)
        cost_analysis = CostAnalysisEngine.calculate_total_expected_loss(
            all_osd_scores,
            investment_amount,
            industry_category
        )
        
        cash_loss_analysis = CashLossAnalysis(
            total_expected_loss=cost_analysis["total_expected_loss"],
            cost_breakdown=CostBreakdown(**cost_analysis["cost_breakdown"]),
            loss_by_risk=cost_analysis["loss_by_risk"],
            probability_weighted_loss=cost_analysis["probability_weighted_loss"]
        )
        
        # 4. AI 조언 구조화
        ai_recommendations = [
            AIRecommendation(**rec) for rec in gpt_report["ai_recommendations"]
        ]
        
        # 최종 보고서 생성
        final_report = FinalRiskReport(
            session_id=session_id,
            business_name=business_name,
            overall_risk_score=overall_risk_score,
            overall_risk_level=overall_risk_level,
            risk_grade=risk_grade,
            method_results=method_results,
            cash_loss_analysis=cash_loss_analysis,
            ai_recommendations=ai_recommendations,
            executive_summary=gpt_report["executive_summary"],
            created_at=datetime.now().isoformat(),
            analysis_methods_used=[m.value for m in methods]
        )
        
        # 세션 업데이트 (답변 저장)
        self.session_store.update_session(session_id, {
            "answers": [a.dict() for a in answer_request.answers],
            "stage": "report_generated",
            "final_report": final_report.dict()
        })
        
        return final_report

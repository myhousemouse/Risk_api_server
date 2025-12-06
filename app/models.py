from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class IndustryCategory(str, Enum):
    """업종 카테고리"""
    EDUCATION = "education"
    IT_STARTUP = "it_startup"
    MANUFACTURING = "manufacturing"
    MARKETING = "marketing"
    FINANCE = "finance"
    SERVICE = "service"
    PROJECT_MANAGEMENT = "project_management"
    GENERAL_BUSINESS = "general_business"


class AnalysisMethod(str, Enum):
    """분석 기법"""
    # 교육
    LOGIC_MODEL = "Logic Model"
    SMART_GOAL = "SMART Goal"
    
    # IT/스타트업
    LEAN_CANVAS = "Lean Canvas"
    SWOT = "SWOT 분석"
    FIVE_WHY = "5 Why"
    
    # 제조
    FMEA = "FMEA"
    FTA = "FTA"
    HAZOP = "HAZOP"
    
    # 마케팅
    STP = "STP 분석"
    FOUR_P = "4P 분석"
    PORTER_FIVE_FORCES = "Porter 5 Forces"
    
    # 금융
    VAR = "VaR (Value at Risk)"
    MONTE_CARLO = "Monte Carlo Simulation"
    SENSITIVITY_ANALYSIS = "Sensitivity Analysis"
    
    # 서비스
    SERVICE_BLUEPRINT = "Service Blueprint"
    SIPOC = "SIPOC"
    
    # 프로젝트
    RAID_LOG = "RAID Log"
    PERT_CPM = "PERT/CPM"
    RBS = "RBS (Risk Breakdown Structure)"
    
    # 범용
    CJM = "CJM (Customer Journey Map)"


# 1단계: 초기 사업 정보 입력
class InitialBusinessInput(BaseModel):
    """초기 사업 정보"""
    concept: str = Field(..., description="사업 아이디어/컨셉", min_length=1, max_length=2000)


# 1단계 응답: 업종 분류 및 분석 기법 선택
class IndustryCategoryInfo(BaseModel):
    """업종 카테고리 정보"""
    category_id: IndustryCategory
    category_name: str
    confidence_score: float = Field(..., description="매칭 신뢰도 (0~100)", ge=0, le=100)


class InitialAnalysisResponse(BaseModel):
    """초기 분석 응답"""
    session_id: str = Field(..., description="세션 ID")
    selected_methods: List[AnalysisMethod] = Field(..., description="선택된 분석 기법 (2개)")


# 3단계: 질문 생성 요청
class QuestionGenerationRequest(BaseModel):
    """질문 생성 요청"""
    session_id: str = Field(..., description="세션 ID")


# 3단계 응답: 생성된 질문들
class Question(BaseModel):
    """개별 질문"""
    question_id: str = Field(..., description="질문 ID (예: method1_q1)")
    method: AnalysisMethod = Field(..., description="해당 분석 기법")
    question_text: str = Field(..., description="질문 내용")
    question_type: str = Field(..., description="답변 유형 (text/number/choice)", pattern="^(text|number|choice)$")
    choices: Optional[List[str]] = Field(None, description="선택형인 경우 선택지")


class QuestionGenerationResponse(BaseModel):
    """질문 생성 응답"""
    session_id: str
    questions: List[Question] = Field(..., description="생성된 질문 목록 (10~20개)")
    total_questions: int


# 4단계: 사용자 답변 제출
class Answer(BaseModel):
    """개별 답변"""
    question_id: str
    answer: str = Field(..., description="사용자의 답변")


class AnswerSubmissionRequest(BaseModel):
    """답변 제출 요청"""
    session_id: str
    answers: List[Answer]


# 5단계 응답: 최종 리스크 보고서
class OSDScore(BaseModel):
    """OSD 기반 리스크 측정"""
    occurrence: int = Field(..., description="발생 가능성 (1~10)", ge=1, le=10)
    severity: int = Field(..., description="심각도 (1~10)", ge=1, le=10)
    detection: int = Field(..., description="발견 가능성 (1~10, 낮을수록 발견 어려움)", ge=1, le=10)
    risk_score: int = Field(..., description="리스크 점수 (O×S×D, 1~1000)", ge=1, le=1000)
    description: str = Field(..., description="리스크 설명")


class CostBreakdown(BaseModel):
    """비용 구성 요소"""
    capex: float = Field(..., description="초기 투자비 (CAPEX)")
    opex: float = Field(..., description="운영비 (OPEX)")
    risk_impact_cost: float = Field(..., description="리스크 영향 비용")
    details: Dict[str, float] = Field(..., description="상세 비용 항목")


class CashLossAnalysis(BaseModel):
    """현금 손실액 분석"""
    total_expected_loss: float = Field(..., description="총 예상 손실액 (원)")
    cost_breakdown: CostBreakdown = Field(..., description="비용 구성")
    loss_by_risk: List[Dict[str, Any]] = Field(..., description="리스크별 손실액")
    probability_weighted_loss: float = Field(..., description="확률 가중 손실액")


class AIRecommendation(BaseModel):
    """AI 조언"""
    category: str = Field(..., description="조언 카테고리")
    priority: str = Field(..., description="우선순위 (높음/중간/낮음)")
    action: str = Field(..., description="권장 액션")
    expected_impact: str = Field(..., description="예상 효과")
    implementation_difficulty: str = Field(..., description="구현 난이도 (쉬움/보통/어려움)")


class MethodAnalysisResult(BaseModel):
    """분석 기법별 결과"""
    method: AnalysisMethod
    osd_risks: List[OSDScore] = Field(..., description="OSD 기반 리스크 목록")
    key_findings: List[str] = Field(..., description="주요 발견사항")
    method_specific_insights: str = Field(..., description="분석 기법별 인사이트")


class FinalRiskReport(BaseModel):
    """최종 리스크 보고서"""
    session_id: str
    business_name: str
    
    # 1. 리스크 위험도 측정
    overall_risk_score: float = Field(..., description="종합 리스크 점수 (0~100점, 높을수록 위험)", ge=0, le=100)
    overall_risk_level: str = Field(..., description="종합 위험 수준 (낮음/중간/높음/매우높음)")
    risk_grade: str = Field(..., description="리스크 등급 (A~F)")
    method_results: List[MethodAnalysisResult] = Field(..., description="분석 기법별 상세 결과")
    
    # 2. 현금 손실액 측정 (투자금액이 입력된 경우만)
    cash_loss_analysis: Optional[CashLossAnalysis] = Field(None, description="현금 손실액 분석 (투자금액 입력 시)")
    
    # 3. AI 조언 요약
    ai_recommendations: List[AIRecommendation] = Field(..., description="AI 조언 목록 (우선순위별)")
    executive_summary: str = Field(..., description="경영진 요약")
    
    # 메타 정보
    created_at: str
    analysis_methods_used: List[str] = Field(..., description="사용된 분석 기법")


# 헬스체크
class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str
    version: str
    timestamp: str

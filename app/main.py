from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from .models import (
    InitialBusinessInput,
    InitialAnalysisResponse,
    QuestionGenerationRequest,
    QuestionGenerationResponse,
    AnswerSubmissionRequest,
    FinalRiskReport,
    HealthResponse
)
from .service import RiskAnalysisService, SessionStore
from .gpt_service import GPTService
from .config import settings


# FastAPI 앱 생성
app = FastAPI(
    title="Risk Manager API",
    description="사업 시작 전 리스크를 수치적으로 분석해주는 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
session_store = SessionStore()
gpt_service = GPTService(api_key=settings.openai_api_key)
risk_service = RiskAnalysisService(gpt_service, session_store)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Risk Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "openai_configured": bool(settings.openai_api_key),
        "environment": settings.environment
    }


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """헬스체크"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/v1/analyze/initial", response_model=InitialAnalysisResponse)
async def analyze_initial_business(business_input: InitialBusinessInput):
    """
    1단계: 초기 사업 정보 분석
    
    - 사용자가 사업명, 사업 내용, 투자금액을 입력
    - 시스템이 업종을 분류하고 적합한 분석 기법 2개를 선택
    """
    try:
        result = risk_service.analyze_initial_business(business_input)
        return result
    except ValueError as e:
        # 입력 검증 실패 (비즈니스 아이디어가 아님)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")


@app.post("/api/v1/analyze/questions", response_model=QuestionGenerationResponse)
async def generate_questions(request: QuestionGenerationRequest):
    """
    3단계: 맞춤형 질문 생성
    
    - 선택된 분석 기법에 따라 GPT가 10~20개의 질문을 생성
    """
    try:
        result = risk_service.generate_questions(request.session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"질문 생성 중 오류가 발생했습니다: {str(e)}")


@app.post("/api/v1/analyze/report", response_model=FinalRiskReport)
async def generate_risk_report(answer_request: AnswerSubmissionRequest):
    """
    5단계: 최종 리스크 보고서 생성
    
    - 사용자의 답변을 분석하여 종합 리스크 보고서 생성
    """
    try:
        result = risk_service.generate_final_report(answer_request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}")


@app.get("/api/v1/session/{session_id}")
async def get_session_info(session_id: str):
    """
    세션 정보 조회 (디버깅/개발용)
    """
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    return {
        "session_id": session_id,
        "stage": session.get("stage"),
        "business_name": session.get("business_name"),
        "created_at": session.get("created_at")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )

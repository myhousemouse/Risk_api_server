# Risk Manager API Server

초보 창업자를 위한 사업 리스크 분석 API 서버 (Google Gemini AI 기반)

## 주요 특징

- ✨ **Google Gemini AI** 기반 리스크 분석
- 🎯 **업종별 맞춤형 질문** 생성 (IT, 교육, 제조, 서비스 등)
- 📊 **OSD 방법론** (Occurrence × Severity × Detection)
- 🚀 **초보 창업자 친화적** 용어 및 질문

## 워크플로우

### 1단계: 초기 사업 정보 입력
사용자가 사업명, 사업 설명, 투자금액을 입력

**요청 예시:**
```json
{
  "businessName": "대학생 중고 교재 플랫폼",
  "businessDescription": "대학생들이 중고 교재를 사고팔 수 있는 모바일 앱",
  "investmentAmount": 50000000
}
```

### 2단계: 업종 분류 및 분석 기법 선택
AI가 업종을 자동 분류하고 최적의 분석 기법 2개를 선택 (SWOT, Lean Canvas 등)

**응답 예시:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "matched_categories": [
    {
      "category_id": "it_startup",
      "category_name": "IT/스타트업",
      "confidence_score": 95.0
    }
  ],
  "selected_methods": ["Lean Canvas", "SWOT"],
  "reasoning": "IT/스타트업 업종으로 분류되어 Lean Canvas과 SWOT 분석 기법이 선택되었습니다."
}
```

### 3단계: 업종별 맞춤 질문 생성 (총 5개)
선택된 분석 기법별로 **구체적이고 실행 가능한** 질문 생성
- IT/앱: 개발자, 경쟁 앱, 예상 사용자 수 등
- 교육: 강사, 수강료, 학습 결과 등
- 제조: 설비, 생산량, 불량률 등
- 서비스/외식: 위치, 유동인구, 원가율 등

### 4단계: 사용자 답변 수집
생성된 질문에 대한 답변 수집

### 5단계: OSD 기반 리스크 보고서 생성
- **발생가능성(O)**, **심각도(S)**, **발견가능성(D)** 기반 정량 평가
- AI 기반 우선순위별 개선 조언
- 경영진 요약

## 설치 및 실행

```bash
# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 GEMINI_API_KEY 입력

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 엔드포인트

### 초기 분석
**POST** `/api/v1/analyze/initial`

**Request:**
```json
{
  "businessName": "사업명",
  "businessDescription": "사업 설명",
  "investmentAmount": 50000000
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "matched_categories": [
    {
      "category_id": "it_startup",
      "category_name": "IT/스타트업",
      "confidence_score": 95.0
    }
  ],
  "selected_methods": ["Method1", "Method2"],
  "reasoning": "선택 이유"
}
```

### 질문 생성
**POST** `/api/v1/analyze/questions`

### 리스크 보고서
**POST** `/api/v1/analyze/report`

### 헬스체크
**GET** `/api/v1/health`

## 기술 스택

- **AI**: Google Gemini API (gemini-2.5-flash)
- **Framework**: FastAPI
- **Deployment**: Zeabur
- **Language**: Python 3.13+

## 배포 URL

- Production: https://ebizapi.zeabur.app
- API Docs: https://ebizapi.zeabur.app/docs

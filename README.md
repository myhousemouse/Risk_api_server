# Risk Manager API Server

사업 시작 전 리스크를 수치적으로 분석해주는 API 서버

## 워크플로우

### 1단계: 초기 사업 정보 입력
사용자가 사업명, 사업 내용, 투자금액을 입력

### 2단계: 업종 분류 및 분석 기법 선택
8개 카테고리 중 적합한 업종을 AI가 분류하고 최적의 분석 기법 2개 선택

### 3단계: 맞춤형 질문 생성
선택된 분석 기법별로 5~10개의 질문을 GPT API가 생성

### 4단계: 사용자 답변 수집
생성된 질문에 대한 사용자의 답변 수집

### 5단계: 종합 리스크 보고서 생성
모든 데이터를 기반으로 최종 리스크 분석 보고서 생성

## 설치 및 실행

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 입력

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

## API 엔드포인트

- `POST /api/v1/analyze/initial` - 1단계: 초기 사업 정보 분석
- `POST /api/v1/analyze/questions` - 3단계: 맞춤형 질문 생성
- `POST /api/v1/analyze/report` - 5단계: 최종 리스크 보고서 생성
- `GET /api/v1/health` - 헬스체크

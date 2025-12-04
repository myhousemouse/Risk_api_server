# Zeabur 배포 가이드

## 1. 필수 환경 변수 설정

Zeabur 대시보드에서 다음 환경 변수를 설정하세요:

```
GEMINI_API_KEY=your-actual-gemini-api-key
ENVIRONMENT=production
PORT=8000
```

## 2. 자동 배포 설정

이 프로젝트는 다음 파일들로 Zeabur에서 자동으로 인식됩니다:

- `requirements.txt` - Python 의존성
- `zbpack.json` - Zeabur 빌드 설정
- `app/main.py` - FastAPI 진입점

## 3. zbpack.json 설정 내용

```json
{
  "python": {
    "entry": "app/main.py"
  },
  "start_command": "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
}
```

## 4. 배포 단계

1. GitHub에 코드 푸시
2. Zeabur에서 새 프로젝트 생성
3. GitHub 저장소 연결
4. 환경 변수 설정 (GEMINI_API_KEY 필수)
5. 자동 배포 시작

## 5. 배포 후 확인

배포가 완료되면 다음 엔드포인트를 확인하세요:

- `GET /` - 기본 정보
- `GET /docs` - Swagger UI (API 문서)
- `GET /api/v1/health` - 헬스체크

## 6. API 엔드포인트

- `POST /api/v1/analyze/initial` - 비즈니스 아이디어 분석
- `POST /api/v1/analyze/questions` - 맞춤형 질문 생성
- `POST /api/v1/analyze/report` - 최종 리스크 보고서

## 7. 주의사항

- GEMINI_API_KEY는 반드시 설정해야 합니다
- .env 파일은 Git에 포함되지 않습니다 (.gitignore 설정됨)
- 프로덕션 환경에서는 CORS 설정을 제한하는 것을 권장합니다

## 8. Gemini API 키 발급 방법

1. https://aistudio.google.com/app/apikey 접속
2. "Create API Key" 클릭
3. 발급된 API 키를 복사
4. Zeabur 환경 변수에 `GEMINI_API_KEY`로 설정

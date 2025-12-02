from typing import Dict, List
from .models import IndustryCategory, AnalysisMethod


# 업종별 분석 기법 매핑
INDUSTRY_METHODS: Dict[IndustryCategory, List[AnalysisMethod]] = {
    IndustryCategory.EDUCATION: [
        AnalysisMethod.LOGIC_MODEL,
        AnalysisMethod.SMART_GOAL,
        AnalysisMethod.CJM,
    ],
    IndustryCategory.IT_STARTUP: [
        AnalysisMethod.LEAN_CANVAS,
        AnalysisMethod.SWOT,
        AnalysisMethod.CJM,
        AnalysisMethod.FIVE_WHY,
    ],
    IndustryCategory.MANUFACTURING: [
        AnalysisMethod.FMEA,
        AnalysisMethod.FTA,
        AnalysisMethod.HAZOP,
    ],
    IndustryCategory.MARKETING: [
        AnalysisMethod.STP,
        AnalysisMethod.FOUR_P,
        AnalysisMethod.PORTER_FIVE_FORCES,
        AnalysisMethod.SWOT,
    ],
    IndustryCategory.FINANCE: [
        AnalysisMethod.VAR,
        AnalysisMethod.MONTE_CARLO,
        AnalysisMethod.SENSITIVITY_ANALYSIS,
    ],
    IndustryCategory.SERVICE: [
        AnalysisMethod.SERVICE_BLUEPRINT,
        AnalysisMethod.SIPOC,
        AnalysisMethod.CJM,
    ],
    IndustryCategory.PROJECT_MANAGEMENT: [
        AnalysisMethod.RAID_LOG,
        AnalysisMethod.PERT_CPM,
        AnalysisMethod.RBS,
    ],
    IndustryCategory.GENERAL_BUSINESS: [
        AnalysisMethod.SWOT,
        AnalysisMethod.LEAN_CANVAS,
        AnalysisMethod.CJM,
    ],
}


# 업종 카테고리 한글명
INDUSTRY_NAMES: Dict[IndustryCategory, str] = {
    IndustryCategory.EDUCATION: "교육 / 학습 / 에듀테크",
    IndustryCategory.IT_STARTUP: "IT / 앱 / 소프트웨어 / 스타트업",
    IndustryCategory.MANUFACTURING: "제조 / 공장 / 설비 / 하드웨어",
    IndustryCategory.MARKETING: "마케팅 / 광고 / 브랜딩 / 소비재",
    IndustryCategory.FINANCE: "금융 / 투자 / 재무",
    IndustryCategory.SERVICE: "서비스업 / 외식 / 프랜차이즈 / 숙박",
    IndustryCategory.PROJECT_MANAGEMENT: "프로젝트 / 건설 / 공공사업 / 인프라",
    IndustryCategory.GENERAL_BUSINESS: "기타 / 범용 비즈니스 / 아직 모르겠음",
}


# 업종 카테고리 키워드
INDUSTRY_KEYWORDS: Dict[IndustryCategory, List[str]] = {
    IndustryCategory.EDUCATION: [
        "교육", "학습", "에듀테크", "강의", "온라인 강좌", "학원", "교육 콘텐츠",
        "이러닝", "학생", "교사", "교육 플랫폼", "교육용", "학습 관리"
    ],
    IndustryCategory.IT_STARTUP: [
        "앱", "애플리케이션", "소프트웨어", "플랫폼", "SaaS", "모바일", "웹",
        "스타트업", "IT", "기술", "개발", "서비스 개발", "디지털", "온라인 서비스"
    ],
    IndustryCategory.MANUFACTURING: [
        "제조", "생산", "공장", "설비", "하드웨어", "제품 생산", "생산라인",
        "제조업", "공정", "조립", "기계", "제작", "양산"
    ],
    IndustryCategory.MARKETING: [
        "마케팅", "광고", "브랜드", "브랜딩", "홍보", "프로모션", "캠페인",
        "소비재", "B2C", "고객 유치", "브랜드 인지도", "마케팅 전략"
    ],
    IndustryCategory.FINANCE: [
        "금융", "투자", "재무", "펀드", "자산 운용", "주식", "채권", "대출",
        "핀테크", "금융 상품", "포트폴리오", "리스크 관리", "자산 관리"
    ],
    IndustryCategory.SERVICE: [
        "서비스", "외식", "음식점", "레스토랑", "카페", "프랜차이즈", "숙박",
        "호텔", "게스트하우스", "고객 서비스", "오프라인 매장", "점포"
    ],
    IndustryCategory.PROJECT_MANAGEMENT: [
        "프로젝트", "건설", "공공사업", "인프라", "시공", "공사", "토목",
        "대형 프로젝트", "건축", "사회기반시설", "정부 발주", "공공 입찰"
    ],
}


# 분석 기법 설명
METHOD_DESCRIPTIONS: Dict[AnalysisMethod, str] = {
    AnalysisMethod.LOGIC_MODEL: "교육 성과를 Input→Outcome 구조로 분석",
    AnalysisMethod.SMART_GOAL: "교육/학습 목표가 현실적인지 평가",
    AnalysisMethod.LEAN_CANVAS: "스타트업 BM 전체 리스크를 한 장에 구조화",
    AnalysisMethod.SWOT: "내부·외부 요인을 빠르게 분석",
    AnalysisMethod.CJM: "사용자 여정 분석 (유입→사용→이탈 지점 찾기)",
    AnalysisMethod.FIVE_WHY: "문제·버그의 근본 원인 분석",
    AnalysisMethod.FMEA: "고장·불량 리스크를 정량화 (O/S/D)",
    AnalysisMethod.FTA: "고장의 근본 원인을 트리 형태로 추적",
    AnalysisMethod.HAZOP: "공정/작업 환경의 위험요인 분석",
    AnalysisMethod.STP: "시장·타겟·포지셔닝 구조화",
    AnalysisMethod.FOUR_P: "제품·가격·유통·프로모션 점검",
    AnalysisMethod.PORTER_FIVE_FORCES: "시장 경쟁 강도 분석",
    AnalysisMethod.VAR: "손실 리스크를 확률적으로 계산",
    AnalysisMethod.MONTE_CARLO: "변수 변동을 시뮬레이션하여 리스크 측정",
    AnalysisMethod.SENSITIVITY_ANALYSIS: "이익이 변수 변화에 얼마나 민감한지 분석",
    AnalysisMethod.SERVICE_BLUEPRINT: "고객 경험 + 백오피스 프로세스를 동시에 분석",
    AnalysisMethod.SIPOC: "서비스 프로세스를 전체 흐름으로 시각화",
    AnalysisMethod.RAID_LOG: "리스크·이슈·가정·의존성을 구조적으로 관리",
    AnalysisMethod.PERT_CPM: "일정 지연 리스크 및 크리티컬 경로 계산",
    AnalysisMethod.RBS: "대형 프로젝트 리스크를 구조적 분류",
}

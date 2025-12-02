"""
OSD (Occurrence × Severity × Detection) 기반 리스크 계산 엔진
"""
from typing import List, Dict, Any, Tuple
from .models import IndustryCategory, AnalysisMethod, OSDScore


class OSDRiskEngine:
    """OSD 기반 리스크 측정 엔진"""
    
    # 업종별 보정 계수
    INDUSTRY_CORRECTION = {
        IndustryCategory.IT_STARTUP: {"O": 1.2, "S": 1.1, "D": 0.9},  # 높은 변동성
        IndustryCategory.EDUCATION: {"O": 0.9, "S": 1.0, "D": 1.1},
        IndustryCategory.MANUFACTURING: {"O": 1.0, "S": 1.3, "D": 1.0},  # 높은 심각도
        IndustryCategory.MARKETING: {"O": 1.1, "S": 0.9, "D": 1.0},
        IndustryCategory.FINANCE: {"O": 0.8, "S": 1.5, "D": 1.2},  # 낮은 발생률, 높은 심각도
        IndustryCategory.SERVICE: {"O": 1.0, "S": 1.0, "D": 1.0},
        IndustryCategory.PROJECT_MANAGEMENT: {"O": 1.1, "S": 1.2, "D": 0.9},
        IndustryCategory.GENERAL_BUSINESS: {"O": 1.0, "S": 1.0, "D": 1.0},
    }
    
    @staticmethod
    def calculate_osd_score(occurrence: int, severity: int, detection: int) -> int:
        """
        OSD 리스크 점수 계산
        
        Args:
            occurrence: 발생 가능성 (1~10)
            severity: 심각도 (1~10)
            detection: 발견 가능성 (1~10, 낮을수록 발견 어려움)
            
        Returns:
            int: 리스크 점수 (1~1000)
        """
        return occurrence * severity * detection
    
    @staticmethod
    def get_risk_level(risk_score: int) -> str:
        """
        리스크 점수를 수준으로 변환
        
        Args:
            risk_score: OSD 리스크 점수 (1~1000)
            
        Returns:
            str: 위험 수준
        """
        if risk_score < 100:
            return "낮음"
        elif risk_score < 300:
            return "중간"
        elif risk_score < 600:
            return "높음"
        else:
            return "매우높음"
    
    @staticmethod
    def get_risk_grade(risk_score: int) -> str:
        """
        리스크 점수를 등급으로 변환
        
        Args:
            risk_score: OSD 리스크 점수 (1~1000)
            
        Returns:
            str: 리스크 등급 (A~F)
        """
        if risk_score < 50:
            return "A"
        elif risk_score < 100:
            return "B"
        elif risk_score < 200:
            return "C"
        elif risk_score < 400:
            return "D"
        elif risk_score < 700:
            return "E"
        else:
            return "F"
    
    @staticmethod
    def apply_industry_correction(
        osd_values: Dict[str, int],
        industry: IndustryCategory
    ) -> Dict[str, float]:
        """
        업종별 보정치 적용
        
        Args:
            osd_values: {"O": 7, "S": 8, "D": 6} 형태
            industry: 업종 카테고리
            
        Returns:
            Dict: 보정된 OSD 값
        """
        correction = OSDRiskEngine.INDUSTRY_CORRECTION.get(
            industry, 
            {"O": 1.0, "S": 1.0, "D": 1.0}
        )
        
        corrected = {
            "O": min(10, round(osd_values["O"] * correction["O"])),
            "S": min(10, round(osd_values["S"] * correction["S"])),
            "D": min(10, round(osd_values["D"] * correction["D"]))
        }
        
        return corrected
    
    @staticmethod
    def calculate_overall_risk(osd_scores: List[OSDScore]) -> Tuple[float, str, str]:
        """
        전체 리스크 점수 계산 (100점 만점으로 환산)
        
        Args:
            osd_scores: OSD 리스크 목록
            
        Returns:
            Tuple[float, str, str]: (평균 리스크 점수 0~100, 위험 수준, 등급)
        """
        if not osd_scores:
            return 0.0, "낮음", "A"
        
        # 가중 평균 (상위 리스크에 더 높은 가중치)
        sorted_scores = sorted([r.risk_score for r in osd_scores], reverse=True)
        
        if len(sorted_scores) == 1:
            avg_score_osd = sorted_scores[0]
        else:
            # 상위 3개에 더 높은 가중치
            weights = [0.4, 0.3, 0.2] + [0.1 / max(1, len(sorted_scores) - 3)] * (len(sorted_scores) - 3)
            weights = weights[:len(sorted_scores)]
            avg_score_osd = sum(s * w for s, w in zip(sorted_scores, weights))
        
        # OSD 점수(1~1000)를 100점 만점으로 환산
        # 1000점 = 100점, 비례식 적용
        avg_score_100 = (avg_score_osd / 1000) * 100
        
        # 기존 level/grade 계산은 OSD 원점수 기준 유지
        level = OSDRiskEngine.get_risk_level(int(avg_score_osd))
        grade = OSDRiskEngine.get_risk_grade(int(avg_score_osd))
        
        return round(avg_score_100, 2), level, grade


class CostAnalysisEngine:
    """현금 손실액 계산 엔진"""
    
    # 업종별 기본 비용 비율
    INDUSTRY_COST_STRUCTURE = {
        IndustryCategory.IT_STARTUP: {
            "개발비": 0.4,
            "디자인비": 0.1,
            "PM비용": 0.1,
            "서버비": 0.1,
            "마케팅비": 0.2,
            "기타": 0.1
        },
        IndustryCategory.EDUCATION: {
            "콘텐츠_제작비": 0.3,
            "강사비": 0.25,
            "플랫폼_운영비": 0.15,
            "마케팅비": 0.2,
            "기타": 0.1
        },
        IndustryCategory.MANUFACTURING: {
            "설비비": 0.3,
            "재료비": 0.25,
            "인건비": 0.2,
            "유지보수비": 0.15,
            "기타": 0.1
        },
        IndustryCategory.SERVICE: {
            "임대료": 0.25,
            "인건비": 0.3,
            "원재료비": 0.2,
            "마케팅비": 0.15,
            "기타": 0.1
        },
        IndustryCategory.MARKETING: {
            "광고비": 0.4,
            "크리에이티브_제작비": 0.2,
            "인건비": 0.2,
            "도구_라이선스": 0.1,
            "기타": 0.1
        },
        IndustryCategory.FINANCE: {
            "시스템_구축비": 0.3,
            "인건비": 0.25,
            "규제_대응비": 0.2,
            "보안비": 0.15,
            "기타": 0.1
        },
        IndustryCategory.PROJECT_MANAGEMENT: {
            "인건비": 0.35,
            "장비_임대료": 0.25,
            "재료비": 0.2,
            "관리비": 0.1,
            "기타": 0.1
        },
        IndustryCategory.GENERAL_BUSINESS: {
            "인건비": 0.3,
            "운영비": 0.25,
            "마케팅비": 0.2,
            "시스템비": 0.15,
            "기타": 0.1
        }
    }
    
    @staticmethod
    def estimate_cost_breakdown(
        investment_amount: int,
        industry: IndustryCategory
    ) -> Dict[str, float]:
        """
        투자금액을 업종별 비용 항목으로 분해
        
        Args:
            investment_amount: 총 투자 금액
            industry: 업종
            
        Returns:
            Dict: 비용 항목별 금액
        """
        structure = CostAnalysisEngine.INDUSTRY_COST_STRUCTURE.get(
            industry,
            CostAnalysisEngine.INDUSTRY_COST_STRUCTURE[IndustryCategory.GENERAL_BUSINESS]
        )
        
        breakdown = {}
        for category, ratio in structure.items():
            breakdown[category] = investment_amount * ratio
        
        return breakdown
    
    @staticmethod
    def calculate_risk_impact_cost(
        osd_score: OSDScore,
        total_investment: int
    ) -> float:
        """
        개별 리스크의 영향 비용 계산
        
        Args:
            osd_score: OSD 리스크
            total_investment: 총 투자액
            
        Returns:
            float: 해당 리스크로 인한 예상 손실액
        """
        # 리스크 점수를 확률로 변환 (0~1)
        probability = min(1.0, osd_score.risk_score / 1000.0)
        
        # 심각도에 따른 영향 비율
        severity_impact = {
            range(1, 4): 0.1,    # 낮은 심각도: 10% 영향
            range(4, 7): 0.3,    # 중간 심각도: 30% 영향
            range(7, 11): 0.6    # 높은 심각도: 60% 영향
        }
        
        impact_ratio = 0.3  # 기본값
        for range_obj, ratio in severity_impact.items():
            if osd_score.severity in range_obj:
                impact_ratio = ratio
                break
        
        # 예상 손실 = 확률 × 영향 비율 × 총 투자액
        expected_loss = probability * impact_ratio * total_investment
        
        return expected_loss
    
    @staticmethod
    def calculate_total_expected_loss(
        osd_scores: List[OSDScore],
        investment_amount: int,
        industry: IndustryCategory
    ) -> Dict[str, Any]:
        """
        총 예상 손실액 계산
        
        Args:
            osd_scores: OSD 리스크 목록
            investment_amount: 투자 금액
            industry: 업종
            
        Returns:
            Dict: 손실액 분석 결과
        """
        # 비용 구성
        cost_details = CostAnalysisEngine.estimate_cost_breakdown(
            investment_amount,
            industry
        )
        
        # CAPEX/OPEX 분류 (간단히 6:4 비율로)
        capex = investment_amount * 0.6
        opex = investment_amount * 0.4
        
        # 각 리스크별 손실액 계산
        loss_by_risk = []
        total_risk_cost = 0
        
        for osd in osd_scores:
            risk_cost = CostAnalysisEngine.calculate_risk_impact_cost(
                osd,
                investment_amount
            )
            total_risk_cost += risk_cost
            
            loss_by_risk.append({
                "risk_description": osd.description,
                "osd_score": osd.risk_score,
                "probability": min(1.0, osd.risk_score / 1000.0),
                "expected_loss": risk_cost
            })
        
        # 확률 가중 총 손실액
        probability_weighted_loss = sum(item["expected_loss"] for item in loss_by_risk)
        
        return {
            "total_expected_loss": probability_weighted_loss,
            "cost_breakdown": {
                "capex": capex,
                "opex": opex,
                "risk_impact_cost": total_risk_cost,
                "details": cost_details
            },
            "loss_by_risk": loss_by_risk,
            "probability_weighted_loss": probability_weighted_loss
        }

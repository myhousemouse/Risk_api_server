from typing import List, Tuple
from .models import IndustryCategory, AnalysisMethod, IndustryCategoryInfo
from .constants import INDUSTRY_KEYWORDS, INDUSTRY_METHODS, INDUSTRY_NAMES


class IndustryClassifier:
    """업종 분류 로직"""
    
    @staticmethod
    def classify_business(business_description: str) -> List[IndustryCategoryInfo]:
        """
        사업 내용을 분석하여 적합한 업종 카테고리를 분류
        
        Args:
            business_description: 사업 내용 설명
            
        Returns:
            List[IndustryCategoryInfo]: 매칭된 업종 카테고리 (최대 2개, 신뢰도 순)
        """
        description_lower = business_description.lower()
        scores = {}
        
        # 각 업종별 키워드 매칭 점수 계산
        for category, keywords in INDUSTRY_KEYWORDS.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                # 신뢰도 계산 (매칭된 키워드 수 기반)
                confidence = min(score * 15, 95)  # 최대 95%
                scores[category] = {
                    'confidence': confidence,
                    'matched_keywords': matched_keywords
                }
        
        # 매칭된 카테고리가 없으면 범용 비즈니스로 분류
        if not scores:
            scores[IndustryCategory.GENERAL_BUSINESS] = {
                'confidence': 50,
                'matched_keywords': []
            }
        
        # 신뢰도 순으로 정렬하여 상위 2개 선택
        sorted_categories = sorted(
            scores.items(), 
            key=lambda x: x[1]['confidence'], 
            reverse=True
        )[:2]
        
        result = []
        for category, data in sorted_categories:
            result.append(IndustryCategoryInfo(
                category_id=category,
                category_name=INDUSTRY_NAMES[category],
                confidence_score=data['confidence']
            ))
        
        return result
    
    @staticmethod
    def select_analysis_methods(
        categories: List[IndustryCategoryInfo]
    ) -> List[AnalysisMethod]:
        """
        분류된 업종에 따라 최적의 분석 기법 2개 선택
        
        Args:
            categories: 분류된 업종 카테고리들
            
        Returns:
            List[AnalysisMethod]: 선택된 분석 기법 정확히 2개
        """
        selected = []
        
        if not categories:
            # 카테고리가 없으면 범용 기법 반환
            return [AnalysisMethod.SWOT, AnalysisMethod.LEAN_CANVAS]
        
        # 첫 번째 카테고리의 대표 기법 선택
        first_category_methods = INDUSTRY_METHODS.get(categories[0].category_id, [])
        if first_category_methods:
            selected.append(first_category_methods[0])
        
        # 두 번째 기법 선택
        if len(categories) > 1:
            # 두 번째 카테고리가 있으면 그 카테고리의 대표 기법 선택
            second_category_methods = INDUSTRY_METHODS.get(categories[1].category_id, [])
            for method in second_category_methods:
                if method not in selected:
                    selected.append(method)
                    break
        else:
            # 카테고리가 1개만 있으면 해당 카테고리의 두 번째 기법 선택
            if len(first_category_methods) > 1:
                selected.append(first_category_methods[1])
        
        # 아직 2개가 안 되면 첫 번째 카테고리의 나머지 기법에서 선택
        if len(selected) < 2 and first_category_methods:
            for method in first_category_methods:
                if method not in selected:
                    selected.append(method)
                    if len(selected) == 2:
                        break
        
        # 그래도 부족하면 범용 기법 추가
        if len(selected) < 2:
            fallback_methods = [
                AnalysisMethod.SWOT, 
                AnalysisMethod.LEAN_CANVAS,
                AnalysisMethod.CJM
            ]
            for method in fallback_methods:
                if method not in selected:
                    selected.append(method)
                    if len(selected) == 2:
                        break
        
        # 정확히 2개만 반환 (안전장치)
        return selected[:2] if len(selected) >= 2 else selected + [AnalysisMethod.SWOT, AnalysisMethod.LEAN_CANVAS][:2-len(selected)]
    
    @staticmethod
    def generate_classification_reasoning(
        business_description: str,
        categories: List[IndustryCategoryInfo],
        methods: List[AnalysisMethod]
    ) -> str:
        """
        분류 근거 설명 생성
        
        Args:
            business_description: 사업 내용
            categories: 분류된 카테고리
            methods: 선택된 분석 기법
            
        Returns:
            str: 분류 근거 설명
        """
        reasoning_parts = []
        
        # 업종 분류 근거
        if len(categories) == 1:
            reasoning_parts.append(
                f"귀하의 사업은 '{categories[0].category_name}' 업종으로 분류되었습니다 "
                f"(신뢰도: {categories[0].confidence_score:.0f}%)."
            )
        else:
            reasoning_parts.append(
                f"귀하의 사업은 '{categories[0].category_name}'과(와) "
                f"'{categories[1].category_name}'의 융합 업종으로 분류되었습니다."
            )
        
        # 선택된 분석 기법 설명
        method_names = [method.value for method in methods]
        reasoning_parts.append(
            f"\n\n이에 따라 {', '.join(method_names)} 기법을 사용하여 "
            f"리스크를 분석합니다."
        )
        
        # 각 기법이 왜 선택되었는지 간단히 설명
        from .constants import METHOD_DESCRIPTIONS
        reasoning_parts.append("\n\n선택된 분석 기법:")
        for i, method in enumerate(methods, 1):
            description = METHOD_DESCRIPTIONS.get(method, "")
            reasoning_parts.append(f"\n{i}. {method.value}: {description}")
        
        return "".join(reasoning_parts)

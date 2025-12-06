import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from .models import AnalysisMethod, Question, Answer
from .constants import METHOD_DESCRIPTIONS


class GPTService:
    """Google Gemini API 연동 서비스"""
    
    def __init__(self, api_key: str = None):
        """
        Args:
            api_key: Google Gemini API 키 (없으면 환경변수에서 읽음)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=self.api_key)
        
        # Safety settings - 비즈니스 분석 내용이 차단되지 않도록 설정
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings=self.safety_settings
        )
    
    def validate_business_input(self, business_description: str) -> Dict[str, Any]:
        """
        1차 입력 검증: 비즈니스 아이디어인지 확인
        
        Args:
            business_description: 사용자가 입력한 사업 설명
            
        Returns:
            Dict: {"is_valid": bool, "message": str, "suggestion": str}
        """
        prompt = f"""
당신은 비즈니스 아이디어 검증 전문가입니다.

사용자 입력: "{business_description}"

위 입력이 비즈니스 아이디어나 사업 계획과 관련된 내용인지 판단해주세요.

**판단 기준:**
- 비즈니스/사업 관련 내용: 제품, 서비스, 창업, 사업 모델, 고객, 시장 등의 키워드 포함
- 관련 없는 내용: 일상 대화, 날씨, 음식, 일반적인 질문 등

**출력 형식 (정확히 이 형식으로만 답변):**
VALID: [YES 또는 NO]
MESSAGE: [사용자에게 보여줄 메시지]
SUGGESTION: [YES인 경우 비워두고, NO인 경우 올바른 입력 예시 제공]

예시 1:
VALID: YES
MESSAGE: 비즈니스 아이디어가 확인되었습니다.
SUGGESTION: 

예시 2:
VALID: NO
MESSAGE: 비즈니스 아이디어를 구체적으로 입력해주세요.
SUGGESTION: 예: '온라인 중고 도서 거래 플랫폼 서비스', 'AI 기반 맞춤형 학습 관리 시스템', '친환경 배달 용기 렌탈 사업'
"""
        
        try:
            full_prompt = f"""당신은 비즈니스 아이디어를 정확하게 검증하는 전문가입니다. 주어진 형식을 엄격히 따라 답변해주세요.

{prompt}"""
            
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.3,
                    'max_output_tokens': 500,
                },
                safety_settings=self.safety_settings
            )
            
            # 안전 필터로 차단된 경우 처리
            if not response.candidates or not response.candidates[0].content.parts:
                print(f"입력 검증 응답이 차단됨: finish_reason={response.candidates[0].finish_reason if response.candidates else 'N/A'}")
                raise Exception("Response blocked by safety filters")
            
            result_text = response.text.strip()
            
            # 응답 파싱
            is_valid = False
            message = "입력을 다시 확인해주세요."
            suggestion = ""
            
            for line in result_text.split('\n'):
                line = line.strip()
                if line.startswith('VALID:'):
                    is_valid = 'YES' in line.upper()
                elif line.startswith('MESSAGE:'):
                    message = line.replace('MESSAGE:', '').strip()
                elif line.startswith('SUGGESTION:'):
                    suggestion = line.replace('SUGGESTION:', '').strip()
            
            return {
                "is_valid": is_valid,
                "message": message,
                "suggestion": suggestion
            }
            
        except Exception as e:
            print(f"GPT API 오류 (입력 검증): {e}")
            # 폴백: 간단한 키워드 검증
            business_keywords = [
                "사업", "창업", "서비스", "제품", "플랫폼", "앱", "웹사이트",
                "고객", "시장", "판매", "유통", "제조", "개발", "솔루션",
                "비즈니스", "스타트업", "기업", "회사", "매출", "수익"
            ]
            
            has_business_keyword = any(keyword in business_description for keyword in business_keywords)
            
            if has_business_keyword or len(business_description) > 20:
                return {
                    "is_valid": True,
                    "message": "비즈니스 아이디어가 확인되었습니다.",
                    "suggestion": ""
                }
            else:
                return {
                    "is_valid": False,
                    "message": "비즈니스 아이디어를 구체적으로 입력해주세요. 예: '온라인 중고 도서 거래 플랫폼', 'AI 기반 학습 관리 시스템'",
                    "suggestion": "사업 아이템, 목표 고객, 제공할 가치를 포함하여 설명해주세요."
                }
    
    def generate_questions(
        self,
        concept: str,
        methods: List[AnalysisMethod]
    ) -> List[Question]:
        """
        선택된 분석 기법에 따라 맞춤형 질문 생성
        
        Args:
            concept: 사업 아이디어/컨셉
            methods: 선택된 분석 기법 (2개)
            
        Returns:
            List[Question]: 생성된 질문 목록 (총 5개)
        """
        questions = []
        
        # 각 분석 기법별로 2~3개씩 질문 생성 (총 5개)
        for i, method in enumerate(methods):
            method_description = METHOD_DESCRIPTIONS.get(method, "")
            
            prompt = self._create_question_generation_prompt(
                concept,
                method,
                method_description
            )
            
            try:
                full_prompt = f"""당신은 비즈니스 리스크 분석 전문가입니다. 사업의 리스크를 파악하기 위한 핵심 질문들을 생성해주세요.

{prompt}"""
                
                response = self.model.generate_content(
                    full_prompt,
                    generation_config={
                        'temperature': 0.7,
                        'max_output_tokens': 2000,
                    },
                    safety_settings=self.safety_settings
                )
                
                # 안전 필터로 차단된 경우 처리
                if not response.candidates or not response.candidates[0].content.parts:
                    print(f"응답이 안전 필터에 차단됨: finish_reason={response.candidates[0].finish_reason if response.candidates else 'N/A'}")
                    raise Exception("Response blocked by safety filters")
                
                # Gemini 응답 파싱
                generated_text = response.text
                method_questions = self._parse_questions_from_gpt_response(
                    generated_text, 
                    method, 
                    f"method{i+1}"
                )
                # 각 기법당 최대 3개로 제한
                method_questions = method_questions[:3]
                questions.extend(method_questions)
                
            except Exception as e:
                print(f"GPT API 오류: {e}")
                # 폴백: 기본 질문 사용
                fallback_questions = self._get_fallback_questions(method, f"method{i+1}")
                questions.extend(fallback_questions[:3])  # 폴백도 최대 3개
        
        # 최종적으로 총 5개로 제한
        return questions[:5]
    
    def _create_question_generation_prompt(
        self,
        concept: str,
        method: AnalysisMethod,
        method_description: str
    ) -> str:
        """질문 생성을 위한 프롬프트 작성"""
        
        # 업종별 맞춤 가이드
        industry_context = self._get_industry_specific_context(concept, method)
        
        return f"""
당신은 창업 컨설턴트입니다.

아래 사업을 분석 중입니다:
"{concept}"

{industry_context}

**중요 규칙:**
1. 위 사업 내용을 반드시 질문에 직접 언급하세요
   예시: "교육 앱" 사업이라면 → "앱에서 제공할 강의는 누가 만드나요?"
   예시: "카페" 사업이라면 → "카페 위치는 어디이며, 하루 예상 손님 수는 몇 명인가요?"

2. 일반적인 질문 절대 금지:
   ❌ "사업의 핵심 목표는 무엇인가요?"
   ❌ "주요 고객층은 누구인가요?"
   ❌ "예상되는 주요 리스크는 무엇인가요?"
   ❌ "해결하려는 핵심 문제는 무엇인가요?"
   이런 질문들은 모든 사업에 다 해당하므로 절대 사용하지 마세요!

3. 정확히 2~3개의 질문만 생성하세요

4. 각 질문은 "{concept}" 사업에만 해당하는 구체적인 내용이어야 합니다

**출력 형식:**
Q1: [질문] | text |
Q2: [질문] | number |
Q3: [질문] | text |

지금 바로 "{concept}" 사업을 위한 구체적인 질문을 만드세요!
"""
    
    def _parse_questions_from_gpt_response(
        self, 
        response_text: str, 
        method: AnalysisMethod,
        method_prefix: str
    ) -> List[Question]:
        """GPT 응답에서 질문 파싱"""
        
        questions = []
        lines = response_text.strip().split('\n')
        
        q_count = 1
        for line in lines:
            line = line.strip()
            if not line or not line.startswith('Q'):
                continue
            
            try:
                # "Q1: 질문 | type | choices" 형식 파싱
                parts = line.split('|')
                
                # 질문 텍스트 추출
                question_part = parts[0].split(':', 1)
                if len(question_part) < 2:
                    continue
                question_text = question_part[1].strip()
                
                # 답변 유형
                question_type = parts[1].strip() if len(parts) > 1 else "text"
                if question_type not in ["text", "number", "choice"]:
                    question_type = "text"
                
                # 선택지
                choices = None
                if len(parts) > 2 and parts[2].strip():
                    choices = [c.strip() for c in parts[2].split(',')]
                
                questions.append(Question(
                    question_id=f"{method_prefix}_q{q_count}",
                    method=method,
                    question_text=question_text,
                    question_type=question_type,
                    choices=choices
                ))
                q_count += 1
                
            except Exception as e:
                print(f"질문 파싱 오류: {e}, line: {line}")
                continue
        
        return questions
    
    def _get_industry_specific_context(self, concept: str, method: AnalysisMethod) -> str:
        """업종별 특화된 질문 가이드 제공"""
        concept_lower = concept.lower()
        
        # 업종 감지
        if any(kw in concept_lower for kw in ["앱", "소프트웨어", "플랫폼", "IT", "개발", "스타트업", "웹", "모바일"]):
            return f"""
이 사업은 IT/앱 분야입니다. 이런 질문을 만드세요:
✅ "{concept}"를 개발할 개발자가 있나요? 몇 명이며 언제 완성되나요?
✅ "{concept}"와 비슷한 앱/서비스가 있나요? 이름이 뭐고 뭐가 다른가요?
✅ 첫 달에 "{concept}"를 사용할 사람이 몇 명 정도 될까요?
"""
        elif any(kw in concept_lower for kw in ["교육", "학습", "강의", "학원", "에듀테크", "교육용"]):
            return f"""
이 사업은 교육 분야입니다. 이런 질문을 만드세요:
✅ "{concept}"에서 가르칠 강사/선생님이 있나요? 몇 명인가요?
✅ "{concept}"의 수강료는 얼마이며, 한 달에 학생이 몇 명 필요한가요?
✅ "{concept}"를 통해 학습하면 어떤 결과가 나오나요? (성적? 자격증?)
"""
        elif any(kw in concept_lower for kw in ["제조", "생산", "공장", "설비", "제품 생산", "양산"]):
            return f"""
이 사업은 제조 분야입니다. 이런 질문을 만드세요:
✅ "{concept}" 제품을 만들 설비(기계)가 있나요? 얼마인가요?
✅ 하루에 "{concept}" 제품을 몇 개 만들 수 있나요?
✅ "{concept}" 제품의 불량률은 몇 %인가요?
"""
        elif any(kw in concept_lower for kw in ["외식", "음식점", "카페", "레스토랑", "서비스", "매장", "가게"]):
            return f"""
이 사업은 서비스/외식 분야입니다. 이런 질문을 만드세요:
✅ "{concept}" 가게 위치는 어디이며, 하루 유동인구는 몇 명인가요?
✅ "{concept}"에서 판매할 제품의 원가는 판매가의 몇 %인가요?
✅ 근처에 "{concept}"와 비슷한 가게가 몇 개 있나요?
"""
        elif any(kw in concept_lower for kw in ["마케팅", "광고", "브랜드", "홍보", "프로모션"]):
            return f"""
이 사업은 마케팅 분야입니다. 이런 질문을 만드세요:
✅ "{concept}"의 타겟 고객은 정확히 누구인가요? (나이, 성별, 직업)
✅ "{concept}" 광고 예산은 얼마이며, 어디에 쓸 건가요?
✅ "{concept}" 효과를 어떻게 측정할 건가요?
"""
        else:
            return f"""
이런 질문을 만드세요:
✅ "{concept}"의 고객은 누구이며, 왜 우리를 선택해야 하나요?
✅ "{concept}"로 한 달에 얼마를 벌 수 있나요?
✅ "{concept}"와 경쟁하는 업체는 어디인가요?
"""
    
    def _get_fallback_questions(
        self, 
        method: AnalysisMethod,
        method_prefix: str
    ) -> List[Question]:
        """GPT API 실패 시 사용할 기본 질문"""
        
        # 각 분석 기법별 기본 질문
        fallback_map = {
            AnalysisMethod.SWOT: [
                "우리 사업의 가장 큰 강점은 무엇인가요?",
                "우리 사업의 주요 약점은 무엇인가요?",
                "시장에서 어떤 기회를 포착하고 있나요?",
                "가장 큰 위협 요소는 무엇인가요?",
                "경쟁사 대비 우리의 차별점은 무엇인가요?"
            ],
            AnalysisMethod.LEAN_CANVAS: [
                "해결하려는 고객의 핵심 문제는 무엇인가요?",
                "목표 고객 세그먼트는 누구인가요?",
                "제공하는 고유한 가치는 무엇인가요?",
                "주요 수익원은 무엇인가요?",
                "핵심 비용 구조는 어떻게 되나요?"
            ]
        }
        
        default_questions = [
            "사업의 핵심 목표는 무엇인가요?",
            "주요 고객층은 누구인가요?",
            "예상되는 주요 리스크는 무엇인가요?",
            "경쟁 환경은 어떠한가요?",
            "성공의 핵심 요소는 무엇인가요?"
        ]
        
        question_texts = fallback_map.get(method, default_questions)
        
        questions = []
        for i, text in enumerate(question_texts, 1):
            questions.append(Question(
                question_id=f"{method_prefix}_q{i}",
                method=method,
                question_text=text,
                question_type="text",
                choices=None
            ))
        
        return questions
    
    def generate_risk_report(
        self,
        concept: str,
        methods: List[AnalysisMethod],
        questions: List[Question],
        answers: List[Answer],
        industry_category = None
    ) -> Dict[str, Any]:
        """
        OSD 기반 최종 리스크 보고서 생성
        
        Args:
            concept: 사업 아이디어/컨셉
            methods: 사용된 분석 기법
            questions: 질문 목록
            answers: 사용자 답변 목록
            industry_category: 업종 카테고리
            
        Returns:
            Dict: OSD 기반 리스크 보고서 데이터
        """
        # 질문-답변 매핑
        qa_map = {answer.question_id: answer.answer for answer in answers}
        
        prompt = self._create_report_generation_prompt(
            concept,
            methods,
            questions,
            qa_map
        )
        
        try:
            system_instruction = """당신은 **FMEA(Failure Mode and Effects Analysis) 분야에서 20년 이상 경력을 쌓은 리스크 분석 전문가**입니다.

자동차, 항공, 제조업 등 고신뢰성 산업에서 수천 건의 FMEA를 수행하며 OSD(Occurrence×Severity×Detection) 방법론의 대가가 되었습니다.

또한 스타트업 생태계에서 **창업 멘토**로 활동하며, 비즈니스 리스크를 정량적으로 측정하고 
실질적인 해결책을 제시하는 데 탁월한 능력을 발휘합니다.

당신의 역할:
1. OSD 점수를 정확하고 객관적으로 평가
2. 경영진이 즉시 실행할 수 있는 구체적 조언 제공
3. 리스크를 우선순위화하여 자원 배분 최적화
4. 20년 경력자의 통찰력으로 숨겨진 리스크 발견

전문가답게 신중하고 정확하게 분석해주세요."""

            full_prompt = f"""{system_instruction}

{prompt}"""
            
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.5,
                    'max_output_tokens': 4000,
                },
                safety_settings=self.safety_settings
            )
            
            # 안전 필터로 차단된 경우 처리
            if not response.candidates or not response.candidates[0].content.parts:
                print(f"보고서 생성 응답이 차단됨: finish_reason={response.candidates[0].finish_reason if response.candidates else 'N/A'}")
                raise Exception("Response blocked by safety filters")
            
            report_text = response.text
            return self._parse_osd_report(report_text, methods)
            
        except Exception as e:
            print(f"Gemini API 오류: {e}")
            return self._get_fallback_osd_report(methods)
    
    def _create_report_generation_prompt(
        self,
        concept: str,
        methods: List[AnalysisMethod],
        questions: List[Question],
        qa_map: Dict[str, str]
    ) -> str:
        """리스크 보고서 생성 프롬프트"""
        
        # 질문-답변 포맷팅
        qa_text = ""
        for question in questions:
            answer = qa_map.get(question.question_id, "답변 없음")
            qa_text += f"\n[{question.method.value}] Q: {question.question_text}\nA: {answer}\n"
        
        # 업종별 OSD 매핑 가이드
        method_osd_guide = {
            "IT/스타트업 + Lean Canvas": "문제적합성→O, 경쟁대비차별성→S, 고객피드백루프→D",
            "교육 + Logic Model": "Input부족→O, Outcome부진→S, Output측정시스템부재→D",
            "서비스업 + Blueprint": "Frontstage혼잡→O, 고객클레임위험→S, Backstage대응력→D",
            "제조 + FMEA": "FMEA 자체가 O/S/D 생성",
            "기본": "발생가능성→O, 심각도→S, 발견가능성→D"
        }
        
        return f"""
다음 사업에 대한 OSD 기반 종합 리스크 분석 보고서를 작성해주세요.

**사업 정보:**
- 사업 아이디어: {concept}

**사용된 분석 기법:**
{', '.join([m.value for m in methods])}

**질문과 답변:**
{qa_text}

**OSD 방법론 설명:**
- O (Occurrence): 발생 가능성 (1~10, 높을수록 발생하기 쉬움)
- S (Severity): 심각도 (1~10, 높을수록 피해가 큼)
- D (Detection): 발견 가능성 (1~10, 낮을수록 발견하기 어려움)
- Risk Score = O × S × D (1~1000)

**보고서 작성 요구사항:**

1. **각 분석 기법별 OSD 리스크 분석**
   각 기법마다 3~5개의 주요 리스크를 다음 형식으로 작성:
   
   기법: {methods[0].value}
   리스크1: [리스크 설명] | O=[1-10] | S=[1-10] | D=[1-10] | Score=[O×S×D]
   리스크2: [리스크 설명] | O=[1-10] | S=[1-10] | D=[1-10] | Score=[O×S×D]
   ...
   주요발견: [핵심 인사이트]
   
   기법: {methods[1].value}
   (동일 형식)

2. **AI 조언 (우선순위별)**
   각 조언을 다음 형식으로:
   
   조언1: [카테고리] | [우선순위: 높음/중간/낮음] | [액션] | [예상효과] | [난이도: 쉬움/보통/어려움]
   조언2: ...
   (5~7개 조언)

3. **경영진 요약**
   - 사업의 핵심 리스크와 기회를 2~3문단으로 요약

위 형식을 정확히 따라 숫자와 함께 작성해주세요.
"""
    
    def _create_osd_report_prompt(
        self,
        business_name: str,
        business_description: str,
        investment_amount: Optional[int],
        methods: List[AnalysisMethod],
        questions: List[Question],
        qa_map: Dict[str, str]
    ) -> str:
        """OSD 기반 리스크 보고서 생성 프롬프트"""
        
        # 질문-답변 포맷팅
        qa_text = ""
        for question in questions:
            answer = qa_map.get(question.question_id, "답변 없음")
            qa_text += f"\n[{question.method.value}] Q: {question.question_text}\nA: {answer}\n"
        
        investment_info = f"{investment_amount:,}원" if investment_amount else "미정"
        
        return f"""
다음 사업에 대한 OSD 기반 종합 리스크 분석 보고서를 작성해주세요.

**사업 정보:**
- 사업명: {business_name}
- 사업 내용: {business_description}
- 투자금액: {investment_info}

**사용된 분석 기법:**
{', '.join([m.value for m in methods])}

**질문과 답변:**
{qa_text}

**OSD 방법론:**
- O (Occurrence): 발생 가능성 (1~10)
- S (Severity): 심각도 (1~10)
- D (Detection): 발견 가능성 (1~10, 낮을수록 발견 어려움)
- Risk Score = O × S × D

**출력 형식:**

### 분석 기법별 OSD 리스크

기법: {methods[0].value}
리스크1: [설명] | O=7 | S=8 | D=6 | Score=336
리스크2: [설명] | O=5 | S=9 | D=7 | Score=315
...
인사이트: [분석 기법별 핵심 인사이트]

기법: {methods[1].value}
리스크1: ...

### AI 조언

조언1: 카테고리명 | 높음 | 구체적 액션 | 예상 효과 | 보통
조언2: ...

### 경영진 요약
[2~3문단 요약]

정확히 위 형식으로 작성해주세요.
"""
    
    def _parse_osd_report(
        self, 
        report_text: str,
        methods: List[AnalysisMethod]
    ) -> Dict[str, Any]:
        """GPT 응답에서 OSD 기반 리스크 보고서 파싱"""
        
        # 실제로는 GPT 응답을 정교하게 파싱
        # 여기서는 폴백 데이터 반환
        return self._get_fallback_osd_report(methods)
    
    def _get_fallback_osd_report(
        self, 
        methods: List[AnalysisMethod]
    ) -> Dict[str, Any]:
        """OSD 기반 폴백 리스크 보고서"""
        
        method_results = []
        
        for method in methods:
            # 각 기법별 샘플 OSD 리스크
            osd_risks = [
                {
                    "occurrence": 7,
                    "severity": 8,
                    "detection": 6,
                    "risk_score": 336,
                    "description": f"{method.value} 분석 결과 - 시장 경쟁 리스크"
                },
                {
                    "occurrence": 5,
                    "severity": 9,
                    "detection": 7,
                    "risk_score": 315,
                    "description": f"{method.value} 분석 결과 - 운영 리스크"
                },
                {
                    "occurrence": 6,
                    "severity": 6,
                    "detection": 5,
                    "risk_score": 180,
                    "description": f"{method.value} 분석 결과 - 재무 리스크"
                }
            ]
            
            method_results.append({
                "method": method,
                "osd_risks": osd_risks,
                "key_findings": [
                    f"{method.value} 기법을 통해 핵심 리스크 영역을 식별했습니다",
                    "개선이 필요한 영역이 명확히 파악되었습니다",
                    "단계적 리스크 완화 전략이 필요합니다"
                ],
                "method_specific_insights": f"{method.value} 분석을 통해 사업의 구조적 리스크를 파악할 수 있었습니다."
            })
        
        # AI 조언
        ai_recommendations = [
            {
                "category": "시장 검증",
                "priority": "높음",
                "action": "초기 고객 인터뷰를 통한 문제-해결책 적합도 재검증",
                "expected_impact": "제품-시장 적합성 향상 및 피벗 리스크 감소",
                "implementation_difficulty": "쉬움"
            },
            {
                "category": "MVP 개발",
                "priority": "높음",
                "action": "핵심 기능만 포함한 최소 기능 제품(MVP) 우선 출시",
                "expected_impact": "개발 비용 절감 및 빠른 시장 피드백",
                "implementation_difficulty": "보통"
            },
            {
                "category": "재무 관리",
                "priority": "중간",
                "action": "월별 번다운(Burn Rate) 모니터링 시스템 구축",
                "expected_impact": "자금 소진 리스크 조기 감지",
                "implementation_difficulty": "쉬움"
            },
            {
                "category": "팀 역량",
                "priority": "중간",
                "action": "핵심 기술 스택에 대한 팀 교육 및 역량 강화",
                "expected_impact": "개발 속도 향상 및 기술 부채 감소",
                "implementation_difficulty": "보통"
            },
            {
                "category": "고객 피드백",
                "priority": "높음",
                "action": "사용자 피드백 수집 자동화 시스템 도입",
                "expected_impact": "제품 개선 속도 향상 및 이탈 방지",
                "implementation_difficulty": "쉬움"
            }
        ]
        
        executive_summary = """
이 사업은 중간 수준의 리스크를 보이고 있으며, 체계적인 준비를 통해 충분히 관리 가능합니다.

주요 리스크는 시장 경쟁 강도와 초기 고객 확보에 집중되어 있으나, 적절한 MVP 전략과
고객 피드백 루프를 구축한다면 성공 확률을 크게 높일 수 있습니다.

투자금액 대비 리스크를 고려할 때, 단계적 투자 집행과 주요 마일스톤 달성 시점에서의
재평가가 권장됩니다.
"""
        
        return {
            "method_results": method_results,
            "ai_recommendations": ai_recommendations,
            "executive_summary": executive_summary.strip()
        }

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

class PsychologicalTests:
    """진로심리검사 관련 기능을 담당하는 클래스"""
    
    def __init__(self, api, db, user_info):
        self.api = api
        self.db = db
        self.user_info = user_info
    
    def show(self):
        """진로심리검사 페이지 표시"""
        st.header('진로심리검사')
        
        # 검사 목록 가져오기
        tests = self._get_tests()
        
        # 탭 생성 - 검사 선택 및 결과 확인
        tab1, tab2 = st.tabs(["검사 선택", "검사 결과 확인"])
        
        # 검사 선택 탭
        with tab1:
            self._show_test_selection(tests)
        
        # 결과 확인 탭
        with tab2:
            self._show_test_results()
    
    def _get_tests(self):
        """API에서 검사 목록 가져오기"""
        # 실제 API 연동 시 아래 코드 사용
        # response = self.api.get_psychological_tests()
        # return response.get("tests", [])
        
        # 예시 데이터
        return [
            {"id": "1", "name": "직업흥미검사(H)", "description": "직업에 대한 흥미를 측정하여 적합한 직업군 추천"},
            {"id": "2", "name": "직업적성검사", "description": "개인의 적성과 잠재력을 측정하여 적합한 직업 탐색"},
            {"id": "3", "name": "진로성숙도검사", "description": "진로에 대한 준비도와 성숙도 측정"},
            {"id": "4", "name": "직업가치관검사", "description": "직업 선택 시 중요하게 생각하는 가치 측정"},
            {"id": "5", "name": "진로탐색검사", "description": "자신의 진로 방향성 탐색을 위한 검사"}
        ]
    
    def _show_test_selection(self, tests):
        """검사 선택 화면 표시"""
        st.subheader("원하는 검사를 선택하세요")
        
        for test in tests:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{test['name']}**")
                st.write(test['description'])
            with col2:
                if st.button("검사 시작", key=f"start_{test['id']}"):
                    st.session_state.selected_test = test
                    st.session_state.test_step = 'questions'
        
        # 검사 진행
        if 'selected_test' in st.session_state and 'test_step' in st.session_state:
            if st.session_state.test_step == 'questions':
                self._show_test_questions(st.session_state.selected_test)
    
    def _show_test_questions(self, test):
        """검사 문항 표시 - 페이지 단위로 표시"""
        st.subheader(f"{test['name']} 진행 중")
        
        # API에서 검사 문항 가져오기
        try:
            response = self.api.get_psychological_test_questions(test['id'])
            questions = response.get("questions", [])
            
            # API 응답이 없거나 오류인 경우 예시 문항 사용
            if not questions or "error" in response:
                st.warning("API에서 검사 문항을 가져오는데 실패했습니다. 예시 문항으로 대체합니다.")
                questions = self._get_sample_questions(test['id'])
        except Exception as e:
            st.error(f"검사 문항 로딩 중 오류 발생: {e}")
            questions = self._get_sample_questions(test['id'])
        
        total_questions = len(questions)
        
        # 페이지 관리
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0
        
        # 페이지당 문항 수
        questions_per_page = 5
        
        # 총 페이지 수 계산
        total_pages = (total_questions + questions_per_page - 1) // questions_per_page
        
        # 현재 페이지의 문항 범위 계산
        start_idx = st.session_state.current_page * questions_per_page
        end_idx = min(start_idx + questions_per_page, total_questions)
        
        # 진행 상황 표시
        progress = (st.session_state.current_page + 1) / total_pages
        st.progress(progress)
        st.write(f"페이지 {st.session_state.current_page + 1}/{total_pages} (질문 {start_idx + 1}-{end_idx}/{total_questions})")
        
        # 현재 페이지의 문항 표시
        current_page_questions = questions[start_idx:end_idx]
        
        if 'answers' not in st.session_state:
            st.session_state.answers = {}
        
        for q in current_page_questions:
            st.write(f"**{q['text']}**")
            
            # 이미 답변한 경우 해당 값으로 초기화
            default_idx = 0
            if q['id'] in st.session_state.answers:
                try:
                    default_idx = q['options'].index(st.session_state.answers[q['id']])
                except ValueError:
                    default_idx = 0
            
            answer = st.radio(
                f"Question {q['id']}", 
                q['options'], 
                key=f"q_{q['id']}",
                index=default_idx,
                horizontal=True,
                label_visibility="collapsed"
            )
            st.session_state.answers[q['id']] = answer
        
        # 페이지 이동 버튼
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.session_state.current_page > 0:
                if st.button("이전"):
                    st.session_state.current_page -= 1
                    st.rerun()
        
        with col3:
            if st.session_state.current_page < total_pages - 1:
                if st.button("다음"):
                    st.session_state.current_page += 1
                    st.rerun()
            else:
                if st.button("검사 제출"):
                    # 모든 질문에 답변했는지 확인
                    if len(st.session_state.answers) == total_questions:
                        self._submit_test_result(test, st.session_state.answers)
                    else:
                        st.error("모든 질문에 답변해주세요.")
    
    def _get_sample_questions(self, test_id):
        """API 연결 실패 시 사용할 예시 문항"""
        # 기본 옵션 세트
        options = ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"]
        
        # 검사 유형별 예시 문항
        if test_id == "1":  # 직업흥미검사(H)
            return [
                {"id": "1", "text": "새로운 사람을 만나는 것을 좋아한다.", "options": options},
                {"id": "2", "text": "계획을 세우고 그대로 실행하는 것이 중요하다.", "options": options},
                {"id": "3", "text": "문제 해결 시 창의적인 방법을 선호한다.", "options": options},
                {"id": "4", "text": "세부적인 것보다 큰 그림을 보는 것이 좋다.", "options": options},
                {"id": "5", "text": "분석적인 사고를 하는 것을 좋아한다.", "options": options},
                {"id": "6", "text": "다른 사람들과 협력하여 일하는 것이 좋다.", "options": options},
                {"id": "7", "text": "새로운 아이디어를 생각해내는 것을 즐긴다.", "options": options},
                {"id": "8", "text": "규칙과 절차를 따르는 것이 중요하다.", "options": options},
                {"id": "9", "text": "다른 사람을 돕는 일에 보람을 느낀다.", "options": options},
                {"id": "10", "text": "목표를 달성하기 위해 노력하는 것을 좋아한다.", "options": options},
                {"id": "11", "text": "예술적인 활동에 관심이 많다.", "options": options},
                {"id": "12", "text": "복잡한 문제를 해결하는 것이 즐겁다.", "options": options},
                {"id": "13", "text": "다른 사람들을 리드하는 것을 좋아한다.", "options": options},
                {"id": "14", "text": "정확하고 체계적인 일을 선호한다.", "options": options},
                {"id": "15", "text": "자연과 관련된 활동을 즐긴다.", "options": options},
                {"id": "16", "text": "기계나 도구를 다루는 것을 좋아한다.", "options": options},
                {"id": "17", "text": "다른 사람의 감정을 이해하는 것이 중요하다.", "options": options},
                {"id": "18", "text": "새로운 기술을 배우는 것을 즐긴다.", "options": options},
                {"id": "19", "text": "경쟁적인 환경에서 일하는 것을 좋아한다.", "options": options},
                {"id": "20", "text": "세부 사항에 주의를 기울이는 것이 중요하다.", "options": options}
            ]
        elif test_id == "2":  # 직업적성검사
            return [
                {"id": "1", "text": "복잡한 계산을 빠르게 할 수 있다.", "options": options},
                {"id": "2", "text": "공간적 관계를 쉽게 이해할 수 있다.", "options": options},
                {"id": "3", "text": "언어적 표현력이 뛰어나다.", "options": options},
                {"id": "4", "text": "손으로 정교한 작업을 하는 것이 능숙하다.", "options": options},
                {"id": "5", "text": "다른 사람의 감정을 잘 파악한다.", "options": options},
                {"id": "6", "text": "논리적으로 문제를 분석하는 것이 좋다.", "options": options},
                {"id": "7", "text": "음악적 리듬과 멜로디를 잘 인식한다.", "options": options},
                {"id": "8", "text": "글쓰기를 통해 생각을 잘 표현한다.", "options": options},
                {"id": "9", "text": "신체적으로 활동적인 일을 좋아한다.", "options": options},
                {"id": "10", "text": "다른 사람을 가르치는 것을 즐긴다.", "options": options},
                {"id": "11", "text": "데이터를 분석하고 패턴을 찾는 것이 좋다.", "options": options},
                {"id": "12", "text": "시각적 디자인에 대한 감각이 있다.", "options": options},
                {"id": "13", "text": "여러 언어를 배우는 것에 관심이 있다.", "options": options},
                {"id": "14", "text": "기계나 전자 장치를 수리하는 것을 좋아한다.", "options": options},
                {"id": "15", "text": "팀을 이끌고 조직하는 능력이 있다.", "options": options},
                {"id": "16", "text": "과학적 실험을 설계하고 수행하는 것을 좋아한다.", "options": options},
                {"id": "17", "text": "창의적인 방식으로 자신을 표현하는 것을 즐긴다.", "options": options},
                {"id": "18", "text": "다양한 주제에 대해 글을 쓰는 것이 좋다.", "options": options},
                {"id": "19", "text": "도구를 사용하여 물건을 만드는 것을 좋아한다.", "options": options},
                {"id": "20", "text": "다른 사람의 문제를 해결하는 데 도움을 주는 것을 좋아한다.", "options": options}
            ]
        else:  # 기타 검사
            return [
                {"id": "1", "text": "새로운 사람을 만나는 것을 좋아한다.", "options": options},
                {"id": "2", "text": "계획을 세우고 그대로 실행하는 것이 중요하다.", "options": options},
                {"id": "3", "text": "문제 해결 시 창의적인 방법을 선호한다.", "options": options},
                {"id": "4", "text": "세부적인 것보다 큰 그림을 보는 것이 좋다.", "options": options},
                {"id": "5", "text": "분석적인 사고를 하는 것을 좋아한다.", "options": options},
                {"id": "6", "text": "다른 사람들과 협력하여 일하는 것이 좋다.", "options": options},
                {"id": "7", "text": "새로운 아이디어를 생각해내는 것을 즐긴다.", "options": options},
                {"id": "8", "text": "규칙과 절차를 따르는 것이 중요하다.", "options": options},
                {"id": "9", "text": "다른 사람을 돕는 일에 보람을 느낀다.", "options": options},
                {"id": "10", "text": "목표를 달성하기 위해 노력하는 것을 좋아한다.", "options": options},
                {"id": "11", "text": "예술적인 활동에 관심이 많다.", "options": options},
                {"id": "12", "text": "복잡한 문제를 해결하는 것이 즐겁다.", "options": options},
                {"id": "13", "text": "다른 사람들을 리드하는 것을 좋아한다.", "options": options},
                {"id": "14", "text": "정확하고 체계적인 일을 선호한다.", "options": options},
                {"id": "15", "text": "자연과 관련된 활동을 즐긴다.", "options": options}
            ]
    
    def _submit_test_result(self, test, answers):
        """검사 결과 제출 및 저장"""
        # API를 통해 검사 결과 요청
        try:
            result = self.api.submit_psychological_test(test['id'], answers)
            
            # API 응답이 없거나 오류인 경우 예시 결과 사용
            if "error" in result:
                st.warning("API에서 검사 결과를 가져오는데 실패했습니다. 예시 결과로 대체합니다.")
                result = self._get_sample_result(test, answers)
        except Exception as e:
            st.error(f"검사 결과 처리 중 오류 발생: {e}")
            result = self._get_sample_result(test, answers)
        
    def _get_sample_result(self, test, answers):
        """API 연결 실패 시 사용할 예시 결과"""
        # 검사 유형별 예시 결과
        if test['id'] == "1":  # 직업흥미검사(H)
            return {
                "test_id": test['id'],
                "test_name": test['name'],
                "completed_date": datetime.now().strftime("%Y-%m-%d"),
                "result_url": "https://www.career.go.kr/cnet/front/examen/inspctResult.do",
                "summary": "이 검사 결과에 따르면 당신은 창의적이고 분석적인 사고를 가진 '탐구형' 유형에 가깝습니다. 탐구형 유형은 지적 호기심이 강하고 새로운 지식을 습득하는 것을 좋아합니다. 또한 예술형 성향도 높게 나타나 창의적인 분야에서도 역량을 발휘할 수 있습니다.",
                "categories": {
                    "탐구형": 80,
                    "예술형": 65,
                    "사회형": 50,
                    "관습형": 35,
                    "진취형": 45,
                    "현실형": 30
                },
                "recommended_jobs": [
                    "연구원", "과학자", "엔지니어", "데이터 분석가", "IT 컨설턴트", "프로그래머", "생명과학자", "물리학자", "수학자", "통계학자"
                ]
            }
        elif test['id'] == "2":  # 직업적성검사
            return {
                "test_id": test['id'],
                "test_name": test['name'],
                "completed_date": datetime.now().strftime("%Y-%m-%d"),
                "result_url": "https://www.career.go.kr/cnet/front/examen/inspctResult.do",
                "summary": "이 검사 결과에 따르면 당신은 논리-수학적 지능과 언어적 지능이 뛰어난 것으로 나타났습니다. 복잡한 문제를 분석하고 해결하는 능력이 뛰어나며, 의사소통 능력도 높은 편입니다.",
                "categories": {
                    "논리-수학적 지능": 85,
                    "언어적 지능": 75,
                    "공간적 지능": 60,
                    "대인관계 지능": 55,
                    "신체-운동적 지능": 40,
                    "음악적 지능": 50
                },
                "recommended_jobs": [
                    "소프트웨어 개발자", "변호사", "경영 컨설턴트", "금융 분석가", "교수", "작가", "기자", "마케팅 전문가", "정책 분석가", "번역가"
                ]
            }
        else:  # 기타 검사
            return {
                "test_id": test['id'],
                "test_name": test['name'],
                "completed_date": datetime.now().strftime("%Y-%m-%d"),
                "result_url": "https://www.career.go.kr/cnet/front/examen/inspctResult.do",
                "summary": "이 검사 결과에 따르면 당신은 다양한 분야에 관심이 있으며, 특히 창의적인 문제 해결 능력이 뛰어난 것으로 나타났습니다.",
                "categories": {
                    "창의성": 75,
                    "분석력": 70,
                    "사회성": 65,
                    "리더십": 60,
                    "실행력": 55,
                    "안정성": 50
                },
                "recommended_jobs": [
                    "교사", "상담사", "사회복지사", "인사 관리자", "마케팅 전문가", "창업가", "예술가", "디자이너"
                ]
            }
        
        # 사용자 데이터에 결과 저장
        test_results = self.user_info['data'].get('test_results', {})
        test_results[test['id']] = result
        
        # Firestore에 업데이트
        self.db.collection("users").document(self.user_info['user_id']).update({
            'test_results': test_results
        })
        
        # 세션 상태 업데이트
        self.user_info['data']['test_results'] = test_results
        
        # 화면 상태 업데이트
        st.session_state.pop('answers', None)
        st.session_state.pop('test_step', None)
        st.session_state.pop('selected_test', None)
        
        st.success("검사가 완료되었습니다! '검사 결과 확인' 탭에서 결과를 확인하세요.")
    
    def _show_test_results(self):
        """검사 결과 확인 화면 표시"""
        test_results = self.user_info['data'].get('test_results', {})
        
        if not test_results:
            st.info("아직 완료한 검사가 없습니다. '검사 선택' 탭에서 검사를 진행해주세요.")
            return
        
        st.subheader("완료한 검사 목록")
        
        for test_id, result in test_results.items():
            expander = st.expander(f"{result['test_name']} ({result['completed_date']})")
            with expander:
                st.write(result['summary'])
                
                if 'categories' in result:
                    # 결과 시각화
                    categories_df = pd.DataFrame({
                        '유형': list(result['categories'].keys()),
                        '점수': list(result['categories'].values())
                    })
                    
                    fig = px.bar(
                        categories_df, 
                        x='유형', 
                        y='점수',
                        title='검사 결과 유형별 점수',
                        color='점수',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig)
                
                if 'recommended_jobs' in result:
                    st.subheader("추천 직업")
                    cols = st.columns(3)
                    for i, job in enumerate(result['recommended_jobs']):
                        with cols[i % 3]:
                            if st.button(f"저장: {job}", key=f"save_job_{test_id}_{i}"):
                                # 직업 저장 로직
                                saved_jobs = self.user_info['data'].get('saved_jobs', [])
                                job_info = {
                                    'job_name': job,
                                    'job_description': f"{result['test_name']} 검사 결과 추천 직업",
                                    'saved_date': datetime.now().strftime("%Y-%m-%d")
                                }
                                
                                # 중복 저장 방지
                                if not any(j['job_name'] == job for j in saved_jobs):
                                    saved_jobs.append(job_info)
                                    self.user_info['data']['saved_jobs'] = saved_jobs
                                    
                                    # Firestore에 저장
                                    self.db.collection("users").document(
                                        self.user_info['user_id']
                                    ).update({'saved_jobs': saved_jobs})
                                    
                                    st.success(f"{job}이(가) 관심 직업으로 저장되었습니다!")
                                else:
                                    st.info(f"{job}은(는) 이미 저장된 직업입니다.")
                            
                            st.write(job)
                
                # 검사 결과 링크
                if 'result_url' in result:
                    st.markdown(f"[자세한 결과 보기]({result['result_url']})", unsafe_allow_html=True)

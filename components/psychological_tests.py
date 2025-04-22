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
        """검사 문항 표시"""
        st.subheader(f"{test['name']} 진행 중")
        
        # 실제 API 연동 시 아래 코드 사용
        # questions = self.api.get_psychological_test_questions(test['id'])
        
        # 예시 문항 (실제 구현 시 API 응답으로 대체)
        questions = [
            {"id": "1", "text": "새로운 사람을 만나는 것을 좋아한다.", "options": ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"]},
            {"id": "2", "text": "계획을 세우고 그대로 실행하는 것이 중요하다.", "options": ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"]},
            {"id": "3", "text": "문제 해결 시 창의적인 방법을 선호한다.", "options": ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"]},
            {"id": "4", "text": "세부적인 것보다 큰 그림을 보는 것이 좋다.", "options": ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"]},
            {"id": "5", "text": "분석적인 사고를 하는 것을 좋아한다.", "options": ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"]}
        ]
        
        if 'answers' not in st.session_state:
            st.session_state.answers = {}
        
        for q in questions:
            st.write(f"**{q['text']}**")
            answer = st.radio(
                f"Question {q['id']}", 
                q['options'], 
                key=f"q_{q['id']}",
                index=0,
                horizontal=True,
                label_visibility="collapsed"
            )
            st.session_state.answers[q['id']] = answer
        
        if st.button("검사 제출"):
            # 검사 결과 생성 (실제로는 API 호출)
            self._submit_test_result(test, st.session_state.answers)
    
    def _submit_test_result(self, test, answers):
        """검사 결과 제출 및 저장"""
        # 실제 API 연동 시 아래 코드 사용
        # result = self.api.submit_psychological_test(test['id'], answers)
        
        # 예시 결과 (실제 구현 시 API 응답으로 대체)
        result = {
            "test_id": test['id'],
            "test_name": test['name'],
            "completed_date": datetime.now().strftime("%Y-%m-%d"),
            "result_url": "https://www.career.go.kr/cnet/front/examen/inspctResult.do",
            "summary": "이 검사 결과에 따르면 당신은 창의적이고 분석적인 사고를 가진 '탐구형' 유형에 가깝습니다.",
            "categories": {
                "탐구형": 80,
                "예술형": 65,
                "사회형": 50,
                "관습형": 35,
                "진취형": 45,
                "현실형": 30
            },
            "recommended_jobs": [
                "연구원", "과학자", "엔지니어", "데이터 분석가", "IT 컨설턴트"
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

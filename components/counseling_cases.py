import streamlit as st
import pandas as pd

class CounselingCases:
    """진로상담 사례 관련 기능을 담당하는 클래스"""
    
    def __init__(self, api, db, user_info):
        self.api = api
        self.db = db
        self.user_info = user_info
    
    def show(self):
        """진로상담 사례 페이지 표시"""
        st.header('진로상담 사례')
        
        # 검색 필터
        st.subheader("상담 사례 검색")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 상담 카테고리 선택
            categories = [
                "전체",
                "진로탐색",
                "진학상담",
                "학업고민",
                "직업정보",
                "적성/흥미",
                "학교생활",
                "창업/취업",
                "기타"
            ]
            selected_category = st.selectbox("상담 분야", categories)
        
        with col2:
            # 키워드 검색
            keyword = st.text_input("검색어")
        
        if st.button("검색"):
            if selected_category == "전체":
                category_param = None
            else:
                category_param = selected_category
            
            # 상담 사례 목록 가져오기
            cases = self._get_counseling_cases(category_param, keyword)
            
            if cases:
                st.session_state.case_search_results = cases
            else:
                st.warning("검색 결과가 없습니다. 다른 검색어로 시도해보세요.")
        
        # 검색 결과 표시
        if 'case_search_results' in st.session_state:
            self._show_case_list(st.session_state.case_search_results)
        
        # 상담 사례 상세 정보 표시
        if 'selected_case' in st.session_state:
            self._show_case_detail(st.session_state.selected_case)
    
    def _get_counseling_cases(self, category=None, keyword=None):
        """API에서 상담 사례 목록 가져오기"""
        # 실제 API 연동 시 아래 코드 사용
        # response = self.api.get_counseling_cases(keyword, category)
        # return response.get("cases", [])
        
        # 예시 데이터
        cases = [
            {"id": "1", "title": "진로 선택에 고민이 있어요", "category": "진로탐색", "date": "2023-05-15"},
            {"id": "2", "title": "수학과 진학에 대한 조언 부탁드립니다", "category": "진학상담", "date": "2023-06-20"},
            {"id": "3", "title": "프로그래머가 되고 싶어요", "category": "직업정보", "date": "2023-07-05"},
            {"id": "4", "title": "성적이 낮아서 걱정돼요", "category": "학업고민", "date": "2023-08-10"},
            {"id": "5", "title": "진로심리검사 결과 해석 도움이 필요해요", "category": "적성/흥미", "date": "2023-09-25"},
            {"id": "6", "title": "친구관계로 학교생활이 힘들어요", "category": "학교생활", "date": "2023-10-15"},
            {"id": "7", "title": "졸업 후 취업 준비 어떻게 해야 할까요?", "category": "창업/취업", "date": "2023-11-03"},
            {"id": "8", "title": "동아리 활동과 진로 연계 방법", "category": "기타", "date": "2023-12-01"}
        ]
        
        # 카테고리와 키워드로 필터링
        filtered_cases = cases
        
        if category:
            filtered_cases = [case for case in filtered_cases if case["category"] == category]
        
        if keyword:
            filtered_cases = [case for case in filtered_cases if keyword.lower() in case["title"].lower()]
        
        return filtered_cases
    
    def _show_case_list(self, cases):
        """상담 사례 목록 표시"""
        st.subheader(f"검색 결과: {len(cases)}개의 상담 사례")
        
        # 상담 사례 목록을 테이블로 표시
        case_df = pd.DataFrame(cases)
        if not case_df.empty:
            st.dataframe(case_df[["title", "category", "date"]], use_container_width=True)
        
        # 상담 사례 선택
        selected_case_id = st.selectbox(
            "상세 내용을 볼 사례 선택",
            options=[case["id"] for case in cases],
            format_func=lambda x: next((case["title"] for case in cases if case["id"] == x), "")
        )
        
        if st.button("상세 내용 보기"):
            # 선택한 상담 사례 정보 가져오기
            selected_case = next((case for case in cases if case["id"] == selected_case_id), None)
            if selected_case:
                st.session_state.selected_case = selected_case
                # 실제 구현에서는 API 호출로 상세 정보를 가져옴
                # case_detail = self.api.get_counseling_detail(selected_case_id)
    
    def _show_case_detail(self, case):
        """상담 사례 상세 정보 표시"""
        st.subheader(f"상담 사례: {case['title']}")
        
        # 예시 데이터 (실제 구현 시 API 응답으로 대체)
        case_detail = {
            "id": case["id"],
            "title": case["title"],
            "category": case["category"],
            "date": case["date"],
            "question": f"안녕하세요. 저는 고등학교 2학년 학생입니다. {case['title']} 관련해서 고민이 있어 상담을 요청합니다...",
            "answer": f"안녕하세요. 학생의 고민 잘 읽었습니다. {case['category']} 관련 고민이신 것 같아요. 먼저, 이런 고민을 가진 학생들이 많이 있다는 것을 알려드리고 싶습니다. 여러 가지 방법을 고려해볼 수 있습니다...",
            "similar_cases": [
                {"id": "101", "title": "비슷한 사례 1"},
                {"id": "102", "title": "비슷한 사례 2"},
                {"id": "103", "title": "비슷한 사례 3"}
            ]
        }
        
        # 사례 정보 표시
        st.write(f"**분야:** {case_detail['category']}")
        st.write(f"**작성일:** {case_detail['date']}")
        
        # 질문 내용
        st.subheader("상담 질문")
        st.write(case_detail['question'])
        
        # 답변 내용
        st.subheader("상담 답변")
        st.write(case_detail['answer'])
        
        # 유사 사례
        if case_detail.get('similar_cases'):
            st.subheader("유사한 상담 사례")
            for similar_case in case_detail['similar_cases']:
                if st.button(similar_case['title'], key=f"similar_{similar_case['id']}"):
                    # 실제 구현에서는 유사 사례 상세 정보를 가져와 표시
                    st.info(f"{similar_case['title']} 상세 내용은 준비 중입니다.")
        
        # 나만의 상담 질문하기
        st.subheader("나만의 진로 고민 등록하기")
        st.write("비슷한 고민이 있다면 상담을 요청해보세요.")
        
        my_question = st.text_area("상담 내용 작성", height=150)
        
        if st.button("상담 요청하기"):
            if my_question:
                st.success("상담 요청이 등록되었습니다. 답변이 등록되면 알려드리겠습니다.")
            else:
                st.warning("상담 내용을 작성해주세요.")

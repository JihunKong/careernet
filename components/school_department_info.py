import streamlit as st
import pandas as pd
from datetime import datetime

class SchoolDepartmentInfo:
    """학교 및 학과 정보 관련 기능을 담당하는 클래스"""
    
    def __init__(self, api, db, user_info):
        self.api = api
        self.db = db
        self.user_info = user_info
    
    def show(self):
        """학교 및 학과 정보 페이지 표시"""
        st.header('학교 및 학과 정보')
        
        # 학교와 학과 탭 생성
        tab1, tab2 = st.tabs(["학교 정보", "학과 정보"])
        
        # 학교 정보 탭
        with tab1:
            self._show_school_info()
        
        # 학과 정보 탭
        with tab2:
            self._show_department_info()
        
    def _show_school_info(self):
        """학교 정보 탭 내용"""
        st.subheader("학교 검색")
        
        # 검색 필터
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 학교 유형 선택
            school_types = [
                "전체",
                "초등학교",
                "중학교",
                "고등학교",
                "대학교",
                "대학원"
            ]
            school_type = st.selectbox("학교 유형", school_types)
        
        with col2:
            # 지역 선택
            regions = [
                "전체",
                "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
                "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"
            ]
            region = st.selectbox("지역", regions)
        
        with col3:
            # 학교명 검색
            school_name = st.text_input("학교명")
        
        if st.button("학교 검색"):
            if school_type == "전체":
                school_type_param = None
            else:
                school_type_param = school_type
            
            if region == "전체":
                region_param = None
            else:
                region_param = region
            
            # 학교 목록 가져오기
            schools = self._get_schools(school_type_param, region_param, school_name)
            
            if schools:
                st.session_state.school_search_results = schools
            else:
                st.warning("검색 결과가 없습니다. 다른 검색어로 시도해보세요.")
        
        # 검색 결과 표시
        if 'school_search_results' in st.session_state:
            self._show_school_list(st.session_state.school_search_results)
        
        # 학교 상세 정보 표시
        if 'selected_school' in st.session_state:
            self._show_school_detail(st.session_state.selected_school)
    
    def _get_schools(self, school_type=None, region=None, name=None):
        """API에서 학교 목록 가져오기"""
        # 실제 API 연동 시 아래 코드 사용
        # response = self.api.get_schools(school_type, region, name)
        # return response.get("schools", [])
        
        # 예시 데이터
        schools = [
            {"id": "1", "name": "서울대학교", "type": "대학교", "region": "서울", "address": "서울특별시 관악구"},
            {"id": "2", "name": "연세대학교", "type": "대학교", "region": "서울", "address": "서울특별시 서대문구"},
            {"id": "3", "name": "고려대학교", "type": "대학교", "region": "서울", "address": "서울특별시 성북구"},
            {"id": "4", "name": "한양대학교", "type": "대학교", "region": "서울", "address": "서울특별시 성동구"},
            {"id": "5", "name": "경북대학교", "type": "대학교", "region": "경북", "address": "대구광역시 북구"},
            {"id": "6", "name": "서울과학고등학교", "type": "고등학교", "region": "서울", "address": "서울특별시 종로구"},
            {"id": "7", "name": "대전과학고등학교", "type": "고등학교", "region": "대전", "address": "대전광역시 유성구"},
            {"id": "8", "name": "경기과학고등학교", "type": "고등학교", "region": "경기", "address": "경기도 수원시"}
        ]
        
        # 필터링
        filtered_schools = schools
        
        if school_type:
            filtered_schools = [school for school in filtered_schools if school["type"] == school_type]
        
        if region:
            filtered_schools = [school for school in filtered_schools if school["region"] == region]
        
        if name:
            filtered_schools = [school for school in filtered_schools if name.lower() in school["name"].lower()]
        
        return filtered_schools
    
    def _show_school_list(self, schools):
        """학교 목록 표시"""
        st.subheader(f"검색 결과: {len(schools)}개의 학교")
        
        # 학교 목록을 테이블로 표시
        school_df = pd.DataFrame(schools)
        if not school_df.empty:
            st.dataframe(school_df[["name", "type", "region", "address"]], use_container_width=True)
        
        # 학교 선택
        selected_school_id = st.selectbox(
            "상세 정보를 볼 학교 선택",
            options=[school["id"] for school in schools],
            format_func=lambda x: next((school["name"] for school in schools if school["id"] == x), "")
        )
        
        if st.button("학교 정보 보기"):
            # 선택한 학교 정보 가져오기
            selected_school = next((school for school in schools if school["id"] == selected_school_id), None)
            if selected_school:
                st.session_state.selected_school = selected_school
    
    def _show_school_detail(self, school):
        """학교 상세 정보 표시"""
        st.subheader(f"{school['name']} 정보")
        
        # 예시 데이터 (실제 구현 시 API 응답으로 대체)
        school_detail = {
            "id": school["id"],
            "name": school["name"],
            "type": school["type"],
            "region": school["region"],
            "address": school["address"],
            "website": f"https://www.{school['name'].replace(' ', '')}.ac.kr",
            "established": "1946년",
            "description": f"{school['name']}는 {school['region']}에 위치한 {school['type']}입니다. 다양한 학과와 프로그램을 제공합니다.",
            "departments": [
                {"id": "101", "name": "컴퓨터공학과"},
                {"id": "102", "name": "경영학과"},
                {"id": "103", "name": "심리학과"},
                {"id": "104", "name": "기계공학과"},
                {"id": "105", "name": "화학과"}
            ] if school["type"] == "대학교" else [],
            "admission_info": f"{school['name']}의 입학 안내 정보입니다. 자세한 사항은 학교 홈페이지를 참고하세요."
        }
        
        # 학교 정보 표시
        st.write(f"**유형:** {school_detail['type']}")
        st.write(f"**지역:** {school_detail['region']}")
        st.write(f"**주소:** {school_detail['address']}")
        st.write(f"**설립년도:** {school_detail['established']}")
        st.write(f"**웹사이트:** [{school_detail['website']}]({school_detail['website']})")
        
        st.subheader("학교 소개")
        st.write(school_detail['description'])
        
        # 학과 정보 (대학교인 경우)
        if school_detail["type"] == "대학교" and school_detail["departments"]:
            st.subheader("주요 학과")
            
            cols = st.columns(3)
            for i, dept in enumerate(school_detail["departments"]):
                with cols[i % 3]:
                    if st.button(dept["name"], key=f"dept_{dept['id']}"):
                        # 학과 정보 저장
                        self._save_department(school, dept)
        
        # 입학 안내
        st.subheader("입학 안내")
        st.write(school_detail['admission_info'])
        
        # 관심 학교 저장 버튼
        if st.button("관심 학교로 저장"):
            self._save_school(school_detail)
    
    def _show_department_info(self):
        """학과 정보 탭 내용"""
        st.subheader("학과 검색")
        
        # 검색 필터
        col1, col2 = st.columns(2)
        
        with col1:
            # 학과 계열 선택
            department_categories = [
                "전체",
                "인문계열",
                "사회계열",
                "교육계열",
                "공학계열",
                "자연계열",
                "의약계열",
                "예체능계열"
            ]
            dept_category = st.selectbox("학과 계열", department_categories)
        
        with col2:
            # 학과명 검색
            dept_name = st.text_input("학과명")
        
        if st.button("학과 검색"):
            if dept_category == "전체":
                category_param = None
            else:
                category_param = dept_category
            
            # 학과 목록 가져오기
            departments = self._get_departments(category_param, dept_name)
            
            if departments:
                st.session_state.dept_search_results = departments
            else:
                st.warning("검색 결과가 없습니다. 다른 검색어로 시도해보세요.")
        
        # 검색 결과 표시
        if 'dept_search_results' in st.session_state:
            self._show_department_list(st.session_state.dept_search_results)
        
        # 학과 상세 정보 표시
        if 'selected_department' in st.session_state:
            self._show_department_detail(st.session_state.selected_department)
    
    def _get_departments(self, category=None, name=None):
        """API에서 학과 목록 가져오기"""
        # 실제 API 연동 시 아래 코드 사용
        # response = self.api.get_departments(category, name)
        # return response.get("departments", [])
        
        # 예시 데이터
        departments = [
            {"id": "201", "name": "컴퓨터공학과", "category": "공학계열"},
            {"id": "202", "name": "전자공학과", "category": "공학계열"},
            {"id": "203", "name": "기계공학과", "category": "공학계열"},
            {"id": "204", "name": "경영학과", "category": "사회계열"},
            {"id": "205", "name": "경제학과", "category": "사회계열"},
            {"id": "206", "name": "심리학과", "category": "사회계열"},
            {"id": "207", "name": "화학과", "category": "자연계열"},
            {"id": "208", "name": "물리학과", "category": "자연계열"},
            {"id": "209", "name": "의학과", "category": "의약계열"},
            {"id": "210", "name": "간호학과", "category": "의약계열"}
        ]
        
        # 필터링
        filtered_departments = departments
        
        if category:
            filtered_departments = [dept for dept in filtered_departments if dept["category"] == category]
        
        if name:
            filtered_departments = [dept for dept in filtered_departments if name.lower() in dept["name"].lower()]
        
        return filtered_departments
    
    def _show_department_list(self, departments):
        """학과 목록 표시"""
        st.subheader(f"검색 결과: {len(departments)}개의 학과")
        
        # 학과 목록을 테이블로 표시
        dept_df = pd.DataFrame(departments)
        if not dept_df.empty:
            st.dataframe(dept_df[["name", "category"]], use_container_width=True)
        
        # 학과 선택
        selected_dept_id = st.selectbox(
            "상세 정보를 볼 학과 선택",
            options=[dept["id"] for dept in departments],
            format_func=lambda x: next((dept["name"] for dept in departments if dept["id"] == x), "")
        )
        
        if st.button("학과 정보 보기"):
            # 선택한 학과 정보 가져오기
            selected_dept = next((dept for dept in departments if dept["id"] == selected_dept_id), None)
            if selected_dept:
                st.session_state.selected_department = selected_dept
                # 실제 구현에서는 API 호출로 상세 정보를 가져옴
                # dept_detail = self.api.get_department_detail(selected_dept_id)
    
    def _show_department_detail(self, department):
        """학과 상세 정보 표시"""
        st.subheader(f"{department['name']} 정보")
        
        # 예시 데이터 (실제 구현 시 API 응답으로 대체)
        dept_detail = {
            "id": department["id"],
            "name": department["name"],
            "category": department["category"],
            "description": f"{department['name']}는 {department['category']}에 속하는 학과로, 다양한 커리큘럼을 제공합니다.",
            "curriculum": [
                "기초 과목 1",
                "기초 과목 2",
                "심화 과목 1",
                "심화 과목 2",
                "실습 과목"
            ],
            "career_paths": [
                "진로 경로 1",
                "진로 경로 2",
                "진로 경로 3"
            ],
            "related_jobs": [
                "관련 직업 1",
                "관련 직업 2",
                "관련 직업 3"
            ],
            "universities": [
                {"id": "1", "name": "서울대학교"},
                {"id": "2", "name": "연세대학교"},
                {"id": "3", "name": "고려대학교"}
            ]
        }
        
        # 학과 정보 표시
        st.write(f"**계열:** {dept_detail['category']}")
        st.write(f"**학과 소개:**")
        st.write(dept_detail['description'])
        
        # 교육과정
        st.subheader("주요 교육과정")
        for curriculum in dept_detail['curriculum']:
            st.write(f"- {curriculum}")
        
        # 진로 경로
        st.subheader("주요 진로 경로")
        for path in dept_detail['career_paths']:
            st.write(f"- {path}")
        
        # 관련 직업
        st.subheader("관련 직업")
        for job in dept_detail['related_jobs']:
            st.write(f"- {job}")
        
        # 학과가 있는 대학
        st.subheader("학과가 있는 주요 대학")
        for univ in dept_detail['universities']:
            st.write(f"- {univ['name']}")
        
        # 관심 학과 저장 버튼
        if st.button("관심 학과로 저장"):
            self._save_department_only(dept_detail)
    
    def _save_school(self, school_detail):
        """관심 학교 저장"""
        saved_schools = self.user_info['data'].get('saved_schools', [])
        
        # 학교 정보 구성
        school_info = {
            'school_id': school_detail['id'],
            'school_name': school_detail['name'],
            'school_type': school_detail['type'],
            'region': school_detail['region'],
            'department_name': '',
            'saved_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        # 중복 저장 방지
        if not any(school['school_id'] == school_detail['id'] and not school['department_name'] for school in saved_schools):
            saved_schools.append(school_info)
            self.user_info['data']['saved_schools'] = saved_schools
            
            # Firestore에 저장
            self.db.collection("users").document(
                self.user_info['user_id']
            ).update({'saved_schools': saved_schools})
            
            st.success(f"{school_detail['name']}이(가) 관심 학교로 저장되었습니다!")
        else:
            st.info(f"{school_detail['name']}은(는) 이미 저장된 학교입니다.")
    
    def _save_department(self, school, department):
        """관심 학교-학과 조합 저장"""
        saved_schools = self.user_info['data'].get('saved_schools', [])
        
        # 학교-학과 정보 구성
        school_dept_info = {
            'school_id': school['id'],
            'school_name': school['name'],
            'school_type': school['type'],
            'region': school['region'],
            'department_id': department['id'],
            'department_name': department['name'],
            'saved_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        # 중복 저장 방지
        if not any(s['school_id'] == school['id'] and s.get('department_id') == department['id'] for s in saved_schools):
            saved_schools.append(school_dept_info)
            self.user_info['data']['saved_schools'] = saved_schools
            
            # Firestore에 저장
            self.db.collection("users").document(
                self.user_info['user_id']
            ).update({'saved_schools': saved_schools})
            
            st.success(f"{school['name']}의 {department['name']}이(가) 관심 학교/학과로 저장되었습니다!")
        else:
            st.info(f"{school['name']}의 {department['name']}은(는) 이미 저장된 학교/학과입니다.")
    
    def _save_department_only(self, department_detail):
        """관심 학과만 저장 (학교 정보 없이)"""
        saved_schools = self.user_info['data'].get('saved_schools', [])
        
        # 학과 정보 구성
        dept_info = {
            'school_id': '',
            'school_name': '',
            'school_type': '',
            'region': '',
            'department_id': department_detail['id'],
            'department_name': department_detail['name'],
            'saved_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        # 중복 저장 방지
        if not any(s.get('department_id') == department_detail['id'] and not s['school_name'] for s in saved_schools):
            saved_schools.append(dept_info)
            self.user_info['data']['saved_schools'] = saved_schools
            
            # Firestore에 저장
            self.db.collection("users").document(
                self.user_info['user_id']
            ).update({'saved_schools': saved_schools})
            
            st.success(f"{department_detail['name']}이(가) 관심 학과로 저장되었습니다!")
        else:
            st.info(f"{department_detail['name']}은(는) 이미 저장된 학과입니다.")

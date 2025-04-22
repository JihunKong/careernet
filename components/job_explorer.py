import streamlit as st
import pandas as pd
from datetime import datetime

class JobExplorer:
    """직업백과 탐색 관련 기능을 담당하는 클래스"""
    
    def __init__(self, api, db, user_info):
        self.api = api
        self.db = db
        self.user_info = user_info
    
    def show(self):
        """직업백과 탐색 페이지 표시"""
        st.header('직업백과 탐색')
        
        # 검색 필터
        st.subheader("직업 검색")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 직업 분야 선택
            categories = [
                "전체",
                "경영·사무·금융·보험",
                "교육·법률·사회복지·경찰·소방·군인",
                "보건·의료",
                "예술·디자인·방송·스포츠",
                "미용·여행·숙박·음식·경비·청소",
                "영업·판매·운전·운송",
                "건설·채굴",
                "설치·정비·생산",
                "농림어업",
                "IT·인터넷"
            ]
            selected_category = st.selectbox("직업 분야", categories)
        
        with col2:
            # 키워드 검색
            keyword = st.text_input("직업명 검색")
        
        if st.button("검색"):
            if selected_category == "전체":
                category_param = None
            else:
                category_param = selected_category
            
            # 직업 목록 가져오기
            jobs = self._get_jobs(category_param, keyword)
            
            if jobs:
                st.session_state.job_search_results = jobs
            else:
                st.warning("검색 결과가 없습니다. 다른 검색어로 시도해보세요.")
        
        # 검색 결과 표시
        if 'job_search_results' in st.session_state:
            self._show_job_list(st.session_state.job_search_results)
        
        # 직업 상세 정보 표시
        if 'selected_job' in st.session_state:
            self._show_job_detail(st.session_state.selected_job)
    
    def _get_jobs(self, category=None, keyword=None):
        """API에서 직업 목록 가져오기"""
        # 실제 API 연동 시 아래 코드 사용
        # response = self.api.get_job_list(category, keyword)
        # return response.get("jobs", [])
        
        # 예시 데이터
        jobs = [
            {"id": "1", "name": "소프트웨어 개발자", "category": "IT·인터넷"},
            {"id": "2", "name": "데이터 과학자", "category": "IT·인터넷"},
            {"id": "3", "name": "인공지능 전문가", "category": "IT·인터넷"},
            {"id": "4", "name": "웹 디자이너", "category": "예술·디자인·방송·스포츠"},
            {"id": "5", "name": "마케팅 전문가", "category": "경영·사무·금융·보험"},
            {"id": "6", "name": "교사", "category": "교육·법률·사회복지·경찰·소방·군인"},
            {"id": "7", "name": "의사", "category": "보건·의료"},
            {"id": "8", "name": "간호사", "category": "보건·의료"}
        ]
        
        # 카테고리와 키워드로 필터링
        filtered_jobs = jobs
        
        if category:
            filtered_jobs = [job for job in filtered_jobs if job["category"] == category]
        
        if keyword:
            filtered_jobs = [job for job in filtered_jobs if keyword.lower() in job["name"].lower()]
        
        return filtered_jobs
    
    def _show_job_list(self, jobs):
        """직업 목록 표시"""
        st.subheader(f"검색 결과: {len(jobs)}개의 직업")
        
        # 직업 목록을 테이블로 표시
        job_df = pd.DataFrame(jobs)
        if not job_df.empty:
            st.dataframe(job_df[["name", "category"]], use_container_width=True)
        
        # 직업 선택
        selected_job_id = st.selectbox(
            "상세 정보를 볼 직업 선택",
            options=[job["id"] for job in jobs],
            format_func=lambda x: next((job["name"] for job in jobs if job["id"] == x), "")
        )
        
        if st.button("상세 정보 보기"):
            # 선택한 직업 정보 가져오기
            selected_job = next((job for job in jobs if job["id"] == selected_job_id), None)
            if selected_job:
                st.session_state.selected_job = selected_job
                # 실제 구현에서는 API 호출로 상세 정보를 가져옴
                # job_detail = self.api.get_job_detail(selected_job_id)
                # st.session_state.selected_job_detail = job_detail
    
    def _show_job_detail(self, job):
        """직업 상세 정보 표시"""
        st.subheader(f"{job['name']} 상세 정보")
        
        # 실제 API 연동 시 아래 코드 사용
        # job_detail = self.api.get_job_detail(job['id'])
        
        # 예시 데이터 (실제 구현 시 API 응답으로 대체)
        job_detail = {
            "id": job["id"],
            "name": job["name"],
            "category": job["category"],
            "description": f"{job['name']}는 {job['category']} 분야의 직업으로, 다양한 업무를 수행합니다.",
            "work_tasks": [
                "관련 업무 1",
                "관련 업무 2",
                "관련 업무 3"
            ],
            "required_skills": [
                "필요 기술 1",
                "필요 기술 2",
                "필요 기술 3"
            ],
            "education": {
                "high_school": 10,
                "college": 20,
                "university": 50,
                "graduate_school": 20
            },
            "salary_range": "3000만원 ~ 7000만원",
            "job_outlook": "향후 10년간 고용 증가 예상",
            "related_majors": ["관련 학과 1", "관련 학과 2", "관련 학과 3"]
        }
        
        # 직업 정보 표시
        st.write(f"**분야:** {job_detail['category']}")
        st.write(f"**직업 설명:**")
        st.write(job_detail['description'])
        
        # 업무 내용
        st.subheader("주요 업무")
        for task in job_detail['work_tasks']:
            st.write(f"- {task}")
        
        # 필요 역량
        st.subheader("필요 역량 및 기술")
        for skill in job_detail['required_skills']:
            st.write(f"- {skill}")
        
        # 학력 분포
        st.subheader("학력 분포")
        education_df = pd.DataFrame({
            '학력': list(job_detail['education'].keys()),
            '비율': list(job_detail['education'].values())
        })
        st.bar_chart(education_df.set_index('학력'))
        
        # 급여 정보
        st.subheader("급여 범위")
        st.write(job_detail['salary_range'])
        
        # 직업 전망
        st.subheader("직업 전망")
        st.write(job_detail['job_outlook'])
        
        # 관련 학과
        st.subheader("관련 학과")
        for major in job_detail['related_majors']:
            st.write(f"- {major}")
        
        # 관심 직업 저장 버튼
        if st.button("관심 직업으로 저장"):
            self._save_job(job_detail)
    
    def _save_job(self, job_detail):
        """관심 직업 저장"""
        saved_jobs = self.user_info['data'].get('saved_jobs', [])
        
        # 직업 정보 구성
        job_info = {
            'job_id': job_detail['id'],
            'job_name': job_detail['name'],
            'job_category': job_detail['category'],
            'job_description': job_detail['description'],
            'saved_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        # 중복 저장 방지
        if not any(job['job_id'] == job_detail['id'] for job in saved_jobs):
            saved_jobs.append(job_info)
            self.user_info['data']['saved_jobs'] = saved_jobs
            
            # Firestore에 저장
            self.db.collection("users").document(
                self.user_info['user_id']
            ).update({'saved_jobs': saved_jobs})
            
            st.success(f"{job_detail['name']}이(가) 관심 직업으로 저장되었습니다!")
        else:
            st.info(f"{job_detail['name']}은(는) 이미 저장된 직업입니다.")

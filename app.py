import os
import json
import requests
from datetime import datetime

import streamlit as st

# 페이지 설정 (반드시 다른 st 명령어보다 먼저 호출해야 함)
st.set_page_config(
    page_title="나만의 진로 탐색 로드맵",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import auth as firebase_auth

# Firebase 설정
firebase_config = {
    "apiKey": "AIzaSyBUd8mS_PlgU6yBoqliAP93akYIHpcJCBc",
    "authDomain": "careernet-b43ec.firebaseapp.com",
    "projectId": "careernet-b43ec",
    "databaseURL": "https://careernet-b43ec-default-rtdb.firebaseio.com",
    "storageBucket": "careernet-b43ec.firebasestorage.app",
    "messagingSenderId": "318261988853",
    "appId": "1:318261988853:web:8cf1f28fd438e497e524bc"
}

# Firebase Admin 초기화 (Firestore 접근용)
if 'firebase_admin_initialized' not in st.session_state:
    try:
        # Firebase Admin SDK 초기화 (Streamlit secrets에서 가져오기)
        firebase_creds = dict(st.secrets["firebase"])
        
        # 개인 키 형식 확인 및 수정
        if isinstance(firebase_creds["private_key"], str):
            firebase_creds["private_key"] = firebase_creds["private_key"].replace('\\n', '\n')
        
        # 이미 초기화된 앱이 있는지 확인
        try:
            app = firebase_admin.get_app()
            st.session_state.db = firestore.client()
            st.session_state.firebase_admin_initialized = True
        except ValueError:
            # 앱이 초기화되지 않은 경우 초기화
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            st.session_state.db = firestore.client()
            st.session_state.firebase_admin_initialized = True
    except Exception as e:
        st.error(f"Firebase Admin SDK 초기화 오류: {e}")

# 커리어넷 API 관련 모듈 가져오기
try:
    from utils.api_requests import CareerNetAPI
    from components.psychological_tests import PsychologicalTests
    from components.job_explorer import JobExplorer
    from components.school_department_info import SchoolDepartmentInfo
    from components.counseling_cases import CounselingCases
except ImportError as e:
    st.error(f"모듈 가져오기 오류: {e}")

# Pyrebase 초기화 (인증용)
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# 커리어넷 API 키 (Streamlit secrets에서 가져오기)
try:
    CAREER_API_KEY = st.secrets["careernet"]["api_key"]
    career_api = CareerNetAPI(CAREER_API_KEY)
except Exception as e:
    st.warning(f"API 키 설정 오류: {e}. 직접 설정한 API 키를 사용합니다.")
    # 직접 API 키 설정 (secrets.toml에서 로드 실패 시 사용)
    CAREER_API_KEY = "90747c26b8d3bc27dc18e2cfdf49f8b7"
    career_api = CareerNetAPI(CAREER_API_KEY)

# 세션 상태 초기화
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# 로그인 상태 확인
def check_login_state():
    if st.session_state.user_info is not None:
        return True
    return False

# 로그인 페이지
def login_page():
    st.title("진로 탐색 로드맵 - 로그인")
    
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        email = st.text_input("이메일", key="login_email")
        password = st.text_input("비밀번호", type="password", key="login_password")
        
        if st.button("로그인"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                
                # Firestore에서 사용자 데이터 가져오기
                if 'firebase_admin_initialized' in st.session_state:
                    user_doc = st.session_state.db.collection("users").document(user['localId']).get()
                    
                    if user_doc.exists:
                        user_data = user_doc.to_dict()
                    else:
                        # 사용자 문서가 없으면 기본 데이터 생성
                        user_data = {
                            'name': '',
                            'grade': '',
                            'interests': [],
                            'test_results': {},
                            'saved_jobs': [],
                            'saved_schools': []
                        }
                        # Firestore에 저장
                        st.session_state.db.collection("users").document(user['localId']).set(user_data)
                    
                    st.session_state.user_info = {
                        'token': user['idToken'],
                        'user_id': user['localId'],
                        'data': user_data
                    }
                    st.success("로그인 성공!")
                    st.rerun()
                else:
                    st.error("Firebase 초기화 오류. 서비스 계정 키를 확인해주세요.")
            except Exception as e:
                st.error(f"로그인 실패: {e}")
    
    with tab2:
        new_email = st.text_input("이메일", key="signup_email", placeholder="example@example.com")
        new_password = st.text_input("비밀번호", type="password", key="signup_password", help="6자 이상의 비밀번호를 입력하세요")
        new_name = st.text_input("이름")
        
        if st.button("회원가입"):
            # 이메일 형식 검증
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            if not re.match(email_pattern, new_email):
                st.error("유효한 이메일 주소를 입력해주세요.")
            elif len(new_password) < 6:
                st.error("비밀번호는 최소 6자 이상이어야 합니다.")
            elif not new_name.strip():
                st.error("이름을 입력해주세요.")
            else:
                try:
                    # Firebase Authentication으로 사용자 생성
                    user = auth.create_user_with_email_and_password(new_email, new_password)
                    
                    # 초기 사용자 데이터 생성
                    user_data = {
                        'name': new_name,
                        'grade': '',
                        'interests': [],
                        'test_results': {},
                        'saved_jobs': [],
                        'saved_schools': []
                    }
                    
                    # Firestore에 사용자 정보 저장
                    if 'firebase_admin_initialized' in st.session_state:
                        st.session_state.db.collection("users").document(user['localId']).set(user_data)
                        st.success("회원가입 성공! 이제 로그인할 수 있습니다.")
                    else:
                        st.error("Firebase 초기화 오류. 서비스 계정 키를 확인해주세요.")
                except Exception as e:
                    error_message = str(e)
                    if "INVALID_EMAIL" in error_message:
                        st.error("유효하지 않은 이메일 형식입니다.")
                    elif "EMAIL_EXISTS" in error_message:
                        st.error("이미 등록된 이메일입니다.")
                    elif "WEAK_PASSWORD" in error_message:
                        st.error("비밀번호가 너무 약합니다. 6자 이상의 비밀번호를 사용하세요.")
                    else:
                        st.error(f"회원가입 실패: {e}")

# 로그아웃 함수
def logout():
    st.session_state.user_info = None
    st.success("로그아웃 되었습니다.")
    st.rerun()

# 메인 앱
def main_app():
    st.title(f"안녕하세요, {st.session_state.user_info['data']['name']}님!")
    
    # 사이드바 메뉴
    st.sidebar.title('나의 진로 탐색')
    page = st.sidebar.radio('메뉴 선택', 
        ['메인 화면', '진로심리검사', '직업백과 탐색', '학교/학과 정보', '진로상담 사례', 'AI 진로 추천'])
    
    # 로그아웃 버튼
    if st.sidebar.button("로그아웃"):
        logout()
    
    if page == '메인 화면':
        st.header('나만의 진로 탐색 로드맵')
        
        # 기본 정보 수정
        st.subheader('기본 정보')
        name = st.text_input('이름', st.session_state.user_info['data']['name'])
        grade_options = ['중학교 1학년', '중학교 2학년', '중학교 3학년', 
                        '고등학교 1학년', '고등학교 2학년', '고등학교 3학년']
        
        grade_index = 0
        if st.session_state.user_info['data']['grade'] in grade_options:
            grade_index = grade_options.index(st.session_state.user_info['data']['grade'])
        
        grade = st.selectbox('학년', grade_options, index=grade_index)
        
        interests = st.multiselect(
            '관심 분야',
            ['과학', '기술', '공학', '예술', '수학', '인문학', '사회과학', '경영', '의학', '법학'],
            default=st.session_state.user_info['data'].get('interests', [])
        )
        
        if st.button('정보 저장'):
            # 사용자 데이터 업데이트
            user_data = st.session_state.user_info['data']
            user_data['name'] = name
            user_data['grade'] = grade
            user_data['interests'] = interests
            
            # Firestore에 저장
            st.session_state.db.collection("users").document(st.session_state.user_info['user_id']).update(user_data)
            
            # 세션 상태 업데이트
            st.session_state.user_info['data'] = user_data
            
            st.success('정보가 저장되었습니다!')
        
        # 진행 상황 표시
        st.subheader('나의 진로 탐색 현황')
        col1, col2, col3 = st.columns(3)
        
        test_results = st.session_state.user_info['data'].get('test_results', {})
        saved_jobs = st.session_state.user_info['data'].get('saved_jobs', [])
        saved_schools = st.session_state.user_info['data'].get('saved_schools', [])
        
        with col1:
            st.metric("완료한 심리검사", f"{len(test_results)}/5")
        with col2:
            st.metric("저장한 관심 직업", f"{len(saved_jobs)}")
        with col3:
            st.metric("저장한 관심 학교/학과", f"{len(saved_schools)}")
        
        # 관심 직업 목록 표시
        if saved_jobs:
            st.subheader("관심 직업 목록")
            for job in saved_jobs:
                st.write(f"- {job['job_name']}: {job['job_description']}")
        
        # 관심 학교/학과 목록 표시
        if saved_schools:
            st.subheader("관심 학교/학과 목록")
            for school in saved_schools:
                st.write(f"- {school['school_name']}: {school['department_name']}")
    
    elif page == '진로심리검사':
        tests = PsychologicalTests(career_api, st.session_state.db, st.session_state.user_info)
        tests.show()
    
    elif page == '직업백과 탐색':
        job_explorer = JobExplorer(career_api, st.session_state.db, st.session_state.user_info)
        job_explorer.show()
    
    elif page == '학교/학과 정보':
        school_info = SchoolDepartmentInfo(career_api, st.session_state.db, st.session_state.user_info)
        school_info.show()
    
    elif page == '진로상담 사례':
        counseling = CounselingCases(career_api, st.session_state.db, st.session_state.user_info)
        counseling.show()
    
    elif page == 'AI 진로 추천':
        st.header('AI 진로 추천')
        
        st.subheader('흥미와 적성에 맞는 직업 추천')
        
        # 기존 심리검사 결과 및 관심 분야 기반 추천
        if not st.session_state.user_info['data'].get('test_results'):
            st.warning('진로심리검사를 먼저 완료해주세요. 더 정확한 추천을 받을 수 있습니다.')
        
        # 관심 분야에 따른 추천
        st.write('관심 분야에 기반한 직업 추천:')
        
        user_interests = st.session_state.user_info['data'].get('interests', [])
        if not user_interests:
            st.warning('관심 분야를 먼저 설정해주세요.')
        else:
            # 실제 구현에서는 API 호출 또는 데이터베이스에서 관련 직업을 가져옴
            # 예시 데이터
            for interest in user_interests:
                st.subheader(f"{interest} 관련 추천 직업")
                if interest == '과학':
                    jobs = ['연구원', '생물학자', '화학자', '천문학자']
                elif interest == '기술':
                    jobs = ['소프트웨어 개발자', '데이터 과학자', '시스템 관리자']
                elif interest == '공학':
                    jobs = ['기계공학자', '전기공학자', '토목공학자', '항공우주공학자']
                elif interest == '예술':
                    jobs = ['그래픽 디자이너', '웹 디자이너', '미술가', '음악가']
                elif interest == '수학':
                    jobs = ['수학자', '통계학자', '보험계리사', '데이터 분석가']
                elif interest == '인문학':
                    jobs = ['작가', '번역가', '역사학자', '철학자']
                elif interest == '사회과학':
                    jobs = ['심리학자', '사회학자', '경제학자', '정치학자']
                elif interest == '경영':
                    jobs = ['경영컨설턴트', '마케팅 매니저', '인사 관리자', '재무 분석가']
                elif interest == '의학':
                    jobs = ['의사', '간호사', '약사', '의료기술자']
                elif interest == '법학':
                    jobs = ['변호사', '법무사', '검사', '판사']
                else:
                    jobs = []
                
                for job in jobs:
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button(f"저장 {job}", key=f"save_{job}"):
                            # 직업 저장 로직
                            saved_jobs = st.session_state.user_info['data'].get('saved_jobs', [])
                            job_info = {
                                'job_name': job,
                                'job_description': f"{interest} 관련 직업",
                                'saved_date': datetime.now().strftime("%Y-%m-%d")
                            }
                            
                            # 중복 저장 방지
                            if not any(j['job_name'] == job for j in saved_jobs):
                                saved_jobs.append(job_info)
                                st.session_state.user_info['data']['saved_jobs'] = saved_jobs
                                
                                # Firestore에 저장
                                st.session_state.db.collection("users").document(
                                    st.session_state.user_info['user_id']
                                ).update({'saved_jobs': saved_jobs})
                                
                                st.success(f"{job}이(가) 관심 직업으로 저장되었습니다!")
                            else:
                                st.info(f"{job}은(는) 이미 저장된 직업입니다.")
                    
                    with col2:
                        st.write(f"{job} - {interest} 분야 관련 직업")

# 메인 실행 부분
def main():
    if check_login_state():
        main_app()
    else:
        login_page()

if __name__ == "__main__":
    main()

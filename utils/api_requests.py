import requests
import json

class CareerNetAPI:
    """커리어넷 API 호출을 담당하는 클래스"""
    
    BASE_URL = "https://www.career.go.kr/cnet/openapi/api"
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def _make_request(self, endpoint, params=None, method="GET", data=None):
        """API 요청 실행"""
        if params is None:
            params = {}
        
        # API 키 추가
        params["apiKey"] = self.api_key
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                response = requests.post(url, params=params, json=data)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메소드: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return {"error": str(e)}
    
    # 진로심리검사 관련 API
    def get_psychological_tests(self):
        """진로심리검사 목록 조회"""
        return self._make_request("psychTest")
    
    def get_psychological_test_questions(self, test_id):
        """진로심리검사 문항 조회"""
        # 커리어넷 API 문서에 따라 엔드포인트 수정
        # 1. 기존 방식 시도
        result = self._make_request(f"psychTest/{test_id}/questions")
        if "error" in result or not result.get("questions"):
            # 2. 대체 방식 시도 (검사 유형 코드 사용)
            result = self._make_request(f"inspct/question/{test_id}")
            if "error" in result or not result.get("questions"):
                # 3. 또 다른 대체 방식 시도
                result = self._make_request(f"inspct/question", params={"seq": test_id})
        
        # 디버깅을 위한 로그 추가
        print(f"API 응답: {result}")
        return result
    
    def submit_psychological_test(self, test_id, answers):
        """진로심리검사 결과 요청"""
        return self._make_request(f"psychTest/{test_id}/results", method="POST", data=answers)
    
    # 직업백과 관련 API
    def get_job_list(self, category=None, keyword=None):
        """직업백과 목록 조회"""
        params = {}
        if category:
            params["category"] = category
        if keyword:
            params["keyword"] = keyword
        
        return self._make_request("job", params=params)
    
    def get_job_detail(self, job_id):
        """직업백과 상세 정보 조회"""
        return self._make_request(f"job/{job_id}")
    
    # 학교/학과 정보 관련 API
    def get_schools(self, school_type=None, region=None, name=None):
        """학교 정보 조회"""
        params = {}
        if school_type:
            params["schoolType"] = school_type
        if region:
            params["region"] = region
        if name:
            params["name"] = name
        
        return self._make_request("school", params=params)
    
    def get_departments(self, category=None, name=None):
        """학과 정보 조회"""
        params = {}
        if category:
            params["category"] = category
        if name:
            params["name"] = name
        
        return self._make_request("department", params=params)
    
    def get_department_detail(self, department_id):
        """학과 상세 정보 조회"""
        return self._make_request(f"department/{department_id}")
    
    # 진로상담 사례 관련 API
    def get_counseling_cases(self, keyword=None, category=None, page=1, size=10):
        """진로상담 사례 조회"""
        params = {
            "page": page,
            "size": size
        }
        if keyword:
            params["keyword"] = keyword
        if category:
            params["category"] = category
        
        return self._make_request("counseling", params=params)
    
    def get_counseling_detail(self, case_id):
        """진로상담 사례 상세 조회"""
        return self._make_request(f"counseling/{case_id}")

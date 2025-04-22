import requests
import json

class CareerNetAPI:
    """커리어넷 API 요청 클래스"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        # 기본 URL 수정 (v1 API용)
        self.base_url = "https://www.career.go.kr/inspct/openapi/"
        # v2 API용 URL
        self.base_url_v2 = "https://www.career.go.kr/inspct/openapi/v2/"
    
    def _make_request(self, endpoint, params=None, method="GET", data=None, use_v2=False):
        """API 요청 처리"""
        if params is None:
            params = {}
        
        # API 키 추가 (v1 API는 apikey, v2 API는 apiKey)
        if use_v2:
            params["apikey"] = self.api_key
            base = self.base_url_v2
        else:
            params["apikey"] = self.api_key
            base = self.base_url
        
        url = f"{base}{endpoint}"
        
        try:
            print(f"API 요청 URL: {url}")
            print(f"API 요청 파라미터: {params}")
            
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                response = requests.post(url, params=params, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            print(f"API 응답 상태 코드: {response.status_code}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return {"error": str(e)}
    
    # 진로심리검사 관련 API
    def get_psychological_tests(self):
        """진로심리검사 목록 조회 (v2 API)"""
        return self._make_request("tests", use_v2=True)
    
    def get_psychological_test_questions(self, test_id):
        """진로심리검사 문항 조회"""
        # 커리어넷 API 문서에 따라 엔드포인트 수정
        # 1. v1 API 방식 시도 - 문서에 명시된 방식
        result = self._make_request("test/questions", params={"q": test_id})
        if "error" in result or not result.get("RESULT"):
            # 2. v2 API 방식 시도
            result = self._make_request("test", params={"q": test_id}, use_v2=True)
            if "error" in result or not result.get("result"):
                # 3. 다른 가능한 엔드포인트 시도
                result = self._make_request(f"test/questions/{test_id}")
                if "error" in result or not result.get("RESULT") and not result.get("questions"):
                    # 4. 또 다른 대체 방식 시도
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

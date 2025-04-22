import requests
import json
import time

class CareerNetAPI:
    """커리어넷 API 요청 클래스"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        # 기본 URL
        self.base_url = "https://www.career.go.kr/"
        
        print(f"API 키 초기화: {api_key}")
    
    def _make_request(self, url, params=None, method="GET", data=None):
        """API 요청 처리"""
        if params is None:
            params = {}
        
        # API 키 추가
        params["apikey"] = self.api_key
        
        full_url = url
        if params and method == "GET":
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_str}"
        
        try:
            print(f"\n==== API 요청 정보 ====")
            print(f"API 요청 URL: {url}")
            print(f"API 요청 파라미터: {params}")
            print(f"API 전체 URL: {full_url}")
            
            # 요청 헤더 추가
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json"
            }
            
            # 재시도 로직 추가
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    if method == "GET":
                        response = requests.get(url, params=params, headers=headers, timeout=10)
                    elif method == "POST":
                        response = requests.post(url, params=params, json=data, headers=headers, timeout=10)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")
                    
                    print(f"API 응답 상태 코드: {response.status_code}")
                    
                    # 응답 본문 출력 (디버깅용)
                    response_text = response.text[:500]  # 처음 500자만 출력
                    print(f"API 응답 본문 (일부): {response_text}")
                    
                    # 성공적인 응답이면 JSON으로 변환
                    if response.status_code == 200:
                        return response.json()
                    else:
                        print(f"API 요청 실패 (상태 코드: {response.status_code})")
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"{retry_count}번째 재시도 (총 {max_retries}회 중)...")
                            time.sleep(1)  # 1초 대기 후 재시도
                        else:
                            return {"error": f"API 요청 실패 (상태 코드: {response.status_code})"}
                
                except Exception as e:
                    print(f"API 요청 중 오류 발생: {e}")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"{retry_count}번째 재시도 (총 {max_retries}회 중)...")
                        time.sleep(1)  # 1초 대기 후 재시도
                    else:
                        return {"error": str(e)}
            
            return {"error": "Maximum retries exceeded"}
            
        except Exception as e:
            print(f"API 요청 오류: {e}")
            return {"error": str(e)}
    
    # 진로심리검사 관련 API
    def get_psychological_tests(self):
        """진로심리검사 목록 조회"""
        # v2 API 시도
        v2_url = f"{self.base_url}inspct/openapi/v2/tests"
        result = self._make_request(v2_url)
        
        # v2 API 실패시 v1 API 시도
        if "error" in result:
            v1_url = f"{self.base_url}inspct/openapi/test/list"
            result = self._make_request(v1_url)
        
        return result
    
    def get_psychological_test_questions(self, test_id):
        """진로심리검사 문항 조회"""
        # 커리어넷 API 문서에 따라 정확한 URL 사용
        
        # 중요: API 키는 'apikey'가 아닌 'apiKey'로 전달해야 함
        
        # 1. v1 API 시도 - 문서에 명시된 정확한 URL
        # https://www.career.go.kr/inspct/openapi/test/questions?apikey=인증키&q=심리검사번호
        print(f"\n==== 진로심리검사 문항 요청 (v1) ====")
        print(f"API 키: {self.api_key}")
        print(f"검사 ID: {test_id}")
        
        # 직접 요청 시도 (requests 라이브러리 사용)
        v1_url = f"https://www.career.go.kr/inspct/openapi/test/questions"
        params = {"apiKey": self.api_key, "q": test_id}  # apiKey로 변경
        
        try:
            print(f"\n전체 URL: {v1_url}?apiKey={self.api_key}&q={test_id}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            response = requests.get(v1_url, params=params, headers=headers, timeout=10)
            print(f"API 응답 상태 코드: {response.status_code}")
            print(f"API 응답 헤더: {response.headers}")
            
            # 응답 본문 출력 (디버깅용)
            response_text = response.text[:500]  # 처음 500자만 출력
            print(f"API 응답 본문 (일부): {response_text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if "RESULT" in result:
                        return result
                except Exception as json_error:
                    print(f"JSON 파싱 오류: {json_error}")
            
            # v1 API 실패시 v2 API 시도
            print(f"\n==== 진로심리검사 문항 요청 (v2) ====")
            v2_url = "https://www.career.go.kr/inspct/openapi/v2/test"
            v2_params = {"apikey": self.api_key, "q": test_id}
            
            print(f"\n전체 URL: {v2_url}?apikey={self.api_key}&q={test_id}")
            v2_response = requests.get(v2_url, params=v2_params, headers=headers, timeout=10)
            print(f"v2 API 응답 상태 코드: {v2_response.status_code}")
            
            v2_text = v2_response.text[:500]
            print(f"v2 API 응답 본문 (일부): {v2_text}")
            
            if v2_response.status_code == 200:
                try:
                    result = v2_response.json()
                    return result
                except Exception as json_error:
                    print(f"v2 JSON 파싱 오류: {json_error}")
            
            # 두 API 모두 실패한 경우
            return {"error": "API 요청 실패"}
            
        except Exception as e:
            print(f"API 요청 오류: {e}")
            return {"error": str(e)}
    
    def submit_psychological_test(self, test_id, answers):
        """진로심리검사 결과 요청"""
        # 문서에 따라 정확한 URL 사용
        # https://www.career.go.kr/inspct/openapi/test/report?apikey=인증키&qestrnSeq=심리검사번호
        url = f"{self.base_url}inspct/openapi/test/report"
        params = {"apikey": self.api_key, "qestrnSeq": test_id}
        return self._make_request(url, params=params, method="POST", data=answers)
    
    # 직업백과 관련 API
    def get_job_list(self, category=None, keyword=None):
        """직업백과 목록 조회"""
        url = f"{self.base_url}cnet/front/openapi/jobs.json"
        params = {}
        if category:
            params["searchJobCd"] = category
        if keyword:
            params["searchJobNm"] = keyword
        
        return self._make_request(url, params=params)
    
    def get_job_detail(self, job_id):
        """직업백과 상세 정보 조회"""
        url = f"{self.base_url}cnet/front/openapi/job.json"
        params = {"seq": job_id}
        return self._make_request(url, params=params)
    
    # 학교 및 학과 정보 API
    def get_schools(self, school_type=None, region=None, name=None):
        """학교 정보 조회"""
        url = f"{self.base_url}cnet/openapi/getOpenApi.json"
        params = {
            "svcType": "api",
            "svcCode": "SCHOOL",
            "contentType": "json"
        }
        if school_type:
            params["gubun"] = school_type
        if region:
            params["region"] = region
        if name:
            params["searchSchulNm"] = name
        
        return self._make_request(url, params=params)
    
    def get_departments(self, category=None, name=None):
        """학과 정보 조회"""
        url = f"{self.base_url}cnet/openapi/getOpenApi.json"
        params = {
            "svcType": "api",
            "svcCode": "MAJOR",
            "contentType": "json"
        }
        if category:
            params["gubun"] = category
        if name:
            params["searchMajorNm"] = name
        
        return self._make_request(url, params=params)
    
    def get_department_detail(self, department_id):
        """학과 상세 정보 조회"""
        url = f"{self.base_url}cnet/openapi/getOpenApi.json"
        params = {
            "svcType": "api",
            "svcCode": "MAJOR_VIEW",
            "contentType": "json",
            "majorSeq": department_id
        }
        return self._make_request(url, params=params)
    
    # 진로상담 사례 API
    def get_counseling_cases(self, keyword=None, category=None, page=1, size=10):
        """진로상담 사례 조회"""
        url = f"{self.base_url}cnet/openapi/getOpenApi.json"
        params = {
            "svcType": "api",
            "svcCode": "COUNSEL",
            "contentType": "json",
            "thisPage": page,
            "perPage": size
        }
        if keyword:
            params["searchKeyword"] = keyword
        if category:
            params["searchCounselType"] = category
        
        return self._make_request(url, params=params)
    
    def get_counseling_detail(self, case_id):
        """진로상담 사례 상세 조회"""
        url = f"{self.base_url}cnet/openapi/getOpenApi.json"
        params = {
            "svcType": "api",
            "svcCode": "COUNSEL_VIEW",
            "contentType": "json",
            "seq": case_id
        }
        return self._make_request(url, params=params)

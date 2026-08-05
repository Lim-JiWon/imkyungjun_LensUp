<div align="center">

<img src="./FE_source_code/public/minwon-logo.png" width="150" alt="LensUp logo" />

LensUp

공공 민원 데이터로 사회문제의 조짐을 탐지하는 AI 분석 서비스

공공 민원 데이터를 자동으로 수집하고, 키워드 흐름과 위험 신호를 분석하여이슈 요약·전망·원인 후보·지역별 현황을 대시보드로 제공하는 캡스톤 프로젝트입니다.

🌐 서비스 바로가기 ·📊 분석 대시보드 ·🔍 민원 검색

<br />

<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black"/>
<img src="https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white"/>
<img src="https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white"/>
<img src="https://img.shields.io/badge/Leaflet-199900?style=flat-square&logo=leaflet&logoColor=white"/>

</div>

📌 프로젝트 소개

많은 민원 데이터에는 시민들이 반복적으로 겪는 불편과 사회문제의 초기 신호가 포함되어 있습니다.하지만 원본 데이터는 양이 많고 형태가 복잡하여, 사용자가 변화 흐름과 핵심 이슈를 빠르게 파악하기 어렵습니다.

LensUp은 국민권익위원회 민원 빅데이터 API에서 데이터를 수집한 뒤 다음 과정을 자동으로 수행합니다.

급등 키워드와 민원 관련 데이터 수집

응답 데이터 정제 및 공통 형식 변환

주요 키워드와 연관어 분석

AI 기반 이슈 요약·전망·위험도 생성

PostgreSQL 저장 및 REST API 제공

대시보드·지도·검색 화면으로 시각화

단순 민원 목록을 보여주는 것을 넘어,반복적으로 증가하는 키워드와 지역·기관 흐름을 통해 문제의 조짐을 빠르게 확인하는 것을 목표로 합니다.

✨ 주요 기능

1. 공공 민원 데이터 자동 수집

국민권익위원회 민원 빅데이터 API 연동

날짜 범위와 검색 키워드 기반 데이터 수집

여러 응답 구조를 공통 데이터 형식으로 변환

원본 응답 캐시 및 오류 확인 기능

2. 자동 키워드 탐색

여러 민원 데이터셋에서 주요 키워드 후보 수집

키워드 점수와 출처를 기반으로 처리 대상 선정

자동 탐색 실패 시 keywords.txt를 사용하는 fallback 처리

3. AI 기반 민원 이슈 분석

수집된 데이터를 바탕으로 구조화된 분석 결과를 생성합니다.

이슈 제목

핵심 요약

향후 전망

원인 후보

주요 키워드

상태 및 위험 단계

0~100 기준 이슈 점수

AI 응답을 정해진 스키마로 검증하고, API 키가 없거나 호출에 실패한 경우 mock 응답으로 전환할 수 있도록 구성했습니다.

4. 분석 대시보드

전체 이슈 수, 고위험 이슈 수, 평균 점수

최신 민원 이슈 카드

위험 단계와 민원 건수

카테고리별 이슈 현황

지역·기관별 민원 순위

대한민국 지도 기반 지역 데이터 시각화

5. 이슈 상세 분석

이슈 요약과 전망

주요·급상승·연관 키워드

원인 후보

기간별 키워드 추이

증가·감소·유지 흐름 판정

위험 신호 상태와 설명

6. 키워드 검색 및 검색 도우미

제목, 핵심 키워드, 연관어, 검색 별칭 등을 활용한 검색

일반적인 불용어와 노이즈 검색어 제거

의미가 유사한 키워드 매칭

자연어 문장에서 키워드를 추출하는 검색 도우미

관련 민원 주제와 상세 페이지 연결

🏗️ 서비스 아키텍처

flowchart LR
    A[국민권익위원회<br/>민원 빅데이터 API]
    B[Backend 1<br/>데이터 수집·전처리]
    C[AI 분석<br/>요약·전망·위험도]
    D[Backend 2<br/>FastAPI]
    E[(PostgreSQL)]
    F[React Web<br/>대시보드·검색·지도]

    A --> B
    B --> C
    C -->|JSON Payload| D
    D --> E
    E --> D
    D -->|REST API| F

데이터 처리 흐름

공공데이터 수집
→ 데이터 형식 정리
→ 키워드 및 민원 흐름 분석
→ AI 구조화 분석 결과 생성
→ Backend 2로 Payload 전송
→ PostgreSQL 저장
→ FastAPI 조회 API 제공
→ React 화면 시각화

👩‍💻 담당 역할 — 임지원

Backend 1 · 데이터 수집 및 분석 파이프라인

공공 민원 데이터 API 연동

날짜·키워드 기반 데이터 수집 로직 구현

서로 다른 API 응답 구조 정규화

수집 데이터 전처리 및 분석용 형식 변환

자동 키워드 탐색과 수동 키워드 fallback 구성

AI 입력 프롬프트 및 구조화 결과 스키마 구성

이슈 요약, 전망, 원인 후보, 키워드, 위험도 결과 생성

Backend 2 전달용 JSON Payload 생성

API Key 기반 서버 간 전송 및 실패 Payload 저장

데이터 파이프라인 통합 테스트 및 연동 확인

👥 팀 구성

Team 즉석의 낭만 · 3인 팀 프로젝트

역할

담당

주요 업무

Backend 1

임지원

공공데이터 수집, 전처리, 분석 결과 생성, 키워드 추출

Backend 2

박경수

FastAPI 서버, PostgreSQL DB 설계, REST API, 배포

Frontend

차도준

React UI, 대시보드, 지도 시각화, 사용자 흐름

🛠️ 기술 스택

Backend 1 — Data Pipeline

기술

활용 내용

Python

데이터 수집·전처리 및 파이프라인 구현

Requests

공공데이터 API와 Backend 2 통신

OpenAI API

민원 이슈 요약·전망·위험도 생성

Pydantic

AI 분석 결과 스키마 검증

python-dotenv

API Key와 환경변수 관리

JSON

서비스 간 분석 데이터 전달

Backend 2 — Server & Database

기술

활용 내용

FastAPI

민원 이슈 조회·검색·대시보드 API

PostgreSQL

분석 이슈, 키워드, 원인, 추이 데이터 저장

SQLAlchemy

ORM 기반 데이터베이스 연동

Pydantic

요청·응답 데이터 검증

CORS

프론트엔드와 API 서버 연결

Frontend

기술

활용 내용

React

컴포넌트 기반 사용자 화면

Vite

프론트엔드 개발 및 빌드

Axios

Backend API 호출

React Router

페이지 라우팅

Leaflet / React Leaflet

대한민국 지도 시각화

Lucide React

UI 아이콘

📂 프로젝트 구조

imkyungjun_LensUp/
├── BE1_source_code/                 # 데이터 수집·분석 파이프라인
│   ├── services/
│   │   ├── public_api_service.py    # 공공데이터 API 호출
│   │   ├── auto_keyword_service.py  # 자동 키워드 탐색
│   │   ├── data_formatter.py        # 데이터 정제
│   │   ├── gpt_service.py           # AI 분석
│   │   ├── payload_builder.py       # 전달 Payload 생성
│   │   └── backend2_sender.py       # Backend 2 전송
│   ├── main_pipeline.py             # 메인 분석 파이프라인
│   ├── main_dashboard_sync.py       # 대시보드 데이터 동기화
│   ├── keywords.txt                 # 수동 키워드 fallback
│   └── cache/                       # 수집·분석 캐시
│
├── BE2_source_code/                 # API 서버 및 데이터베이스
│   ├── models/                      # SQLAlchemy 모델
│   ├── routers/                     # API 라우터
│   ├── schemas/                     # 요청·응답 스키마
│   ├── services/                    # 저장 및 처리 서비스
│   ├── create_db.py                 # DB 테이블 생성
│   ├── database.py                  # PostgreSQL 연결
│   └── main.py                      # FastAPI 실행 진입점
│
├── FE_source_code/                  # React 웹 애플리케이션
│   ├── public/
│   ├── src/
│   │   ├── api/                     # Backend API 호출
│   │   ├── components/              # 공통 UI·지도·챗봇
│   │   ├── pages/                   # 서비스 페이지
│   │   └── styles/                  # CSS
│   └── package.json
│
└── README.md

🔌 주요 API

Method

Endpoint

설명

GET

/dashboard

대시보드 통계와 최신 이슈 조회

GET

/dashboard/map-data

지역·기관·카테고리 지도 데이터 조회

GET

/dashboard/region-rankings

지역별 민원 순위 조회

GET

/dashboard/categories

카테고리별 민원 이슈 조회

GET

/dashboard/{issue_id}

민원 이슈 상세 분석 조회

GET

/search

키워드 기반 민원 검색

POST

/chat/search-assistant

자연어 기반 민원 주제 검색

🚀 실행 방법

1. 저장소 복제

git clone https://github.com/Lim-JiWon/imkyungjun_LensUp.git
cd imkyungjun_LensUp

2. PostgreSQL 준비

BE2_source_code/database.py의 DATABASE_URL을 자신의 PostgreSQL 환경에 맞게 설정합니다.

DATABASE_URL = "postgresql://사용자명:비밀번호@localhost:5432/DB이름"

공개 저장소에서는 DB 비밀번호를 코드에 직접 작성하기보다 .env로 분리하는 것을 권장합니다.

3. Backend 2 실행

cd BE2_source_code

python -m venv .venv

Windows:

.venv\Scripts\activate

macOS / Linux:

source .venv/bin/activate

패키지 설치:

pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic

DB 테이블 생성:

python create_db.py

서버 실행:

uvicorn main:app --reload

API 문서:

http://127.0.0.1:8000/docs

4. Backend 1 환경변수 설정

BE1_source_code/.env 파일을 새로 생성합니다.

# 공공데이터 API
PUBLIC_API_SERVICE_KEY=발급받은_서비스키

# Backend 2 연결
BACKEND2_URL=http://127.0.0.1:8000
BACKEND2_API_KEY=서버간_통신_API_KEY

# AI 분석
OPENAI_ENABLED=true
OPENAI_API_KEY=발급받은_OpenAI_API_KEY
OPENAI_MODEL=사용할_모델명
OPENAI_USE_MOCK_FALLBACK=true

# 데이터 수집 기간
DATE_FROM=20260301
DATE_TO=20260331

# 자동 키워드 탐색
USE_AUTO_KEYWORD_DISCOVERY=true
AUTO_KEYWORD_LIMIT=5
AUTO_KEYWORD_RESULT_COUNT=10

API 키가 없는 경우 OPENAI_ENABLED=false로 설정하면 mock 분석 결과를 사용할 수 있습니다.

5. Backend 1 실행

새 터미널에서:

cd BE1_source_code

python -m venv .venv

Windows:

.venv\Scripts\activate

macOS / Linux:

source .venv/bin/activate

패키지 설치:

pip install requests python-dotenv openai pydantic

파이프라인 실행:

python main_pipeline.py

6. Frontend 실행

새 터미널에서:

cd FE_source_code
npm install
npm run dev

브라우저에서 아래 주소로 접속합니다.

http://localhost:5173

🖥️ 주요 화면

페이지

경로

설명

메인

/

서비스 소개와 핵심 이슈

민원 보기

/complaints

주제별 민원 탐색

대시보드

/dashboard

위험도, 민원 건수, 지도 분석

검색

/search

키워드 기반 이슈 검색

이슈 상세

/issues/:id

요약, 전망, 원인, 키워드 추이

시연 흐름

/demo

데이터 수집부터 화면 표시까지의 과정

기술 스택

/stack

서비스 아키텍처와 핵심 기술

팀 소개

/team

역할 분담과 협업 과정

🔐 보안 및 공개 저장소 주의사항

다음 값은 GitHub에 업로드하지 않습니다.

공공데이터 API Key

OpenAI API Key

Backend 간 통신 API Key

PostgreSQL 비밀번호

운영 서버 환경변수

개인 민원 원문 또는 개인정보

.env 파일은 .gitignore에 포함하고, 공개용 예시는 .env.example로 관리하는 것을 권장합니다.

🌱 개선 계획

DB 연결 정보를 환경변수로 완전히 분리

Backend별 requirements.txt 추가

실행 환경을 위한 Docker Compose 구성

데이터 수집 스케줄러 적용

자동 테스트와 CI/CD 구성

지도 및 시계열 시각화 고도화

검색어 유사어 사전 자동 확장

실제 운영 환경에 맞춘 CORS 설정

📎 참고

본 프로젝트는 한림대학교 소프트웨어 캡스톤디자인 팀 프로젝트입니다.

공개된 데이터와 집계 결과를 활용하며, 개별 민원인의 개인정보를 분석 대상으로 사용하지 않습니다.

AI 분석 결과는 공공 민원 흐름을 이해하기 위한 보조 정보이며, 확정적인 행정 판단을 의미하지 않습니다.

<div align="center">

민원 속 반복되는 신호를 발견하고, 이해하기 쉬운 정보로 연결합니다.

LensUp · Team 즉석의 낭만

</div>

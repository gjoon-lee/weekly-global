싱가포르 콘텐츠·엔터테인먼트 산업(게임, OTT, 영화·방송, 음악, 패션 IP, 테크 미디어) 뉴스를 일주일 단위로 자동 수집·분류·요약하여 Notion 데이터베이스로 보내는 파이프라인입니다

## 1. 개요
- 링크 수집 : Deep Research(OpenAI), Perplexity, NewsAPI, RSS 4가지 소스로부터 최근 7일 기사 URL 수집
- 관련성 판정 : 뉴스 주제 적합 여부를 Yes / No 로 평가
- 한국어 요약 : GPT‑4o‑mini로 한글 요약(헤드라인 / 핵심 포인트 / 시사점)
- Notion 업로드 : 이미 존재하는 URL은 건너뛰고 새 기사만 추가

## 2. API 키
`.env` 파일을 프로젝트 루트에 두고 아래 항목을 채워주세요!
- `OPEN_API_KEY`: 발급 방법 =>[OpenAI Platform] → Profile → API keys → Create new secret key
- `PPLX_API_KEY`: 발급 방법 => [Perplexity Dashboard] → API Keys → Generate
- `NEWSAPI_KEY`: 발급 방법 => [newsapi.org] 가입 → Get API key(선택 사항, 사용하지 않으면 빈 값 유지)
- `NOTION_TOKEN`: 발급 방법 => Notion → 설정 & 멤버 → Integrations → New integration 후 Internal Integration Token 복사
- `NOTION_DB_ID`: 발급 방법 => 통합을 공유한 데이터베이스 열기 → URL 중 마지막 32글자 복사

## 3. Notion 데이터베이스 준비
- 새 데이터베이스를 Table 형식으로 만들고 아래 속성을 생성합니다.
  - Name : 제목(Title)
  - URL  : URL(URL)
  - Summary : 요약(Rich text)
- 방금 만든 데이터베이스를 프로젝트용 Integration 과 공유합니다.
- 데이터베이스 오른쪽 상단 ••• → Add Connections → 통합 선택
- URL 끝부분의 32자리 ID를 NOTION_DB_ID 로 사용합니다.

## 4. 설치 및 실행
1) 저장소 클론
- $ git clone https://github.com/gjoon-lee/weekly-global.git
- $ cd weekly-global

2) 가상환경 생성 및 활성화
- $ python -m venv .venv
Windows
- $ .venv\Scripts\activate
macOS/Linux
- $ source .venv/bin/activate

3) 패키지 설치
- (.venv) $ pip install -r requirements.txt

4) .env 파일 작성 및 노션 데이터베이스 준비(위 설명 참고)

5) 파이프라인 실행
- (.venv) $ python gather_links.py




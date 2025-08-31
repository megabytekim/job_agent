# Job Agent

Agent-to-Agent (A2A) 프로토콜과 Model Context Protocol (MCP)을 활용한 스마트 AI 구직 어시스턴트로, 포괄적인 커리어 가이드와 구직 지원을 제공합니다.

## 설명

Job Agent는 구직자들의 커리어 조언, 구직 활동, 이력서 최적화, 면접 준비, 전문성 개발을 도와주는 지능형 커리어 어시스턴트입니다. [Agent-to-Agent (A2A) 프로토콜](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge?hl=ko#1)을 기반으로 하고 Model Context Protocol (MCP) 도구로 강화되어, 실시간 웹 검색 기능과 개인화된 커리어 가이드를 제공합니다.

새로운 기회를 적극적으로 찾고 있거나, 면접을 준비하고 있거나, 커리어 조언을 구하고 있다면, 이 도구는 AI 기반 대화와 실시간 정보 수집을 통해 지능적인 지원을 제공합니다.

## 주요 기능

- **A2A 프로토콜 지원**: 에이전트 카드 발견을 포함한 완전한 Agent-to-Agent 프로토콜 구현
- **내장 웹 채팅 UI**: 웹 브라우저를 통해 접근 가능한 인터랙티브 채팅 인터페이스
- **실시간 웹 검색**: DuckDuckGo를 사용한 MCP 기반 웹 검색 (API 키 불필요)
- **구직 도구**: 사용자 정의 검색 기준을 가진 모의 채용 추천
- **커리어 가이드**: 포괄적인 커리어 조언 및 전문성 개발 지원
- **한국어 지원**: 네이티브 한국어 인터페이스 및 응답
- **Cloud Run 배포**: CI/CD를 통한 Google Cloud Run 배포 준비 완료
- **MCP 통합**: 확장 가능한 기능을 위한 Model Context Protocol 도구
- **세션 관리**: 상호작용 간 지속적인 대화 컨텍스트

## 시작하기

### 사전 요구사항

- Python 3.12 이상
- 결제가 활성화된 Google Cloud Platform 계정
- Google Cloud CLI (gcloud) 설치
- Docker (컨테이너 배포용)
- uv 패키지 매니저 (권장)

### 설치

1. 저장소 클론:
   ```bash
   git clone https://github.com/megabytekim/job_agent.git
   cd job_agent
   ```

2. job-agent 디렉토리로 이동:
   ```bash
   cd job-agent
   ```

3. 의존성 설치:
   ```bash
   # uv 사용 (권장)
   uv sync
   
   # 또는 pip 사용
   pip install -r requirements.txt
   ```

4. Google Cloud 설정:
   ```bash
   # Google Cloud 인증
   gcloud auth login
   
   # 프로젝트 ID 설정
   gcloud config set project YOUR_PROJECT_ID
   
   # 필요한 API 활성화
   gcloud services enable run.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   ```

5. 환경 변수 설정:
   ```bash
   # 환경 변수 템플릿 복사 및 편집
   cp .env.example .env
   # .env 파일을 특정 설정으로 편집
   ```

## 사용법

### 아키텍처 개요

Job Agent는 A2A 프로토콜과 MCP 통합을 가진 단일 에이전트 아키텍처를 구현합니다:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   사용자        │    │  Job Agent      │    │  MCP 도구       │
│   (웹 UI)       │◄──►│  (A2A 서버)     │◄──►│  (웹 검색)      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Google Cloud   │
                       │  Run 서비스     │
                       └─────────────────┘
```

### 핵심 구성 요소

- **Job Agent**: Gemini 2.5 Flash Lite로 구동되는 메인 AI 어시스턴트
- **웹 채팅 UI**: 사용자 상호작용을 위한 내장 채팅 인터페이스
- **A2A 프로토콜**: 에이전트 카드 발견 및 메시지 처리
- **MCP 도구**: 웹 검색 및 구직 검색 기능
- **LangGraph**: 상태 유지 대화 관리

### 기본 명령어

```bash
# 로컬에서 job agent 시작
cd job-agent
uv run . --host 127.0.0.1 --port 8080

# 웹 인터페이스 접근
open http://localhost:8080

# A2A 에이전트 카드 테스트
curl http://localhost:8080/.well-known/agent.json

# 채팅 엔드포인트 테스트
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "안녕하세요", "contextId": "test"}'

# Cloud Run에 배포
gcloud run deploy job-agent --source .

# 배포 로그 확인
gcloud logs read --service=job-agent
```

### A2A 프로토콜 구현

시스템은 에이전트 통신을 위한 A2A 프로토콜을 구현합니다:

1. **에이전트 발견**: `/.well-known/agent.json`에서 에이전트 카드 사용 가능
2. **메시지 처리**: A2A 프로토콜 메시지를 위한 `/message/send` 엔드포인트
3. **스트리밍 지원**: 실시간 통신을 위한 `/message/stream` 엔드포인트
4. **웹 UI 통합**: 루트 `/` 엔드포인트의 내장 채팅 인터페이스
5. **세션 관리**: 세션 ID를 통한 지속적인 대화 컨텍스트

### MCP 통합

Model Context Protocol (MCP) 도구는 확장된 기능을 제공합니다:

1. **웹 검색**: DuckDuckGo를 사용한 실시간 웹 검색 (API 키 불필요)
2. **구직 검색**: 사용자 정의 기준을 가진 모의 채용 추천
3. **확장 가능한 아키텍처**: 새로운 MCP 도구의 쉬운 추가
4. **FastMCP 프레임워크**: 표준 MCP 서버 구현

## 프로젝트 구조

```
job_agent/
├── README.md                    # 메인 프로젝트 문서
├── job-agent/                   # 독립 실행형 job agent 패키지
│   ├── __init__.py             # 패키지 초기화
│   ├── __main__.py             # 웹 UI가 포함된 진입점
│   ├── agent.py                # MCP 도구가 포함된 핵심 JobAgent
│   ├── agent_executor.py       # A2A 프로토콜 어댑터
│   ├── web_search_server.py    # MCP 웹 검색 서버
│   ├── pyproject.toml          # 의존성 및 메타데이터
│   ├── Dockerfile              # Cloud Run 컨테이너
│   ├── README.md               # 에이전트별 문서
│   ├── test_cloud_run.py       # Cloud Run 배포 테스트
│   └── .env                    # 로컬 환경 변수
├── cloudbuild.yaml             # Cloud Run용 CI/CD 파이프라인
├── study/                      # 문서 및 가이드
│   ├── modules-reference.md    # 기술 모듈 문서
│   └── project-architecture.md # 아키텍처 개요
└── .gitignore                  # Git 무시 패턴
```

## 배포

### 로컬 개발

```bash
# 로컬에서 에이전트 시작
cd job-agent
uv run . --host 127.0.0.1 --port 8080

# 웹 인터페이스 접근
open http://localhost:8080
```

### Cloud Run 배포

프로젝트는 Cloud Build를 통한 자동화된 CI/CD를 포함합니다:

```bash
# 수동 배포
gcloud run deploy job-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated

# 또는 제공된 cloudbuild.yaml을 사용한 자동 배포
# GitHub main 브랜치에 푸시하면 자동 배포 트리거
```

### 환경 변수

Cloud Run에 필요한 환경 변수:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

## 기여하기

1. 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 엽니다

## 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 연락처

- 프로젝트 링크: [https://github.com/megabytekim/job_agent](https://github.com/megabytekim/job_agent)

## 감사의 말

- **Google Codelabs**: 이 프로젝트는 [Agent-to-Agent (A2A) Protocol 튜토리얼](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge?hl=ko#1)에서 영감을 받았습니다
- **Google Cloud Platform**: 인프라와 서비스를 제공해주셔서 감사합니다
- **A2A Protocol**: 에이전트 간 통신 표준을 확립해주셔서 감사합니다
- **Model Context Protocol (MCP)**: 확장 가능한 AI 도구 통합을 가능하게 해주셔서 감사합니다
- **FastMCP**: MCP 서버 개발을 단순화하는 Python 프레임워크를 제공해주셔서 감사합니다

## 기술 참고 자료

- [Agent-to-Agent (A2A) Protocol 문서](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge?hl=ko#1)
- [Google Cloud Run 문서](https://cloud.google.com/run/docs)
- [Model Context Protocol (MCP) 문서](https://modelcontextprotocol.io/)
- [FastMCP 문서](https://github.com/jlowin/fastmcp)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)

---

**참고**: 이 프로젝트는 A2A 프로토콜과 MCP 통합을 가진 단일 에이전트 구현을 보여줍니다. 에이전트는 커리어 가이드, 구직 지원, 실시간 웹 검색 기능을 제공합니다.

# 💻 Developer — 선정된 데이터 소스를 기반으로 웹사이트의 기술 스택(프론트엔드/백엔드) 및 데이터베이스 구조에 대한 초기 아키텍처 설계를 시작합니다.

💻 Developer: 작업 시작합니다.

# 🏛️ 주식 트레이더 웹사이트 초기 아키텍처 설계

CEO의 지시에 따라, '주식 트레이더 웹사이트'의 핵심 요구사항(실시간 데이터, 백테스팅, 고성능 시각화)을 충족시키기 위한 기술 스택 및 데이터베이스 구조에 대한 초기 아키텍처 설계를 제시합니다.

## 1. 기술 스택 제안 (Technology Stack Proposal)

시스템의 **실시간 처리 능력**과 **데이터 안정성**을 최우선으로 고려하여, 현대적이고 확장 가능한 스택을 제안합니다.

### 1.1. 프론트엔드 (Frontend: 사용자 경험 및 시각화)
*   **기술:** **React (Next.js)**
    *   **선택 이유:** 서버 사이드 렌더링(SSR) 및 정적 사이트 생성(SSG) 기능을 통해 초기 로딩 속도를 확보하고, 복잡한 차트 라이브러리(예: TradingView 통합)와의 연동에 용이합니다.
*   **데이터 시각화 라이브러리:** **D3.js** 또는 **Recharts** (핵심 지표 시각화), **TradingView Lightweight Charts** (고급 차트 렌더링)

### 1.2. 백엔드 (Backend: 데이터 처리 및 API 제공)
*   **기술:** **Node.js (Express/NestJS)** 또는 **Python (FastAPI)**
    *   **선택 이유:** 금융 데이터 파이프라인의 복잡성을 관리하고, 특히 **WebSocket**을 통한 실시간 스트리밍 통신을 효율적으로 처리하기에 적합합니다. (Python은 데이터 분석 라이브러리 연동에 강점, Node.js는 실시간 I/O 처리에 강점)
*   **실시간 통신:** **WebSocket** (실시간 시세 스트리밍)
*   **비동기 작업 처리:** **Redis** (캐싱 및 세션 관리), **BullMQ/Celery** (백테스팅 및 대규모 데이터 처리 작업 큐)

### 1.3. 데이터베이스 및 캐싱 (Database & Caching)
*   **시계열 데이터 (Historical Data):** **PostgreSQL (TimescaleDB 확장)**
    *   **선택 이유:** 관계형 데이터의 안정성과 강력한 시계열 데이터 확장성(TimescaleDB)을 결합하여, 수년간의 OHLCV 데이터를 정합성 있게 저장하고 고속으로 쿼리할 수 있습니다.
*   **실시간 상태 및 캐시:** **Redis**
    *   **용도:** 현재 시장 상태, 사용자 세션, 자주 요청되는 차트 데이터의 임시 캐싱에 사용합니다.

---

## 2. 데이터 파이프라인 및 시스템 구조 (Data Pipeline & System Architecture)

데이터의 수집, 처리, 서비스 제공의 흐름을 **실시간(Streaming)**과 **배치(Batch)**로 분리하여 안정성을 확보합니다.

### 2.1. 시스템 다이어그램 (High-Level Flow)

```mermaid
graph TD
    subgraph Data Sources
        A[External Market APIs] --> B(Data Ingestion Service);
    end

    subgraph Data Pipeline (Backend)
        B --> C{Data Normalization & Validation};
        C --> D[PostgreSQL/TimescaleDB (Historical Storage)];
        C --> E[Redis (Real-time Cache)];
        B --> F(WebSocket Streamer);
    end

    subgraph Application Layer
        F --> G[Real-time API Gateway (WebSocket)];
        G --> H[Frontend (React/Next.js)];
        H --> I(Data Visualization & Interaction);
    end

    subgraph Batch Processing
        D --> J[Backtesting Engine (Worker Queue)];
        J --> K[Results Storage];
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#ccf,stroke:#333,stroke-width:2px
```

### 2.2. 각 구성 요소별 상세 역할

| 구성 요소 | 역할 | 핵심 기술 | 목표 |
| :--- | :--- | :--- | :--- |
| **Data Ingestion Service** | 외부 API로부터 데이터를 수집하고 정규화 | Python/Node.js, API Clients | 데이터의 정확한 수집 및 초기 정제 |
| **PostgreSQL (TimescaleDB)** | 모든 과거 시계열 데이터의 영구 저장소 | PostgreSQL + TimescaleDB | 데이터 무결성 및 장기 보관 |
| **Redis** | 실시간 시세 캐싱 및 세션 관리 | Redis | 초고속 데이터 접근 및 시스템 부하 감소 |
| **WebSocket Streamer** | 데이터베이스/캐시의 변경 사항을 프론트엔드로 실시간 전송 | Node.js/FastAPI WebSocket | 지연 없는 실시간 데이터 업데이트 |
| **Backtesting Engine** | 사용자가 입력한 전략에 따른 과거 데이터 시뮬레이션 | Worker Queue (BullMQ/Celery) | 무거운 계산 작업을 비동기로 처리 |

## 3. 데이터베이스 스키마 초기 설계 (PostgreSQL/TimescaleDB)

핵심 데이터 테이블의 초기 구조를 정의합니다.

### 테이블 1: `market_data_ticks` (실시간/고빈도 데이터)
*   **Primary Key:** `timestamp` (타임스탬프, TimescaleDB의 시계열 인덱스 역할)
*   **Columns:**
    *   `symbol` (VARCHAR, 인덱스)
    *   `timestamp` (TIMESTAMPTZ, Primary Index)
    *   `open` (NUMERIC)
    *   `high` (NUMERIC)
    *   `low` (NUMERIC)
    *   `close` (NUMERIC)
    *   `volume` (BIGINT)
    *   `vwap` (NUMERIC)

### 테이블 2: `fundamental_data` (기초 데이터)
*   **Primary Key:** `symbol`
*   **Columns:**
    *   `symbol` (VARCHAR, Primary Index)
    *   `company_name` (VARCHAR)
    *   `pe_ratio` (NUMERIC)
    *   `pb_ratio` (NUMERIC)
    *   `market_cap` (NUMERIC)
    *   `last_updated` (TIMESTAMPTZ)

### 테이블 3: `backtest_results` (백테스팅 결과 저장)
*   **Primary Key:** `result_id`
*   **Columns:**
    *   `strategy_name` (VARCHAR)
    *   `symbol` (VARCHAR)
    *   `start_date` (DATE)
    *   `end_date` (DATE)
    *   `initial_capital` (NUMERIC)
    *   `final_capital` (NUMERIC)
    *   `net_profit` (NUMERIC)
    *   `win_rate` (NUMERIC)
    *   `max_drawdown` (NUMERIC)

---

📊 평가: 진행중 — 기술 스택과 데이터 흐름에 대한 구체적인 설계가 완료되었으며, 다음 단계에서는 실제 API

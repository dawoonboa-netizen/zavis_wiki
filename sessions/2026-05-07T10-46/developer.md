# 💻 Developer — 수립된 전략을 구현하기 위한 백테스팅 환경, 데이터 수집 API 연동 구조, 그리고 트레이딩 로직의 초기 아키텍처(데이터 파이프라인)를 설계하라.

💻 Developer: 작업 시작합니다.

## 📊 초기 트레이딩 시스템 아키텍처 설계 (Data Pipeline & Backtesting Framework)

수립된 투자 전략(스윙 트레이딩, 기술적/기본적 분석 결합, 1:2 리스크/보상)을 구현하기 위한 데이터 수집, 처리, 백테스팅 환경의 초기 아키텍처를 설계합니다. 이 설계는 실행 가능한 Python 기반의 모듈 구조를 목표로 합니다.

### 1. 시스템 아키텍처 개요 (High-Level Architecture)

시스템은 **데이터 수집 계층(Data Ingestion)**, **데이터 처리 계층(Data Processing)**, **전략 실행 계층(Strategy Execution)**, **결과 보고 계층(Reporting)**의 4단계로 구성됩니다.

```mermaid
graph TD
    A[외부 데이터 소스: API/DB] --> B{Data Ingestion Layer};
    B --> C[Data Storage: Time-Series DB (e.g., PostgreSQL/Parquet)];
    C --> D{Data Processing Layer: Indicator Calculation};
    D --> E[Strategy Layer: Signal Generation];
    E --> F[Backtesting Engine];
    F --> G[Reporting & Visualization];
```

### 2. 데이터 수집 및 연동 구조 (Data Ingestion & API Linkage)

**목표:** 신뢰성 있고 안정적인 시계열 데이터(가격, 거래량)를 확보합니다.

#### 2.1. API 연동 모듈 정의
외부 데이터 소스(예: Yahoo Finance API, 증권사 API)에 대한 접근을 관리하는 인터페이스를 정의합니다.

*   **모듈:** `data_fetcher.py`
*   **기능:** 특정 종목 코드와 기간을 입력받아 원시 가격 데이터(OHLCV)를 요청하고 JSON/CSV 형태로 반환합니다.
*   **보안:** 모든 API 키 및 인증 정보는 환경 변수(`os.environ`)를 통해 주입받으며, 코드 내에 하드코딩하지 않습니다.

#### 2.2. 데이터 저장 구조 (Data Storage)
과거 데이터의 효율적인 조회를 위해 시계열 데이터베이스 또는 Parquet 파일을 사용합니다.

*   **저장 방식:** 시계열 데이터는 `Timestamp`, `Open`, `High`, `Low`, `Close`, `Volume` 필드를 포함하는 **Parquet 파일** 형태로 저장합니다.
*   **장점:** 대용량 데이터 처리에 효율적이며, 백테스팅 시 데이터 로딩 속도를 최적화합니다.

### 3. 데이터 처리 및 전략 로직 (Data Processing & Strategy Logic)

**목표:** 원시 데이터를 분석 지표로 변환하고, 정의된 투자 스타일을 적용하여 매매 신호를 생성합니다.

#### 3.1. 지표 계산 모듈 정의
연구에서 정의된 지표(VIX, 이동평균선, 볼린저 밴드 등)를 계산하는 함수를 모듈화합니다.

*   **모듈:** `indicator_calculator.py`
*   **기능:** 저장된 OHLCV 데이터를 입력받아, 기술적 분석에 필요한 모든 지표(예: 5일/20일 이동평균선, RSI, MACD)를 계산하여 데이터셋에 추가합니다.

#### 3.2. 트레이딩 로직 (Signal Generation)
실제 매매 결정을 내리는 핵심 로직을 구현합니다.

*   **모듈:** `strategy_engine.py`
*   **로직:**
    1.  **필터링:** 거시 경제 데이터(선택 사항) 또는 시장 심리 지표를 기반으로 전체 포트폴리오의 위험 수준을 점검합니다.
    2.  **신호 생성:** `indicator_calculator`의 결과를 바탕으로 **진입(Buy/Sell)** 및 **청산(Exit)** 신호를 생성합니다.
    3.  **규칙 적용:** 리스크 관리 규칙(포지션 사이징, 손절매 레벨)을 신호에 적용하여 최종 실행 가능한 거래 명령을 출력합니다.

### 4. 백테스팅 환경 구축 (Backtesting Environment)

**목표:** 실제 시장 데이터가 아닌 과거 데이터를 사용하여 전략의 성과를 검증합니다.

*   **모듈:** `backtester.py`
*   **기능:**
    1.  **데이터 로드:** 저장소에서 필요한 과거 데이터를 로드합니다.
    2.  **시뮬레이션:** `strategy_engine`에서 생성된 신호를 시간 순서대로 따라가며 가상의 거래를 실행합니다.
    3.  **성과 측정:** 거래 시점별 수익률, 최대 손실 폭(Max Drawdown), 연평균 수익률(CAGR), 승률(Win Rate) 등을 계산하여 결과를 산출합니다.
    4.  **위험 검증:** 백테스팅 결과가 설정된 최대 허용 손실(-20%) 규칙을 위반했는지 검증합니다.

### 5. 초기 실행 예시 (Skeleton Code)

다음은 데이터 수집과 지표 계산의 기본 골격입니다.

```python
# data_fetcher.py (예시)
import requests
import os
import pandas as pd

def fetch_historical_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    외부 API에서 주가 데이터를 가져와 DataFrame으로 반환합니다.
    (실제 API 연동 로직은 여기에 구현됩니다.)
    """
    # API 키는 환경 변수에서 로드
    api_key = os.environ.get("TRADING_API_KEY")
    if not api_key:
        raise ValueError("API 키가 설정되지 않았습니다.")
        
    # --- 실제 API 호출 및 데이터 파싱 로직 ---
    print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
    
    # 더미 데이터 반환 (실제 구현 시 API 호출 결과로 대체)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    data = {
        'Date': dates,
        'Close': 100 + (pd.np.random.randn(len(dates)) * 5), # 더미 가격
        'Volume': pd.np.random.randint(10000, 50000, len(dates))
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

# indicator_calculator.py (예시)
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    주어진 가격 데이터에 기술적 지표를 추가합니다.
    """
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_20']

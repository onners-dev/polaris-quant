┌──────────────────────────┐
                       │   Data Sources (Free)    │
                       │ ──────────────────────── │
                       │ • Yahoo Finance          │
                       │ • FRED (macro)           │
                       │ • Alpha Vantage (fund.)  │
                       └──────────┬───────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │         Data Ingestion Layer             │
             │ (Python scripts, scheduled daily)        │
             │ • API clients with retry logic           │
             │ • Rate limiting handlers                 │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │    Data Quality & Validation Layer       │
             │ ─────────────────────────────────────── │
             │ • Missing data detection & imputation    │
             │ • Outlier detection (splits, errors)     │
             │ • Schema validation                      │
             │ • Corporate actions adjustment           │
             │ • Alert system for data gaps             │
             │ • Survivorship bias checks               │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │          Storage Layer (Free)           │
             │ ─────────────────────────────────────── │
             │ DuckDB Local Warehouse:                  │
             │   ├─ raw/ (immutable source data)        │
             │   ├─ cleaned/ (validated, adjusted)      │
             │   ├─ features/ (engineered features)     │
             │   └─ predictions/ (model outputs)        │
             │ • Parquet backups on Google Drive        │
             │ • DVC for dataset versioning             │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │        Feature Engineering Layer         │
             │ ─────────────────────────────────────── │
             │ Technical Features:                      │
             │ • Rolling stats (volatility, momentum)   │
             │ • Price patterns & indicators            │
             │ Fundamental Features:                    │
             │ • Valuation ratios with point-in-time    │
             │ • Growth metrics, quality scores         │
             │ Macro Features:                          │
             │ • Interest rates, yield curves           │
             │ • Economic indicators merged by date     │
             │ Alternative Features:                    │
             │ • Sentiment, seasonality, correlations   │
             │ • Saved as materialized tables           │
             │ • Feature importance tracking            │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │          ML Training Layer               │
             │ ─────────────────────────────────────── │
             │ Model Options:                           │
             │ • XGBoost/LightGBM (primary)             │
             │ • Simple LSTM for sequences (optional)   │
             │ • Ensemble combinations                  │
             │ Validation:                              │
             │ • Walk-forward/purged K-fold             │
             │ • Train/val/test split (time-based)      │
             │ • Hold-out unseen data (2023-2024)       │
             │ • Strong regularization                  │
             │ • Cross-validation with time gaps        │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │      Model Registry & Versioning         │
             │ ─────────────────────────────────────── │
             │ • MLflow or JSON-based tracking          │
             │ • Model versioning (date, hash)          │
             │ • Hyperparameters logged                 │
             │ • Training data snapshot references      │
             │ • Feature importance per model           │
             │ • Performance metrics history            │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │           Backtesting Engine             │
             │ ─────────────────────────────────────── │
             │ • VectorBT (choose one, not both)        │
             │ Realistic Simulation:                    │
             │ • Transaction costs (bps)                │
             │ • Slippage modeling                      │
             │ • Bid-ask spread estimates               │
             │ • Position sizing rules                  │
             │ Risk Metrics:                            │
             │ • Sharpe, Sortino, Calmar ratios         │
             │ • Maximum drawdown analysis              │
             │ • Win rate, profit factor                │
             │ • Rolling performance windows            │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │         Model Selection Layer            │
             │ ─────────────────────────────────────── │
             │ • Compare multiple model versions        │
             │ • Ensemble logic (if using multiple)     │
             │ • Statistical significance tests         │
             │ • Select champion model                  │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │      Signal Generation & Risk Mgmt       │
             │ ─────────────────────────────────────── │
             │ Signal Logic:                            │
             │ • Buy/sell/hold decisions                │
             │ • Position sizing (Kelly, fixed, etc.)   │
             │ • Entry/exit rules                       │
             │ Risk Management:                         │
             │ • Position limits per asset              │
             │ • Portfolio heat (total risk)            │
             │ • Correlation monitoring                 │
             │ • Drawdown circuit breakers              │
             │ • Sector/concentration limits            │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │         Paper Trading Layer              │
             │ ─────────────────────────────────────── │
             │ • Execute signals with live data         │
             │ • Track slippage vs backtest             │
             │ • Demo mode performance tracking         │
             │ • Verify execution logic                 │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │            REST API Layer                │
             │ ─────────────────────────────────────── │
             │ Backend: FastAPI or Flask                │
             │                                          │
             │ Endpoints:                               │
             │ GET  /api/portfolio/summary              │
             │ GET  /api/signals/current                │
             │ GET  /api/signals/history                │
             │ GET  /api/models/list                    │
             │ GET  /api/models/{id}/performance        │
             │ POST /api/backtest/run                   │
             │ GET  /api/backtest/{id}/results          │
             │ GET  /api/features/importance            │
             │ GET  /api/data/quality                   │
             │ GET  /api/paper-trades/positions         │
             │ POST /api/paper-trades/execute           │
             │ GET  /api/monitoring/drift               │
             │ GET  /api/monitoring/alerts              │
             │                                          │
             │ • JWT authentication                     │
             │ • Rate limiting                          │
             │ • Request validation (Pydantic)          │
             │ • CORS configuration                     │
             │ • WebSocket for real-time updates        │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │          React Web Application           │
             │ ─────────────────────────────────────── │
             │ Tech Stack:                              │
             │ • React 18+ with TypeScript              │
             │ • Vite or Next.js                        │
             │ • TanStack Query (data fetching)         │
             │ • Zustand or Redux (state management)    │
             │ • TailwindCSS (styling)                  │
             │ • shadcn/ui (component library)          │
             │                                          │
             │ Pages/Features:                          │
             │ ├─ Dashboard                             │
             │ │  • Portfolio overview cards            │
             │ │  • Current signals table               │
             │ │  • Performance metrics                 │
             │ │  • Real-time P&L chart                 │
             │ │                                        │
             │ ├─ Models                                │
             │ │  • Model comparison table              │
             │ │  • Performance charts (Recharts)       │
             │ │  • Feature importance plots            │
             │ │  • Training history                    │
             │ │                                        │
             │ ├─ Backtesting                           │
             │ │  • Parameter configuration form        │
             │ │  • Run backtest button                 │
             │ │  • Results visualization               │
             │ │  • Equity curve, drawdown chart        │
             │ │  • Trade list table                    │
             │ │                                        │
             │ ├─ Paper Trading                         │
             │ │  • Open positions table                │
             │ │  • Execute trade form                  │
             │ │  • Performance vs backtest comparison  │
             │ │  • Slippage analysis                   │
             │ │                                        │
             │ ├─ Data Quality                          │
             │ │  • Data freshness indicators           │
             │ │  • Missing data heatmap                │
             │ │  • Outlier alerts                      │
             │ │  • Update logs                         │
             │ │                                        │
             │ ├─ Monitoring                            │
             │ │  • Drift detection charts              │
             │ │  • Feature distribution plots          │
             │ │  • Alert history                       │
             │ │  • System health dashboard             │
             │ │                                        │
             │ └─ Settings                              │
             │    • Risk parameters                     │
             │    • Position sizing rules               │
             │    • Alert configurations                │
             │    • Model selection                     │
             │                                          │
             │ Charting:                                │
             │ • Recharts (simple, responsive)          │
             │ • Or Plotly.js (advanced, interactive)   │
             │ • TradingView lightweight charts         │
             │                                          │
             │ • Responsive design (mobile-friendly)    │
             │ • Dark/light theme toggle                │
             │ • Real-time updates via WebSocket        │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │          Monitoring Layer                │
             │ ─────────────────────────────────────── │
             │ • Prediction drift detection             │
             │ • Feature distribution monitoring        │
             │ • Performance degradation alerts         │
             │ • Compare live vs backtest metrics       │
             │ • Data quality ongoing checks            │
             │ • Anomaly detection                      │
             └────────────────────┬────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │       Automation & CI/CD Layer           │
             │ ─────────────────────────────────────── │
             │ Backend:                                 │
             │ • GitHub Actions for daily updates       │
             │ • Automated data ingestion               │
             │ • Scheduled retraining (weekly/monthly)  │
             │ • Automated backtesting reports          │
             │ • pytest for pipeline testing            │
             │ • Pre-commit hooks for code quality      │
             │ • Automated alerts (email/Slack)         │
             │                                          │
             │ Frontend:                                │
             │ • GitHub Actions for build/deploy        │
             │ • ESLint + Prettier                      │
             │ • TypeScript type checking               │
             │ • Component testing (Vitest/Jest)        │
             │ • E2E tests (Playwright)                 │
             └─────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════
PROJECT STRUCTURE
═══════════════════════════════════════════════════════════════

trading-system/
├── backend/                      # Python backend
│   ├── src/
│   │   ├── ingestion/           # Data collection scripts
│   │   ├── validation/          # Data quality checks
│   │   ├── features/            # Feature engineering
│   │   ├── models/              # ML models
│   │   ├── backtesting/         # Backtesting engine
│   │   ├── signals/             # Signal generation
│   │   ├── risk/                # Risk management
│   │   └── api/                 # FastAPI application
│   │       ├── routes/          # API endpoints
│   │       ├── models/          # Pydantic schemas
│   │       ├── dependencies.py
│   │       └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/                     # React application
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── charts/          # Chart components
│   │   │   └── tables/          # Table components
│   │   ├── pages/               # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Models.tsx
│   │   │   ├── Backtesting.tsx
│   │   │   ├── PaperTrading.tsx
│   │   │   ├── DataQuality.tsx
│   │   │   └── Monitoring.tsx
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API client functions
│   │   ├── store/               # State management
│   │   ├── types/               # TypeScript types
│   │   ├── utils/               # Helper functions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── data/                         # Data storage
│   ├── database.duckdb          # Main DuckDB file
│   ├── raw/                     # Raw data files
│   ├── cleaned/                 # Processed data
│   └── backups/                 # Parquet backups
│
├── models/                       # Saved models
│   ├── registry.json            # Model metadata
│   └── artifacts/               # Model files
│
├── configs/                      # Configuration files
│   ├── data_sources.yaml
│   ├── features.yaml
│   ├── models.yaml
│   └── risk_params.yaml
│
├── scripts/                      # Utility scripts
│   ├── setup_db.py
│   ├── daily_update.py
│   └── backfill_data.py
│
├── .github/
│   └── workflows/
│       ├── backend-ci.yml
│       ├── frontend-ci.yml
│       └── daily-update.yml
│
├── docker-compose.yml            # Optional: containerization
└── README.md


═══════════════════════════════════════════════════════════════
IMPLEMENTATION PHASES
═══════════════════════════════════════════════════════════════

Phase 1 (MVP Backend - 3-4 weeks):
├─ Data ingestion (Yahoo Finance only)
├─ Basic data validation
├─ DuckDB storage (raw + cleaned)
├─ Simple feature engineering (20-30 features)
├─ XGBoost model with walk-forward validation
├─ Basic backtesting with transaction costs
└─ FastAPI with minimal endpoints (portfolio, signals)

Phase 2 (MVP Frontend - 2-3 weeks):
├─ React app setup (Vite + TypeScript)
├─ Dashboard page (portfolio overview, signals)
├─ Basic charts (Recharts)
├─ API integration
└─ Responsive layout with TailwindCSS

Phase 3 (Enhanced Backend - 4-6 weeks):
├─ Add FRED + Alpha Vantage data
├─ Comprehensive feature engineering
├─ Model registry (MLflow)
├─ Advanced backtesting metrics
├─ Risk management rules
├─ All API endpoints
└─ WebSocket for real-time updates

Phase 4 (Enhanced Frontend - 3-4 weeks):
├─ All pages (Models, Backtesting, Paper Trading)
├─ Interactive backtesting interface
├─ Advanced charts and visualizations
├─ Real-time updates
└─ Dark mode, polish

Phase 5 (Production Features - 4-6 weeks):
├─ Paper trading implementation
├─ Monitoring & alerting system
├─ Ensemble models
├─ Full monitoring dashboard
├─ GitHub Actions automation
└─ Comprehensive testing suite

Phase 6 (Advanced - Ongoing):
├─ Model experimentation
├─ Alternative data sources
├─ Portfolio optimization
├─ Mobile-responsive refinements
└─ Performance optimizations


═══════════════════════════════════════════════════════════════
DEPLOYMENT OPTIONS
═══════════════════════════════════════════════════════════════

Local Development:
├─ Backend: uvicorn backend/src/api/main:app --reload
├─ Frontend: npm run dev
└─ Access: http://localhost:5173

Free Deployment (Recommended for Start):
├─ Backend: Railway, Render, or Fly.io (free tiers)
├─ Frontend: Vercel, Netlify, or Cloudflare Pages (free)
├─ Database: Local DuckDB file (mount as volume)
└─ Total cost: $0/month

Production Deployment (Later):
├─ Backend: AWS EC2/Lightsail, DigitalOcean
├─ Frontend: Vercel Pro, Cloudflare
├─ Database: Persistent storage volume
└─ Monitoring: Sentry, LogRocket


═══════════════════════════════════════════════════════════════
KEY TECH DECISIONS
═══════════════════════════════════════════════════════════════

Backend:
✅ FastAPI over Flask - Better async, auto docs, type safety
✅ Pydantic for validation - Type-safe request/response
✅ DuckDB stays local - No need for PostgreSQL yet

Frontend:
✅ Vite over CRA - Faster builds, better DX
✅ TanStack Query - Best data fetching/caching for React
✅ shadcn/ui - Copy-paste components, full control
✅ Recharts - Simple, React-native charts
   (or Plotly.js if you need advanced interactivity)

State Management:
✅ TanStack Query for server state
✅ Zustand for UI state (lightweight vs Redux)

Styling:
✅ TailwindCSS - Fast development, consistent design
# Polaris Quant

A full-stack quantitative trading platform for multi-ticker research, machine learning model development, and strategy prototyping. Built with modern tools for speed, scalability, and ease of use.

---

## 🌟 Features

### Data & Infrastructure
- **Multi-ticker support** throughout the entire pipeline
- **Yahoo Finance integration** with extensible architecture for FRED, Alpha Vantage, and custom sources
- **DuckDB warehouse** - ultra-fast local analytics database with deduplication and versioning
- **Append-only tables** - immutable raw data, versioned cleaned/features datasets
- **Smart ingestion** - only downloads missing data for requested tickers and date ranges

### Machine Learning
- **Cross-sectional feature engineering** for advanced ML modeling
- **XGBoost/LightGBM** integration with walk-forward validation
- **Model registry** - track experiments, hyperparameters, and performance metrics
- **Feature importance tracking** and visualization

### Frontend
- **Modern React stack** - TypeScript, Vite, TailwindCSS, shadcn/ui
- **Company name autocomplete** with intelligent ticker search
- **Multi-ticker selection** interface
- **Interactive dashboards** for data exploration and model analysis
- **Responsive design** - works on desktop, tablet, and mobile

### Extensibility
- Modular architecture for adding new data sources
- Plugin-ready modeling frameworks
- Customizable visualization components

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/onners-dev/polaris-quant.git
cd polaris-quant/trading-system
```

2. **Set up the backend**
```bash

cd backend
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```

3. **Start the backend server**
```bash
uvicorn src.api.main:app --reload
```
Backend will be available at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

4. **Set up the frontend** (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at `http://localhost:5173`

---

## 📊 Usage

### Basic Workflow

1. **Data Ingestion**
   - Use the UI to search and select tickers
   - Specify date range for historical data
   - Click "Ingest Data" - only missing data will be downloaded

2. **Feature Engineering**
   - Configure feature parameters (rolling windows, indicators)
   - Generate cross-sectional features across all tickers
   - Features are cached in DuckDB for instant access

3. **Model Training**
   - Select training period and target variable
   - Configure model hyperparameters
   - Train model with walk-forward validation
   - Results automatically logged to model registry

4. **Analysis**
   - View model performance metrics
   - Analyze feature importance
   - Compare multiple model versions
   - Export results for further analysis

### API Endpoints

```bash
# Health check
GET /api/health

# Data ingestion
POST /api/ingest
GET /api/data/tickers
GET /api/data/summary

# Features
POST /api/features/generate
GET /api/features/list

# Models
POST /api/models/train
GET /api/models/list
GET /api/models/{model_id}/performance

# See full documentation at /docs
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     React Frontend (TypeScript)     │
│  • Dashboard, Charts, Controls      │
└──────────────┬──────────────────────┘
               │ REST API
┌──────────────┴──────────────────────┐
│      FastAPI Backend (Python)       │
│  • Data ingestion & validation      │
│  • Feature engineering              │
│  • ML training & backtesting        │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│        DuckDB Data Warehouse        │
│  raw/ → cleaned/ → features/        │
└─────────────────────────────────────┘
```

### Project Structure

```
polaris-quant/
├── trading-system/
│   ├── backend/
│   │   ├── src/
│   │   │   ├── api/              # FastAPI routes
│   │   │   ├── ingestion/        # Data collection
│   │   │   ├── features/         # Feature engineering
│   │   │   ├── models/           # ML models
│   │   │   └── utils/            # Helper functions
│   │   ├── tests/
│   │   └── requirements.txt
│   │
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── components/       # React components
│   │   │   ├── pages/            # Page views
│   │   │   ├── services/         # API clients
│   │   │   └── types/            # TypeScript types
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   ├── data/                     # DuckDB database
│   ├── models/                   # Trained models
│   └── configs/                  # Configuration files
```

---

## 🛣️ Roadmap

### In Progress
- [ ] Enhanced feature engineering (fundamental ratios, macro indicators)
- [ ] Automated pipeline scheduling (daily data refresh)
- [ ] Advanced backtesting engine with realistic costs/slippage

### Planned
- [ ] Paper trading simulation interface
- [ ] Model comparison and ensemble tools
- [ ] Risk management and position sizing
- [ ] Production deployment guides (Docker, cloud)
- [ ] Real-time monitoring and drift detection
- [ ] Portfolio analytics and optimization
- [ ] Alternative data sources (news sentiment, social data)

### Future
- [ ] Multi-strategy portfolio management
- [ ] Live trading integration (with broker APIs)
- [ ] Community model sharing
- [ ] Mobile app

---

## 🧪 Development

### Running Tests (not ready yet)

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test


## 📝 Status

**Current Version:** MVP / Active Development


---
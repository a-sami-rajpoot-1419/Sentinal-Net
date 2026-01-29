# Phase 5: Frontend Dashboard - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env.local
```

Then edit `.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=https://jfhbgfpuusvlreucjvmf.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your_anon_key>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 📋 Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout with header/footer
│   ├── page.tsx           # Home page (hero + features)
│   ├── dashboard/
│   │   └── page.tsx       # Real-time dashboard with agent stats
│   ├── predictions/
│   │   └── page.tsx       # Prediction history table
│   ├── agents/
│   │   └── page.tsx       # ML agents overview
│   ├── settings/
│   │   └── page.tsx       # Configuration and management
│   └── globals.css        # Global styles and animations
│
├── lib/
│   ├── api.ts            # FastAPI HTTP client (11 endpoints)
│   └── supabase.ts       # Supabase client + real-time subscriptions
│
├── components/           # Reusable React components (coming next)
├── hooks/               # Custom React hooks (coming next)
├── types/               # TypeScript interfaces (coming next)
│
├── package.json         # Dependencies (Next.js, Tailwind, etc.)
├── tsconfig.json        # TypeScript configuration
├── tailwind.config.ts   # Tailwind CSS theme
├── next.config.js       # Next.js configuration
└── .env.example         # Environment variables template
```

---

## 🎨 Pages Overview

### 1. **Home Page** (`/`)
- Hero section with CTA buttons
- System statistics (agents, sessions, predictions)
- Feature highlights
- Architecture overview

### 2. **Dashboard** (`/dashboard`)
- **Real-time Agent Cards** showing:
  - Accuracy progress bar
  - Total predictions
  - Correct predictions
  - Current weight
- **Weight Visualization** bar chart
- **System Status** (backend, database, agents)

### 3. **Prediction History** (`/predictions`)
- Sortable table of all consensus predictions
- Columns: Sample ID, Predicted Class, Confidence, Timestamp
- Real-time updates via Supabase subscriptions

### 4. **Agents** (`/agents`)
- Cards for each ML agent (NaiveBayes, SVM, RandomForest, LogisticRegression)
- Accuracy metrics
- Training status
- Agent descriptions

### 5. **Settings** (`/settings`)
- RWPV parameter configuration (read-only for now)
- Reset weights button
- Database info
- Danger zone for future admin actions

---

## 🔌 API Integration

### Available Endpoints

**Consensus Predictions:**
- `POST /consensus/predict` - Single prediction
- `POST /consensus/batch-predict` - Batch predictions
- `GET /consensus/weights` - Current agent weights
- `GET /consensus/reputations` - All agent reputations
- `GET /consensus/reputation/{agent}` - Specific agent
- `POST /consensus/update-weights` - Update weights from feedback
- `POST /consensus/reset-weights` - Reset to initial
- `GET /consensus/prediction-history` - Historical data

**Agent Management:**
- `GET /agents/list` - All agents
- `GET /agents/{name}` - Specific agent
- `GET /agents/performance/comparison` - Performance comparison

### Usage Example

```typescript
import { getAPIClient } from '@/lib/api'

const api = getAPIClient()

// Make a prediction
const response = await api.predict({
  features: [/* 1004 dimensions */]
})

// Get agent weights
const weights = await api.getWeights()

// Get reputations
const reputations = await api.getReputations()
```

---

## 🔄 Real-time Updates

### Supabase Subscriptions

```typescript
import { subscribeToConsensusResults } from '@/lib/supabase'

const subscription = subscribeToConsensusResults((payload) => {
  console.log('New consensus result:', payload.new)
})

// Cleanup
subscription.unsubscribe()
```

---

## 🎯 Key Features

### ✅ Completed
- Next.js 14 app with App Router
- TypeScript with strict types
- Tailwind CSS with glass morphism effects
- Dark theme optimized for ML dashboard
- Responsive grid layouts
- API client library (11 endpoints)
- Supabase real-time subscriptions
- 5 main pages with content
- Global animations (spin, fade, pulse)

### 🚀 Coming Next
- WebSocket integration for live updates
- Data visualization charts (Recharts)
- Authentication pages (sign in/sign up)
- Advanced filtering and search
- Export prediction data
- Admin panel for weight management
- Performance comparison graphs
- Agent performance timeline

---

## 🛠 Development

### Run Dev Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
npm start
```

### Type Check
```bash
npm run type-check
```

### Lint Code
```bash
npm run lint
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Next.js | 14.0.4 | React framework |
| React | 18.2.0 | UI library |
| TypeScript | 5.3.3 | Type safety |
| Tailwind CSS | 3.3.6 | Styling |
| Axios | 1.6.2 | HTTP client |
| SWR | 2.2.4 | Data fetching |
| Supabase | 2.38.4 | Backend services |
| Recharts | 2.10.3 | Data visualization |

---

## 🔐 Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | `https://jfhbgfpuusvlreucjvmf.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase client key | `eyJhbGciO...` |
| `NEXT_PUBLIC_API_URL` | FastAPI backend URL | `http://localhost:8000` |
| `NEXT_PUBLIC_API_TIMEOUT` | Request timeout (ms) | `30000` |
| `NEXT_PUBLIC_ENV` | Environment | `development` |

---

## 🎓 Learning Resources

### Files to Study
1. `lib/api.ts` - Complete HTTP client with 11 endpoints
2. `app/layout.tsx` - Root layout and navigation
3. `app/dashboard/page.tsx` - Real-time data fetching and display
4. `lib/supabase.ts` - Real-time subscription setup

### Key Patterns
- **SWR for data fetching** - Automatic refetching and caching
- **Glass morphism** - Semi-transparent cards with backdrop blur
- **Gradient text** - Tailwind `bg-clip-text` for gradient effect
- **Responsive grid** - `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`

---

## 🚀 Next Steps

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env.local
   # Edit with your credentials
   ```

3. **Start backend (Phase 4):**
   ```bash
   cd backend
   python -m uvicorn api.main:app --reload
   ```

4. **Start frontend (Phase 5):**
   ```bash
   npm run dev
   ```

5. **Add more features:**
   - Charts with Recharts
   - Authentication pages
   - WebSocket for real-time predictions
   - Export/download functionality

---

## 📞 Support

- **Phase 4 (Backend):** See `PHASE_4_README.md`
- **Database:** See `SUPABASE_SETUP_GUIDE.md`
- **Types:** All TypeScript interfaces are exported from `lib/api.ts`

---

## 📝 Summary

Phase 5 is the **real-time frontend dashboard** that brings the entire Sentinel-Net system to life:
- **Phase 3:** ML models (4 trained agents)
- **Phase 4:** RWPV consensus engine (FastAPI backend)
- **Phase 5:** Interactive dashboard (Next.js frontend)

The frontend provides complete visibility into:
- Agent predictions and confidence
- Dynamic weights and reputation
- Prediction history and performance
- System status and configuration

All pages are fully typed with TypeScript and connected to the Phase 4 API backend.

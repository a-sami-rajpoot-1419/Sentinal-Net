# Phase 5: Frontend Dashboard - Complete Implementation Guide

## 📊 Overview

**Phase 5** is a production-ready Next.js 14 frontend dashboard for real-time monitoring of the RWPV consensus engine from Phase 4.

### Technology Stack
- **Framework:** Next.js 14 (React 18 + TypeScript)
- **Styling:** Tailwind CSS with custom animations
- **Backend:** FastAPI (Phase 4)
- **Database:** Supabase PostgreSQL
- **HTTP Client:** Axios
- **Real-time:** Supabase Subscriptions
- **State Management:** SWR + React Hooks

---

## 🎯 Features Implemented

### 1. **Home Page** (`/`)
- Hero section with project overview
- Statistics cards (agents, sessions, predictions)
- Feature highlights
- System architecture explanation

### 2. **Real-time Dashboard** (`/dashboard`)
- **Agent Performance Cards** (4x agents):
  - Accuracy with progress bar
  - Total and correct predictions
  - Average confidence
  - Current weight display
- **Weight Visualization:**
  - Bar chart showing relative weights
  - Updates every 5 seconds
- **System Status:**
  - Backend connectivity
  - Database status
  - Active agents count
  - Last update timestamp

### 3. **Prediction History** (`/predictions`)
- Scrollable table of all predictions
- Columns: Sample ID, Predicted Class, Confidence (with bar), Timestamp
- Auto-loading on page load
- Real-time updates via Supabase

### 4. **ML Agents** (`/agents`)
- Agent cards with details:
  - Agent name and training status
  - Accuracy metrics
  - Prediction counts
  - Algorithm descriptions
- Ensemble architecture explanation
- RWPV mechanism details

### 5. **Settings** (`/settings`)
- RWPV parameter display (read-only)
- Reset weights functionality
- Database configuration info
- Danger zone for future actions

### 6. **Global Navigation**
- Sticky header with logo and nav links
- Footer with copyright
- Responsive mobile menu

---

## 📁 File Structure

```
frontend/
│
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout (header, footer, nav)
│   ├── globals.css              # Global styles, animations, utilities
│   ├── page.tsx                 # Home page
│   │
│   ├── dashboard/
│   │   └── page.tsx             # Real-time dashboard
│   ├── predictions/
│   │   └── page.tsx             # Prediction history
│   ├── agents/
│   │   └── page.tsx             # Agent overview
│   └── settings/
│       └── page.tsx             # Configuration
│
├── lib/                         # Utilities and clients
│   ├── api.ts                  # FastAPI HTTP client
│   │   ├── APIClient class     # 11 API endpoints
│   │   ├── Type definitions    # Request/response types
│   │   └── Singleton pattern   # getAPIClient()
│   │
│   └── supabase.ts             # Supabase configuration
│       ├── Client init         # createClient()
│       ├── Auth functions      # signIn, signUp, signOut
│       ├── Subscriptions       # Real-time updates
│       └── Session management  # getSession()
│
├── components/                  # Reusable React components
│   └── (coming in Phase 5b)
│
├── hooks/                       # Custom React hooks
│   └── (coming in Phase 5b)
│
├── types/                       # TypeScript interfaces
│   └── (coming in Phase 5b)
│
├── package.json                 # Dependencies
├── tsconfig.json                # TypeScript config
├── next.config.js              # Next.js config
├── tailwind.config.ts          # Tailwind theme
├── postcss.config.js           # CSS processing
├── .env.example                # Environment template
└── .gitignore                  # Git ignore rules
```

---

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://jfhbgfpuusvlreucjvmf.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000

# Environment
NEXT_PUBLIC_ENV=development
```

### 3. Start Development Server
```bash
npm run dev
```

### 4. Open in Browser
```
http://localhost:3000
```

---

## 🌐 Pages & Routes

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | `app/page.tsx` | Home page with overview |
| `/dashboard` | `app/dashboard/page.tsx` | Real-time agent stats |
| `/predictions` | `app/predictions/page.tsx` | Prediction history |
| `/agents` | `app/agents/page.tsx` | ML agent details |
| `/settings` | `app/settings/page.tsx` | Configuration |

---

## 🔌 API Client

### Available Methods

```typescript
import { getAPIClient } from '@/lib/api'
const api = getAPIClient()

// Consensus Predictions
await api.predict({ features: [...] })
await api.batchPredict({ features: [...] })
await api.updateWeights({ true_label: 1, predictions: {...} })
await api.getWeights()
await api.getReputations()
await api.getReputation('agent_name')
await api.resetWeights()
await api.getPredictionHistory(limit)

// Agent Management
await api.listAgents()
await api.getAgent('agent_name')
await api.compareAgentPerformance()

// Health Check
await api.health()
```

### Error Handling

```typescript
try {
  const response = await api.predict(request)
} catch (error) {
  if (error.response?.status === 400) {
    console.error('Invalid request:', error.response.data)
  } else if (error.response?.status === 500) {
    console.error('Server error:', error.response.data)
  } else {
    console.error('Network error:', error.message)
  }
}
```

---

## 🎨 Styling & Components

### Tailwind CSS Configuration

**Colors:**
```css
primary: #3b82f6 (Blue)
secondary: #8b5cf6 (Purple)
success: #10b981 (Green)
warning: #f59e0b (Amber)
error: #ef4444 (Red)
```

**Classes:**
```css
.glass              /* Semi-transparent cards */
.gradient-text     /* Gradient text effect */
.transition-smooth /* Smooth transitions */
.fade-in          /* Fade-in animation */
.pulse            /* Pulse animation */
.spinner          /* Loading spinner */
```

### Example Components

**Agent Card:**
```tsx
<div className="glass p-6 rounded-lg space-y-3">
  <h3 className="font-semibold capitalize">{agent.agent_name}</h3>
  <div className="w-full bg-gray-700/50 rounded-full h-2">
    <div 
      className="bg-blue-400 h-2 rounded-full"
      style={{ width: `${agent.accuracy * 100}%` }}
    />
  </div>
</div>
```

---

## 🔄 Real-time Updates

### Supabase Subscriptions

**Consensus Results:**
```typescript
import { subscribeToConsensusResults } from '@/lib/supabase'

const subscription = subscribeToConsensusResults((payload) => {
  console.log('New result:', payload.new)
  // Update UI
})

return () => subscription.unsubscribe()
```

**Weight Updates:**
```typescript
import { subscribeToWeightUpdates } from '@/lib/supabase'

const subscription = subscribeToWeightUpdates((payload) => {
  console.log('Weight updated:', payload.new)
})
```

---

## 🧪 Testing

### Manual Testing Checklist

- [ ] Navigation between all pages
- [ ] Dashboard loads and updates every 5 seconds
- [ ] Agent cards display correct stats
- [ ] Weights are visualized correctly
- [ ] Prediction history table loads
- [ ] Settings page shows parameters
- [ ] Reset weights button works
- [ ] Mobile responsive (check at 375px, 768px, 1024px)

### Browser Console Commands

```javascript
// Test API client
const api = getAPIClient()
const response = await api.health()
console.log(response)

// Test data fetching
const weights = await api.getWeights()
console.log('Weights:', weights)

const reputations = await api.getReputations()
console.log('Reputations:', reputations)
```

---

## 🚀 Production Deployment

### Build for Production
```bash
npm run build
npm start
```

### Environment Variables (Production)
```env
NEXT_PUBLIC_SUPABASE_URL=<production_url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<production_key>
NEXT_PUBLIC_API_URL=https://api.sentinel-net.com
NEXT_PUBLIC_ENV=production
```

### Deployment Options
- **Vercel** (recommended for Next.js)
- **Netlify**
- **Docker container**
- **Self-hosted VPS**

---

## 📦 Key Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| `next` | React framework | 14.0.4 |
| `react` | UI library | 18.2.0 |
| `axios` | HTTP client | 1.6.2 |
| `@supabase/supabase-js` | Backend client | 2.38.4 |
| `swr` | Data fetching | 2.2.4 |
| `tailwindcss` | CSS framework | 3.3.6 |
| `typescript` | Type safety | 5.3.3 |

---

## 🎓 Learning Path

### Phase 5 Knowledge Flow
1. **Start:** `app/page.tsx` (home page structure)
2. **Learn:** `lib/api.ts` (API client patterns)
3. **Understand:** `app/dashboard/page.tsx` (data fetching with useEffect)
4. **Study:** `app/globals.css` (Tailwind animations)
5. **Advanced:** `lib/supabase.ts` (real-time subscriptions)

### Key Concepts
- **Next.js App Router:** File-based routing in `app/` folder
- **Server vs Client:** `'use client'` for interactive components
- **TypeScript:** Strict type checking for API responses
- **Tailwind CSS:** Utility-first CSS with dark mode
- **Real-time:** Supabase PostgreSQL subscriptions
- **SWR:** Stale-while-revalidate data fetching

---

## 🔐 Security Considerations

### Environment Variables
- ✅ `NEXT_PUBLIC_*` prefixed variables are publicly exposed
- ✅ Use Supabase anon key (row-level security protects data)
- ✅ Never commit `.env.local` (in `.gitignore`)

### API Security
- ✅ JWT tokens from Supabase auth
- ✅ CORS configured on FastAPI backend
- ✅ Service role key only used server-side

### RLS Policies
- Database tables have RLS enabled
- Fine-grained access control in Supabase
- Production: Implement proper auth-based policies

---

## 🐛 Troubleshooting

### Frontend Won't Start
```bash
# Clear cache and reinstall
rm -rf node_modules
npm install
npm run dev
```

### API Calls Failing
1. Check backend is running: `http://localhost:8000/health`
2. Verify `NEXT_PUBLIC_API_URL` in `.env.local`
3. Check browser console for CORS errors

### TypeScript Errors
```bash
npm run type-check
```

### Tailwind Classes Not Applied
- Clear Next.js cache: `rm -rf .next`
- Rebuild: `npm run build`

---

## 📝 Code Examples

### Fetching Data with useEffect

```typescript
useEffect(() => {
  const fetchData = async () => {
    try {
      const api = getAPIClient()
      const [agents, weights] = await Promise.all([
        api.getReputations(),
        api.getWeights(),
      ])
      setAgents(agents)
      setWeights(weights)
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  fetchData()
  const interval = setInterval(fetchData, 5000) // Refresh every 5s
  
  return () => clearInterval(interval)
}, [])
```

### Glass Morphism Card

```tsx
<div className="glass p-6 rounded-lg border border-white/10">
  <h3 className="font-semibold mb-4">Agent Performance</h3>
  <div className="space-y-3">
    {/* Content */}
  </div>
</div>
```

---

## 🎯 Phase 5 Complete!

✅ **Implemented:**
- 5 functional pages with full content
- API client with 11 endpoints
- Real-time Supabase integration
- Responsive Tailwind design
- Global animations and utilities
- TypeScript type safety
- Production-ready structure

✅ **Ready to:**
- Deploy to Vercel/Netlify
- Add charts with Recharts
- Implement authentication
- Create custom hooks
- Build additional components

---

## 📞 Integration Points

**From Phase 3 (ML Models):**
- Receives 1004-dimensional feature vectors
- Gets predictions from 4 agents

**From Phase 4 (Consensus Engine):**
- Calls 11 FastAPI endpoints
- Displays predictions and weights
- Shows reputation metrics
- Stores data in Supabase

**Phase 5 → Users:**
- Real-time dashboard
- Prediction history
- Agent performance
- System configuration

---

## 🎬 Next Phase Ideas

**Phase 5b - Advanced Features:**
- Recharts for data visualization
- Authentication (sign in/sign up)
- User preferences and bookmarks
- Advanced filtering and search
- Export predictions to CSV/JSON
- Webhook notifications
- API key management
- Admin panel features

**Phase 6 - Mobile & PWA:**
- React Native mobile app
- Progressive Web App
- Offline support
- Push notifications

---

**Phase 5 Status:** ✅ **COMPLETE**

The frontend dashboard is now fully functional and ready for integration with the Phase 4 backend. All 5 pages are implemented, the API client supports all endpoints, and real-time updates are configured through Supabase.

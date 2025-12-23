# GAIA Frontend

Modern React frontend for the Global AI Intelligence Analyzer (GAIA) project - an AI-powered ESG analysis platform featuring a multi-agent system.

## Features

- **Multi-Agent Visualization**: Real-time visualization of 6 AI agents working collaboratively
- **ESG Scoring**: Comprehensive Environmental, Social, and Governance metrics
- **SDG Impact Analysis**: Assessment against all 17 UN Sustainable Development Goals
- **Greenwashing Detection**: AI-powered detection of misleading sustainability claims
- **Real-time Updates**: WebSocket integration for live agent activity
- **Modern UI**: Built with React, TypeScript, Tailwind CSS, and Framer Motion

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **TanStack Query** - Data fetching
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── AnalysisDashboard.tsx    # Main dashboard component
│   │   ├── AgentVisualization.tsx   # Agent activity display
│   │   ├── SDGImpact.tsx            # SDG impact visualization
│   │   ├── GreenwashingAlert.tsx    # Greenwashing alerts
│   │   └── ESGScoreCard.tsx         # ESG score cards
│   ├── services/
│   │   └── api.ts                   # API client & WebSocket
│   ├── types/
│   │   └── index.ts                 # TypeScript types
│   ├── App.tsx                      # Root component
│   ├── main.tsx                     # Entry point
│   └── index.css                    # Global styles
├── index.html
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

## Key Components

### AnalysisDashboard
Main dashboard with company search, analysis trigger, and results display.

### AgentVisualization
Displays the 6 AI agents:
- Data Scraper
- ESG Analyzer
- SDG Mapper
- Greenwashing Detective
- Critical Analyst
- Consensus Builder

### SDGImpact
Visualizes company impact on UN's 17 Sustainable Development Goals with scores and evidence.

### GreenwashingAlert
Shows detected greenwashing instances with severity levels and confidence scores.

## API Integration

The frontend communicates with the backend via:
- REST API for analysis requests
- WebSocket for real-time agent updates

Configure endpoints in `.env`:
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Customization

### Theme Colors
Edit `tailwind.config.js` to customize the GAIA color palette:
```javascript
colors: {
  gaia: {
    // Custom green shades for brand
  },
  earth: {
    // Earth tone colors
  }
}
```

### Animations
Framer Motion animations can be customized in component files.

## Production Build

1. Build the project:
```bash
npm run build
```

2. Preview the build:
```bash
npm run preview
```

3. Deploy the `dist/` folder to your hosting service.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT

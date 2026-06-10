# ThreadSignal Frontend

React/Vite frontend for ThreadSignal, an AI-native mini CRM for D2C campaign execution.

The UI is intentionally chat-first:

- Campaign Agent: marketer describes a goal in natural language.
- Dashboard: campaign list, delivery/engagement chart, and message-level receipt logs.
- Customers: seeded shopper data used by the backend agent for segmentation.

## Local Development

```bash
npm install
npm run dev
```

Set the API URL when deploying:

```bash
VITE_API_URL=https://your-backend-service.onrender.com
```

The app falls back to `http://localhost:8000` for local development.

## Scripts

```bash
npm run lint
npm run build
```

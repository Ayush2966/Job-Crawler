# Job Crawler Frontend

React + TypeScript frontend for configuring the Job Crawler application.

## Features

- 📧 Multiple receiver email configuration
- 📍 Multiple location preferences
- 💰 Multiple salary ranges (LPA)
- 💼 Experience range (min/max years)
- 🔎 Job title/search query input

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000` and proxy API requests to `http://localhost:5000`.

## Build

To build for production:
```bash
npm run build
```

## API Endpoints

The frontend communicates with the Flask API at `http://localhost:5000`:

- `GET /api/health` - Health check
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
- `GET /api/profiles` - Get all user profiles
- `GET /api/profiles/<email>` - Get specific user profile


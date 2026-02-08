# Quickstart Guide: Phase II Todo Frontend

## Prerequisites
- Node.js 18+ 
- npm or yarn package manager
- Git version control

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Environment Variables
Create a `.env.local` file in the frontend root:
```env
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### 4. Initialize Better Auth
```bash
npx better-auth-cli init
```

## Running the Application

### Development Mode
```bash
cd frontend
npm run dev
```

### Production Mode
```bash
cd frontend
npm run build
npm run start
```

## Testing the Application

### 1. Start the development server
```bash
npm run dev
```

### 2. Open the application
Visit `http://localhost:3000` in your browser

### 3. Test features
- Navigate to login/signup pages
- Authenticate with valid credentials
- Create, read, update, and delete tasks
- Verify responsive design on different screen sizes

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run linting
- `npm run test` - Run tests

## Folder Structure

- `src/app/` - Next.js App Router pages
- `src/components/` - Reusable UI components
- `src/hooks/` - Custom React hooks
- `src/lib/` - Utility functions and API calls
- `src/providers/` - Context providers
- `src/styles/` - Global styles

## Running Tests

### Unit Tests
```bash
npm run test
```

### E2E Tests
```bash
npm run test:e2e
```
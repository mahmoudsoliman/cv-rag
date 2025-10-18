# CV Search UI

A modern React-based web interface for the CV Search API. This frontend provides an intuitive way to search and explore candidate profiles using natural language queries.

## 🚀 Features

- **Natural Language Search**: Ask questions in plain English to find candidates
- **Real-time Results**: Instant search with loading states and response times
- **Evidence Panel**: View detailed candidate profiles and supporting documents
- **Query History**: Keep track of previous searches for easy reference
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Error Handling**: Graceful error handling with retry capabilities
- **Mock Mode**: Built-in mock data for development and testing

## 🎨 UI Components

- **Query Form**: Clean input interface with submit and loading states
- **Answer Panel**: Displays AI-generated answers with metadata
- **Evidence Panel**: Shows candidate facts and document snippets
- **History List**: Sidebar with search history and quick re-run
- **Error Banner**: User-friendly error messages with retry options
- **App Shell**: Consistent layout and navigation structure

## 📋 Prerequisites

- Node.js 16+ 
- npm or yarn
- CV Search API running on `http://localhost:8000` (or configured endpoint)

## 🛠️ Installation

1. **Navigate to the website directory:**
   ```bash
   cd website
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables (optional):**
   Create a `.env` file in the website directory:
   ```bash
   VITE_API_BASE_URL=http://localhost:8000
   VITE_USE_MOCK=false
   ```

## 🚀 Running the Application

### Development Mode
```bash
npm run dev
```

The application will start on `http://localhost:5173`

### Production Build
```bash
npm run build
npm run preview
```

### Other Scripts
```bash
npm run lint          # Run ESLint
npm run typecheck     # Run TypeScript type checking
```

## 🔧 Configuration

### Environment Variables

- `VITE_API_BASE_URL`: Backend API URL (default: `http://localhost:8000`)
- `VITE_USE_MOCK`: Enable mock mode for development (default: `false`)

### Mock Mode

When `VITE_USE_MOCK=true`, the application uses built-in mock data instead of calling the API. This is useful for:
- Frontend development without backend
- UI/UX testing
- Demo purposes

## 🎯 Usage

1. **Start the CV Search API** (see API README for instructions)
2. **Start the frontend application** using `npm run dev`
3. **Open your browser** to `http://localhost:5173`
4. **Enter your search query** in the input field
5. **View results** including:
   - AI-generated answer
   - Candidate profiles (facts)
   - Supporting document snippets
   - Query metadata and timing

## 🔍 Example Queries

- "Find candidates with React experience"
- "Who has worked at Google or Microsoft?"
- "Show me software engineers with AWS certification"
- "Find candidates with Computer Science degrees from Stanford"
- "Summarize all candidates"

## 🏗️ Project Structure

```
website/
├── src/
│   ├── components/         # React components
│   │   ├── AppShell.tsx   # Main layout wrapper
│   │   ├── QueryForm.tsx  # Search input form
│   │   ├── AnswerPanel.tsx # Answer display
│   │   ├── EvidencePanel.tsx # Facts and snippets
│   │   ├── HistoryList.tsx # Search history
│   │   └── ErrorBanner.tsx # Error handling
│   ├── api.ts             # API client functions
│   ├── types.ts           # TypeScript type definitions
│   ├── App.tsx            # Main application component
│   └── main.tsx           # Application entry point
├── index.html             # HTML template
├── package.json           # Dependencies and scripts
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

## 🎨 Styling

The application uses:
- **Tailwind CSS** for utility-first styling
- **Lucide React** for icons
- **Custom components** with consistent design system
- **Responsive design** with mobile-first approach

## 🔌 API Integration

The frontend communicates with the CV Search API through:

- **POST /ask**: Submit search queries
- **GET /health**: Health check (optional)
- **Error handling**: HTTP status codes and error messages
- **Type safety**: Full TypeScript integration

## 🧪 Development

### Adding New Components

1. Create component file in `src/components/`
2. Export from component file
3. Import and use in `App.tsx` or other components
4. Add TypeScript types in `types.ts` if needed

### Modifying API Integration

1. Update API functions in `src/api.ts`
2. Modify types in `src/types.ts`
3. Update component props and state management
4. Test with both mock and real API modes

## 🚨 Troubleshooting

1. **API Connection Error**: Ensure the CV Search API is running on the correct port
2. **CORS Issues**: Check that the API has CORS enabled for the frontend URL
3. **Build Errors**: Run `npm run typecheck` to identify TypeScript issues
4. **Styling Issues**: Ensure Tailwind CSS is properly configured
5. **Mock Mode Not Working**: Check `VITE_USE_MOCK` environment variable

## 📝 Notes

- The application is built with Vite for fast development and building
- All API calls are asynchronous with proper error handling
- The UI is fully responsive and works on all screen sizes
- Mock data is included for development without backend dependencies
- TypeScript provides full type safety throughout the application

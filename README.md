# Vercel FastAPI Example

This is a minimal FastAPI application deployed on Vercel. It demonstrates how to set up and deploy a FastAPI backend on Vercel's serverless platform.

## Features

- ✨ FastAPI with async/await support
- 🚀 Serverless deployment on Vercel
- 🔄 CORS middleware for cross-origin requests
- 📝 Multiple API endpoints with examples
- 🏥 Health check endpoint

## Project Structure

```
.
├── api/
│   └── index.py          # Main FastAPI application
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## API Endpoints

### GET `/`
Welcome message
```bash
curl https://your-deployment.vercel.app/
```

### GET `/api/hello`
Greeting endpoint with optional name parameter
```bash
curl "https://your-deployment.vercel.app/api/hello?name=FastAPI"
```

### GET `/api/health`
Health check endpoint
```bash
curl https://your-deployment.vercel.app/api/health
```

### POST `/api/echo`
Echo endpoint that returns the received data
```bash
curl -X POST https://your-deployment.vercel.app/api/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Local Development

### Prerequisites
- Python 3.9+
- pip or poetry

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Jer00hn/vercel-fastapi.git
cd vercel-fastapi
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
uvicorn api.index:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI or `http://localhost:8000/redoc` for ReDoc.

## Deployment to Vercel

### Prerequisites
- Vercel account (free at https://vercel.com)
- Vercel CLI installed: `npm install -g vercel`

### Steps

1. Login to Vercel:
```bash
vercel login
```

2. Deploy:
```bash
vercel
```

3. Follow the prompts and your app will be deployed!

### Environment Variables

If you need environment variables, add them in your Vercel dashboard or via CLI:
```bash
vercel env add VARIABLE_NAME
```

## Configuration

The `vercel.json` file contains the deployment configuration:
- Uses `@vercel/python` runtime
- Routes all requests to `api/index.py`
- Supports serverless functions

## Dependencies

- **FastAPI** - Modern web framework for building APIs
- **Uvicorn** - ASGI server for running FastAPI
- **python-multipart** - For form data parsing

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vercel Python Runtime](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## License

MIT

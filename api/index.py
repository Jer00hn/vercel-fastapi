from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return JSONResponse({
        "message": "Welcome to FastAPI on Vercel!",
        "version": "1.0.0"
    })


@app.get("/api/hello")
async def hello(name: str = "World"):
    return JSONResponse({
        "message": f"Hello, {name}!",
        "status": "success"
    })


@app.get("/api/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "service": "fastapi-vercel"
    })


@app.post("/api/echo")
async def echo(data: dict):
    return JSONResponse({
        "received": data,
        "status": "success"
    })

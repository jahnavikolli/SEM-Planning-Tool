from fastapi import FastAPI
from models import Inputs
from services import generate_sem_plan
from routes import inputs, seeds, keyword_ideas, consolidate, evaluate, adgroups
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SEM Planner Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows all origins; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(inputs.router)
app.include_router(seeds.router)
app.include_router(keyword_ideas.router)
app.include_router(consolidate.router)
app.include_router(evaluate.router)
app.include_router(adgroups.router)

# Main endpoint to generate SEM plan
@app.post("/generate-plan")
def generate_plan(input_data: Inputs):
    return generate_sem_plan(input_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

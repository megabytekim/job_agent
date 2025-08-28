# Job Agent (Standalone)

Minimal A2A-compatible agent using Vertex AI Gemini + LangGraph.

## Environment
- GOOGLE_CLOUD_PROJECT
- GOOGLE_CLOUD_LOCATION (e.g., us-central1)
- Optional: HOST_OVERRIDE (external URL for Agent Card)

## Run locally
uv sync
uv run . --host 0.0.0.0 --port 8080

## Deploy to Cloud Run
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/job-agent:latest

gcloud run deploy job-agent \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/job-agent:latest \
  --platform managed \
  --region $GOOGLE_CLOUD_LOCATION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION

## Test the deployed agent
uvx python test_cloud_run.py --url https://<your-service-url>

<#
.SYNOPSIS
Deployment script for NutriMind to Google Cloud (Cloud Run + Cloud SQL PostgreSQL).

.DESCRIPTION
Before running this script, you MUST:
1. Install the Google Cloud CLI (gcloud)
2. Run `gcloud auth login`
3. Set your project ID below.

This script will:
1. Enable necessary Google Cloud APIs.
2. Create a managed PostgreSQL database.
3. Build your Docker container on Google Cloud.
4. Deploy the container to Cloud Run and link the database securely via Unix Sockets.
#>

# =======================================================
# 1. SET YOUR VARIABLES HERE
# =======================================================
$PROJECT_ID = "your-gcp-project-id"          # Replace with your actual GCP Project ID
$REGION = "us-central1"                      # The region for your app and DB
$DB_INSTANCE = "nutrimind-db"                # Name for your database instance
$DB_USER = "postgres"                        # Default postgres user
$DB_PASSWORD = "Sup3rS3cretPassword_123!"    # REPLACE WITH A STRONG PASSWORD!
$DB_NAME = "nutrimind_prod"                  # Name of the database inside the instance
$SERVICE_NAME = "nutrimind-app"              # Name of your Cloud Run service
# =======================================================

# Set the active project
Write-Host "Setting active GCP Project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required Google APIs
Write-Host "Enabling Cloud Run, Cloud SQL, and Cloud Build APIs..."
gcloud services enable run.googleapis.com sqladmin.googleapis.com cloudbuild.googleapis.com

# Create the Cloud SQL PostgreSQL Instance (This takes 5-10 minutes)
Write-Host "Creating Cloud SQL PostgreSQL instance (micro tier)..."
gcloud sql instances create $DB_INSTANCE `
    --database-version=POSTGRES_15 `
    --tier=db-f1-micro `
    --region=$REGION `
    --root-password=$DB_PASSWORD

# Create the database inside the instance
Write-Host "Creating the $DB_NAME database..."
gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE

# Build and Push the Docker Image using Cloud Build
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME"
Write-Host "Building Docker Image in the cloud..."
gcloud builds submit --tag $IMAGE_TAG .

# Construct the SQLAlchemy Database URL
# Cloud Run connects to Cloud SQL via secure hidden unix sockets at /cloudsql/CONNECTION_NAME
$CONNECTION_NAME = "${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
$DATABASE_URL = "postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${CONNECTION_NAME}"

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_TAG `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars="DATABASE_URL=$DATABASE_URL"

Write-Host "========================================="
Write-Host "Deployment Complete! Look above for your live Service URL."
Write-Host "========================================="

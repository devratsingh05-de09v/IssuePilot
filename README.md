IssuePilot
> **Turn a confusing problem into a clear resolution path.**
IssuePilot is a serverless, multimodal AI troubleshooting assistant built during WeMakeDevs × AWS First Commit 2026.
Instead of treating a technical problem as a single chat prompt, IssuePilot turns it into a structured case:
Problem → Evidence → AI Diagnosis → Targeted Questions → Guided Fix → Resolved
A user can describe a problem in plain language and optionally attach a screenshot or error file. IssuePilot stores the case and evidence, sends relevant context to Amazon Bedrock / Nova 2 Lite, and returns a structured diagnosis with practical next steps, questions, and safety notes.
Quick links
🚀 Live Demo: Add deployed IssuePilot URL
🎥 Demo Video: Add YouTube URL
📦 Repository: This GitHub repository

---
Why IssuePilot?
When something breaks, users often know the symptom but not the information needed to diagnose it:
“Chrome won't open.”
“My Wi-Fi is connected but websites don't load.”
“This application keeps crashing.”
“What does this error code mean?”
Traditional troubleshooting often makes users search through long documentation or guess which details matter.
IssuePilot is designed around a simpler workflow:
Describe what is happening.
Show evidence when available.
Diagnose the issue with AI.
Ask targeted questions when context is missing.
Follow guided steps toward resolution.
Mark the case resolved and retain its state.
---
What makes the MVP different?
Multimodal troubleshooting
IssuePilot can use both the user's description and attached visual evidence. A screenshot containing an error message, code, dialog, or UI state can become part of the diagnosis context.
Evidence-aware cases
Evidence is attached to a case rather than being treated as a separate chat message.
```text
Case
 ├── Problem description
 ├── Evidence
 ├── Diagnosis
 ├── Questions
 ├── Next steps
 └── Resolution status
```
Structured AI output
The model is asked to return a predictable troubleshooting structure:
```json
{
  "title": "",
  "category": "",
  "severity": "",
  "summary": "",
  "likely_cause": "",
  "next_steps": [],
  "questions": [],
  "safety_notes": []
}
```
This lets the frontend present the response as a resolution workflow instead of a wall of generated text.
Resolution lifecycle
Cases move through a simple lifecycle:
```text
DIAGNOSING
     ↓
GUIDED_FIX
     ↓
RESOLVED
```
---
Architecture
```text
                         ┌──────────────────────┐
                         │      User Browser    │
                         │   IssuePilot UI      │
                         └──────────┬───────────┘
                                    │ HTTPS
                                    ▼
                         ┌──────────────────────┐
                         │  Lambda Function URL │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Flask Application    │
                         │ running on Lambda    │
                         └──────┬────────┬──────┘
                                │        │
                    ┌───────────┘        └──────────────┐
                    ▼                                   ▼
           ┌────────────────┐                  ┌────────────────┐
           │   DynamoDB     │                  │       S3       │
           │ IssuePilotCases│                  │ Evidence files │
           └────────────────┘                  └───────┬────────┘
                                                       │
                                                       │ screenshot
                                                       ▼
                                             ┌────────────────────┐
                                             │ Amazon Bedrock     │
                                             │ Nova 2 Lite        │
                                             │ multimodal AI      │
                                             └─────────┬──────────┘
                                                       │
                                                       ▼
                                             Structured diagnosis
```
AWS services used
AWS service	Role in IssuePilot
AWS Lambda	Runs the Flask backend without managing servers
Lambda Function URL	Provides the public HTTPS entry point for the deployed app
Amazon Bedrock	Provides the AI inference layer
Amazon Nova 2 Lite	Performs text and image-aware troubleshooting
Amazon S3	Stores uploaded screenshots/evidence
Amazon DynamoDB	Stores cases, evidence metadata, diagnosis and status
Amazon CloudWatch	Provides Lambda logs and operational visibility
Verified AWS deployment
The deployed MVP was verified in the AWS Console in `ap-south-1` (Mumbai).
AWS Lambda function: `IssuePilot`
Runtime: Python 3.12
Entry point: Lambda Function URL
Amazon Bedrock: Amazon Nova 2 Lite
Deployed model identifier: `global.amazon.nova-2-lite-v1:0`
DynamoDB table: `IssuePilotCases`
S3 evidence bucket: `issuepilot-evidence-550426`
IAM execution role: `IssuePilotLambdaRole`
These are the AWS resources used by the deployed MVP, rather than mock services or a README-only architecture.
The project is intentionally serverless: there is no EC2 server, RDS database, or NAT gateway in the MVP.
---
Core request flow
1. Create a case
```http
POST /cases
```
The backend creates a unique case ID and stores the initial problem.
2. Upload evidence
```http
POST /cases/{case_id}/evidence
```
The uploaded file is stored in S3 and its metadata is associated with the case.
3. Diagnose
```http
POST /cases/{case_id}/diagnose
```
IssuePilot sends the problem and supported image evidence to Amazon Bedrock.
4. Resolve
```http
POST /cases/{case_id}/resolve
```
The case status becomes:
```text
RESOLVED
```
---
Project structure
```text
issuepilot/
│
├── backend/
│   ├── app.py
│   ├── bedrock.py
│   ├── storage.py
│   └── test_bedrock.py
│
├── frontend/
│   └── index.html
│
├── deploy/
│   ├── lambda_handler.py
│   ├── frontend/
│   │   └── index.html
│   └── ...
│
├── .env
├── .gitignore
├── requirements.txt
└── issuepilot-lambda.zip
```
> `venv/`, `.env`, deployment ZIPs, credentials and other local/runtime artifacts should not be committed to Git.
---
Local development
Requirements
Python 3.10+
AWS CLI
An AWS account
Access to Amazon Bedrock in the selected region
An S3 bucket for evidence
A DynamoDB table named `IssuePilotCases`
Install dependencies
```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```
Environment variables
Create `.env`:
```env
AWS_REGION=ap-south-1
BEDROCK_MODEL_ID=amazon.nova-2-lite-v1:0
```
For local development, use the Bedrock model identifier or inference profile available to your AWS account and selected region.
The deployed Lambda currently uses the Amazon Nova 2 Lite global inference profile:
```text
global.amazon.nova-2-lite-v1:0
```
AWS authentication
Authenticate the AWS CLI using your preferred secure method.
For temporary AWS CLI login sessions:
```powershell
aws login --remote --region ap-south-1
```
Verify:
```powershell
aws sts get-caller-identity
```
Do not put AWS access keys, secret keys, session tokens, or credentials in `.env` committed to GitHub.
Run locally
```powershell
.\venv\Scripts\python.exe .\backend\app.py
```
Then open:
```text
http://127.0.0.1:5000
```
---
Deployment
The current MVP uses:
```text
Python 3.12
AWS Lambda
Handler: lambda_handler.lambda_handler
Region: ap-south-1
```
The deployment package contains the backend, frontend and Lambda adapter.
Example deployment flow:
```powershell
Copy-Item .\frontend\index.html .\deploy\frontend\index.html -Force

Remove-Item .\issuepilot-lambda.zip -Force -ErrorAction SilentlyContinue

Compress-Archive `
  -Path .\deploy\* `
  -DestinationPath .\issuepilot-lambda.zip `
  -Force

aws lambda update-function-code `
  --function-name IssuePilot `
  --zip-file fileb://issuepilot-lambda.zip `
  --region ap-south-1 `
  --no-cli-pager

aws lambda wait function-updated `
  --function-name IssuePilot `
  --region ap-south-1
```
---
Multimodal evidence pipeline
One of the core demonstrations of IssuePilot is screenshot-aware diagnosis.
```text
User attaches screenshot
          ↓
IssuePilot creates case
          ↓
Screenshot uploaded to S3
          ↓
S3 URI associated with case
          ↓
Bedrock receives problem + image evidence
          ↓
Nova 2 Lite analyzes visible information
          ↓
Structured diagnosis
```
For example, a screenshot containing a visible application error can provide information that is absent from the user's text description.
This is why evidence is part of the product workflow rather than an optional decoration.
---
Safety and reliability
IssuePilot's system prompt instructs the model to:
Avoid inventing facts.
Ask targeted questions when important context is missing.
Give understandable, practical steps.
Avoid dangerous or destructive actions.
Avoid security or licensing bypass instructions.
Clearly identify uncertainty.
The AI output is therefore presented as a guided troubleshooting aid, not as a guarantee that a diagnosis is correct.
---
Demo scenario
The recommended demo is a short end-to-end troubleshooting case.
Example
Problem
> Chrome won't open and I'm getting an application error.
Evidence
Attach a screenshot containing the visible application error.
IssuePilot
```text
Problem
   ↓
Evidence
   ↓
AI Diagnosis
   ↓
Likely Cause
   ↓
Next Steps
   ↓
Resolution
```
The demo should show the actual deployed application and the AWS-powered flow, not just screenshots of the source code.
---
Hackathon submission
IssuePilot was built for:
WeMakeDevs × AWS — First Commit 2026
The First Commit rules require a submission consisting of:
A public repository
A YouTube demo of up to three minutes
A short write-up covering the problem, build and AWS usage
The rules also require the deployed project to actually use AWS and require the demo to show that AWS usage. AI coding tools are allowed, but they must be listed in the write-up.
Official event:  
https://www.wemakedevs.org/aws/first-commit
Official rules:  
https://www.wemakedevs.org/aws/first-commit/rules
---
AI and development tools
AI-assisted development was used during the build.
Tools used:
ChatGPT — planning, debugging, architecture discussion, code assistance and UI iteration
Amazon Bedrock / Amazon Nova 2 Lite — runtime AI diagnosis in IssuePilot
VS Code — development environment
AWS CLI — deployment and AWS resource management
The application logic, AWS configuration, integration, testing and final project decisions were developed and verified as part of the hackathon build.
---
What I learned
IssuePilot was built as a practical exercise in moving from an idea to a deployed AWS application.
Key learning areas:
Designing a serverless architecture
Deploying Flask on AWS Lambda
Working with Lambda Function URLs
Using S3 for evidence storage
Persisting application state in DynamoDB
Integrating Amazon Bedrock
Passing image evidence to a multimodal model
Handling model output as structured JSON
Debugging AWS permissions and temporary CLI sessions
Building and deploying a complete end-to-end MVP
---
Future roadmap
The MVP focuses on the core resolution loop. Possible next iterations include:
Authentication and private case history
Multiple evidence files per investigation
OCR for error logs and documents
Automatic evidence classification
Follow-up diagnosis after each troubleshooting step
Confidence/explanation indicators
Browser and system diagnostics
Team/shared investigations
Knowledge-base retrieval for verified troubleshooting documentation
Resolution analytics
More specialized troubleshooting agents
---
Credits
Built with curiosity during First Commit 2026.
Special thanks to:
AWS for the cloud infrastructure and AI services
WeMakeDevs for creating the First Commit builder community
> **Small problems. Clearer paths. Better resolutions.**
---
License
Add the project's chosen license before publishing the repository.
If third-party assets, libraries, icons, illustrations or code are added, keep their required attribution and license information with the project.

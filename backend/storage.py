import os
import uuid
import boto3
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

boto3.setup_default_session(region_name=AWS_REGION)

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

table = dynamodb.Table("IssuePilotCases")

s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION", "ap-south-1")
)

S3_BUCKET = "issuepilot-evidence-550426"

_cases = {}
def create_case(problem):
    case_id = str(uuid.uuid4())

    case = {
        "case_id": case_id,
        "problem": problem.strip(),
        "evidence": [],
        "status": "DIAGNOSING",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "diagnosis": None
    }

    table.put_item(Item=case)

    return case

def upload_evidence(case_id, file):
    case = get_case(case_id)

    if not case:
        return None

    filename = file.filename
    key = f"cases/{case_id}/{uuid.uuid4()}-{filename}"

    s3.upload_fileobj(
        file,
        S3_BUCKET,
        key,
        ExtraArgs={
            "ContentType": file.content_type or "application/octet-stream"
        }
    )

    evidence = {
        "filename": filename,
        "s3_key": key,
        "type": file.content_type or "application/octet-stream"
    }

    case["evidence"].append(evidence)
    table.put_item(Item=case)

    return evidence

def get_case(case_id):
    response = table.get_item(Key={"case_id": case_id})
    return response.get("Item")


def add_evidence(case_id, evidence):
    case = get_case(case_id)

    if not case:
        return None

    case["evidence"].append(evidence)

    table.put_item(Item=case)

    return case


def set_diagnosis(case_id, diagnosis):
    case = get_case(case_id)

    if not case:
        return None

    case["diagnosis"] = diagnosis
    case["status"] = "GUIDED_FIX"

    table.put_item(Item=case)

    return case


def resolve_case(case_id):
    case = get_case(case_id)

    if not case:
        return None

    case["status"] = "RESOLVED"

    table.put_item(Item=case)

    return case
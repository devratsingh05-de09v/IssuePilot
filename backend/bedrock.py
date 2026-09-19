import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = "ap-south-1"
MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "amazon.nova-2-lite-v1:0"
)

client = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION
)

SYSTEM_PROMPT = """
You are IssuePilot, an AI problem-resolution assistant.

Your job is to take a confusing user problem and turn it into:

PROBLEM → DIAGNOSIS → NEXT ACTION → RESOLUTION

Analyze the problem carefully.

Do not invent facts.
If important information is missing, ask targeted questions.

Return ONLY valid JSON using exactly these fields:

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

Rules:
- Keep the explanation understandable.
- Give practical and actionable steps.
- Ask only useful questions.
- Never recommend dangerous or destructive actions.
- Never recommend bypassing security or licensing.
- If uncertain, clearly say what information is missing.
"""


def fallback_diagnosis(problem):
    """Temporary diagnosis engine while Bedrock access is unavailable."""

    problem_lower = problem.lower()

    if any(word in problem_lower for word in ["wifi", "internet", "network", "dns"]):
        return {
            "title": "Network connectivity problem",
            "category": "Network",
            "severity": "Medium",
            "summary": "The problem appears to be related to internet or network connectivity.",
            "likely_cause": "Possible DNS, router connectivity, Wi-Fi, or local network configuration issue.",
            "next_steps": [
                "Check whether another device can access the internet.",
                "Restart the Wi-Fi router.",
                "Reconnect the affected device to Wi-Fi.",
                "Check DNS and network configuration if the issue continues."
            ],
            "questions": [
                "Can other devices access the internet?",
                "Does the device show 'Connected, no internet'?"
            ],
            "safety_notes": [
                "Avoid factory-resetting the router unless necessary."
            ]
        }

    if any(word in problem_lower for word in ["python", "code", "error", "exception", "program"]):
        return {
            "title": "Software or programming problem",
            "category": "Software",
            "severity": "Medium",
            "summary": "The reported issue appears to involve a software or programming error.",
            "likely_cause": "The exact cause requires the error message, relevant code, and the steps that produced the problem.",
            "next_steps": [
                "Read the complete error message.",
                "Identify the line or operation where the error occurs.",
                "Check recent code or configuration changes.",
                "Test the smallest reproducible version of the problem."
            ],
            "questions": [
                "What exact error message are you seeing?",
                "What were you doing immediately before the error occurred?"
            ],
            "safety_notes": [
                "Do not delete project files or system configuration before identifying the cause."
            ]
        }

    return {
        "title": "Issue requires more information",
        "category": "General",
        "severity": "Medium",
        "summary": "The problem needs additional information before a reliable diagnosis can be made.",
        "likely_cause": "Insufficient information to identify the root cause.",
        "next_steps": [
            "Describe exactly what is happening.",
            "Provide the exact error message if one is shown.",
            "Explain what changed before the problem started."
        ],
        "questions": [
            "What exactly is not working?",
            "When did the problem start?",
            "What have you already tried?"
        ],
        "safety_notes": [
            "Avoid destructive changes until the cause is understood."
        ]
    }

def diagnose(problem, evidence=None):
    try:
        content = [
            {
                "text": problem
            }
        ]

        if evidence:
            for item in evidence:
                if item.get("type", "").startswith("image/"):
                    image_format = item["type"].split("/")[-1].lower()

                    if image_format == "jpg":
                        image_format = "jpeg"

                    if image_format in ["jpeg", "png", "gif", "webp"]:
                        content.append({
                            "image": {
                                "format": image_format,
                                "source": {
                                    "s3Location": {
                                        "uri": f"s3://issuepilot-evidence-550426/{item['s3_key']}",
                                        "bucketOwner": "645314607728"
                                    }
                                }
                            }
                        })

            content.append({
                "text": (
                    "Inspect the attached screenshot carefully. "
                    "Use visible error messages, error codes, UI elements, "
                    "and other relevant visual information as evidence for "
                    "your diagnosis. If an image is attached, do not claim "
                    "that no screenshot was provided."
                )
            })

        response = client.converse(
            modelId=MODEL_ID,
            system=[
                {
                    "text": SYSTEM_PROMPT
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            inferenceConfig={
                "maxTokens": 800,
                "temperature": 0.2
            }
        )

        text = response["output"]["message"]["content"][0]["text"]

        try:
            cleaned_text = text.strip()

            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text.replace("```json", "", 1)
                cleaned_text = cleaned_text.replace("```", "", 1)
                cleaned_text = cleaned_text.strip()

            return json.loads(cleaned_text)

        except json.JSONDecodeError:
            return {
                "title": "Analysis completed",
                "category": "Unknown",
                "severity": "Unknown",
                "summary": text,
                "likely_cause": "",
                "next_steps": [],
                "questions": [],
                "safety_notes": []
            }

    except Exception as e:
        print(f"Bedrock unavailable: {e}")
        print("Using IssuePilot fallback diagnosis engine.")
        return fallback_diagnosis(problem)
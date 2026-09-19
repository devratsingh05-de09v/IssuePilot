from bedrock import diagnose

problem = """
My laptop connects to Wi-Fi, but websites are not loading.
"""

result = diagnose(problem)

print("\n=== ISSUEPILOT RESULT ===")
print(result)
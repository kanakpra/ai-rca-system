import requests
import urllib3

# ⚠️ Disable SSL warning (only for testing)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 🔹 Step 1: Fetch logs from Splunk
def get_logs_from_splunk():
    SPLUNK_URL = "https://your-splunk-host:8089/services/search/jobs/export"
    USERNAME = "your_username"
    PASSWORD = "your_password"

    query = "search index=main ERROR OR WARN earliest=-15m"

    payload = {
        "search": query,
        "output_mode": "json"
    }

    try:
        response = requests.post(
            SPLUNK_URL,
            data=payload,
            auth=(USERNAME, PASSWORD),
            verify=False  # ⚠️ for local/testing only
        )

        if response.status_code != 200:
            print("Error fetching logs from Splunk:", response.text)
            return ""

        return response.text

    except Exception as e:
        print("Splunk connection error:", e)
        return ""


# 🔹 Step 2: Send logs to your RCA API
def send_to_rca_api(logs):
    API_URL = "http://127.0.0.1:8000/analyze"

    try:
        response = requests.post(
            API_URL,
            json={"logs": logs}
        )

        return response.json()

    except Exception as e:
        return {"error": str(e)}


# 🔹 Step 3: Main flow
def main():
    print("=== Fetching logs from Splunk ===")

    logs = get_logs_from_splunk()

    if not logs:
        print("No logs retrieved")
        return

    print("\n=== Sending logs to RCA API ===")

    result = send_to_rca_api(logs)

    print("\n=== RCA RESULT ===")
    print(result)


if __name__ == "__main__":
    main()
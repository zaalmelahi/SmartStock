import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

TEST_CASES = [
    {"name": "Normal Request", "params": {"q": "laptop"}, "expected_status": 200},
    {"name": "OR 1=1 Attack", "params": {"q": "' OR 1=1 --"}, "expected_status": 403},
    {"name": "UNION SELECT Attack", "params": {"q": "' UNION SELECT username, password FROM auth_user --"}, "expected_status": 403},
    {"name": "Stacked Query Attack", "params": {"q": "laptop; DROP TABLE store_product;"}, "expected_status": 403},
    {"name": "Comment Injection (#)", "params": {"q": "admin' #"}, "expected_status": 403},
    {"name": "Time-based Attack", "params": {"q": "' AND SLEEP(5) --"}, "expected_status": 403},
]

def run_tests():
    print(f"Starting SQLi Protection Tests on {BASE_URL}...")
    success_count = 0
    
    for test in TEST_CASES:
        print(f"Running: {test['name']}...", end=" ", flush=True)
        try:
            # Test GET
            response = requests.get(f"{BASE_URL}/", params=test['params'], timeout=5)
            
            if response.status_code == test['expected_status']:
                print("✅ PASS")
                success_count += 1
            else:
                print(f"❌ FAIL (Status: {response.status_code}, Expected: {test['expected_status']})")
                
        except requests.exceptions.ConnectionError:
            print("❌ FAIL (Server not running)")
            return
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

    print(f"\nTests completed: {success_count}/{len(TEST_CASES)} passed.")

if __name__ == "__main__":
    run_tests()

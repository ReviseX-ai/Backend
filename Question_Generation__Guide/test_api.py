import requests
import json

def test_api_connection():
    """Test if the API is running and accessible"""
    base_url = "http://127.0.0.1:5001"
    
    print("=== Testing API Connectivity ===")
    
    # 1. Test the test endpoint
    try:
        response = requests.get(f"{base_url}/api/test")
        print(f"Test endpoint: Status Code: {response.status_code}")
        if response.ok:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error connecting to test endpoint: {str(e)}")
    
    print("\n=== Testing OPTIONS Request ===")
    
    # 2. Test OPTIONS request to the generate_questions endpoint
    try:
        options_response = requests.options(f"{base_url}/api/generate_questions")
        print(f"OPTIONS Status Code: {options_response.status_code}")
        print(f"OPTIONS Headers: {dict(options_response.headers)}")
        try:
            print(f"OPTIONS Response: {options_response.json()}")
        except:
            print(f"OPTIONS Response Text: {options_response.text}")
    except Exception as e:
        print(f"Error making OPTIONS request: {str(e)}")
    
    print("\n=== Testing POST Request ===")
    
    # 3. Test a simple POST request with minimal data
    try:
        test_data = {
            "exam_type": "jee",
            "subject": "physics",
            "chapters": ["Mechanics"],
            "num_questions": 1
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        print(f"Sending POST request with data: {test_data}")
        post_response = requests.post(
            f"{base_url}/api/generate_questions", 
            data=json.dumps(test_data),
            headers=headers
        )
        
        print(f"POST Status Code: {post_response.status_code}")
        print(f"POST Headers: {dict(post_response.headers)}")
        
        if post_response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_response = post_response.json()
                print(f"POST Response JSON: {json.dumps(json_response, indent=2)[:500]}...")
            except:
                print(f"Failed to parse JSON response")
                print(f"POST Response Text: {post_response.text[:500]}...")
        else:
            print(f"POST Response Text: {post_response.text[:500]}...")
            
    except Exception as e:
        print(f"Error making POST request: {str(e)}")

if __name__ == "__main__":
    print("Testing API connectivity...\n")
    test_api_connection()
    print("\nAPI testing complete.")

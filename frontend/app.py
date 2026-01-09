from UPS import app
from UPS.job import init_job
from UPS.cv import init_cv
import requests

# Example function to call the backend API
def call_backend():
    response = requests.get('http://localhost:5000/api/example')
    if response.status_code == 200:
        print("Response from backend:", response.json())
    else:
        print("Failed to connect to backend. Status code:", response.status_code)

if __name__ == '__main__':
    # Call the backend API as an example
    call_backend()

    init_job()
    init_cv()
    app.run(debug=True)
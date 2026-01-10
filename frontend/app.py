from UPS import app
from UPS.job import init_job
from UPS.cv import init_cv
from seed import seed_database
import requests

if __name__ == '__main__':
    init_job()
    init_cv()

    seed_database()
    # Change this to port 8000
    app.run(debug=True, port=8000)
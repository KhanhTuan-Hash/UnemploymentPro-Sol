from UPS import app
from UPS.job import init_job
from UPS.cv import init_cv

if __name__ == '__main__':
    init_job()
    init_cv()
    app.run(debug=True)
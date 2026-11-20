Apex Motors — IBM Full Stack Software Developer Capstone
A complete cars dealership capstone built as four cooperating services:

Service	Technology	Responsibility
frontend	React	Responsive dealership experience
django	Django + SQLite	Registration, sessions, admin, API gateway
dealer-service	Node.js + Express + MongoDB	Dealers, reviews, makes and models
sentiment-service	Flask + TextBlob	Local sentiment scoring
Run the complete project
Requirements: Docker Desktop, Git, and a browser.

git clone <your-repository-url>
cd <your-repository-directory>
docker compose up --build
Open http://localhost:3000. Django is at http://localhost:8000, Express is at http://localhost:5001, and Flask is at http://localhost:5002.

Create the Django administrator in a second terminal:

docker compose exec django python manage.py createsuperuser
Then use http://localhost:8000/admin/. SQLite is created in backend/db.sqlite3; Mongo data is persisted in the mongo_data volume.

Local development without Compose
Start MongoDB first, then use four terminals:

cd backend && pip install -r requirements-course.txt && python manage.py migrate && python manage.py runserver 8000
cd dealer-service && npm install && MONGO_URL=mongodb://localhost:27017 DB_NAME=dealership npm start
cd sentiment-service && pip install -r requirements.txt && python app.py
cd frontend && yarn install && REACT_APP_BACKEND_URL=http://localhost:8000 yarn start
The backend reads MONGO_URL, DB_NAME, DEALER_SERVICE_URL, and SENTIMENT_SERVICE_URL from environment configuration. Docker Compose supplies service names; preview configuration uses localhost ports.

API and cURL evidence
BASE=http://localhost:8000/api
curl "$BASE/dealers"
curl "$BASE/dealers?state=Kansas"
curl "$BASE/dealers/dealer-kansas-city"
curl "$BASE/makes"
curl -c cookies.txt -X POST "$BASE/auth/register" -H 'Content-Type: application/json' -d '{"username":"demo","first_name":"Demo","last_name":"Driver","email":"demo@example.com","password":"DemoPass123!"}'
curl -b cookies.txt -X POST "$BASE/auth/login" -H 'Content-Type: application/json' -d '{"username":"demo","password":"DemoPass123!"}'
curl -b cookies.txt "$BASE/auth/user"
curl -b cookies.txt -X POST "$BASE/reviews" -H 'Content-Type: application/json' -d '{"dealer_id":"dealer-kansas-city","rating":5,"comment":"Excellent service and a friendly team."}'
curl "$BASE/reviews?dealer_id=dealer-kansas-city"
curl -X POST http://localhost:5002/analyze -H 'Content-Type: application/json' -d '{"text":"The buying experience was excellent"}'
Authentication uses Django sessions and SQLite. Review documents are written to MongoDB, and each review is analyzed by Flask/TextBlob before persistence. When an auxiliary process is temporarily unavailable, Django performs the same database-backed operation locally rather than returning a mock response.

Tests and CI
Run Python syntax checks and the Django API test suite from the repository root:

python -m py_compile backend/server.py backend/config/*.py backend/dealership/*.py sentiment-service/app.py
python backend/manage.py test backend/dealership
node --check dealer-service/server.js
.github/workflows/ci.yml repeats Python checks, Node syntax validation, dependency installation, and docker compose config on every push and pull request.

28 capstone evidence tasks
Capture one screenshot or terminal response for each: (1) repository tree, (2) README, (3) homepage, (4) responsive mobile homepage, (5) dealer listing, (6) Kansas filter, (7) dealer detail, (8) registration form, (9) registration response, (10) login form, (11) login response, (12) logout, (13) admin login, (14) admin logout, (15) review form, (16) persisted review, (17) review list, (18) positive sentiment, (19) negative sentiment, (20) neutral sentiment, (21) makes endpoint, (22) Django SQLite migration, (23) Mongo persistence, (24) Express health endpoint, (25) Flask health endpoint, (26) Docker Compose build, (27) GitHub Actions run, and (28) Code Engine deployment configuration.

IBM Cloud Code Engine
Build and push frontend, backend, dealer-service, and sentiment-service images to a registry. Create four Code Engine applications, expose the frontend and Django gateway publicly, and configure internal service URLs for Django-to-Express and Django-to-Flask traffic. Add MONGO_URL, DB_NAME, DEALER_SERVICE_URL, SENTIMENT_SERVICE_URL, and DJANGO_SECRET_KEY as application environment variables. Attach a managed MongoDB connection to the dealer service and use the container filesystem for the SQLite Django database during a demo deployment.# apex-motors-dealership

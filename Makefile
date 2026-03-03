.PHONY: setup train run-backend run-frontend docker-up

setup:
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

dataset:
	cd backend && python -m ml.dataset_prep

train:
	cd backend && python -m ml.train_yolo --data datasets/pothole/data.yaml --epochs 100 --model-size n

run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm start

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down
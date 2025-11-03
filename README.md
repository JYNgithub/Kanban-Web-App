# Project is in development
---
# Setup
## 1. Install Python dependencies
pip install -r requirements.txt

## 2. Install Vue dependencies
cd frontend
npm install

## 3. Run both apps
### Backend:
cd backend
uvicorn main:app --reload

### Frontend:
cd frontend
npm run dev
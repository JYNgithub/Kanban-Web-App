# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Vue dependencies
cd frontend
npm install

# 3. Run both apps
# Terminal 1 (Backend):
uvicorn main:app --reload

# Terminal 2 (Frontend):
npm run dev
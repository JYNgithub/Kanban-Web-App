# TODO
1. Fix CSS scope + Overall design
2. Forgot password feature
3. Edit records feature
4. Rework add record button design
5. Add JS to check server health

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Vue dependencies
cd frontend
npm install

# 3. Run both apps
# Terminal 1 (Backend):
cd backend
uvicorn main:app --reload

# Terminal 2 (Frontend):
cd frontend
npm run dev
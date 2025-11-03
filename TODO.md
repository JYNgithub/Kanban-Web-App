# TODO
- [ ] Edit records
- [ ] Add Google login
- [ ] Add Forgotten Password 
- [ ] Redesign 
- [ ] Fix deprecated datetime.utcnow()
- [ ] Fix long user input breaking kanban record cards

# In Progress


# On Hold
1. Sequential int as keys may have security risk
- Must check user_id = current_user["user_id"] at every endpoint
- Consider to do checking + using UUID instead

# Completed
- [x] Delete records
- [x] Add expected revenue to records
# Certificate Role-Based Access Control Implementation

## Summary
Implemented role-based access control for certificate operations. Now:
- **Volunteers**: Can ONLY download their own certificate
- **Admins**: Have full access (edit, delete, download any volunteer's certificate)

---

## Files Modified

### 1. `app/models.py`
**Change**: Added user relationship to Volunteer model
- Added `user_id` field (foreign key to User)
- Added `user` relationship to link Volunteer to User account

### 2. `app/routes/nss.py`
**Changes**: Updated authorization checks on 4 routes

#### `volunteers()` Route
- Volunteers now see ONLY their own volunteer record
- Admins see ALL volunteers

#### `generate_certificate()` Route  
- OLD: Only admins could view certificates
- NEW: Admins can view any, volunteers can view their own only

#### `download_certificate()` Route
- OLD: Only admins could download certificates
- NEW: Admins can download any, volunteers can download their own only

#### `edit_volunteer()` Route
- Unchanged: Admins only (no volunteer access)

#### `delete_volunteer()` Route
- Unchanged: Admins only (no volunteer access)

### 3. `app/templates/volunteers.html`
**Change**: Updated button display logic

- **For Admins**: Shows `Edit`, `Certificate` (download), and `Delete` buttons
- **For Volunteers**: Shows only `Download Certificate` button

---

## Database Migration

A migration file has been created: `migrations/versions/add_user_id_to_volunteers.py`

### To Apply the Migration:

```bash
# 1. Navigate to project directory
cd c:\Users\keert\e-plastic-management

# 2. Activate your Python environment (if using venv)
# .venv\Scripts\activate  (Windows)
# source venv/bin/activate  (Linux/Mac)

# 3. Apply the migration
flask db upgrade
```

### What the migration does:
- Adds `user_id` column to `volunteers` table
- Creates foreign key constraint to `users` table
- Allows linking volunteers to user accounts

---

## How to Link Volunteers to Users

After running the migration, you need to link existing volunteers to user accounts. You can do this by:

### Option 1: Manual SQL Update
```sql
UPDATE volunteers 
SET user_id = (SELECT id FROM users WHERE email = volunteers.email LIMIT 1)
WHERE user_id IS NULL AND email IS NOT NULL;
```

### Option 2: Python Script
```python
from app.models import User, Volunteer
from app import db

# Link volunteers to users by email
volunteers = Volunteer.query.filter_by(user_id=None).all()
for vol in volunteers:
    user = User.query.filter_by(username=vol.email).first()
    if user:
        vol.user_id = user.id
        db.session.add(vol)

db.session.commit()
```

---

## Authorization Logic

### Backend (Routes)
- Check: `if not current_user.is_admin() and volunteer.user_id != current_user.id:`
- This prevents unauthorized access at the API level

### Frontend (Templates)
- Conditional button rendering based on `current_user.is_admin()`
- Volunteers see limited options

---

## Testing the Implementation

1. **Log in as Admin**
   - Should see all volunteers
   - Can edit, download, and delete any certificate

2. **Log in as Volunteer**
   - Should see ONLY their own record
   - Can download only their own certificate
   - Cannot access edit/delete buttons

3. **Try Direct URL Access**
   - Volunteer accessing `/certificate/other_volunteer_id` → Redirected with error message
   - Admin accessing any ID → Works normally

---

## Notes

- Volunteers who are not linked to a user account cannot download certificates
- The `user_id` field is nullable for backward compatibility
- Edit and Delete operations are restricted to admins only
- Authorization is enforced both on backend routes AND frontend templates (defense in depth)

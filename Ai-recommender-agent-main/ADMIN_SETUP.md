# Admin Setup Guide

## Making a User an Admin

After creating a user account, you can make them an admin using the provided script:

```bash
cd backend
python make_admin.py <user_email>
```

Example:
```bash
python make_admin.py admin@example.com
```

## SQL Query Alternative

You can also set a user as admin directly in PostgreSQL:

```sql
-- Connect to your database
psql -U postgres -d job_recommender

-- Update user to admin
UPDATE users SET is_admin = true WHERE email = 'your-email@example.com';
```

## Verifying Admin Status

After making a user admin:
1. Logout and login again
2. The admin dashboard link should appear on the main dashboard
3. You can access `/admin` route

## Features Available to Admins

- View system statistics
- Manage all jobs (activate/deactivate, delete)
- View all users
- Trigger manual job scraping
- Access admin-only API endpoints


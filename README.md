# Pastebin App

A modern Flask-based pastebin application with user authentication, role-based access control, tags, search, and more!

## Features

✨ **Core Features:**
- 🔥 New paste highlights (< 24h)
- 👁️ View counter system
- 🏷️ Tags support
- 🔍 Full-text search
- ⏱️ Relative time display
- 📌 Pin important pastes

👥 **User & Admin Features:**
- User registration and authentication
- Role-based hierarchy (OWNER → MANAGER → MOD → COUNCIL → HELPER → MEMBERS)
- Admin panel for user management
- User directory page
- Rank customization

🎨 **UI/UX:**
- Modern dark theme with cyan accent colors
- Fully responsive design
- Smooth animations and transitions
- Intuitive navigation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/pastebin.git
cd pastebin
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Create an Account
- Click "Register" to create a new account (default rank: MEMBERS)
- Click "Login" to log in

### Create a Paste
- Click "📝 New Paste"
- Add title, content, and optional tags
- Click "Create Paste 🚀"

### Manage Content (OWNER/MANAGER/MOD only)
- Pin important pastes with the 📌 button
- Delete pastes with the 🗑️ button

### Admin Panel (OWNER only)
- Access at `/admin`
- View all users
- Change user ranks using the dropdown menu

### View Users
- Click "👥 Users" to see all registered users and their ranks

## Rank Hierarchy

| Rank | Permissions |
|------|------------|
| **OWNER** | Full access, manage all users and ranks |
| **MANAGER** | Manage content and lower ranks |
| **MOD** | Delete and pin content |
| **COUNCIL** | Community moderator |
| **HELPER** | Can assist users |
| **MEMBERS** | Regular user |

## Database

The app uses SQLite (`site.db`) with two main tables:
- **users**: username, password, rank
- **pastes**: title, content, author, views, created, tags, pinned

## Default Admin Account

Username: `Admin`
Password: `1[YFx[h2'D1Pa6Ds7:`

⚠️ **Change this immediately in production!**

## Deployment

### Option 1: Deploy to Heroku

1. Create a `Procfile`:
```
web: python app.py
```

2. Create a `runtime.txt`:
```
python-3.9.16
```

3. Update `app.py` for production:
```python
if __name__=="__main__":
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)
```

4. Push to Heroku:
```bash
heroku create your-app-name
git push heroku main
```

### Option 2: Deploy to PythonAnywhere

1. Upload your files to PythonAnywhere
2. Create a web app with Flask
3. Configure the WSGI file to point to your app
4. Set up the virtual environment with dependencies

### Option 3: Deploy to Railway/Render

Follow their documentation for Flask apps.

## Security Notes

- Change the `secret_key` in `app.py`
- Update default admin credentials
- Use environment variables for sensitive data
- Enable HTTPS in production
- Set `debug=False` in production

## License

MIT License - feel free to use and modify!

## Contributing

Pull requests are welcome!

## Support

For issues and questions, please open a GitHub issue.

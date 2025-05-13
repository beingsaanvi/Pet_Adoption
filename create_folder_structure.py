import os

def create_file(path, content=""):
    """Create a file with optional content."""
    with open(path, 'w') as f:
        f.write(content)

def create_folder_structure():
    """Create the folder structure for the Django pet_adoption project."""
    # Base directory
    base_dir = "pet_adoption"
    os.makedirs(base_dir, exist_ok=True)

    # frontend app directory
    frontend_dir = os.path.join(base_dir, "frontend")
    os.makedirs(frontend_dir, exist_ok=True)

    # frontend/migrations
    migrations_dir = os.path.join(frontend_dir, "migrations")
    os.makedirs(migrations_dir, exist_ok=True)
    create_file(os.path.join(migrations_dir, "__init__.py"))

    # frontend/static/css
    static_css_dir = os.path.join(frontend_dir, "static", "css")
    os.makedirs(static_css_dir, exist_ok=True)
    create_file(os.path.join(static_css_dir, "styles.css"), "/* Custom styles */\n")

    # frontend/static/js
    static_js_dir = os.path.join(frontend_dir, "static", "js")
    os.makedirs(static_js_dir, exist_ok=True)
    create_file(os.path.join(static_js_dir, "scripts.js"), "// Custom JavaScript\n")

    # frontend/templates
    templates_dir = os.path.join(frontend_dir, "templates")
    os.makedirs(templates_dir, exist_ok=True)
    template_files = [
        "base.html",
        "index.html",
        "pet_detail.html",
        "adoption_request.html",
        "admin_dashboard.html",
        "admin_pets.html",
        "admin_requests.html"
    ]
    for template in template_files:
        create_file(os.path.join(templates_dir, template))

    # frontend app files
    frontend_files = [
        "__init__.py",
        "admin.py",
        "apps.py",
        "models.py",
        "tests.py",
        "urls.py",
        "views.py"
    ]
    for file in frontend_files:
        create_file(os.path.join(frontend_dir, file))

    # pet_adoption project directory
    project_dir = os.path.join(base_dir, "pet_adoption")
    os.makedirs(project_dir, exist_ok=True)
    project_files = [
        "__init__.py",
        "asgi.py",
        "settings.py",
        "urls.py",
        "wsgi.py"
    ]
    for file in project_files:
        create_file(os.path.join(project_dir, file))

    # Root files
    create_file(os.path.join(base_dir, "manage.py"))
    create_file(os.path.join(base_dir, "requirements.txt"), """django==4.2.7
djangorestframework==3.14.0
requests==2.31.0
""")

if __name__ == "__main__":
    create_folder_structure()
    print("Folder structure created successfully!")
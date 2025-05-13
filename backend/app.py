import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/uploads/*": {"origins": "*"},
    r"/pets/*": {"origins": "*"},
    r"/adoption-requests/*": {"origins": "*"}
})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max filesize
app.secret_key = 'supersecretkey'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    age = db.Column(db.String(20))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    adopted = db.Column(db.Boolean, default=False)

class AdoptionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    rejected = db.Column(db.Boolean, default=False)  # New column
    pet = db.relationship('Pet', backref=db.backref('adoption_requests', lazy=True))

def is_admin_logged_in():
    return session.get('admin_logged_in', False)

def admin_login_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            return jsonify({'error': 'Unauthorized, please login'}), 401
        return func(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('admin_logged_in', None)
    return jsonify({'message': 'Logged out successfully'})

@app.route('/pets', methods=['GET'])
def get_pets():
    type_filter = request.args.get('type')
    adopted_filter = request.args.get('adopted')
    query = Pet.query
    if type_filter:
        query = query.filter_by(type=type_filter)
    if adopted_filter:
        query = query.filter_by(adopted=adopted_filter.lower() == 'true')
    pets = query.all()
    base_url = request.url_root.rstrip('/')
    return jsonify([{
        'id': pet.id,
        'name': pet.name,
        'type': pet.type,
        'breed': pet.breed,
        'gender': pet.gender,
        'age': pet.age,
        'description': pet.description,
        'image_url': f"{base_url}{pet.image_url}" if pet.image_url else None,
        'adopted': pet.adopted
    } for pet in pets])

@app.route('/pets/<int:id>', methods=['GET'])
def get_pet(id):
    pet = Pet.query.get_or_404(id)
    return jsonify({
        'id': pet.id,
        'name': pet.name,
        'type': pet.type,
        'breed': pet.breed,
        'gender': pet.gender,
        'age': pet.age,
        'description': pet.description,
        'image_url': pet.image_url,
        'adopted': pet.adopted
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/pets', methods=['POST'])
@admin_login_required
def add_pet():
    name = request.form.get('name')
    pet_type = request.form.get('type')
    breed = request.form.get('breed', '')
    gender = request.form.get('gender', '')
    age = request.form.get('age', '')
    description = request.form.get('description', '')
    
    # Handle file upload
    file = request.files.get('image')
    image_url = None
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_url = f'/uploads/{filename}'
    
    new_pet = Pet(
        name=name,
        type=pet_type,
        breed=breed,
        gender=gender,
        age=age,
        description=description,
        image_url=image_url
    )
    
    db.session.add(new_pet)
    db.session.commit()
    
    return jsonify({'message': 'Pet added successfully'}), 201

@app.route('/pets/<int:id>/adopted', methods=['PATCH'])
@admin_login_required
def mark_adopted(id):
    pet = Pet.query.get_or_404(id)
    pet.adopted = True
    db.session.commit()
    return jsonify({'message': 'Pet marked as adopted'})

@app.route('/pets/<int:id>', methods=['DELETE'])
@admin_login_required
def delete_pet(id):
    pet = Pet.query.get_or_404(id)
    db.session.delete(pet)
    db.session.commit()
    return jsonify({'message': 'Pet deleted successfully'})

@app.route('/adoption-requests', methods=['POST'])
def add_adoption_request():
    data = request.get_json()
    new_request = AdoptionRequest(
        user_name=data['user_name'],
        email=data['email'],
        phone=data.get('phone', ''),
        message=data.get('message', ''),
        pet_id=data['pet_id']
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Adoption request submitted successfully'}), 201

@app.route('/adoption-requests', methods=['GET'])
@admin_login_required
def get_adoption_requests():
    requests = AdoptionRequest.query.all()
    return jsonify([{
        'id': req.id,
        'user_name': req.user_name,
        'email': req.email,
        'phone': req.phone,
        'message': req.message,
        'pet_id': req.pet_id,
        'pet_name': req.pet.name if req.pet else "Unknown",
        'approved': req.approved,
        'rejected': req.rejected  # Added rejected status
    } for req in requests])

@app.route('/adoption-requests/<int:id>/approve', methods=['PATCH'])
@admin_login_required
def approve_adoption_request(id):
    req = AdoptionRequest.query.get_or_404(id)
    req.approved = True
    pet = Pet.query.get_or_404(req.pet_id)
    pet.adopted = True
    db.session.commit()
    return jsonify({'message': 'Adoption request approved and pet marked as adopted'})

@app.route('/adoption-requests/<int:id>/reject', methods=['PATCH'])
@admin_login_required
def reject_adoption_request(id):
    req = AdoptionRequest.query.get_or_404(id)
    req.rejected = True
    req.approved = False  # Ensure it's not approved if previously approved
    db.session.commit()
    return jsonify({'message': 'Adoption request rejected'})

@app.route('/adoption-requests/<int:id>', methods=['DELETE'])
@admin_login_required
def delete_adoption_request(id):
    req = AdoptionRequest.query.get_or_404(id)
    db.session.delete(req)
    db.session.commit()
    return jsonify({'message': 'Adoption request deleted successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

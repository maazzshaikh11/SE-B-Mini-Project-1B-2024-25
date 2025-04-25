import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login_manager
from app.utils.db import execute_query

class User(UserMixin):
    def __init__(self, id, email, first_name, last_name, phone, is_admin, is_approved, referral_code):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.is_admin = is_admin
        self.is_approved = is_approved
        self.referral_code = referral_code
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @staticmethod
    def get_by_id(user_id):
        query = """
        SELECT id, email, first_name, last_name, phone, is_admin, is_approved, referral_code
        FROM users
        WHERE id = %s
        """
        result = execute_query(query, (user_id,))
        
        if result:
            user_data = result[0]
            return User(
                id=user_data['id'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data['phone'],
                is_admin=user_data['is_admin'],
                is_approved=user_data['is_approved'],
                referral_code=user_data['referral_code']
            )
        return None
    
    @staticmethod
    def get_by_email(email):
        query = """
        SELECT id, email, password, first_name, last_name, phone, is_admin, is_approved, referral_code
        FROM users
        WHERE email = %s
        """
        result = execute_query(query, (email,))
        
        if result:
            return result[0]
        return None
    
    @staticmethod
    def get_by_referral_code(referral_code):
        query = """
        SELECT id, email, first_name, last_name, phone, is_admin, is_approved, referral_code
        FROM users
        WHERE referral_code = %s
        """
        result = execute_query(query, (referral_code,))
        
        if result:
            user_data = result[0]
            return User(
                id=user_data['id'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data['phone'],
                is_admin=user_data['is_admin'],
                is_approved=user_data['is_approved'],
                referral_code=user_data['referral_code']
            )
        return None
    
    @staticmethod
    def create_user(email, password, first_name, last_name, phone, is_admin=False):
        # Generate a unique referral code
        referral_code = generate_referral_code()
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        query = """
        INSERT INTO users (email, password, first_name, last_name, phone, is_admin, referral_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (email, hashed_password, first_name, last_name, phone, is_admin, referral_code)
        
        user_id = execute_query(query, params, fetch=False)
        
        return user_id
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        return check_password_hash(stored_password, provided_password)
    
    @staticmethod
    def get_community_members(community_id):
        query = """
        SELECT u.id, u.email, u.first_name, u.last_name, u.phone, u.is_admin, u.is_approved, u.referral_code,
               cm.flat_no, cm.floor_no, cm.is_rented
        FROM users u
        JOIN community_members cm ON u.id = cm.user_id
        WHERE cm.community_id = %s
        """
        return execute_query(query, (community_id,))

def generate_referral_code(length=8):
    """Generate a random referral code."""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        
        # Check if code already exists
        query = "SELECT COUNT(*) as count FROM users WHERE referral_code = %s"
        result = execute_query(query, (code,))
        
        if result[0]['count'] == 0:
            return code

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
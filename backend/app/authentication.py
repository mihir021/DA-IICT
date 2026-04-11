import jwt
import os
from rest_framework import authentication
from rest_framework import exceptions
from .database import get_db, USERS
from bson import ObjectId

JWT_SECRET = os.getenv("DJANGO_SECRET_KEY", "your-secret-key")

class MongoUser:
    def __init__(self, data):
        self.data = data
        self.is_authenticated = True
        self.id = str(data.get("_id"))
    
    def __getitem__(self, key):
        return self.data.get(key)
    
    def get(self, key, default=None):
        return self.data.get(key, default)

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(" ")
            if prefix.lower() != "bearer":
                return None
        except ValueError:
            return None

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                raise exceptions.AuthenticationFailed("Invalid payload")
            
            db = get_db()
            user = db[USERS].find_one({"_id": ObjectId(user_id)})
            if not user:
                raise exceptions.AuthenticationFailed("User not found")
            
            return (MongoUser(user), token)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e))

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from passlib.context import CryptContext
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from typing import Union, Any
from jose import jwt
import os, smtplib, random
from pydantic import BaseModel

load_dotenv()

class TokenData(BaseModel):
    email: str = None

class AuthUtils(BaseModel):
    @staticmethod
    def convert_object_ids(data):
        data['_id'] = str(data['_id'])
    
    @staticmethod
    def send_otp(email: str) -> str:
        otp = random.randint(100000, 999999)
        msg = MIMEMultipart()
        msg["From"] = os.getenv("EMAIL_FROM")
        msg["To"] = email
        msg["Subject"] = "OTP Verification"
        body = f"Your OTP verification code is: {otp}"
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.connect(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT")))
            server.starttls()
            server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
            server.sendmail(os.getenv("EMAIL_FROM"), email, msg.as_string())
            server.quit()

        return otp
    
    @staticmethod
    def get_hashed_password(password: str) -> str:
        return CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)
    
    @staticmethod
    def verify_password(password: str, hashed_pass: str) -> bool:
        return CryptContext(schemes=["bcrypt"], deprecated="auto").verify(password, hashed_pass)

    @staticmethod
    def create_access_token(email: str, expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.now(timezone.utc) + expires_delta
        else:
            expires_delta = datetime.now(timezone.utc) + timedelta(minutes = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))

        to_encode = {"email": str(email), "exp": expires_delta}
        encoded_jwt = jwt.encode(to_encode, os.getenv('JWT_SECRET_KEY'), os.getenv('ALGORITHM'))
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(email: str, expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.now(timezone.utc) + expires_delta
        else:
            expires_delta = datetime.now(timezone.utc) + timedelta(minutes = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES')))

        to_encode = {"email": str(email), "exp": expires_delta}
        encoded_jwt = jwt.encode(to_encode, os.getenv('JWT_REFRESH_SECRET_KEY'), os.getenv('ALGORITHM'))
        return encoded_jwt

    @staticmethod
    def get_current_user(TokenData: str = Depends(OAuth2PasswordBearer(tokenUrl = '/auth/login', scheme_name = 'JWT'))):
        try:
            payload = jwt.decode(TokenData, os.getenv('JWT_SECRET_KEY'), os.getenv('ALGORITHM'))
            if datetime.fromtimestamp(payload['exp']) < datetime.now(timezone.utc):
                return {'status_code': 404, 'TokenData': '', 'message': 'Token Expired'}
            else:
                return TokenData(email = payload['email'])
        except:
            return {'status_code': 404, 'data': {}, 'message': 'Invalid Token'}
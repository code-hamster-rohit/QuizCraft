from fastapi import APIRouter, Depends, Form
from configurations.config import Config
from routes.auth.auth_utils import AuthUtils, TokenData
from operations.rules import Rules
from bson import ObjectId
from datetime import datetime

class Auth:
    def __init__(self):
        self.router = APIRouter()
        self.client = Config().GetClient()
        self.router.add_api_route('/generate_before_auth_otp', self.__generate_before_auth_otp, methods=['POST'])
        self.router.add_api_route('/signup', self.__signup, methods=['POST'])
        self.router.add_api_route('/generate_after_auth_otp', self.__generate_after_auth_otp, methods=['POST'])
        self.router.add_api_route('/login', self.__login, methods=['POST'])
        self.router.add_api_route('/forgot-password', self.__forgot_password, methods=['PUT'])
        self.router.add_api_route('/logout', self.__logout, methods=['PUT'])
        self.router.add_api_route('/delete-account', self.__delete_account, methods=['DELETE'])
        self.router.add_api_route('/me', self.__me, methods=['GET'])
    
    async def __generate_before_auth_otp(self, email: str = Form(...)):
        try:
            user = Rules.get({'email': email}, self.client, 'AUTH', 'USERS')
            if user:
                return {'status_code': 404, 'data': {}, 'message': 'User already exists, try logging in'}
            else:
                self.__otp = str(AuthUtils.send_otp(email))
                # data = {'_id': ObjectId(), 'email': email, 'otp': self.__otp, 'date_sent': datetime.now()}
                # Rules.add(data, self.client, 'AUTH', 'OTPS')
                return {'status_code': 200, 'message': 'Otp sent to your Email Id'}
        except Exception as e:
            return {'status_code': 404, 'message': str(e)}
    
    
    async def __signup(self, first_name: str = Form(...), last_name: str = Form(...), email: str = Form(...), password: str = Form(...), use_type: str = Form(...), otp: str = Form(...)):
        if otp == self.__otp:
            data = {'_id': ObjectId(), 'first_name': first_name, 'last_name': last_name, 'email': email, 'password': AuthUtils.get_hashed_password(password), 'use_type': use_type, 'is_active': True, 'date_joined': datetime.now()}
            operation_id = Rules.add(data, self.client, 'AUTH', 'USERS')
            access_token, refresh_token = AuthUtils.create_access_token(email), AuthUtils.create_refresh_token(email)
            return {'status_code': 200, 'operation_id': operation_id, 'access_token': access_token, 'refresh_token': refresh_token, 'message': 'Signup Successful'}
        else:
            return {'status_code': 404, 'operation_id': '', 'message': 'Invalid OTP'}
    
    async def __generate_after_auth_otp(self, email: str = Form(...)):
        user = Rules.get({'email': email}, self.client, 'AUTH', 'USERS')
        if user:
            self.__otp = str(AuthUtils.send_otp(email))
            # data = {'_id': ObjectId(), 'email': email, 'otp': self.__otp, 'date_sent': datetime.now()}
            # Rules.add(data, self.client, 'AUTH', 'OTPS')
            return {'status_code': 200, 'message': 'Otp sent to your Email Id'}
        else:
            return {'status_code': 404, 'message': 'User does not exist, try signing up'}

    async def __login(self, email: str = Form(...), password: str = Form(...), otp: str = Form(...)):
        if otp == self.__otp:
            query = {'email': email}
            data = AuthUtils.convert_object_ids(Rules.get(query, self.client, 'AUTH', 'USERS'))
            if AuthUtils.verify_password(password, data['password']):
                Rules.update(query, {'is_active': True}, self.client, 'AUTH', 'USERS')
                access_token, refresh_token = AuthUtils.create_access_token(email), AuthUtils.create_refresh_token(email)
                return {'status_code': 200, 'data': data, 'access_token': access_token, 'refresh_token': refresh_token, 'message': 'Login Successful'}
            else:
                return {'status_code': 404, 'data': {}, 'message': 'Invalid Password'}
        else:
            return {'status_code': 404, 'data': {}, 'message': 'Invalid OTP'}
    
    async def __forgot_password(self, email: str = Form(...), otp: str = Form(...), new_password: str = Form(...)):
        if otp == self.__otp:
            Rules.update({'email': email}, {'password': new_password}, self.client, 'AUTH', 'USERS')
            return {'status_code': 200, 'message': 'Password Updated Successfully'}
        else:
            return {'status_code': 404, 'message': 'Invalid OTP'}
          
    async def __logout(self, email: str = Form(...)):
        Rules.update({'email': email}, {'is_active': False}, self.client, 'AUTH', 'USERS')
        return {'status_code': 200, 'message': 'Logged Out Successfully'}
    
    async def __delete_account(self, email: str = Form(...)):
        Rules.delete({'email': email}, self.client, 'AUTH', 'USERS')
        return {'status_code': 200, 'message': 'Account Deleted Successfully'}
    
    async def __me(self, current_user : TokenData = Depends(AuthUtils.get_current_user)):
        return current_user
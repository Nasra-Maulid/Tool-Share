from config import app, db, api
from flask import request, make_response, session
from flask_restful import Resource
from models import User, Tool, Booking, Review
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            user = User(
                username=data['username'],
                email=data['email'],
                phone=data.get('phone', ''),
                address=data.get('address', '')
            )
            user.password_hash = data['password']
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 422

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {'error': 'Invalid credentials'}, 401

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {}, 204

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            return user.to_dict(), 200
        return {}, 401

class Tools(Resource):
    def get(self):
        tools = [tool.to_dict() for tool in Tool.query.all()]
        return tools, 200
    
    def post(self):
        data = request.get_json()
        try:
            tool = Tool(
                name=data['name'],
                description=data['description'],
                image_url=data['image_url'],
                daily_rate=data['daily_rate'],
                deposit=data.get('deposit', 0),
                available=data.get('available', True),
                owner_id=session.get('user_id')
            )
            db.session.add(tool)
            db.session.commit()
            return tool.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 422

class ToolById(Resource):
    def get(self, id):
        tool = Tool.query.get(id)
        if tool:
            return tool.to_dict(), 200
        return {'error': 'Tool not found'}, 404
    
    def patch(self, id):
        tool = Tool.query.get(id)
        if not tool:
            return {'error': 'Tool not found'}, 404
        if tool.owner_id != session.get('user_id'):
            return {'error': 'Unauthorized'}, 403
        
        data = request.get_json()
        try:
            for attr in data:
                setattr(tool, attr, data[attr])
            db.session.commit()
            return tool.to_dict(), 200
        except Exception as e:
            return {'error': str(e)}, 422
    
    def delete(self, id):
        tool = Tool.query.get(id)
        if not tool:
            return {'error': 'Tool not found'}, 404
        if tool.owner_id != session.get('user_id'):
            return {'error': 'Unauthorized'}, 403
        
        db.session.delete(tool)
        db.session.commit()
        return {}, 204

class Bookings(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        bookings = Booking.query.filter_by(borrower_id=user_id).all()
        return [b.to_dict() for b in bookings], 200
    
    def post(self):
        data = request.get_json()
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        try:
            tool = Tool.query.get(data['tool_id'])
            if not tool:
                return {'error': 'Tool not found'}, 404
            
            start_date = datetime.datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_date = datetime.datetime.strptime(data['end_date'], '%Y-%m-%d')
            days = (end_date - start_date).days
            
            booking = Booking(
                start_date=start_date,
                end_date=end_date,
                status='pending',
                total_price=tool.daily_rate * days,
                tool_id=data['tool_id'],
                borrower_id=user_id
            )
            db.session.add(booking)
            db.session.commit()
            return booking.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 422

class Reviews(Resource):
    def get(self, tool_id):
        reviews = Review.query.filter_by(tool_id=tool_id).all()
        return [r.to_dict() for r in reviews], 200
    
    def post(self, tool_id):
        data = request.get_json()
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        try:
            review = Review(
                rating=data['rating'],
                comment=data.get('comment', ''),
                tool_id=tool_id,
                reviewer_id=user_id
            )
            db.session.add(review)
            db.session.commit()
            return review.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 422

api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Tools, '/tools')
api.add_resource(ToolById, '/tools/<int:id>')
api.add_resource(Bookings, '/bookings')
api.add_resource(Reviews, '/tools/<int:tool_id>/reviews')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
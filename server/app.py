#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, UserSchema


class ClearSession(Resource):

    def delete(self):
        session.clear()
        return {}, 204


api.add_resource(ClearSession, '/clear', endpoint='clear')


class Signup(Resource):

    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        user = User(username=username)
        user.password_hash = password

        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

        return UserSchema().dump(user), 201


api.add_resource(Signup, '/signup', endpoint='signup')


class CheckSession(Resource):

    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = db.session.get(User, user_id)

            if user:
                return UserSchema().dump(user), 200

        return {}, 204


api.add_resource(CheckSession, '/check_session', endpoint='check_session')


class Login(Resource):

    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return UserSchema().dump(user), 200

        return {'error': 'Invalid username or password'}, 401


api.add_resource(Login, '/login', endpoint='login')


class Logout(Resource):

    def delete(self):
        session.pop('user_id', None)
        return {}, 204


api.add_resource(Logout, '/logout', endpoint='logout')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
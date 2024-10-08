#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class Heroes(Resource):
    def get(self):
        heroes =[]
        for hero in Hero.query.all():
            hero_dict = {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name
            }
            heroes.append(hero_dict)
        return make_response(jsonify(heroes), 200)

class HeroesId(Resource):
    
    def get(self, id):
        hero = Hero.query.filter(Hero.id == id).first()
        
        if hero:
            hero_dict = {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name,
                "hero_powers": []
            }

            for hero_power in hero.hero_power:
                power_dict = {
                    "hero_id": hero.id,
                    "id": hero_power.power.id,
                    "power":{
                        "description": hero_power.power.description,
                        "id": hero_power.id,
                        "name": hero_power.power.name
                    },
                    "power_id": hero_power.id,
                    "strength": hero_power.strength  
                }
                hero_dict["hero_powers"].append(power_dict)

            return make_response(jsonify(hero_dict), 200)
        else:
            return make_response(jsonify({"error": "Hero not found"}), 404)
        
        
class Powers(Resource):
    
    def get(self):
        powers =[]
        
        for power in Power.query.all():
            power_dict = {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }
            powers.append(power_dict)
        return make_response(jsonify(powers), 200)
    
class PowersId(Resource):
    
    def get(self, id):
        power =  Power.query.filter(Power.id == id).first()
        
        if power:
            power_dict = {
                "id": power.id, 
                "name": power.name, 
                "description": power.description 
            }
            return make_response(jsonify(power_dict), 200)
        else:
            return make_response(jsonify({"error": "Power not found"}), 404)
    
    def patch(self, id):
        power = Power.query.filter(Power.id == id).first()
        
        if not power:
            return make_response(jsonify({"error": "Power not found"}), 404)

        try:
            data = request.get_json()  # Use JSON input
            for attr, value in data.items():
                setattr(power, attr, value)

            db.session.commit()  # Commit changes to the database

            power_dict = {
                "description": power.description,
                "id": power.id,
                "name": power.name 
            }

            return make_response(jsonify(power_dict), 200)

        except Exception as e:  # Catch broader exceptions
            return make_response({"error": str(e)}, 500)

class HeroPower(Resource):
    
    def post(self):
        data = request.get_json()
        new_hero_power = HeroPower(
            strength = data.get('strength'),
            power_id = data.get('power_id'),
            hero_id = data.get('hero_id')
        )
        db.session.add(new_hero_power)
        db.session.commit()
        
        if new_hero_power:
            return make_response(jsonify(new_hero_power.to_dict()), 200)
        else:
            return make_response(jsonify({"errors": ["validation errors"]}), 404)

api.add_resource(Heroes, '/heroes')
api.add_resource(HeroesId, '/heroes/<int:id>')
api.add_resource(Powers, '/powers')
api.add_resource(PowersId, '/powers/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)


from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

# Set up database path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)


# Set up database URI and enable tracking modifications
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database migration
migrate = Migrate(app, db)
db.init_app(app)

# Define index route
@app.route('/')
def home():
    return '<h1>welcome to my super heroes api</h1>'


# Route to get all heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    heroes_list = [hero.simple_dict() for hero in heroes]
    return jsonify(heroes_list)

# Define route to get all powers
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)

    if not hero:
        return jsonify({"error": "Hero not found"}), 404 

    hero_powers = HeroPower.query.filter_by(heroes_id=id).all()

    return jsonify(hero.to_dict(hero_powers=hero_powers))
# Define route to get all powers
@app.route('/powers', methods=['GET'])
def get_powers():
    # obtain and format powers data
    data = []
    powers = Power.query.all()
    for power in powers:
        power_dict = power.less_dict()
        data.append(power_dict)
    response = make_response(data, 200)
    return response

# route to update a power using PATCH method
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404
    data = request.get_json()
    if "description" in data:
        power.description = data["description"]
        db.session.commit()
        return jsonify(power.to_dict())
    return jsonify({"errors": ["validation errors"]}), 400

# post a hero_powers
@app.route('/hero_powers', methods=['POST'])
def hero_power():
    # Create a new hero power relationship
    data = request.get_json()
    new_hero_power = HeroPower(
        strength=data['strength'],
        powers_id=data['power_id'],
        heroes_id=data['hero_id']
    )
    db.session.add(new_hero_power)
    db.session.commit()
    new_hero_power_dict = new_hero_power.to_dict()
    response = make_response(new_hero_power_dict, 200)
    return response

# Define route to get a specific power or update it using GET and PUT methods
@app.route('/powers/<int:id>', methods=['GET'])
def get_specific_power(id):
    specific_power = Power.query.filter(Power.id == id).first()
    if request.method == 'GET':
        if specific_power:
            data = specific_power.less_dict()
            response = make_response(data, 200)
            return response
        else:
            response_body = {'error': 'Power not found'}
            response = make_response(response_body, 404)
            return response




if __name__ == '__main__':
    app.run(port=5555, debug=True)
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    serialize_rules = ('-hero_power.heroes',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)
    def simple_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "super_name": self.super_name
        }
   

    def to_dict(self, hero_powers=None):
        hero_dict = {

            "hero_powers": [],
            "id": self.id,
            "name": self.name,
            "super_name": self.super_name
        }
        
        if hero_powers:
            for hero_power in hero_powers:
                power = Power.query.get(hero_power.powers_id)
                if power:
                    hero_dict["hero_powers"].append({
                        "id": hero_power.id,
                        "hero_id": self.id,
                        "power_id": power.id,
                        "strength": hero_power.strength,
                        "power": {
                            "id": power.id,
                            "name": power.name,
                            "description": power.description
                        }
                    })
        
        return hero_dict

    #Add the relationship
    hero_power = db.relationship('HeroPower', back_populates='heroes', cascade='all, delete')
    powers = association_proxy('hero_power', 'powers', creator=lambda power_obj: HeroPower(power=power_obj))



class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    # add serialization rules
    serialize_rules = ('-hero_power.power',)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add validation
    @validates('description')
    def validate_description(self, key, description):
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters long")
        return description

    def less_dict(self):
        return {
            'description': self.description,
            'id': self.id,
            'name': self.name
        }
    # add relationship
    hero_power = db.relationship('HeroPower', back_populates='power', cascade='all, delete')

    heroes = association_proxy('hero_powers', 'heroes', creator=lambda hero_obj:HeroPower(hero=hero_obj))



class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    # add serialization rules
    serialize_rules = ('-power.hero_power', '-heroes.hero_power')

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # add relationships
    heroes_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    powers_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    power = db.relationship('Power', back_populates='hero_power')
    heroes = db.relationship('Hero', back_populates='hero_power')

    # add validation
    @validates('strength')
    def validate_strength(self, key, strength):
        if strength in {'Strong', 'Weak', 'Average'}:
            return strength
        else:
            raise ValueError('Strength should be Strong, Weak, or Average')

    def less_dict(self):
        return {
            'strength': self.strength,
            'power_id': self.powers_id,
            'hero_id': self.heroes_id
        }

  
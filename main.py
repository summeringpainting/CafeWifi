from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, URL
from wtforms import StringField, SubmitField, BooleanField
from wtforms import validators
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from werkzeug.datastructures import MultiDict
import random
import os
os.chdir("/home/steve/Websites/cafe-api")

app = Flask(__name__)

# Create random secret key
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    __tablename__ = "cafes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, default=False, nullable=True)
    has_wifi = db.Column(db.Boolean, default=False, nullable=True)
    has_sockets = db.Column(db.Boolean, default=False, nullable=True)
    can_take_calls = db.Column(db.Boolean, default=False, nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class CafeForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    map_url = StringField("map_url", validators=[DataRequired()])
    img_url = StringField("img_url", validators=[DataRequired()])
    location = StringField("location", validators=[DataRequired()])
    seats = StringField("seats", validators=[DataRequired()])
    has_toilet = BooleanField("has_toilet", render_kw={'value': int(1)})
    has_wifi = BooleanField("has_wifi", render_kw={'value': int(1)})
    has_sockets = BooleanField("has_sockets", render_kw={'value': int(1)})
    can_take_calls = BooleanField("can_take_calls", render_kw={'value': int(1)})
    coffee_price = StringField("coffee_price", validators=[DataRequired()])
    submit = SubmitField("Submit")

class UpdatePrice(FlaskForm):
    coffee_price = StringField("coffee_price", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/random')
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return render_template("show-cafe.html", cafe=random_cafe)


@app.route('/all')
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return render_template("all.html", cafes=cafes)


@app.route('/search/<qlocation>', methods=['POST', 'GET'])
def get_particular_cafe(qlocation):
    form = UpdatePrice()
    cafe = db.session.query(Cafe).filter_by(location=qlocation).first()
    if cafe:
        if form.validate_on_submit():

            cafe.coffee_price = request.form.get('coffee_price')

        db.session.commit()

        return render_template("show-cafe.html", cafe=cafe, form=form)
    else:
        return "<p>Not Found, Sorry, we don't have a cafe at that location.</p>"


@app.route('/add', methods=['POST', 'GET'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=request.form.get('name'),
            map_url=request.form.get('map_url'),
            img_url=request.form.get('img_url'),
            location=request.form.get('location'),
            seats=request.form.get('seats'),
            has_toilet=request.form.get('has_toilet'),
            has_wifi=request.form.get('has_wifi'),
            has_sockets=request.form.get('has_sockets'),
            can_take_calls=request.form.get('can_take_calls'),
            coffee_price=request.form.get('coffee_price'),
        )

        # Change to Boolean Value for DB
        if new_cafe.has_toilet == '1':
            new_cafe.has_toilet = True
        if new_cafe.has_wifi == '1':
            new_cafe.has_wifi = True
        if new_cafe.has_sockets == '1':
            new_cafe.has_sockets = True
        if new_cafe.can_take_calls == '1':
            new_cafe.can_take_calls = True

        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html",
                               form=form)


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE", "GET", "POST"])
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_cafes'))



if __name__ == '__main__':
    app.run(debug=True)

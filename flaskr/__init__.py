from os import environ as env
from os import makedirs
from flask import Flask
from flask import render_template, redirect, url_for, jsonify, request
from datetime import date, datetime
import json

from .database import db, db_object, add_commands, insert_form_to_database
from .database import Person, Property, Block, Commune, Region
from .database import Form, Transaction, MultiProperty, Cne

from .helpers.utils import convert_to_type, format_run
from dotenv import load_dotenv
from sqlalchemy import and_, or_, case, func, desc

import uuid

MY_SQL = "mysql+mysqlconnector"
MSGS = {
    "alerts": {
        "missing_data": {
            "cne": "Seleccione una opción de CNE",
            "region": "Seleccione alguna región o comuna",
            "commune": "Seleccione alguna comuna",
            "block": "Indique el número de la manzana",
            "property": "Indique el número de la propiedad",
            "seller": "Indique RUN y porcentaje de los enajenantes",
            "buyer": "Indique RUN y porcentaje de los adquirientes",
            "pages": "Indique el número de fojas",
            "inscription_date": "Seleccione la fecha de inscripción",
            "inscription_number": "Indique el número de inscripción",
        },
    }
}


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    load_dotenv()
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=(
            f'{MY_SQL}://{env["DB_USER"]}:{env["DB_PASSWORD"]}@'
            f'{env["DB_HOST"]}:{env["DB_PORT"]}/{env["DB_NAME"]}'),
        SECRET_KEY=env["APP_SECRET"]
    )

    if env["FLASK_ENV"] == 'development':
        app.jinja_env.auto_reload = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True

    db.init_app(app)
    add_commands(app)

    # ensure the instance folder exists
    try:
        makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        db.reflect()
        db.create_all()

    def get_forms():
        forms = Form.query.all()
        forms_data = []
        for form in forms:
            form_data = {
                'attention_number': form.attention_number,
                'cne': form.cne.description,
                'commune': form.property.block.commune.description,
                'block': form.property.block.number,
                'property': form.property.number,
                'pages': form.pages,
                'inscription_date': form.inscription_date,
                'inscription_number': form.inscription_number,
                'transactions': len(form.transactions)
            }
            forms_data.append(form_data)
        return forms_data

    @app.route('/forms/create', methods=('GET', 'POST'))
    def create_form():
        regions_objects = Region.query.order_by(Region.description).all()
        communes_objects = Commune.query.order_by(Commune.description).all()
        cnes_objects = Cne.query.order_by(Cne.description).all()
        current_date = date.today().strftime('%Y-%m-%d')
        alert_msg = MSGS["alerts"]
        missing_data = alert_msg["missing_data"]
        alerts = []
        forms_data = get_forms()

        if request.method == 'POST':
            cne_id = convert_to_type(request.form['cne'], int)
            region_id = convert_to_type(request.form['region'], int)
            commune_id = convert_to_type(request.form['commune'], int)
            block_number = convert_to_type(request.form['block'], int)
            property_number = convert_to_type(request.form['property'], int)
            seller_ruts = request.form.getlist('seller_rut')
            seller_shares = [convert_to_type(
                share, float) for share in request.form.getlist('seller_share')]
            buyer_ruts = request.form.getlist('buyer_rut')
            buyer_shares = [convert_to_type(
                share, float) for share in request.form.getlist('buyer_share')]
            pages = convert_to_type(request.form['fojas'], int)
            inscription_date = convert_to_type(
                request.form['inscription_date'], datetime)
            inscription_number = request.form['inscription_number']

            is_form_valid = True

            is_form_valid = all([
                cne_id, region_id, commune_id, block_number, property_number,
                pages, inscription_date, inscription_number
            ])
            if not cne_id:
                alerts.append(missing_data["cne"])
            if not region_id:
                alerts.append(missing_data["region"])
            if not commune_id:
                alerts.append(missing_data["commune"])
            if not block_number:
                alerts.append(missing_data["block"])
            if not property_number:
                alerts.append(missing_data["property"])
            if not pages:
                alerts.append(missing_data["pages"])
            if not inscription_date:
                alerts.append(missing_data["inscription_date"])
            if not inscription_number:
                alerts.append(missing_data["inscription_number"])

            buyers = tuple(item for item in zip(
                buyer_ruts, buyer_shares) if item[0])
            sellers = tuple(item for item in zip(
                seller_ruts, seller_shares) if item[0])

            if len(buyers) == 0:
                alerts.append(missing_data["buyer"])
                is_form_valid = False

            people_groups = [(buyers, "Adquiriente"), (sellers, "Enajenante")]
            for people_group in people_groups:
                current_person = 1
                group, name = people_group
                for person in group:
                    run, percentage = person

                    try:
                        Person.validate_run(None, None, run)
                    except ValueError as e:
                        is_form_valid = False
                        alerts.append(f"{name} {current_person}: {e}")

                    try:
                        Transaction.validate_percentage(None, None, percentage)
                    except ValueError as e:
                        is_form_valid = False
                        alerts.append(f"{name} {current_person}: {e}")

                    current_person += 1

            if is_form_valid:
                form_object = insert_form_to_database(
                    cne_id, commune_id, block_number, property_number, pages,
                    inscription_date, inscription_number, buyers, sellers
                )

                return redirect(
                    url_for('forms_index', attention_number=form_object.attention_number))

            return render_template(
                'forms/index.html',
                regions=regions_objects,
                communes=communes_objects,
                cnes=cnes_objects,
                current_date=current_date,
                cne_id=cne_id,
                region_id=region_id,
                commune_id=commune_id,
                block_number=block_number,
                property_number=property_number,
                buyers=buyers,
                sellers=sellers,
                pages=pages,
                inscription_date=inscription_date.strftime('%Y-%m-%d'),
                inscription_number=inscription_number,
                alerts=alerts,
                forms_data=forms_data)

        return render_template(
            'forms/index.html',
            regions=regions_objects,
            communes=communes_objects,
            cnes=cnes_objects,
            current_date=current_date,
            forms_data=forms_data)

    @app.route('/forms', defaults={'attention_number': None}, methods=['GET'])
    @app.route('/forms/<attention_number>', methods=['GET'])
    def forms_index(attention_number):
        forms_data = get_forms()
        if not attention_number:
            return render_template('forms/index.html', forms_data=forms_data)

        uuid_attention_num = uuid.UUID(str(attention_number))
        form_object = Form.query.filter_by(
            attention_number=uuid_attention_num).one()
        buyers = [
            transaction for transaction in form_object.transactions
            if transaction.is_buyer]

        sellers = [
            transaction for transaction in form_object.transactions
            if not transaction.is_buyer]

        return render_template(
            'forms/index.html',
            form_data=form_object,
            buyers=buyers,
            sellers=sellers,
            forms_data=forms_data
        )

    @app.route('/api/v1/regions/all', methods=['GET'])
    def get_regions():
        regions = Region.query.order_by(Region.description).all()
        return jsonify([{'id': region.id, 'description': region.description}
                        for region in regions])

    @app.route('/api/v1/communes/all', methods=['GET'])
    def get_communes():
        communes = Commune.query.order_by(Commune.description).all()
        return jsonify([{'id': commune.id, 'description': commune.description}
                        for commune in communes])

    @app.route('/api/v1/regions/<int:region_id>/communes', methods=['GET'])
    def get_region_communes(region_id):
        communes = Commune.query.filter_by(
            region_id=region_id).order_by(Commune.description).all()
        return jsonify([{'id': commune.id, 'description': commune.description}
                        for commune in communes])

    @app.route('/api/v1/communes/<int:commune_id>/region', methods=['GET'])
    def get_commune_region(commune_id):
        if commune_id:
            region = Commune.query.get(commune_id).region
        return jsonify({'id': region.id, 'description': region.description})

    @app.route('/api/v1/validate/run/<run>', methods=['GET'])
    def check_run(run):
        try:
            Person.validate_run(None, None, run)
            status = 'OK'
            message = "Valido"
        except ValueError as e:
            status = 'ERROR'
            message = str(e)
        return jsonify({'status': status, 'message': message})

    @app.route('/', methods=['GET', 'POST'])
    def property_search():
        multi_properties_query = MultiProperty.query.join(
            MultiProperty.property).join(
                Property.block).join(Block.commune).join(Commune.region)

        regions_objects = Region.query.order_by(Region.description).all()
        communes_objects = Commune.query.order_by(Commune.description).all()
        region_id, commune_id, block_number, property_number, year = [None]*5

        min_year = multi_properties_query.with_entities(
            func.min(MultiProperty.final_vigency_year)).scalar()
        max_year = multi_properties_query.with_entities(
            func.max(MultiProperty.final_vigency_year)).scalar()

        min_year = min_year if min_year else date.today().year
        max_year = max_year if max_year else date.today().year

        if request.method == 'POST':
            if "jsonData" in request.files:
                json_string = request.files['jsonData'].read().decode('utf-8')
                json_data = json.loads(json_string)
                f2890 = json_data['F2890']

                malformatedFormCount = 0

                for form_data in f2890:
                    cne_id = convert_to_type(form_data.get('CNE'), int)
                    assets = form_data.get('bienRaiz', {})
                    commune_id = convert_to_type(assets.get('comuna'), int)
                    block_number = convert_to_type(assets.get('manzana'), int)
                    property_number = convert_to_type(
                        assets.get('predio'), int)
                    pages = convert_to_type(form_data.get('fojas'), int)
                    inscription_date = convert_to_type(
                        form_data.get('fechaInscripcion'), datetime)
                    inscription_number = convert_to_type(
                        form_data.get('nroInscripcion'), int)
                    buyers = form_data.get('adquirentes', [])
                    sellers = form_data.get('enajenantes', [])

                    buyers = tuple(
                        (buyer['RUNRUT'], buyer['porcDerecho']) for buyer in buyers)
                    sellers = tuple(
                        (seller['RUNRUT'], seller['porcDerecho']) for seller in sellers)

                    try:
                        insert_form_to_database(
                            cne_id, commune_id, block_number, property_number, pages,
                            inscription_date, inscription_number, buyers, sellers
                        )
                    except ValueError as e:
                        print(e)
                        db.session.rollback()
                        malformatedFormCount += 1

        region_id = request.form.get('region', type=int)
        property_number = request.form.get('property', type=int)
        commune_id = request.form.get('commune', type=int)
        block_number = request.form.get('block', type=int)
        year = request.form.get('year', type=int)

        if region_id:
            multi_properties_query = multi_properties_query.filter(
                Region.id == region_id)
        if commune_id:
            multi_properties_query = multi_properties_query.filter(
                Commune.id == commune_id)
        if block_number:
            multi_properties_query = multi_properties_query.filter(
                Block.number == block_number)
        if property_number:
            multi_properties_query = multi_properties_query.filter(
                Property.number == property_number)
        if year:
            multi_properties_query = multi_properties_query.filter(
                db.and_(
                    db.or_(
                        MultiProperty.final_vigency_year >= year,
                        MultiProperty.final_vigency_year.is_(None)
                    ),
                    MultiProperty.initial_vigency_year <= year
                )
            )

        # Order multiproperty entires by inscription_date
        multi_properties_query = multi_properties_query.order_by(
            desc(MultiProperty.inscription_date))

        multi_properties_objects = multi_properties_query.all()
        return render_template(
            'property/index.html',
            multi_properties=multi_properties_objects,
            communes=communes_objects,
            regions=regions_objects,
            region_id=region_id,
            commune_id=commune_id,
            block_number=block_number,
            selected_year=year,
            property_number=property_number,
            min_year=min_year,
            max_year=max_year
        )

    return app

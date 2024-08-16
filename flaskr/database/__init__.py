from .models.base import db
from .models.person import Person
from .models.cne import Cne
from .models.property import Property
from .models.block import Block
from .models.commune import Commune
from .models.region import Region
from .models.form import Form
from .models.transaction import Transaction, TransactionCopy
from .models.multiproperty import MultiProperty

from ..helpers.utils import format_run
from sqlalchemy import desc, extract

from datetime import date
import click
import pandas as pd
import os

POPULATE_MSG = 'Database cleaned and populated'


def db_object(model, objct_id=-1, insert_if_not_exist=False, **args):
    if objct_id != -1:
        if objct_id is None:
            db_objct = None
        else:
            db_objct = db.session.get(model, objct_id)
    else:
        db_objct = db.session.query(model).filter_by(**args).first()
        if not db_objct and insert_if_not_exist:
            db_objct = model(**args)
            db.session.add(db_objct)
    return db_objct


@click.command('populate-db')
def populate():
    """Clear the existing data and create new tables."""
    db.reflect()

    db.drop_all()
    db.create_all()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    commune_region_path = os.path.join(
        current_dir, 'resources', 'regionesComunas.xlsx')

    xlsx = pd.ExcelFile(commune_region_path)

    for sheet_name in ["regiones", "comunas"]:
        df = xlsx.parse(sheet_name)
        if sheet_name == "regiones":
            df = df.drop(df.columns[2], axis=1)
            df.columns = Region.__table__.columns.keys()
            tb_name = Region.__table__.name
        else:
            df.columns = Commune.__table__.columns.keys()
            tb_name = Commune.__table__.name
        df.to_sql(name=tb_name, con=db.engine, if_exists="append", index=False)
    xlsx.close()

    buy_sell = Cne()
    buy_sell.id = 8
    buy_sell.description = "Compraventa"
    db.session.add(buy_sell)

    regulate_property = Cne()
    regulate_property.id = 99
    regulate_property.description = "Regularización de Patrimonio"
    db.session.add(regulate_property)

    db.session.commit()
    db.session.close()

    click.echo(POPULATE_MSG)


def clone_model(obj):

    clone = MultiProperty()
    clone.property = obj.property
    clone.person = obj.person
    clone.percentage = obj.percentage
    clone.pages = obj.pages
    clone.inscription_date = obj.inscription_date
    clone.inscription_number = obj.inscription_number
    clone.initial_vigency_year = obj.initial_vigency_year
    clone.final_vigency_year = obj.final_vigency_year
    clone.form = obj.form

    return clone


def add_commands(app):
    app.cli.add_command(populate)


def insert_form_to_database(
    cne_id, commune_id, block_number, property_number, pages, inscription_date,
    inscription_number, buyers, sellers
):
    cne_object = db_object(Cne, cne_id)
    commune_object = db_object(Commune, commune_id)
    block_object = db_object(
        Block,
        insert_if_not_exist=True,
        number=block_number,
        commune=commune_object)
    property_object = db_object(
        Property,
        insert_if_not_exist=True,
        number=property_number,
        block=block_object)

    form_object = db_object(
        Form,
        insert_if_not_exist=True,
        cne=cne_object,
        property=property_object,
        pages=pages,
        inscription_date=inscription_date,
        inscription_number=inscription_number
    )

    for group_is_buyer in [(buyers, True), (sellers, False)]:
        group, is_buyer = group_is_buyer
        for person in group:
            run, percentage = person
            run = format_run(run)

            person_object = db_object(
                Person, insert_if_not_exist=True, run=run)
            transaction_object = db_object(
                Transaction,
                insert_if_not_exist=True,
                form=form_object,
                person=person_object,
                percentage=percentage,
                is_buyer=is_buyer
            )

    db.session.commit()
    algorithm.run(form_object)

    return form_object


def save_multi_property_from_transaction(transaction: Transaction):
    mp = db_object(
        MultiProperty,
        insert_if_not_exist=True,
        property=transaction.form.property,
        person=transaction.person,
        percentage=transaction.percentage,
        pages=transaction.form.pages,
        inscription_date=transaction.form.inscription_date,
        inscription_number=transaction.form.inscription_number,
        initial_vigency_year=transaction.form.inscription_date.year,
        final_vigency_year=None,
        form=transaction.form
    )
    db.session.add(mp)


def process_transactions(transactions: list[Transaction]):
    for transaction in transactions:
        save_multi_property_from_transaction(transaction)
    db.session.commit()

class Algorithm:

    __last_processed = None
    last_absolute_form = None

    def __refresh_absolute_form(self, form):
        self.last_absolute_form = (
            db.session.query(Form).join(Form.cne)
            .filter(Form.inscription_date < form.inscription_date)
            .filter(Form.property == form.property)
            .filter(Cne.id == 99)
            .order_by(Form.inscription_date.desc())
            .first()
        )

    def __get_related_forms(self, form):
        property_forms_query = (
            db.session.query(Form)
            .filter(Form.property == form.property)
        )

        prev_form = (
            property_forms_query
            .filter(Form.inscription_date < form.inscription_date)
            .order_by(Form.inscription_date.desc())
            .first()
        )

        next_form = (
            property_forms_query
            .filter(Form.inscription_date > form.inscription_date)
            .order_by(Form.inscription_date.asc())
            .first()
        )

        same_date_form = (
            property_forms_query
            .filter(Form.inscription_date == form.inscription_date)
            .first()
        )

        return (prev_form, same_date_form, next_form)

    def __get_available_mps_to_year(self, prpty, year):
        return (
            MultiProperty.query
            .filter(
                MultiProperty.property == prpty,
                MultiProperty.final_vigency_year.is_(None),
                MultiProperty.initial_vigency_year < year
            )
            .all()
        )

    def regularization(self, form, form_buyers):
        print('Regularización de Patrimonio')

        prev_form, _, next_form = self.__get_related_forms(form)

        first_case = prev_form is None
        second_case = prev_form is not None  # future form arrives
        third_case = next_form is not None  # old form arrives

        fourth_case = (
            lambda first_form, second_form:
            first_form.inscription_date.year == second_form.inscription_date.year
        )

        if first_case:
            print("No hay registros")
            process_transactions(form_buyers)
            db.session.commit()
            
        if second_case:
            print('Hay un form anterior al que llega')
            if fourth_case(form, prev_form):
                print('mismo año: se reemplaza por el que llega')
                for prev_mp in prev_form.multi_properties:
                    db.session.delete(prev_mp)
            else:
                print('distinto año: se ponen fechas vig final y se guarda el que llega')
                for prev_mp in prev_form.multi_properties:
                    prev_mp.final_vigency_year = form.inscription_date.year - 1
            process_transactions(form_buyers)
            db.session.commit()

        if third_case:
            print('Hay un form posterior al que llega, se reprocesa')
            self.run(next_form)

    def trading(self, form, form_buyers, seller_trtions):
        diff_year_prev_mps = list(
            filter(lambda mp: mp.initial_vigency_year < form.inscription_date.year,
                   self.__get_available_mps_to_year(form.property, form.inscription_date.year))
        )

        for registry in diff_year_prev_mps:
            mp = db_object(MultiProperty, registry.id)
            mp.final_vigency_year = form.inscription_date.year - 1
            new_mp = db_object(
                MultiProperty,
                property=mp.property,
                person=mp.person,
                percentage=mp.percentage,
                pages=mp.form.pages,
                inscription_date=mp.inscription_date,
                inscription_number=mp.inscription_number,
                initial_vigency_year=form.inscription_date.year,
                final_vigency_year=None,
                form=form,
                insert_if_not_exist=True
            )

        selling_owners = []
        has_ghosts = False
        for seller_trtion in seller_trtions:
            seller_mp = (
                MultiProperty
                .query
                .filter(
                    MultiProperty.person == seller_trtion.person,
                    MultiProperty.inscription_date < form.inscription_date,
                    MultiProperty.final_vigency_year.is_(None)
                )
                .order_by(desc(MultiProperty.inscription_date))
                .first()
            )
            if seller_mp is None: # GHOST SELLER
                seller_mp = db_object(
                    MultiProperty,
                    property=seller_trtion.form.property,
                    person=seller_trtion.person,
                    percentage=0,
                    initial_vigency_year=form.inscription_date.year,
                    final_vigency_year=None,
                    form=form,
                    insert_if_not_exist=True
                )
                has_ghosts = True
            selling_owners.append(seller_mp)
        db.session.commit()

        print(selling_owners)
        print('Compraventa')

        def get_total_perc(transactions): return sum(
            map(lambda transaction: transaction.percentage, transactions))

        total_sellers_perc = get_total_perc(seller_trtions)
        total_buyers_perc = get_total_perc(form_buyers)

        first_case = total_buyers_perc == 100
        second_case = total_buyers_perc == 0
        third_case = len(seller_trtions) == 1 and len(form_buyers) == 1

        if first_case or second_case:
            print('primer o segundo caso')

            selling_tt_perc = 0
            for selling_owner in selling_owners:
                print("Vendiendo propiedad de {} con {}% del form {}".format(
                    selling_owner.person,
                    selling_owner.percentage,
                    selling_owner.form))
                selling_tt_perc += selling_owner.percentage
                db.session.delete(selling_owner)
            if has_ghosts and selling_tt_perc == 0:
                selling_tt_perc = 100
            db.session.commit()

            equal_perc = selling_tt_perc/len(form_buyers)

            def buyer_perc(perc): return perc * (selling_tt_perc/100)

            for buyer in form_buyers:
                buyer.percentage = buyer_perc(
                    buyer.percentage) if first_case else equal_perc
            
        elif third_case:
            print('tercer caso')

            buyer_mp = form_buyers[0]
            owner_mp = selling_owners[0]

            is_ghost = not bool(owner_mp.inscription_date)

            percentage = (
                (owner_mp.percentage if not is_ghost else 100) * 
                (buyer_mp.percentage/100)
            )
            if not is_ghost:
                owner_mp.percentage -= percentage
            buyer_mp.percentage = percentage
            
        else:
            print('else')
            if has_ghosts: print('has ghost sellers')
            for owner_mp in selling_owners:
                for seller in seller_trtions:
                    if owner_mp.person == seller.person:
                        if has_ghosts:
                            if seller.percentage < owner_mp.percentage:
                                owner_mp.percentage -= seller.percentage
                            else:
                                owner_mp.percentage = 0
                            break
                        else:
                            owner_mp.percentage -= seller.percentage
                            if owner_mp.percentage <= 0:
                                db.session.delete(owner_mp)
                                db.session.commit()
                                break

        process_transactions(form_buyers)
        db.session.commit()

        if has_ghosts:
            print('ghosting')
            print(form.inscription_date.year+1)
            open_mps = self.__get_available_mps_to_year(form.property, form.inscription_date.year+1)
            print(open_mps)
            print(list(map(lambda mp: (mp.percentage, mp.person.run), open_mps)))
            tt_percentage = sum(map(lambda mp: mp.percentage, open_mps))
            print(tt_percentage)
            diff = 100 - tt_percentage

            cero_percentage_mps = list(filter(
                lambda mp: mp.percentage == 0,
                open_mps
            ))

            if tt_percentage < 100:
                print("less than 100")
                for mp in cero_percentage_mps:
                    mp.percentage = diff/len(cero_percentage_mps)
                    print(mp.percentage)
                cero_percentage_mps = []

            elif tt_percentage > 100:
                print("more than 100")
                
                for mp in open_mps:
                    mp.percentage = (mp.percentage/tt_percentage)*100
                    print(mp.percentage)
            
            for mp in cero_percentage_mps:
                db.session.delete(mp)

        db.session.commit()
        
        _, _, next_form = self.__get_related_forms(form)
        if next_form:
            self.run(next_form)

    def reprocess_last_absolute(self, form):
        print("Procesando desde ultimo form absoluto")
        self.run(self.last_absolute_form)

    def run(self, form):
        self.__refresh_absolute_form(form)
        print("\n\n")
        for mp in form.multi_properties:
            db.session.delete(mp)
        db.session.commit()

        print(f"Procesando formulario {form.id}")
        print(f"Fecha de inscripción {form.inscription_date}")

        form_buyers = []
        seller_trtions = []
        for transaction in form.transactions:
            copy = TransactionCopy(
                form,
                transaction.person,
                transaction.percentage,
            )
            if transaction.is_buyer:
                form_buyers.append(copy)
            else:
                seller_trtions.append(copy)

        regularization = form.cne.id == 99
        trading = form.cne.id == 8

        if regularization:
            self.__last_processed = form
            self.regularization(form, form_buyers)
        elif (self.last_absolute_form and self.__last_processed and
              self.__last_processed.inscription_date > form.inscription_date):
            self.__last_processed = form
            self.reprocess_last_absolute(form)
        elif trading:
            self.__last_processed = form
            self.trading(form, form_buyers, seller_trtions)

algorithm = Algorithm()

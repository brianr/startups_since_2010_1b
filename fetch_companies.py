"""
Scrape the Fetch all the company idents
"""

import re
import sys

import requests
import sqlalchemy as sa


def fetch_company_list():
    print "Fetching data from Crunchbase API..."
    resp = requests.get('http://api.crunchbase.com/v/1/companies.js')

    print "Deserializing json..."
    data = resp.json

    # data contains about 100k companies
    conn = engine.connect()
    stmt = sa.text("""
        INSERT INTO company
          (ident, name, category_code)
        VALUES
          (:ident, :name, :category_code)
        """, bind=conn)
    for i, company in enumerate(data):
        if i % 100 == 0:
            print "Processed", i, "companies"
        try:
            ident = company.get('permalink')
            name = company.get('name')
            category_code = company.get('category_code')
            stmt.execute(ident=ident, name=name, category_code=category_code)
        except Exception, e:
            print "Could not process company", company, e
    print "Done!"


def fetch_company_details():
    variable_name = 'fetch_company_details'
    start_id = get_variable(variable_name)
    max_id = get_max('company')

    for i in xrange(start_id, max_id + 1):
        if i % 10 == 0:
            print "Processed", i, "companies"
        try:
            _fetch_company_details(i)
        except Exception, e:
            print "Error loading company", i, e
        finally:
            set_variable(variable_name, i)


def _fetch_company_details(company_id):
    ident = engine.scalar(sa.text("SELECT ident FROM company WHERE id=:id"), id=company_id)
    if not ident:
        return
    resp = requests.get('http://api.crunchbase.com/v/1/company/%s.js' % ident)
    if resp.status_code == 403:
        print "hit rate limit, aborting"
        sys.exit(1)
    data = resp.json
    if data:
        _write_company_details(company_id, data)
    else:
        print "no data for company", company_id


def _write_company_details(company_id, data):
    # update company row
    params = {
        'id': company_id,
        'founded_day': data.get('founded_day'),
        'founded_month': data.get('founded_month'),
        'founded_year': data.get('founded_year'),
        'total_money_raised': data.get('total_money_raised')
    }
    engine.execute(sa.text("""
        UPDATE company
        SET founded_day=:founded_day, founded_month=:founded_month, founded_year=:founded_year,
            total_money_raised=:total_money_raised
        WHERE id=:id
        """), **params)

    # funding rounds
    if data.get('funding_rounds'):
        for round in data['funding_rounds']:
            params = {
                'company_id': company_id,
                'day': round.get('funded_day'),
                'month': round.get('funded_month'),
                'year': round.get('funded_year'),
                'round_code': round.get('round_code'),
                'raised_amount': round.get('raised_amount'),
            }
            engine.execute(sa.text("""
                INSERT INTO funding_round
                  (company_id, day, month, year, round_code, raised_amount)
                VALUES
                  (:company_id, :day, :month, :year, :round_code, :raised_amount)
                """), **params)


def parse_total_money_raised():
    """
    Parse the total_money_raised string into an integer, and save that in the 
    total_money_raised_int column.
    """
    variable_name = 'parse_total_money_raised'
    start_id = get_variable(variable_name)
    max_id = get_max('company')

    for i in xrange(start_id, max_id + 1):
        if i % 100 == 0:
            print "Processed", i, "companies"
        try:
            _parse_total_money_raised(i)
        except Exception, e:
            print "Error parsing money for company", i, e
        finally:
            set_variable(variable_name, i)


def _parse_total_money_raised(company_id):
    value = engine.scalar(sa.text("SELECT total_money_raised FROM company WHERE id = :id"), 
        id=company_id)
    if not value:
        return
    value_int = _parse_money(value)
    engine.execute(sa.text("""
        UPDATE company
        SET total_money_raised_int = :value
        WHERE id = :id
        """), id=company_id, value=value_int)


def _parse_money(value):
    # ignore optional leading ?
    if value.startswith('?'):
        value = value[1:]

    # remove leading currency symbol
    currency = '$'
    currency_symbols = ['kr', 'C$', '$']
    for sym in currency_symbols:
        if value.startswith(sym):
            value = value[len(sym):]
            currency = sym
            break
    
    # ignore other optional ?
    if value.startswith('?'):
        value = value[1:]

    # take scale from the end
    scale = 1
    if value.endswith('k'):
        scale = 1000
        value = value[:-1]
    elif value.endswith('M'):
        scale = 1000000
        value = value[:-1]
    elif value.endswith('B'):
        scale = 1000000000
        value = value[:-1]

    # raises a ValueError if not a parseable float
    number = float(value)

    value_int = number * scale
    # scale by currency
    if currency == 'kr':
        # swedish krona
        value_int *= 0.151
    elif currency == 'C$':
        # canadian dollar
        value_int *= 1.0008

    return value_int


## utils

def get_variable(name, default=0):
    value = engine.scalar(sa.text("SELECT value_unsigned FROM variable WHERE name=:name"), name=name)
    if value is None:
        return default
    return value


def set_variable(name, value):
    engine.execute(sa.text("REPLACE INTO variable (name, value_unsigned) VALUES (:name, :value)"),
        name=name, value=value)


def get_max(table_name):
    return engine.scalar(sa.text("SELECT max(id) FROM %s" % table_name))


if __name__ == '__main__':
    engine = sa.create_engine(sys.argv[1])
    commands = {
        'fetch_company_list': fetch_company_list,
        'fetch_company_details': fetch_company_details,
        'parse_total_money_raised': parse_total_money_raised,
    }
    command = sys.argv[2]
    if command not in commands:
        print "Unrecognized command. Try one of these:", commands.keys()
        sys.exit(1)
    commands[command]()

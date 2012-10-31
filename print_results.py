"""
Outputs results for the quora answer
"""

import sys
import sqlalchemy as sa


def main():
    result = engine.execute(sa.text("""
        SELECT ident, name, category_code, founded_year, founded_month, total_money_raised
        FROM company
        WHERE founded_year >= 2010
          AND category_code IS NOT NULL
          AND category_code != 'biotech'
        ORDER BY total_money_raised_int DESC
        LIMIT 25
        """))
    for row in result:
        data = dict(row)
        data['url'] = 'http://www.crunchbase.com/company/%s' % row['ident']
        if row['founded_month']:
            data['founded'] = '%s/%s' % (row['founded_month'], row['founded_year'])
        else:
            data['founded'] = row['founded_year']
        print "%(name)s - %(category_code)s - %(founded)s - %(total_money_raised)s %(url)s" % data


if __name__ == '__main__':
    engine = sa.create_engine(sys.argv[1])
    main()

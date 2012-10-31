# What is this?

Code to answer this question on Quora: http://www.quora.com/Startups/Which-startups-founded-since-January-2010-are-most-likely-to-be-worth-1+-billion

## Requires

- python
- mysql
- pip

## Setup

    $ pip install -r requirements.txt
    $ # create a mysql database...
    $ mysql < db.sql

## Usage

First, populate the list of companies:

    $ python fetch_companies.py mysql://user:pass@host/dbname fetch_company_list
    
Next, fetch data for each company. You'll probably hit the crunchbase API rate limit here, so best to run it in a loop:
    
    $ ./looper mysql://user:pass@host/dbname

Then, parse the total_money_raised column (it comes in as a string):

    $ python fetch_companies.py mysql://user:pass@host/dbname parse_total_money_raised

Finally, output the result:
    
    $ python print_results.py mysql://user:pass@host/dbname


## Find a bug?

Comment on a commit, open an issue, or send a pull request. Thanks!

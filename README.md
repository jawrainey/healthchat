# Health chat

This repository contains the codebase for my final year project at [Cardiff University](http://www.cs.cf.ac.uk/).

# Overview

Health behaviours that negatively affect an individual, such as lack of physical activity or an unhealthy diet are responsible for the most deaths in the [United Kingdom per year](http://www.ons.gov.uk/ons/rel/vsob1/mortality-statistics--deaths-registered-in-england-and-wales--series-dr-/2013/index.html) when combined.

This novel application provides a chat service where users can openly discuss their diet and exercise habits. The intent of which is to make users think and reflect upon their habits and decisions that negatively affect their lifestyle.

## Main objects

My main objects of this project were to develop solutions to:

1. Construction of a domain-specific ontology from freely available data, such as [research data](http://bioportal.bioontology.org/ontologies/RH-MESH/) or data scrapped from [domain-specific websites](https://www.reddit.com/r/food/).
2. Development and implement an ontology to facilitate appropriate response selection and context detection from user messages.
3. Development of a web-based interface to demonstrate and test the utility and usability of the conversational agent and user experience.

## Deployment

### Environment variables

#### Database access

To enable `postgresql` access, the [database](https://github.com/jawrainey/healthchat/blob/master/settings.py#L21) environment variable `DATABASE_URL` needs to be set to the string of your `postgresql` of your database.

#### Production configuration

The [configuration variable](https://github.com/jawrainey/healthchat/blob/master/manage.py#L6) `ENV` needs to be set to `prod` to disable debugging and enable `postgresql` database access.

## Building locally

### Installing dependencies

I recommend creating a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) when developing:

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Viewing the site

To build the database structure:

    python manage.py init_db

The transitive closure then needs to be populated:

    python manage.py populate_ontology

To add the structured questions to the database:

    python manage.py questions_to_sql

Finally, to run the server locally and see it all in action:

    python manage.py runserver

## License

- Licensed under [MIT](https://github.com/jawrainey/healthchat/blob/master/LICENSE.txt).

## Contribution

All contributions, ideas, and suggestions
are welcomed via [issues](https://github.com/jawrainey/healthchat/issues) and [pull requests](https://github.com/jawrainey/healthchat/pulls).

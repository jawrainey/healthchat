from app import db


class Database:
    '''
    Used to CRUD database. Couples all queries to same object.

    Note: this is preferred over a models.py (declarative SQLAlchemy) as the
    'Closure' table does not contain a primary key, which causes issues.

    Table choices based on:
        http://blog.adimian.com/2014/10/cte-and-closure-tables/
    '''
    def concept_id(self, concept):
        '''
        Obtains the ID for a given ontological concept, i.e. diet.
        TODO: this query is limited as it's specific, consider 'LIKE'.

        Args:
            concept (str): the concept to obtain the ID for.

        Returns:
            str: ID of the concept, otherwise raise exception.
        '''
        query = "SELECT id FROM nodes WHERE name = '" + str(concept) + "'"
        row = db.engine.execute(query).fetchone()
        return row[0] if row else None

    def parent_name(self, parent_id):
        '''
        Obtains the name of a concept based on the ID.
        TODO: error checking; id may not always be valid (unlike above query).

        Args:
            parent_id (str): the ID of the parent to search for.

        Returns:
            str: name of parent concept based on ID.
        '''
        query = 'SELECT name FROM nodes WHERE id = ' + str(parent_id)
        return db.engine.execute(query).fetchone()[0]

    def get_subtree_of_concept(self, concept_id):
        '''
        Includes the concept provided, i.e. diet and all subs of tree.

        Args:
            concept_id (int): the ID of the known concept.

        Returns:
            list: sub-tree elements for the given concept ID.
        '''
        query = ('SELECT n.* FROM nodes n '
                 'JOIN closure a ON (n.id = a.child) '
                 'WHERE a.parent = ' + str(concept_id))
        return db.engine.execute(query).fetchall()

    def create_tables(self):
        '''
        Creates the two tables used to store the ontology concepts and terms.
            - 'nodes' stores the .obo content.
            - 'closure' stores the hierarchy as a transitive representation.
        '''
        db.engine.execute(
            'CREATE TABLE IF NOT EXISTS nodes ('
            'id INTEGER NOT NULL PRIMARY KEY,'
            'parent INTEGER REFERENCES nodes(id),'
            'name VARCHAR(100))')

        db.engine.execute(
            'CREATE TABLE IF NOT EXISTS closure ('
            'parent INTEGER REFERENCES nodes(id), '
            'child INTEGER REFERENCES nodes(id), '
            'depth INTEGER)')
        db.session.commit()

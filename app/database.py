from app import db, models


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
        Obtains the ID for a given ontological concept using stemming.

        Args:
            concept (str): the concept to obtain the ID for.

        Returns:
            str: ID of the concept, otherwise None.
        '''
        from nltk import SnowballStemmer
        concept = SnowballStemmer("english").stem(str(concept))
        row = models.Nodes.query.filter(
            models.Nodes.name.like("%" + concept + "%")).first()
        return row.id if row else None

    def parent_name(self, parent_id):
        '''
        Obtains the name of a concept based on the ID.

        Args:
            parent_id (str): the ID of the parent to search for.

        Returns:
            str: name of parent concept based on ID, otherwise None
        '''
        row = models.Nodes.query.filter_by(id=str(parent_id)).first()
        return row.name if row else None

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

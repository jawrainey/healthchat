# Note: based on - http://blog.adimian.com/2014/10/cte-and-closure-tables/
import sqlite3

conn = sqlite3.connect('test.db')
cursor = conn.cursor()


def create_tables():
    '''
    Creates the two tables used to store the ontology concepts and terms.
        - 'nodes' stores the .obo content.
        - 'closure' stores the hierarchy in a transitive closure representation.
    '''
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS nodes ('
        'id INTEGER NOT NULL PRIMARY KEY,'
        'parent INTEGER REFERENCES nodes(id),'
        'name VARCHAR(100))')

    cursor.execute(
        'CREATE TABLE IF NOT EXISTS closure ('
        'parent INTEGER REFERENCES nodes(id), '
        'child INTEGER REFERENCES nodes(id), '
        'depth INTEGER)')
    conn.commit()


def add_unknown_concepts_to_db(obo_content):
    '''
    Inserts concepts/terms into the database.

    Moreover, the transitive closure table is also updated upon insertion
    of an element to ensure it's retrievable later...

    Args:
        obo_content (list): a list of Stanzas, i.e. dictionaries containing
        the relevant obo structure, such as id, name, and relationship.
    '''
    known_ids = [r[0] for r in
                 cursor.execute('SELECT id FROM nodes').fetchall()]

    for i in obo_content:
        _id = int(str(i.tags['id'][0]).split(':')[1])
        # The root element does not have a parent. Assign it a zero.
        _pid = (int(str(i.tags['is_a'][0]).split(':')[1])
                if 'is_a' in str(i) else 0)
        _name = str(i.tags['name'][0])
        # Only add NEW terms to the database.
        if _id not in known_ids:
            # Add ontological term to node table.
            cursor.execute('INSERT INTO nodes VALUES (?, ?, ?)',
                           (_id, _pid, _name))
            last_id = cursor.lastrowid
            # Collect ancestor of parent, and insert into closure table.
            cursor.execute('SELECT parent, ? as child, depth+1 FROM closure '
                           'WHERE child = ?', (_id, _pid))
            stm = 'INSERT INTO closure (parent, child, depth) VALUES (?, ?, ?)'
            cursor.executemany(stm, cursor.fetchall())
            cursor.execute(stm, (last_id, last_id, 0))
    conn.commit()


if __name__ == "__main__":
    import obo
    create_tables()
    obo_content = [i for i in obo.Parser('../data/structure.obo')]
    add_unknown_concepts_to_db(obo_content)

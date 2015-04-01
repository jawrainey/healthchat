# Note: based on - http://blog.adimian.com/2014/10/cte-and-closure-tables/
import sqlite3

conn = sqlite3.connect('/Users/jawrainey/Dropbox/uni/04/CM3203/healthchat/test.db')
cursor = conn.cursor()


def populate_from_obo():
    '''
    Inserts concepts/terms into the database.

    Moreover, the transitive closure table is also updated upon insertion
    of an element to ensure it's retrievable later.
    '''
    import obo
    # Note: structure.obo MUST contain the initial concepts.
    # TODO: move structure.obo to environmental variable.
    path = '/Users/jawrainey/Dropbox/uni/04/CM3203/healthchat/data/structure.obo'
    obo_content = [i for i in obo.Parser(path)]

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

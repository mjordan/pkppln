"""
Functions shared by PKP PLN microservices.
"""

def get_deposits(state):
    # Get the deposits that have the indicated state value
    # and return them to the microservice for processing.
    con = mdb.connect(db_host, db_user, db_password, db_name)
    try:
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM deposits WHERE state = %s AND outcome = 'success'", state)
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    
    if cur.rowcount:
        deposits = []
        for row in cur:
            deposits.append(str(row[0]))
        return deposits

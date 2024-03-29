
import MySQLdb
import sys
import numpy as np

actor_name = {}
no_actors_set = []
one_row_in_array = []
actorA_list = []
actorB_list = []
list_of_lists = []
names = []
personal_dict = {}
actor_to_index = {}
index_to_actor = {}

try:
    # connect to the database
    conn = MySQLdb.connect(user='root',
                                   passwd='haha123',
                                   host='localhost',
                                   db="mwdb")

    # get the db cursor object to interact with db
    k = 0
    cur = conn.cursor()
    id=0
    # map actorid to actor name
    cur.execute(("SELECT actorid,name FROM mwdb.imdb_actor_info;"))
    for row in cur.fetchall():
        id = row[0]
        name = row[1]
        actor_name[id] = name;
    # get the number of actors
    cur.execute(("SELECT distinct (actorid) FROM mwdb.movie_actor;"))
    for row in cur.fetchall():
        row_ele = row[0]
        no_actors_set.append(row_ele)
        actor_to_index[row_ele] = k
        index_to_actor[k] = row_ele
        k = k + 1
    no_actors = len(no_actors_set)

    my_array = np.array([], float)  # initialize numpy array
    np.set_printoptions(threshold=np.nan)

    for actorA in no_actors_set:
        for actorB in no_actors_set:
            if (actorB == actorA):
                entry = 0.0
            else:
                cur.execute((
                            "SELECT movieid FROM mwdb.movie_actor where actorid={} and movieid in (select movieid from movie_actor where actorid={})".format(
                                actorA, actorB)))
                res = cur.fetchall()
                entry = len(res)
            one_row_in_array.append(entry)
        list_of_lists.append(one_row_in_array)
        one_row_in_array = []

    # create coactor-coactor matrix
    my_array = np.array(list_of_lists)

    # column-normalize the coactor-coactor matrix
    for i in range(my_array.shape[1]):
        sum_column = np.sum((my_array[:, i]))
        my_array[:, i] /= sum_column

    teleport = np.zeros((no_actors, 1))  # teleportation matrix
    prscore = np.zeros((no_actors, 1))  # matrix for pagerank scores

    # construct a teleport and initial pagerank matrix from user input
    for i in sys.argv:
        names.append(i)
    names.remove(sys.argv[0])
    print("List of seed actors-")
    for i in names:
        key = int(i)  # convert string cmd-line arg to int
        personal_dict[actor_to_index[key]] = 1 / len(names)
        teleport[actor_to_index[key]][0] = 1 / len(names)
        prscore[actor_to_index[key]] = 1
        print(actor_name[key])

        # calculate pagerank with personalization

    mean_error = 1
    alpha = 0.85
    no_iter = 0

    while (no_iter < 100):
        # calculate pagerank with rwr approach
        term1 = alpha * np.matmul(my_array, prscore)
        term2 = (1 - alpha) * teleport
        prscore = term1 + term2
        # set current pagerank scores as prevscore values
        no_iter = no_iter + 1

    # sort the pagerank scores and store the rank of the sorted values in sortlist
    sortlist = np.argsort(prscore, axis=0)

    # store (index,rank) values in a dictionary
    sortdict = {}
    k = 0
    for val in sortlist:
        sortdict[k] = val[0]
        k = k + 1

    # sort the dictionary and print the actors with the top 10 ppr values
    k = 0
    print("\nTop ten related actors to the seed set are:\n")
    for i in reversed(range(no_actors)):
        if (k < 10):
            actorpos = [key for key, value in sortdict.items() if value == i]
            temp = index_to_actor[actorpos[0]]
            print(actor_name[temp])
            k = k + 1

except MySQLdb.Error as e:
    print(e)

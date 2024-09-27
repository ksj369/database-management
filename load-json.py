import json
import subprocess
import pymongo
from pymongo import MongoClient, TEXT
import os


if os.name == "nt":
    clear = "cls"
else:
    clear = "clear"

# client=MongoClient()
valid = 0
while not valid:
    server_name = input("enter host server name: ")
    print("connecting to host...")
    try:
        client = MongoClient(server_name, serverSelectionTimeoutMS=10000)
        client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError:

        print("invalid host server")
        input("press enter to retry again")
        os.system(clear)
    else:
        valid = 1


dbnames = client.list_database_names()
if "291db" in dbnames:
    db = client["291db"]
    for name in db.list_collection_names():
        col = db[name]
        col.drop()
    dblp = db["dblp"]

else:
    db = client["291db"]
    dblp = db["dblp"]
    dblp.drop()


# drop any existing indexes
dblp.drop_indexes()


# import files
filename = ""
valid = 0
while not valid:
    filename = input("enter json filename:")
    if os.path.exists(filename):
        valid = 1
    else:
        print("invalid filename")
        print("press enter to try again")
        os.system(clear)

os.system(clear)

# get core count to see how many processes to run, allows multithreading
coreCount = os.cpu_count()

# just in case you cant get core count on lab machines, this prevents it from running 0 workers
if coreCount == None:
    coreCount = 1
print("running mongoImport on {} cores".format(coreCount))
command = "mongoimport --db 291db --collection dblp --batchSize 50000 --file {} --numInsertionWorkers={} --uri {}".format(
    filename, coreCount, server_name)


os.system(command)


print("doing some procomputations (1/2)")
# convert year to string
dblp.update_many({}, [
                 {"$set": {"year": {"$toString": "$year"}}}])
print("doing some precomputation (2/2)")

# make this index first as it will help with the time complexity of this precomp
dblp.create_index([("references", 1)], name="references_index")


# find how many times each doc is referenced
dblp.aggregate([
    {
        '$lookup': {
            'from': 'dblp',
            'localField': 'id',
            'foreignField': 'references',
            'as': 'refBy'
        }
    }, {
        '$set': {
            'ref_by_count': {
                '$size': '$refBy'
            }
        }
    }, {
        '$unset': 'refBy'
    }, {
        '$merge': {
            'into': 'dblp'
        }
    }
])

print("done precomputing")

print("Making indexes (this may take a while, another message will print when done)")

# create the rest of the indexes
dblp.create_index([("id", 1)], name="id_index")
dblp.create_index([("abstract", TEXT), ("authors", TEXT), ("title", TEXT),
                  ("venue", TEXT), ("year", TEXT)], name="abatvy_index")


print("indexes made")

input("press enter to continue")
os.system(clear)

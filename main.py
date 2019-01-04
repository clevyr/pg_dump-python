import json
from os import environ, mkdir, path
from threading import Timer
import tarfile
from time import strftime, gmtime

import boto3 as boto
from bson import BSON
import hvac
from pymongo import MongoClient

s3 = boto.resource("s3")

RENEW_TIMER = None

def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

def renew_token(client):
    global RENEW_TIMER

    client.renew_token(increment=60 * 60 * 72)
    RENEW_TIMER = Timer(60 * 60 * 70, renew_token, (client,)) # Two hours minutes before TTL
    RENEW_TIMER.start()

def exit():
    if RENEW_TIMER is not None:
        RENEW_TIMER.cancel()
        RENEW_TIMER.join(timeout=2)
    quit()

def main():
    global RENEW_TIMER

    vault_secret = environ["VAULT_SECRET"]
    bucket_name = environ["BUCKET_NAME"]
    mongo_host = environ["MONGO_HOST"]


    client = hvac.Client(
        url=environ['VAULT_HOST'],
        token=environ['VAULT_TOKEN']
    )

    RENEW_TIMER = Timer(0, renew_token, (client,)) # Immediately renew, we don't know the TTL
    RENEW_TIMER.start()
    RENEW_TIMER.join()
    
    secret = client.read(vault_secret)['data']
    username = secret['username']
    password = secret['password']

    db_uri = "mongodb://{}:{}@{}/?authSource=admin".format(username, password, mongo_host)
    client = MongoClient(db_uri)

    if path.exists("dump"):
        print("Stopping, dump folder already exists")
        exit()
    else:
        mkdir("dump")

    # For each database
    for db_name in client.list_database_names():
        mkdir("dump/{}".format(db_name))
        database = client.get_database(db_name)

        # For each collection
        for collection_name in database.list_collection_names():
            # Get collection
            collection = database.get_collection(collection_name)
            # Create metadata.json
            with open("dump/{}/{}.metadata.json".format(db_name, collection_name), "w") as f:
                metadata = {
                    "options": {},
                    "indexes": []
                }
                for index in collection.list_indexes():
                    metadata["indexes"].append(index)
                f.write(json.dumps(metadata, separators=(',',':')))

            # Create bson dump
            with open("dump/{}/{}.bson".format(db_name, collection_name), "wb+") as f:
                print("Dumping {}.{}".format(db_name, collection_name))
                count = collection.count_documents({})
                for i, doc in enumerate(collection.find()):
                    printProgressBar(i+1, count)
                    f.write(BSON.encode(doc))

    filename = "backup-{}.tgz".format(strftime("%Y-%m-%d_%H%M%S", gmtime()))

    print("Creating {}".format(filename))
    with tarfile.open("{}".format(filename), "w:gz") as tar:
        tar.add("dump", arcname=path.basename("dump"))

    s3.Bucket(bucket_name).upload_file(filename, filename)
    print("Done")
    exit()

main()
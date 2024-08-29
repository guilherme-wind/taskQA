#Imports
import hashlib
import logging
import os
import argparse
import shutil
import time

def md5_Hash(file):
    if not file:
        return None
    aux_md5 = hashlib.md5()
    if os.path.isfile(file):
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                aux_md5.update(chunk)
    else:            
        input_bytes = file.encode('utf-8')
        aux_md5.update(input_bytes)
    return aux_md5.hexdigest()


def syncFolders(source, replica, log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler())
    
    if not os.path.exists(replica):
        os.makedirs(replica)

    for root, _, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        replica_root = os.path.join(replica, relative_path)

        if not os.path.exists(replica_root):
            os.makedirs(replica_root)

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)

            if not os.path.exists(replica_file) or md5_Hash(source_file) != md5_Hash(replica_file):
                shutil.copy2(source_file, replica_file)
                logging.info(f"Copied/Updated: {source_file} -> {replica_file}")

    for root, _, files in os.walk(replica):
        relative_path = os.path.relpath(root, replica)
        source_root = os.path.join(source, relative_path)

        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_root, file)

            if not os.path.exists(source_file):
                os.remove(replica_file)
                logging.info(f"Removed: {replica_file}")

def main():
    parser = argparse.ArgumentParser(description="Folder Synchronization Script")
    parser.add_argument("source", help="Path to the source folder")
    parser.add_argument("replica", help="Path to the replica folder")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")
    args = parser.parse_args()   
    while True:
        syncFolders(args.source, args.replica, args.log_file)
        time.sleep(args.interval)
        
        
if __name__ == "__main__":
    main()

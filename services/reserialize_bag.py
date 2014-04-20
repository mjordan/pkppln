"""
Script to 1) add tags to bag-info.txt and 2) reserialize Bags containing OJS
journals participating in the PKP PLN.
"""

import os
import ConfigParser
import bagit
import tarfile
import shutil
import hashlib
import string
from datetime import datetime

import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'reserialize_deposit_bags'
microservice_state = 'reserialized'
# The name of the directory under the processing root directory. One of
# 'havested', 'bagValidated', or 'reserialized'.
input_directory = 'bagValidated'

def reserialize_bag(deposit):
    started_on = datetime.now()
    deposit_uuid = deposit['deposit_uuid']
    outcome = 'success'
    error = ''
    
    # Read the source Bag's manifest-md5.txt file and read it into memory
    # so we can verify that the files have copied over intact.
    path_to_source_md5_manifest = staging_server_common.get_input_path(input_directory, [deposit_uuid, deposit_uuid, 'manifest-md5.txt'])
    md5s = {}
    with open(path_to_source_md5_manifest) as md5f:
        for line in md5f:
            (md5, path) = line.split()
            # Remove 'data/' from the file's name.
            clean_path = string.replace(path, 'data/', '')
            print "Path is now " + clean_path
            md5s[clean_path] = md5

    # Copy the files from the 'bagValidate' data directory into a
    # temporary directory, where the new Bag will be created
    path_to_source_files = staging_server_common.get_input_path(input_directory, [deposit_uuid, deposit_uuid, 'data'])
    path_to_temp_directory = staging_server_common.create_microservice_directory(microservice_state, deposit_uuid)
    print path_to_temp_directory
    source_files = os.listdir(path_to_source_files)
    for source_file in source_files:
        # 'virus_check.txt' was not in the original Bag so we skip it.
        if source_file != 'virus_check.txt':
            shutil.copy(os.path.join(path_to_source_files, source_file), path_to_temp_directory)
            path_to_copied_file = os.path.join(path_to_temp_directory, source_file)
            copied_file = open(path_to_copied_file, 'rb')
            md5_value = hashlib.md5()
            while True:
                # Read the file in 10 mb chunks so we don't run out of memory.
                buf = copied_file.read(10 * 1024 * 1024)
                if not buf:
                    break
                md5_value.update(buf)
            copied_file.close()
            if md5s[source_file] != md5_value.hexdigest():
                raise Exception("md5 checksums don't match for %s" % (path_to_copied_file))
    
    
    # Add these tags to bag-info.txt: Bagging-Date, External-Description [value of the journal title and issue number],
    # External-Identifier [value of the deposit URL], PKP-PLN-Journal-UUID, PKP-PLN-Deposit-UUID.
    # @todo: Get journal title and issue number.
    tags = {
        'External-Identifier': deposit['deposit_url'],
        'PKP-PLN-Journal-UUID': deposit['journal_uuid'],
        'PKP-PLN-Deposit-UUID': deposit['deposit_uuid']
    }
    bag = bagit.make_bag(path_to_temp_directory, tags)

    # Reserialize the Bag and assign it a filename using the pattern journaluuid.deposituuid.zip.
    serialized_bag_filename = '.'.join([deposit['journal_uuid'], deposit['deposit_uuid'], 'tar.gz'])
    serialzied_bag_path = os.path.join(config.get('Paths', 'processing_root'), microservice_state, serialized_bag_filename)
    with tarfile.open(serialzied_bag_path, "w:gz") as tar:
        tar.add(path_to_temp_directory, arcname=os.path.basename(path_to_temp_directory))
    
    finished_on = datetime.now()

    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

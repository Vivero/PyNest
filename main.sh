#!/bin/bash -ex

export PYTHONUNBUFFERED=1

export PYNEST_AUTH_FILE='data/auth.yml'

PYNEST_DB_INFO_FILE="data/db_info.sh"

if [[ -e "$PYNEST_DB_INFO_FILE" ]]; then
    source $PYNEST_DB_INFO_FILE

    exec /usr/bin/python /opt/PyNest/pynest.py

else
    printf "Missing '$PYNEST_DB_INFO_FILE'\n"
    printf "Create the file with the following contents:\n\n"
    printf "  export PYNEST_DB_NAME=<PostgreSQL database name>\n"
    printf "  export PYNEST_DB_USER=<PostgreSQL user name>\n"
    printf "  export PYNEST_DB_PASS=<PostgreSQL user password>\n"
    printf "  export PYNEST_DB_HOST=<PostgreSQL hostname>\n"
    printf "\nReplace <...> with appropriate credentials to access your PostgreSQL database.\n\n"
    printf "Running PyNest with database disabled ...\n"
    
    exec /usr/bin/python /opt/PyNest/pynest.py --no-db
fi





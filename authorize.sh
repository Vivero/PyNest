#!/bin/bash -e

NEST_API_KEYS="data/nest_api.sh"

if [[ -e "$NEST_API_KEYS" ]]; then
	source $NEST_API_KEYS
else
	printf "Missing '$NEST_API_KEYS'\n"
	printf "Create the file with the following contents:\n\n"
	printf "  export NEST_CLIENT_ID=<Nest product id>\n"
	printf "  export NEST_CLIENT_SECRET=<Nest product secret>\n"
	printf "\nReplace <Nest product id> and <Nest product secret> with the values from your Nest API.\n\n"
	exit 1
fi

export PYNEST_AUTH_FILE='data/auth.yml'

exec /usr/bin/python /opt/PyNest/pynest.py --authorize

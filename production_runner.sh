#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters. Web code required with not other arguments."
    exit -1
fi

# none of these parameters matter since we are running in test mode. but they are
#       required so we sneak them in here.
nohup /usr/local/bin/python3.6 -d "/r/NHL_Stats" --client-id x3R7jnLD4zHfEA --client-secret 7WeHFrqVmgO7iFhKjnZ9FllsHqA --key GgSFg8d3gkT --bot-name "NHL_Stats" --web-code $1 &
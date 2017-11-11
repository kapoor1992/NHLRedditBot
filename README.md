# NHLRedditBot
Posts NHL information to Reddit.


## Installation
```
pip install praw==5.2 python-dateutil
```

then do a git cloneof the repo. In the root of the project you need to create a file called praw_login.py that contains the following snippits

```python
import praw

r = praw.Reddit(client_id=<YOUR-CLIENT-ID>,
                client_secret=<YOUR-CLIENT-SECRET>,
                user_agent=<YOUR-USER-AGENT>,
                username=<REDDIT-USERNAME>,
                password=<REDDIT-PASSWORD>)
```

If the above variables don't make any sense to you, please read the PRAW docs here: https://praw.readthedocs.io/en/latest/


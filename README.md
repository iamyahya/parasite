# Parasite

Service for parsing cahnnel posts, comments and users.


### Install


Put your telegam app credentials in `.env` file.


#### Install required libs

`
$ pip install -r requirements.txt
`


#### Add first channel (telegram)

```
$ python manage.py --entity source add # this do only for first channel
> Input Source name: telegram

$ python manage.py --entity channel add
> Input Channel name: TheBadComedian
> Input Source name: telegram
```


#### Sync entities

```
$ python sync.py --entity posts

$ python sync.py --entity comments

$ python sync.py --entity users
```

#### :checkered_flag: Before push request

Let linter check code `$ pylint *.py`, and check unit test results `$ python -m pytest tests`

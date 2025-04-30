# CS 351 Flask Application

A simple flask application utilizing a database with `Flask-SQLAlchemy`.

## Installation
Open the terminal and navigate to the project folder (`git clone https://github.com/jtbison/cs-351-project.git`)

- Ensure Python is installed

- Create a virtual environment folder
```bash
python -m venv .venv
```

## Source into the virtual environment, depends on system
1. Windows:
```powershell
.\.venv\Scripts\activate.bat
```
OR:
2. Mac/Linux:
```bash
source .venv/bin/activate
```

## Install the requirmeents
```bash
pip install -r requirements.txt
```

## Now you can run the flask application by running the app.py file
```bash
python app.py
```

## Then, you can navigate to the website `http://127.0.0.1:5000` to see the working flask app

Login with default account:
Username: `Admin`
Password: `supersecret`


## Dependencies (also in requirements.txt)
`blinker`

`click`

`colorama`

`Flask`

`Flask-Scss`

`Flask-SQLAlchemy`

`Flask_Login`

`greenlet`

`itsdangerous`

`Jinja2`

`MarkupSafe`

`pyScss`

`six`

`SQLAlchemy`

`typing_extensions`

`Werkzeug`

UPUTSTVO:

U MySQLu, napraviti bazu kavijardb pod konekcijom username: root, password: root

Importovati .sql fajl na gitu

U konzoli, cd-ovati do direktorijuma kavijar-project/

Uraditi sledece komande (pretpostavljajuci Windows):

venv\scripts\activate

set FLASK_APP=kavijar

set FLASK_ENV=development

flask run

Aplikacija se nalazi na http://127.0.0.1:5000/

Login je na http://127.0.0.1:5000/auth/login

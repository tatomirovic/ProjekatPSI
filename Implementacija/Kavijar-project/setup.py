from setuptools import find_packages, setup

setup(
    name='kavijar',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask', 'python-dotenv', 'pymysql', 'cryptography', 'flask_sqlalchemy', 'markupsafe', 'flask-socketio'
    ],
)
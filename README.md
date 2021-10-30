# Results-Server

__Description__:

All the results data will exist in STUDENTS database where ADMIN has Authority to update STUDENTS data base,
Once student requests for result, after successful authentication with their OTP via Email, the result summary will be sent over email from the database via the results-server.

```bash
# https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04

sudo apt install mysql-server
sudo mysql_secure_installation
# Would you like to setup VALIDATE PASSWORD component? : y
# Please enter 0 = LOW, 1 = MEDIUM and 2 = STRONG: 2
# New password: <Put a strong password>
# Re-enter new password: <re-enter the same strong password>
# Remove anonymous users? : y
# Disallow root login remotely? : y
# Remove test database and access to it? : y
# Reload privilege tables now? : y
sudo mysql
```


```sql
CREATE USER 'vijay'@'localhost' IDENTIFIED BY 'HelloWorld123#';

# if you encounter <ERROR 1396 (HY000): Operation CREATE USER failed for 'vijay'@'localhost'>
# https://stackoverflow.com/questions/5555328/error-1396-hy000-operation-create-user-failed-for-jacklocalhost

DROP USER 'vijay'@'localhost';
CREATE USER 'vijay'@'localhost' IDENTIFIED BY 'HelloWorld123#';

GRANT CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT, REFERENCES, RELOAD on *.* TO 'vijay'@'localhost' WITH GRANT OPTION;

# when we grant some privileges for a user, running the command flush privileges will reloads the grant tables in the mysql database enabling the changes to take effect without reloading or restarting mysql service.

FLUSH PRIVILEGES;
EXIT;
```

```sh
# check whether the service is active and running
systemctl status mysql.service
```


```sh
git clone https://github.com/vijayreddybomma/FyndAcademy-Project.git
cd FyndAcademy-Project
git checkout server-v0

sudo apt install python3-pip
```

## Installation

### Step 1

```sh
pip install virtualenvwrapper

# virtualenv
export WORKON_HOME=~/Envs
mkdir -p $WORKON_HOME

nano ~/.bashrc
# Add the below lines to bashrc
# start ------------------
export WORKON_HOME=~/Envs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=~/.local/bin/virtualenv
source ~/.local/bin/virtualenvwrapper.sh
# ------------------- end

# finally
source ~/.bashrc
mkvirtualenv fyndacademy-project
```

### Step 2

```bash
pip install -r requirements.txt

export DATABASE_USER=vijay
export DATABASE_PASSWORD=HelloWorld123#
export DATABASE_SERVER=localhost
export DATABASE_NAME=students_results_server
# builds the database from csv
python -m app.db.build

export MAIL_USERNAME=vijaybomma0106@gmail.com
export MAIL_PASSWORD=Reddy@123 
export MAIL_FROM=vijaybomma0106@gmail.com
export MAX_ATTEMPTS = 3
export OTP_EXPIRY_SECONDS = 60
# run the server
uvicorn "app.main:app" --host=0.0.0.0 --port=8000

```

## Open in browser

`http://{Public IPv4 DNS}:{port}/{path}`

eg,. http://ec2-3-129-26-101.us-east-2.compute.amazonaws.com:8000/student/results
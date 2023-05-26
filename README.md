# Result-Server

## 1. Description

All the results data will exist in STUDENTS database, Once student requests for result, after successful authentication with their OTP via Email, the result summary will be sent over email in from of PDF from the database via the result-server.

## 2. Working

1. We expect the student results data in a `csv: data/student.csv` which we use to build `MySQL database`. Any further data needs to be added to csv for it to reflect in database.
2. First the webpage is displayed to the user which needs a `valid email` address to be submitted.
3. When the user `submits` the email, we check whether user's `email` exists in the database.
4. If the user is not found, we return `401_UNAUTHORIZED`
5. If the user is found, generate an OTP, store the user's entry {email, OTP, #attempts} in a dictionary. Send the OTP to user's `email` and return `OTP submit form`.
6. The OTP submission if received from the user, the OTP has three validations.
   1. Incorrect OTP - Return `401_UNAUTHORIZED`
   2. Max Number of Attempts Reached (3) - Return `403_FORBIDDEN`
   3. Timeout (OTP expiry after a certain period - 60 seconds) - Return `403_FORBIDDEN`
7. If the user submitted OTP is valid, then send the results via email in the form of PDF. 
   

## 3. Installation

__Below are the instructions to run the application of local (or) any cloud service__

For deploying on AWS EC2 Instance, make sure to ssh into the instance, We follow this blog from [twilio](https://www.twilio.com/blog/deploy-flask-python-app-aws) for app deployment

```sh
ssh ubuntu@{public-IPv4-address-of-ec2-instance} -i {pem-file}

```

### 3.1 MySQL installation
__Installtion follows this blog [Install MySQL](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04)__

```bash
sudo apt install mysql-server
sudo mysql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'HelloWorld123#';
ctrl+D
sudo mysql_secure_installation
# Would you like to setup VALIDATE PASSWORD component? : y
# Please enter 0 = LOW, 1 = MEDIUM and 2 = STRONG: 2
# New password: <Put a strong password>
# Re-enter new password: <re-enter the same strong password>
# Remove anonymous users? : y
# Disallow root login remotely? : y
# Remove test database and access to it? : y
# Reload privilege tables now? : y
sudo mysql -p 
```
### 3.2 MySQL: Create User

```sql
CREATE USER 'vijay'@'localhost' IDENTIFIED BY 'HelloWorld123#';

# if you encounter <ERROR 1396 (HY000): Operation CREATE USER failed for 'vijay'@'localhost'>
# https://stackoverflow.com/questions/5555328/error-1396-hy000-operation-create-user-failed-for-jacklocalhost
DROP USER 'vijay'@'localhost';
CREATE USER 'vijay'@'localhost' IDENTIFIED BY 'HelloWorld123#';

GRANT CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT, REFERENCES, RELOAD on *.* TO 'vijay'@'localhost' WITH GRANT OPTION;

# when we grant some privileges for a user, running the command flush privileges will reload the grant tables in the mysql database enabling the changes to take effect without reloading or restarting mysql service.

FLUSH PRIVILEGES;
EXIT
```

```sh
# check whether the service is active and running
systemctl status mysql.service
```
### 3.3 Clone the project

```sh
git clone https://github.com/vijayreddybomma/FyndAcademy-Project.git
cd FyndAcademy-Project
git checkout main

sudo apt install python3-pip
```

### 3.4 Virtualenv Installation

```sh
pip install virtualenvwrapper

# virtualenv
export WORKON_HOME=~/Envs
mkdir -p $WORKON_HOME

nano ~/.bashrc # opens up editor
# Add the below lines to bashrc
# start ------------------
export WORKON_HOME=~/Envs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=~/.local/bin/virtualenv
source ~/.local/bin/virtualenvwrapper.sh
# ------------------- end

# finally
source ~/.bashrc
# create a new virtual env
mkvirtualenv result-server
# switch/activate a virtual env
workon result-server
# deactivate
deactivate
```

### 3.5 Requirements Installation

```sh
# pdfkit dependency: to generate pdf
sudo apt-get install wkhtmltopdf

workon result-server

pip install pip-tools
cd requirements

# when building project for the first time
# update packages in all.in
pip-compile --output-file all.txt all.in
pip-sync all.txt
cd ..

```

### 3.6 Build the database
```sh
# update the following environment variables to build-db.sh
export DATABASE_USER=vijay
export DATABASE_PASSWORD=HelloWorld123#
export DATABASE_SERVER=localhost
export DATABASE_NAME=result_server
# builds the database from csv
sh build-db.sh
```

### 3.7 Start the server in tmux session

```sh
# tmux allows us to run programs in sessions and detach them so that they can continue running without interruption even if ssh connection is terminated
sudo apt install tmux
# tmux new -s {session_name}
tmux new -s deployment
# switch to working environment
workon result-server

# update the following environment variables in run.sh
export DATABASE_USER=vijay
export DATABASE_PASSWORD=HelloWorld123#
export DATABASE_SERVER=localhost
export DATABASE_NAME=result_server
export MAIL_USERNAME=vijaybomma0106@gmail.com
export MAIL_PASSWORD=yqgfajbztvwqmnyv 
export MAIL_FROM=vijaybomma0106@gmail.com
export MAX_ATTEMPTS=3
export OTP_EXPIRY_SECONDS=60
# run the server
sh run.sh

# click ctrl+b d to detach

tmux ls # displays list of sessions
# tmux attach -t {session_name} 
tmux attach -t deployment # re-attach the session

tmux kill-session -t deployment # kills the session

```

### 3.8 Add more students to database
```sh
# Method 1
# add student details to data/students-results.csv on local, commit
# take a pull on server and build database again
nano data/student.csv
git add data/student.csv
git commit -m 'new student details added'
git push origin {your-current-branch}
git pull origin {your-current-branch} # On server

# Method 2 (in server environment)
# open up the data/students-results.csv in an editor
nano data/student.csv
# Ctrl+X to write/save and Ctrl+O to exit

# Method 3 (in server environment)
# echo new student details and append to csv
echo "{email},{name},{english},{maths},{science}" >> data/student.csv
```

## 4. Open in browser

`http://{Public-IPv4-DNS}:{PORT}/{path}`

For `Public-IPv4-DNS`, Goto [AWS EC2 Management Console](https://us-east-2.console.aws.amazon.com/ec2/v2/home?region=us-east-2#Instances:sort=dnsName)

For `PORT`, refer to the uvicorn server port above (make sure it's added as `CUSTOM TCP Rule`rule in security groups when creating EC2 instance)

eg,. http://ec2-34-207-221-255.compute-1.amazonaws.com:8000/

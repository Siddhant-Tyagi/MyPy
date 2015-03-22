## MyPy
### Python based MySQL monitoring tool

##### Prerequisite
* Python 2.7.6
* pip
* Django 1.6
* MySQL-Python 1.2.5

##### Installation
* Ensure that Python 2.7.6 is installed and the current environment set to it. [Python Installation Doc](https://docs.python.org/2/install/)
* [Install pip] (https://pip.pypa.io/en/latest/installing.html)
* Install Django version 1.6. `sudo pip install django==1.6`
* Install MySQL API for python. `sudo pip install mysql-python`
* Clone this MyPy repo. `git clone https://github.com/Siddhant-Tyagi/MyPy.git`
* Navigate inside the MyPy directory and run command. `python manage.py runserver <HOST>:<PORT>`
* Open the browser and navigate to \<HOST>:\<PORT> (given in the previous command)

##### The problem it solves
MySQL server is the most widely used RDBMS and no wonder it's share in this market tops 70%+. Despite its popularity, it doesn't have many open source options when it comes to monitoring. It is with this end that I developed MyPy. It would help the user(DBA) to get vital stats of the MySQL server in real time.

##### Getting started
* Execute the command `python manage.py runserver <HOST>:<PORT>`, inside the directory where manage.py file is present. For example, to run the server on localhost port 8888 the command would be `python manage.py runserver 127.0.0.1:8888`.
* In the browser navigate to the \<host>:\<port> provided in the runserver command. The landing page provides the user with an interface to add and monitor the MySQL server(s). The tabs on top are the different group of monitors containing different counter values in each group. These counter values are derived from various global variables, status variables and slave status variables. By default the **General Info** group is selected at page load. This is how the landing page looks like.
<br><br>
<img src="http://i.imgur.com/ODD8OqM.png?1">
* To add a server, click on the **Add Server** button. Fill in the details of the MySQL server.<br><br> <img src="http://i.imgur.com/GwJ57iP.png?1">
* Click on the **Save details** button. An alert box will notify the user of the status of the connection. In case the connection is not successful, it returns a proper error number as well the error message.<br><br> <img src="http://i.imgur.com/E5O3mKp.png?1">
* The added server will appear in the left panel on the MyPy page.<br><br> <img src="http://i.imgur.com/oRcWWDt.png?1">
* To edit the server details, click on the server name in the panel.
* The formula used to calculate any of the counter's value can be accessed by hovering the mouse over the given counter name.<br><br><img src="http://i.imgur.com/zKGyNkA.png?1">

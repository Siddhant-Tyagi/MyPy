## MyPy
### Python based MySQL monitoring tool

##### Prerequisite
* Python 2.7.6
* Django 1.6
* MySQL-Python 1.2.5

##### Installation
* Ensure that Python 2.7.6 is installed and the current environment set to it. [Python Installation Doc](https://docs.python.org/2/install/)
* Install Django version 1.6. `sudo pip install django==1.6`
* Install MySQL API for python. `sudo pip install mysql-python`
* Clone this MyPy repo. `git clone https://github.com/Siddhant-Tyagi/MyPy.git`
* Navigate inside the MyPy directory and run command. `python manage.py runserver <HOST>:<PORT>`
* Open the browser and navigate to \<HOST>:\<PORT> (given in the previous command)

##### The problem it solves
MySQL server is the most widely used RDBMS and no wonder it's share in this market tops 70%+. Despite its popularity, it doesn't have many open source options when it comes to monitoring. It is with this end that I developed MyPY. It would help the user(DBA) to get vital stats of the MySQL server.

##### Getting started
* In the browser navigate to the \<host>:\<port> provided in the runserver command. The landing page provides the user with an interface to add and monitor the MySQL server(s). The tabs on top are the different group of monitors containing different counter values in each group. By default the **General Info** group is selected at page load. This is how the landing page looks like.
<br><br>
<img src="http://i.imgur.com/ODD8OqM.png?1">


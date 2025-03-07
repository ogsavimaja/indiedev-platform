# Indiedev-platform

This app is intended to be used by indie game developers who can share their work in progress games on the platform to get & give feedback about their projects. This way indie game developers can get valuable game testing feedback in the work in progress state. This allows for discovery of potential bugs in the game way sooner when they are still easy to fix and don't ruin the imago of the game by being released all buggy. The game testing feedback also reveals what is good in the game and what parts of the game still need improving/rework.

The other good side of using this app is that it lets developers to comment each others projects, plan ideas and planned price of the game way before full release of their games. This helps the lauch of the game go as smoothly as possible with the best price, development roadmap and quality of the game possible.




## Current state

* User can create an account and use it to sign in to the app
* User can add, see, edit and delete project announcements
* User can choose, edit and remove different classes for their announcement
* User can add, see, edit and remove comments on announcements
* User sees project announcements added to the app
* User can search project announcements with a keyword (title&description)
* The app has user pages which show statistics and project announcements and feedback/reviews/comments added by the user
* User can open userpage of others and his own from announcement, comment or only his own from homepage


Current verion of the app accounts for most of if not all of the common errortypes and I werent able to find a way to "crash" the application by using only browser.
The current version of the app also has protective measures against potential misusage of the app like trying to edit/remove announcements without authority.
All of the saved passwords stored in the database are salted before hashing for vastly added rainbow table attack resistance and slightly added dictionary/bruteforce attack resistance in case of database breach.


## Planned features
There are multiple new features planned for this app which are still in the development such as:
* Ability to select a language
* Sorting of search results by a category
* Voting system for good announcements and feedback/comments
* About page
* Multiple QOL and visual improvements


## How to use
1. Download the repository.<br/>
   Use your desired method or download the .zip file from [Here](https://github.com/ogsavimaja/indiedev-platform/archive/refs/heads/main.zip).

2. Download Flask if you don't have it installed already.<br/>
   You can download Flask by using pip if you have pip added to your PATH by using the command shown below in terminal or download it from [pypi.org](https://pypi.org/project/Flask/).
 
```
pip install flask
```

3. Create database and tables.<br/>
   You can create database and the tables in it to the folder containing this project by using commands listed below in your terminal if you are using Linux or by creating a database.db file, opening it with SQLite and     using commands `.read schema.sql` and `.read init.sql`.

```
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```

4. Run the program.<br/>
   You can run the program by running the command shown below in a terminal that has been opened inside the folder containing this application if you have Flask added to your PATH or by running App.py (launches the  application in debug mode).

```
flask run
```

> [!NOTE]
> This "How to use" guide expects you have Python and SQLite downloaded.
> If you don't have [Python](https://www.python.org/downloads/) or [SQLite](https://www.sqlite.org/download.html) downloaded, you can use the links imbedded into this note to navigate to the corresponding download sites.

> [!TIP]
> This application can be run in VS Code (in debug mode) by running App.py in a basic VS Code enviromment

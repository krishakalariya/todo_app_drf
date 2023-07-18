# Todo_App_DRF
1) Take a pull of repo.
2) Command for installing requirements : pip install -r requirements.txt
3) Create .env file in todo_app_drf directory and set value of , DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
4) Perform migrations : python3 manage.py migrate
5) Command for start server : python3 manage.py runserver
6) Steps to execute the urls ::
   1) Register (minimum 2 users)
   2) Login
   3) Create categories
   4) Create ToDo
   5) Share your ToDo with other users
   6) If you will update the ToDo. And You are not Owner then request for Change ToDo will be saved else if you are owener then ToDo will be updated.
   7) Now, Owner can approve/reject the change requests. If owner will approve the changes then changes will reflect in ToDo.
   8) Throughout the process all the changes related to ToDO will be saved as Logs.
   9) You can List all the changes for any ToDo.
7) Please refer postman collection added in project directory > .postman folder

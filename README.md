# StudentApp

A semi-automated application to keep track of students' lessons and their payments.

## Creating .exe file
pyinstaller --onefile --add-data "$(python -m certifi):certifi" --clean main.py

--icon=favicon.ico can be added for a specific icon.

## Usage
Run the .exe file.
Important: credentials.json, tocken.pickle and student_app.db must be in the same directory as the .exe file.

If apple's gatekeeper complains and doesn't allow you to open the app, move the app to a folder in the user folder.
Then you can use: xattr -dr com.apple.quarantine /path/to/StudentApp
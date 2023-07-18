
# Avatar Search

Avatar Search is a web application built with Flask and SQLite that allows you to search for avatars and retrieve their information from a database. You can search by avatar name or ID, upload avatar information from JSON files, and retrieve avatar data in JSON format.

## Features

- Search avatars by name or ID
- Upload avatar information from JSON files
- Retrieve avatar data in JSON format

## Prerequisites

- Python 3.x
- Flask
- SQLite
- Requests

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Fynn9563/AvatarSearch.git` 
```
2.  Install the required dependencies:

```bash
`pip install -r requirements.txt` 
```
3.  Run the application:

```bash
`python server.py` 
```
The application will start running on [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Usage

1.  Access the application in your web browser using the URL `http://127.0.0.1:5000/`.
2.  Enter the avatar name or ID in the search box and click the **Search** button to retrieve matching avatars.
3.  To upload avatar information from a JSON file, click the **Upload** button and select the JSON file.

## VRCX Integration

To integrate with VRCX and enable avatar searching from within VRCX, follow these steps:

1.  Open VRCX and go to **Settings**.
2.  Click on **Advanced**.
3.  Click on **Avatar Database Provider**.
4.  Add `http://127.0.0.1:5000/json` as the avatar database URL.

Now you can search for avatars directly from VRCX using the Avatar Search functionality.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Fynn9563/AvatarSearch/blob/master/LICENSE) file for more information.

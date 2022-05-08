# imessage-backup
![Tests](https://github.com/joeylemon/imessage-backup/workflows/Tests/badge.svg)

Backup all messages from an iPhone to free up space from your phone while allowing you to retain all of your conversation history. This script provides the ability to extract messages from an iPhone and store them freely in a zip file. This zip file can later be viewed in a companion web app (_not yet implemented_) so you never lose your old messages.

## Usage

```
usage: main.py [-h] {backup,gen} ...

Backup messages from an iPhone

positional arguments:
  {backup,gen}
    backup      backup all messages from an iPhone backup
    gen         generate a webpage to easily view messages

optional arguments:
  -h, --help    show this help message and exit
```

### Get started

**Step 1.** Clone this repository:
```
> git clone https://github.com/joeylemon/imessage-backup.git
> cd imessage-backup
```

**Step 2.** Set up the Python virtual environment and install requirements:
```
> python -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt
```

## Backing up your messages
First, create an unencrypted backup of your iPhone directly onto your computer ([how to do this?](https://support.apple.com/guide/iphone/back-up-iphone-iph3ecf67d29/ios)). Then, find the path to the folder containing your backup and pass it to the script:
```
> python main.py  "E:\Users\Joey\Apple\MobileSync\Backup\12345678-000919512230001E" -o backup
```

This will create a file named `backup.zip` containing the following directory structure:
```
backup.zip
--> messages.json
--> contacts.json
--> attachments/
    --> 0AB09373-F366-4D3B-85FC-1ABA33EE534F-jpeg-image-xIcbg.jpeg
    --> 3A5AD82C-1CE0-404E-86D4-149522201EDB-FullSizeRender.jpg
```

The `messages.json` file contains every message sent to and from your phone, with information including the chat title, the chat participants, and a link to an attachment if present. This file represents all chat participants as phone numbers. Therefore, the `contacts.json` file contains all contacts on your phone, allowing the cross-reference of phone numbers to contact names.

## Viewing Stored Messages
_This functionality has not yet been implemented._

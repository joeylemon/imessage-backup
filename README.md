# imessage-backup
![Tests](https://github.com/joeylemon/imessage-backup/workflows/Tests/badge.svg)

Backup all messages (including attachments) from an iPhone to free up space while allowing you to retain all of your conversation history. This script provides the ability to extract messages from your phone and store them freely in a zip file. This zip file can be later viewed in a companion web app (_not yet implemented_) so you never lose access to your old messages.

## Usage

```
usage: main.py [-h] [-o OUT] input

Backup messages from an iPhone

positional arguments:
  input              the directory path containing the iPhone backup

optional arguments:
  -h, --help         show this help message and exit
  -o OUT, --out OUT  the name of the output file
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
> python main.py  "E:\Users\Joey\Apple\MobileSync\Backup\12345678-000919512230001E" -o backup.zip
```

This will create a file named `backup.zip` containing the following directory structure:
```
backup.zip
--> chats/
    --> chat_1634.json
    --> chat_1695.json
--> attachments/
    --> 0AB09373-F366-4D3B-85FC-1ABA33EE534F-jpeg-image-xIcbg.jpeg
    --> 3A5AD82C-1CE0-404E-86D4-149522201EDB-FullSizeRender.jpg
```

The `chats/` directory contains files representing every conversation on your phone, with information including the title, the participants, and all the messages ever received in it. All messages that were sent with attachments contain the path to the attachment stored in the `backup.zip` file.

## Viewing Stored Messages
_This functionality has not yet been implemented._

import logging
import logger
import atexit

data = open('BItitles', 'w')
error = open('errorLog', 'w')

def writeToFile(session, container):
    try:
        if not session.failed and session.dataContainer.title is not None:
            data.write(container.title.replace(",","") + "," + container.date.replace(",","").replace(".","") + "\n")
        else:
            error.write(str(session.returnCode) + " " + session.url + "\n")
    except:
        logger.log(logging.ERROR, "Unhandled exception in storage.py")

def writeToDb(session, container):
    a = "Will come soon - Happy Halloween"

def atexitfct():
    """Cleanly closes file objects"""
    data.close()
    error.close()

atexit.register(atexitfct)
import logging
import logger
import atexit

data = open('BItitles', 'w')
error = open('errorLog', 'w')

def writeToFile(session, container):
    try:
        print str(session.failed)
        if (not session.failed) and (session.dataContainer.title is not None):
            data.write(container.title.replace(",","") + "," + container.date.replace(",","").replace(".","") + "," + session.url +"\n")
        elif session.failed:
            error.write(str(session.returnCode) + " " + session.url + "\n")
        else:
            raise Exception("..")
    except:
        logger.log(logging.ERROR, "Unhandled exception in storage.py")

def writeToDb(session, container):
    a = "Will come soon - Happy Halloween"

def atexitfct():
    """Cleanly closes file objects"""
    data.close()
    error.close()

atexit.register(atexitfct)
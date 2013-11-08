import logging
import logger
import atexit

data = None
error = None

def writeToFile(session, container):
    global data, error
    try:
        if (not session.failed) and (session.dataContainer.title is not None):
            if data is None:
                data = open('output.txt', 'w')
            data.write(container.title.replace(",","") + "," + container.date.replace(",","").replace(".","") + "," + session.url +"\n")
        elif session.failed:
            if error is None:
                error = open('error.txt', 'w')
            error.write(str(session.returnCode).replace(",","") + "," + str(session.errorMsg).replace(",","") + "." + session.url.replace(",","") + "\n")
        #else:
        #    raise Exception("..")
    except:
        logger.log(logging.ERROR, "Unhandled exception in storage.py")

def writeToDb(session, container):
    a = "Will come soon - Happy Halloween"

def atexitfct():
    """Cleanly closes file objects"""
    if data is not None:
        data.close()
    if error is not None:
        error.close()

atexit.register(atexitfct)
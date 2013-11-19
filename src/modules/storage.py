import logging
import logger
import atexit

dataFd = None
errorFd = None

def writeToFile(session, container):
    global dataFd, errorFd
    try:
        if (not session.failed) and (session.dataContainer.title is not None):
            if dataFd is None:
                dataFd = open('output.txt', 'w')
            dataFd.write(container.author.replace(",","") + "," + container.title.replace(",","") + "," + session.url +"\n")
        elif session.failed:
            if errorFd is None:
                errorFd = open('error.txt', 'w')
            errorFd.write(str(session.returnCode).replace(",","") + "," + str(session.errorMsg).replace(",","") + "." + session.url.replace(",","") + "\n")
        #else:
        #    raise Exception("..")
    except:
        logger.log(logging.ERROR, "Unhandled exception in storage.py")

def writeToDb(session, container):
    a = "Will come soon - Happy Halloween"

def atexitfct():
    """Cleanly closes file objects"""
    if dataFd is not None:
        dataFd.close()
    if errorFd is not None:
        errorFd.close()

atexit.register(atexitfct)
import hashlib 
import os.path

def cleanInput(sInput):
    if sInput != None:
        sInput = sInput.upper()
        sInput = sInput.replace("NULL", "")
        sInput = sInput.replace("'", "")  
        sInput = sInput.replace("*", "")
        sInput = sInput.replace("$", "")
        sInput = sInput.replace("\\", "")
        sInput = sInput.replace("\"", "")
        sInput = sInput.replace("SELECT", "")
        sInput = sInput.replace("DROP", "")
        sInput = sInput.replace("SHOW", "")
        sInput = sInput.replace("DESC", "")
        sInput = sInput.replace("TRUNC", "")
        sInput = sInput.replace("DELETE", "")
        sInput = sInput.replace("INSERT", "")
        sInput = sInput.replace("UPDATE", "")
        if sInput == "" or sInput == "/":
            #sInput = "This string doesnt exist"
            sInput = ""
        return sInput

def my_get_argument(ref, sVar, lClean=True):
    try:
        sValue = ref.get_argument(sVar)
        if lClean:
            sValue = cleanInput(sValue)
    except:
        return ""
    return sValue

def DBG(sMsg):
    print sMsg

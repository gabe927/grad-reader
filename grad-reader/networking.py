import asyncio
import json
import websockets

queue = {
    1:{
        "last":-1,
        "q":[
            # {
            #     "mainText":"",
            #     "subText":"",
            #     "status":0    
            # }
        ]
    },
    2:{
        "last":-1,
        "q":[]
    }
}
# status:
# 1 = queued
# 2 = showing
# 3 = showed
users = set()

################
#              #
# WS Functions #
#              #
################

async def register(websocket):
    users.add(websocket)

async def unregister(websocket):
    users.remove(websocket)

async def notifyUsers(message):
    if users:
        for user in users:
            task = asyncio.create_task(user.send(json.dumps(message)))
            done, pending = await asyncio.wait({task})

#####################
#                   #
# Private Functions #
#                   #
#####################

async def _appendQueue(qNum, mainText, subText):
    # add to queue
    queue[qNum]["q"].append({"mainText":mainText, "subText":subText, "status":1})
    print(queue)
    # send response back
    payload = {
        "cmd":"addToQueue_response",
        "qNum":qNum,
        "mainText":mainText,
        "subText":subText,
        "status":1,
        "qID":len(queue[qNum]["q"])-1
    }
    await notifyUsers(payload)

async def _clearLast(qNum):
    lastQId = queue[qNum]["last"]
    if lastQId >= 0:
        # update the previous item of the queue
        queue[qNum]["q"][lastQId]["status"] = 3
        payload = {
            "cmd":"updateQ",
            "qNum":qNum,
            "qId":lastQId,
            "status":3
        }
        await notifyUsers(payload)

# async def _clearItems(qNum, clearAll):

####################
#                  #
# Public Fucntions #
#                  #
####################
async def addToQ(qNum, mainText, subText):
    if qNum == 0:
        for i in range(len(queue)):
            await _appendQueue(i+1, mainText, subText)
    else:
        await _appendQueue(qNum, mainText, subText)

async def showText(qNum, mainText, subText):
    payload = {
        "cmd":"showText",
        "qNum":qNum,
        "mainText":mainText,
        "subText":subText
    }
    await notifyUsers(payload)
    if qNum == 0:
        for i in range(len(queue)):
            await _clearLast(i+1)
    else:
        await _clearLast(qNum)

async def showFromQ(qNum, qId):
    qItem = queue[qNum]["q"][qId]

    # show the item from the queue
    await showText(qNum, qItem["mainText"], qItem["mainText"])

    await _clearLast(qNum)
    queue[qNum]["last"] = qId

    # update the status of the current item
    qItem["status"] = 2
    payload = {
        "cmd":"updateQ",
        "qNum":qNum,
        "qId":qId,
        "status":2
    }
    await notifyUsers(payload)

async def getQ(qNum):
    payload = {
        "cmd":"getQ"
    }
    if qNum == 0:
        for i in range(len(queue)):
            payload.update({"qNum":i+1})
            payload.update({"queue":queue[i+1]["q"]})
            await notifyUsers(payload)
    else:
        payload.update({"qNum":qNum})
        payload.update({"queue":queue[qNum]["q"]})
        await notifyUsers(payload)

# async def clearDone(qNum):
#     # clears the items which have been shown


##########
#        #
# Server #
#        #
##########

async def server(websocket, path):
    # add the user to the list of users
    await register(websocket)
    try:
        # wait for a message
        async for message in websocket:
            dataIn = json.loads(message)
            cmd = dataIn["cmd"]
            if cmd == "addToQ":
                await addToQ(dataIn["qNum"], dataIn["mainText"], dataIn["subText"])
            if cmd == "showText":
                await showText(dataIn["qNum"], dataIn["mainText"], dataIn["subText"])
            if cmd == "showFromQ":
                await showFromQ(dataIn["qNum"], dataIn["qId"])
            if cmd == "getQ":
                await getQ(dataIn["qNum"])
    finally:
        await unregister(websocket)

start_server = websockets.serve(server, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
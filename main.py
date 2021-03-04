import asyncio
import discord
import pyautogui

token = 'Wedz\'s way'
with open('./discord_token.txt') as f:
    token = f.read().strip()

# client
client = discord.Client()

# channel id
channelId_ACckChat = "494840511308234764"

channelList = [
    channelId_ACckChat
]

# building status
# 0 : grey (nobody)
# 1 : blue (us)
# 2 : red (them)
buildingList = [0, 0, 0, 0, 0, 0]

# building position on screenshot. Must be changed each city
buildingPos = [[298, 345], [241, 495], [491, 588], [771, 600], [979, 500], [963, 327]]

# if first test, don't send message since every building goes from 0gray to something else
firstTest = True


@client.event
async def on_ready():
    print("Ready")
    message = "You missed me ? :smirk:"
    await sendMessage(channelId_ACckChat, message)


@client.event
async def on_message(message):
    # annule si l'auteur du message est le bot
    if message.author == client.user:
        return

    # annule si mauvais channel
    if not str(message.channel.id) in channelList:
        return

    if message.content.upper().startswith('WARSTATUS'):
        await message.channel.send(file=discord.File('screen.png'))


def getEmoji(emojiName):
    return str(discord.utils.get(client.emojis, name=emojiName))


def sendMessage(channelParamID, messageParam):
    return client.get_channel(int(channelParamID)).send(messageParam)


async def my_background_task():
    global buildingList
    global buildingPos
    global firstTest

    await client.wait_until_ready()

    # 0 : grey (nobody)
    # 1 : blue (us)
    # 2 : red (them)
    newBuildingList = [0, 0, 0, 0, 0, 0]

    while not client.is_closed():

        # take and save screenshot
        im = pyautogui.screenshot(region=(108, 32, 1109, 693))
        im.save(r"./screen.png")

        # check each buildings for pixel RGB color
        for i in range(0, 6):
            pos1 = buildingPos[i][0]  # building i position x
            pos2 = buildingPos[i][1]  # building i position y
            # get pixel at coords pos1, pos2. return (R, G, B)
            pixel = im.getpixel((pos1, pos2))
            # blue
            if pixel == (144, 179, 235):
                newBuildingList[i] = 1

            # red
            if pixel == (255, 101, 100):
                newBuildingList[i] = 2

            # grey
            if pixel == (94, 106, 131):
                newBuildingList[i] = 0

        # display old status and new status, for debug
        print(buildingList)
        print(newBuildingList)
        print("============================")

        somethingMoved = False
        # only if not first iteration of the background task
        if not firstTest:
            # for each building
            for i in range(0, 6):
                message = ""
                # if status has changed
                if buildingList[i] != newBuildingList[i]:
                    somethingMoved = True

                    # get senior role for ping
                    roles = list(client.guilds)[0].roles
                    for role in roles:
                        if role.name == 'Senior':
                            senior = role
                    message += senior.mention
                    message += " "

                    # if nobody has the building
                    if newBuildingList[i] == 0:
                        if buildingList[i] == 1:  # 1 : was ours
                            message += "We lost building " + str(i+1) + " :weary:\n"
                        else:  # 2 : was theirs
                            message += "They lost building " + str(i+1) + ", focus P bots :grimacing:\n"

                    # if we have the building
                    if newBuildingList[i] == 1:
                        message += "We took "
                        if buildingList[i] == 0:  # 0 : was empty
                            message += "empty building " + str(i+1) + " :grin:\n"
                        else:  # 2 : was theirs
                            message += "their building " + str(i+1) + " " + getEmoji("pika") + "\n"

                    # if they have the building
                    if newBuildingList[i] == 2:
                        message += "They took "
                        if buildingList[i] == 0:  # 0 : was empty
                            message += "empty building " + str(i+1) + " :angry:\n"
                        else:  # 1 : was ours
                            message += "our building " + str(i+1) + " :rage:\n"

            # only if the status of one of the buildings has changed
            if somethingMoved:
                # send message + screenshot
                print("somethingMoved")
                await sendMessage(channelId_ACckChat, message)
                await client.get_channel(int(channelId_ACckChat)).send(file=discord.File('screen.png'))

        # first iteration done, not firstTest anymore
        firstTest = False

        # update building status
        buildingList = newBuildingList[:]

        # task runs every n seconds
        n = 30
        await asyncio.sleep(n)


client.loop.create_task(my_background_task())
client.run(token)

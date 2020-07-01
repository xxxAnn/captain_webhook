import discord, os
from discord.ext import commands
import time
import json
import random
from random import randint
from datetime import datetime
from time import sleep
import operator


lasttime = int(time.time())


class Inventory:
    def __init__(self, content, content_literal):
        self.content = content
        self.legacy_deprecated_content_literal = content_literal

    def has(self, selectid: str):
        for item in self.content:
            if str(item.id) == selectid:
                return item
        return False

    def get(self, selectid: str):
        for item in self.content:
            if str(item.id) == selectid:
                return item
        return None

    def add(self, item):
        self.content.append(item)

class Shop:
    def __init__(self, owner, inv, name):
        self.owner = owner
        self.inv = inv
        self.name = name
        self.id = str(id)

    def save(self):
        global data
        data = jsonLoad()
        content_literal = toContentLiteral(self.inv.content)
        data["Shops"][self.id]["Inventory"] = content_literal


class Item:
    def __init__(self, id, name, amount, exclusive):
        self.id = str(id)
        self.name = name
        self.amount = amount
        self.exclusive = exclusive


class Player:

    def __init__(self, inventory, money, energy, id):
        self.inventory = inventory
        self.money = money
        self.energy = energy
        self.id = str(id)

    def save(self):
        global data
        data = jsonLoad()
        if self.id not in data:
            data[self.id] = {"Energy": None, "Money": None, "Inventory": None}
        data[self.id]["Energy"] = self.energy
        data[self.id]["Money"] = self.money
        content_literal = toContentLiteral(self.inventory.content)
        data[self.id]["Inventory"] = content_literal
        jsonUpdate(data)


def find_id_from_item_name(name: str):
    id_dict = {
    "oil": "1",
    "bronze_ore": "2",
    "frog": "3",
    "diamond_ore": "4",
    "gold_ore": "5",
    "iron_ore": "6",
    "silver_ore": "7",
    "wood": "8",
    "bread": "9",
    "meat": "17",
    "bronze_knife": "100",
    "plastic": "101",
    "toy_knife": "103",
    "diamond_sword": "104",
    "silver_sword": "105"}
    name = str.lower(name)
    if name in id_dict:
        return(id_dict[name])
    else:
        return "Not Found"


def find_item_from_id(element):
    dict_name = {
    "1": "Oil",
    "2": "Bronze Ore",
    "3": "Frog",
    "4": "Diamond Ore",
    "5": "Gold Ore",
    "6": "Iron Ore",
    "7": "Silver Ore",
    "8": "Wood",
    "9": "Bread",
    "17": "Meat",
    "100": "Bronze Knife",
    "101": "Plastic",
    "103": "Toy Knife",
    "104": "Diamond Sword",
    "105": "Silver Sword"}
    if isinstance(element, list):
        new_list = []
        for item in element:
            if item in dict_name:
                item_name = dict_name[item]
                new_list.append(Item(item, item_name, 0, False))
            else:
                return "Not found"
            return new_list
    else:
        if element in dict_name:
            element_name = dict_name[element]
            return Item(element, element_name, 0, False)
        else:
            return "Not found"


def executeSomething():
    global data
    data = jsonLoad()
    for i in data.keys():
        if "Energy" in data[i]:
            player = constructPlayer(i)
            id = int(i)
            if int(time.time()) - data[i]["Energy"]["Recover"] > 299:
                data[i]["Energy"]["Val"] = 10
                player.energy["Val"] = 10
                data[i]["Energy"]["Recover"] = int(time.time())
                player.energy["Recover"] = int(time.time())
                player.save()
        jsonUpdate(data)

def jsonUpdate(data):
    d = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    with open("data/Money.json", "w") as file:
        file.write(d)


def toContentLiteral(inventoryContentItem):
    literal_list = []
    for item in inventoryContentItem:
        x = {"Id": item.id, "Name": item.name, "Amount": item.amount, "Exclusive": item.exclusive}
        literal_list.append(x)
    return literal_list


def jsonLoad():
    with open("data/Money.json", "r") as f:
        x = f.read()
        return json.loads(x)


def cram():
    with open("data/Cram.json", "r") as f:
        x = f.read()
        return json.loads(x)

def constructPlayer(id):
    id = str(id)
    global data
    data = jsonLoad()
    if id not in data:
        data[id] = {"Money": 0, "Inventory": [], "Energy": {"Val": 10, "Recover": int(time.time())}}
    listContent = []
    for i in data[id]["Inventory"]:
        x = Item(i["Id"], i["Name"], i["Amount"], i["Exclusive"])
        listContent.append(x)
    inventoryObject = Inventory(listContent, data[id]["Inventory"])
    playerObject = Player(inventoryObject, data[id]["Money"], data[id]["Energy"], id=id)
    return playerObject

def constructShop(shopId):
    global data
    data = jsonLoad()
    listContent = []
    for i in data["Shops"][shopId]["Inventory"]:
        x = Item(i["Id"], i["Name"], i["Amount"], i["Exclusive"])
        listContent.append(x)
    inventoryObject = Inventory(listContent, data[id]["Inventory"])
    shopObject = Shop(data["Shops"][shopId]["Owner"], inventoryObject, data["Shops"][shopId], shopId)
    return shopObject


class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def idtoname(self, ctx, id: str):
        await ctx.send(find_item_from_id(id).name)

    @commands.command()
    async def bal(self, ctx, *user: discord.Member):
        if not user:
            user = ctx.message.author
        else:
            user = user[0]
        id = str(user.id)
        player = constructPlayer(user.id)
        embed = discord.Embed(title="{0}'s balance".format(user.display_name))
        embed.add_field(name="Money:", value="{0}{1}".format(player.money, data["Currency"]), inline=True)
        await ctx.send(embed=embed)
        player.save()

    @commands.command()
    async def pay(self, ctx, user: discord.Member, amount):
        amount = amount.replace(",", "")
        amount = int(amount)
        if not amount < 0 or ctx.message.author.id == 692901380058382376:
            id = str(user.id)
            idc = str(ctx.message.author.id)
            player = constructPlayer(id)
            playerc = constructPlayer(idc)
            if amount > playerc.money:
                await ctx.send("You ain't got the money")
            else:
                playerc.money -= amount
                player.money += amount
                await ctx.send("Succesfully paid user")
            player.save()
            playerc.save()
        else:
            await ctx.send("Stealing is wrong")

    @commands.command()
    async def top(self, ctx):
        global data
        data = jsonLoad()
        exp = {}
        for i in data:
            if "Money" in data[i]:
                x = data[i]
                exp[i] = x["Money"]
        sortedExp = sorted(exp.items(), key=operator.itemgetter(1))
        sortedExp = list(reversed(sortedExp))
        w = len(exp) - 1
        string = "```pl\n"
        for x in range(0, 10):
            try:
                txt = str(sortedExp[x][0])
            except:
                break
            usa = self.bot.get_user(int(txt))
            w = True
            if not usa:
                data.pop(txt)
                w = False
            elif usa.bot:
                data.pop(txt)
                w = False
            if w:
                val = data[txt]["Money"]
                val = f'{val:,}'.format(val=val)
                string = string + "{" + str(x + 1) + "}     #" + usa.display_name + "\n        Money : [" + str(val) + "] " + data[
                    "Currency"] + "\n"
        string = string + '```'
        await ctx.send(string)

    @commands.command()
    async def addexcl(self, ctx, id: str, *name):
        if ctx.message.author.id == 331431342438875137:
            player = constructPlayer(ctx.author.id)
            name = " ".join(name)
            player.inventory.content.append({"Amount": 1, "Exclusive": True, "Name": name, "Id": id})
            player.save()
        else:
            await ctx.send("Sorry lol you can't do that")
    @commands.command()
    async def craft(self, ctx, itemName, amountx=1):
        def craft(result, ctx, items, amounts, resultAmount, resultId, player):
            ranX = False
            if len(items) > 1:
                ranX = True
                item1 = items[0]
                item2 = items[1]
                amount1 = amounts[0]
                amount2 = amounts[1]
            else:
                item1 = items[0]
                amount1 = amounts[0]
            if ranX is True:
                if player.inventory.has(item1) is not False and player.inventory.has(item2) is not False:
                    item1 = player.inventory.has(item1)
                    item2 = player.inventory.has(item2)
                    if item1.amount > (amount1 - 1) and item2.amount > (amount2 - 1):
                        item1.amount -= amount1
                        item2.amount -= amount2
                        if player.inventory.has(resultId) is False:
                            resultItem = Item(id=resultId, name=result, amount=resultAmount, exclusive=False)
                            player.inventory.content.append(resultItem)
                            player.save()
                        else:
                            resultInInv = player.inventory.has(resultId)
                            resultInInv.amount += resultAmount
                            print("hey")
                            player.save()
                        return ("Successfully Crafted {0}".format(result))
                    else:
                        return ("You dont have sufficient resources")
                else:
                    return ("You dont have sufficient resources")
            else:
                if player.inventory.has(item1) is not False:
                    item1 = player.inventory.has(item1)
                    if item1.amount >= amount1:
                        item1.amount -= amount1
                        if player.inventory.has(resultId) is False:
                            resultItem = Item(id=resultId, name=result, amount=resultAmount, exclusive=False)
                            player.inventory.content.append(resultItem)
                            player.save()
                        else:
                            resultInInv = player.inventory.has(resultId)
                            resultInInv.amount += resultAmount
                            player.save()
                        return ("Successfully Crafted {0}".format(result))
                    else:
                        return ("You dont have sufficient resources")
                else:
                    return ("You dont have sufficient resources")
            return ("error")

        user = ctx.message.author
        player = constructPlayer(user.id)
        cramed = cram()
        crafts = cramed["crafts"]
        itemId = find_id_from_item_name(itemName)
        for item in crafts.keys():
            zx = crafts[item]
            if "Id" in zx:
                if zx["Id"] == itemId:
                    list2 = []
                    for i in zx["list2"]:
                        list2.append(i*amountx)
                    z = craft(zx["Result"], ctx, zx["list1"], list2, (zx["ResultAmount"]*amountx), itemId,  player)
                    await ctx.send(z)
                    return
        await ctx.send("Craft not found")


    @commands.command()
    async def craftable(self, ctx):
        global data
        data= jsonLoad()
        cramed = cram()
        string = ""
        for i in cramed["crafts"].keys():
            item = cramed["crafts"][i]
            text= "**{0}**, Requires Item: **{2}** __x{1}__".format(item["Result"], item["list2"][0], find_item_from_id(list1[0]).name)
            if len(item['list1'])>1:
                text+= " and Item Id **{1}** __x{0}__".format(item["list2"][1], find_item_from_id(list1[1]).name)
            text+="\n"
            string+=text
        await ctx.send(string)

    @commands.command()
    async def energy(self, ctx):
        user = ctx.message.author
        player = constructPlayer(user.id)
        await ctx.send("{0}/10, Recovers in {1} seconds".format(player.energy["Val"], int(-1*(time.time()-(player.energy["Recover"]+300)))))
        player.save()

    @commands.command()
    async def eat(self, ctx, itemName: str):
        player = constructPlayer(ctx.author.id)
        cramed = cram()
        itemId = find_id_from_item_name(itemName)
        if str(itemId) in cramed["Eatables"]:
            if player.inventory.has(itemId) is not False:
                itemX = player.inventory.get(itemId)
                itemX.amount-=1
                player.energy["Val"] += cramed["Eatables"][itemId]
                if player.energy["Val"] > 10:
                    player.energy["Val"] = 10
                await ctx.send("Replenished {0} energy".format(cramed["Eatables"][itemId]))
                player.save()
            else:
                await ctx.send("Y'aint have that")
        else:
            await ctx.send("Ya can't eat that")

    @commands.command(aliases=['inv'])
    async def inventory(self, ctx, *user: discord.Member):
        if not user:
            user = ctx.message.author
        else:
            user = user[0]
        player = constructPlayer(user.id)
        string = "{0}'s inventory:\n".format(user.display_name)
        embed = discord.Embed(title="{0}'s inventory".format(user.display_name))
        for item in player.inventory.content:
            if item.exclusive:
                embed.add_field(name=item.name, value="Exclusive")
                string+=str(item.name) + ": Exclusive\n"
            else:
                embed.add_field(name=item.name, value=item.amount)
                string+=str(item.name) + ": **x{}**\n".format(item.amount)
        player.save()
        await ctx.send(string)

    @commands.command()
    async def click(self, ctx):
        cramed = cram()
        player = constructPlayer(ctx.author.id)
        if player.energy["Val"]>0:
            player.energy["Val"]-=1
            items = [["Frog", 3], ["Oil", 1], ["Diamond Ore", 4], ["Gold Ore", 5], ["Iron Ore", 6], ["Silver Ore", 7], ["Bronze Ore", 2], ["Nothing", 0],
                     ["Wood", 8], ["Bread", 9], ["Meat", 17]]
            weighs = [0.3, 0.3, .005, .0075, .01, .05, .1, .3929, 0.2, 0.1, 0.05]
            itemMulti = 1
            moneyMulti = 1
            result = random.choices(items, weighs)
            result = result[0]
            print(result)
            for item in cramed["itemMulti"].keys():
                if player.inventory.has(item) is not False:
                    item2 = player.inventory.get(item)
                    if item2.amount>0:
                        itemMulti*=cramed["itemMulti"][item]
            for item in cramed["moneyMulti"].keys():
                if player.inventory.has(item) is not False:
                    item2 = player.inventory.get(item)
                    if item2.amount>0:
                        moneyMulti*=cramed["moneyMulti"][item]
            xValue = randint(1, randint(5,10))
            player.money+= moneyMulti*xValue
            if result[1] != 0:
                if player.inventory.has(str(result[1])) is not False:
                    toGiveItem = player.inventory.get(str(result[1]))
                    toGiveItem.amount+= itemMulti
                else:
                    toGiveItem = Item(result[1], result[0], itemMulti, False)
                    player.inventory.add(toGiveItem)
            if result[1] == 0:
                await ctx.send("You gained {0}{1}".format(str(xValue*moneyMulti), "ยง"))
            else:
                await ctx.send("You gained {0}{1} and found {2} {3}".format(str(xValue * moneyMulti), "ยง", itemMulti, toGiveItem.name))
        else:
            await ctx.send("No energy sowwy")
        player.save()

    @commands.Cog.listener()
    async def on_message(self, message):
        global lasttime
        if time.time() - lasttime > 10:
            lasttime = time.time()
            executeSomething()

def setup(bot):
    bot.add_cog(Economy(bot))

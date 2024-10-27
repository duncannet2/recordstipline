# Datetime
import discord, sqlite3, asyncio
from discord.ext import commands
from datetime import datetime
from requests.exceptions import HTTPError
from imgurpython import ImgurClient

# Variables
now = datetime.now()
client_id = ''

# Classes
class imageUtil:
    def imgur_upload(clientid, imageurl):
        client = ImgurClient(clientid, None)
        response = client.upload_from_url(imageurl, config=None, anon=True)
        return response['link']
# COG
class arrests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(description="Log an arrest")
    async def logarrest(self, ctx, suspect: str, *, charges, assisting=None):

        # Permissions
        role_ids = [1294213378448949268, 1293865705040646247, 1293865824808865834]
        roles = list(map(int, role_ids))

        # Checks for the roles
        has_role = any(role.id in roles for role in ctx.author.roles)
        if not has_role:

            # Respond
            await ctx.respond("**!** Warning: You do not have permission to use this command")
            print(f"{ctx.author} attempted to use '/logarrest' (ERROR: NO PERMISSION)")

            # Command Log
            commandlog = self.bot.get_channel()
            
            embed = discord.Embed(
                title = f"{ctx.author}: /logarrest",
                description = f'''Did not execute command due to: `No Permission/Role`''',
                color = discord.Color.red()
            )
            await commandlog.send(embed=embed)
            return
        
        # Connection & Cursor For Records Database
        conn = sqlite3.connect('databases/records.sqlite')
        cur = conn.cursor()

        # Check if Table Exists
        tableExists = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{suspect}'").fetchone() is not None
        
        if not tableExists:
            cur.execute(f"CREATE TABLE {suspect}(charges TEXT, arresting INTEGER, assisting TEXT, date TEXT, mugshot TEXT, logmsg INTEGER)")
        
        # Suspect & Charges are in it already cause suspect and charges is a variable in the function
        # Arresting
        arresting = ctx.author.id

        # - Assist
        if assisting == None:
            assist = "Nobody"
        else:
            assist = assisting
        
        # Date
        arrest_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Mugshot Definition and Upload
        channel = ctx.channel
        mugshotrequest = await ctx.respond("Send Mugshot Image")
        
        # Check
        def check(m):
            return m.author == ctx.author
        
        # Message Wait and Get Image
        msg = await self.bot.wait_for('message', check=check)
        image = msg.attachments[0].url

        # Upload to Imgur Through URL
        url = imageUtil.imgur_upload(client_id, image)

        # Define Embed
        embed = discord.Embed(title=f"Arrest Log: {suspect}",
            description=f'''
            **Charges:** `{charges}`
            **Arresting Personnel:** `{ctx.author.id}`
            **Assisting Personnel:** `{assist}`
            **Date:** `{arrest_date}`
            **Mugshot:**''',
            color=discord.Color.red())
        embed.set_image(url=url)

        # Log Channel
        logChannel = self.bot.get_channel()

        # Respond And Get Message ID of the Embed Message
        logMessage = await logChannel.send(f"{ctx.author.mention}", embed=embed)
        logID = logMessage.id

        # Cursor Execute, insert data and commit.
        cur.execute(f"INSERT INTO {suspect}(charges, arresting, assisting, date, mugshot, logmsg) VALUES (?, ?, ?, ?, ?, ?)", (charges, arresting, assist, arrest_date, url, logID))
        conn.commit()

        # Respond
        msg2 = await channel.send("Logged", reference=msg)

        # Log Command
        commandlog = self.bot.get_channel(1294458506099032164)
            
        embed = discord.Embed(
            title = f"{ctx.author}: /logarrest",
            description = f'''Command Successfully Executed''',
            color = discord.Color.green()
        )
        await commandlog.send(embed=embed)

        # Delete Messages
        await msg.delete()
        await asyncio.sleep(30) # - SLEEP for 30 seconds
        await msg2.delete()

        # Close
        return
        
    @commands.Cog.listener()
    async def on_message(self, message):
        # - I don't know what is needed here so nothing ig
        # Return
        return

class records(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(description="Find a Suspect Arrest (Most Recent Arrest)")
    async def findrecord(self, ctx, suspect: str):

        # Permissions
        role_ids = [1294213378448949268, 1293865705040646247, 1293865824808865834]
        roles = list(map(int, role_ids))

        # Checks for the roles
        has_role = any(role.id in roles for role in ctx.author.roles)
        if not has_role:

            # Respond
            await ctx.respond("**!** Warning: You do not have permission to use this command")
            print(f"{ctx.author} attempted to use '/findrecord' (ERROR: NO PERMISSION)")

            # Command Log
            commandlog = self.bot.get_channel()
            
            embed = discord.Embed(
                title = f"{ctx.author}: /findrecord",
                description = f'''Did not execute command due to: `No Permission/Role`''',
                color = discord.Color.red()
            )
            await commandlog.send(embed=embed)
            return
        
        # Cursor
        conn = sqlite3.connect('databases/records.sqlite')
        cur = conn.cursor()

        # Check if Table Exists
        tableExists = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{suspect}'").fetchone() is not None
        
        if not tableExists:
            await ctx.respond("**!** Warning: No Record Found")
            print(f"{ctx.author} attempted to use '/findrecord' (ERROR: NO RECORD FOUND)")
            return
        
        # Get Data
        charges = cur.execute(f"SELECT charges FROM {suspect}").fetchall()
        arresting = cur.execute(f"SELECT arresting FROM {suspect}").fetchall()
        assisting = cur.execute(f"SELECT assisting FROM {suspect}").fetchall()
        date = cur.execute(f"SELECT date FROM {suspect}").fetchall()
        mugshot = cur.execute(f"SELECT mugshot FROM {suspect}").fetchone()
        logmsg = cur.execute(f"SELECT logmsg FROM {suspect}").fetchall()

        # Define Embed
        embed = discord.Embed(
                title=f"**Record:** {suspect}",
                description=f'''''',
                color=discord.Color.red()
            )
        
        # Load Data
        for i in range(len(charges)):
            val = f'''**Charges:** `{charges[i][0]}`
            **Arresting Personnel:** `{arresting[i][0]}`
            **Assisting Personnel:** `{assisting[i][0]}`
            **Date:** `{date[i][0]}`
            **Recent Arrest Log:** `{logmsg[i][0]}`
            **Mugshot:**'''
            embed.add_field(name=f"{suspect}", value=val, inline=False)
            print("Record Found Adding")
        
        # Load Mugshot
        for a in range(len(mugshot)):
            url = imageUtil.imgur_upload(client_id, mugshot)
            embed.set_image(url=url)
            print("Mugshot Success")
        
        # Log Command
        commandlog = self.bot.get_channel()
            
        embed2 = discord.Embed(
            title = f"{ctx.author}: /findrecord",
            description = f'''Command Successfully Executed''',
            color = discord.Color.green()
        )

        # Mesages
        await commandlog.send(embed=embed2)
        await ctx.author.send(embed=embed)

        # End
        return
# Setup
def setup(bot):
    # - ADD ARRESTS COG
    bot.add_cog(arrests(bot))
    # - ADD RECORDS COG
    bot.add_cog(records(bot))

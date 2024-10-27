# Imports
import discord, os
from discord.ext import commands

class tiplineModal(discord.ui.Modal):
    def __init__(self, bot) -> None:
        super().__init__(title="Submit a tip")
        self.bot = bot

        self.add_item(discord.ui.InputText(label="Name of the tip"))
        self.add_item(discord.ui.InputText(label="Explain your tip in detail", style=discord.InputTextStyle.long))
    
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title=self.children[0].value, description=self.children[1].value)
        channel = self.bot.get_channel(1294478479383072860)
        await channel.send(embed=embed)
        await interaction.response.send_message("You have submitted a tip successfully", ephemeral=True)

class tiplineView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    @discord.ui.button(label="Submit a tip")
    async def submit_tip(self, button, interaction):
        await interaction.response.send_modal(tiplineModal(self.bot))

# COGs
class tipline(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        return
    
    @discord.slash_command(description="[ADMIN] The Tip Line Embed/Button Command!")
    async def tipline(self, ctx: discord.ApplicationContext):

        # Permissions
        role_ids = [1294451568547991573]
        roles = list(map(int, role_ids))

        # Checks for the roles
        has_role = any(role.id in roles for role in ctx.author.roles)
        if not has_role:

            # Respond
            await ctx.respond("**!** Warning: You do not have permission to use this command")
            print(f"{ctx.author} attempted to use '/tipline' (ERROR: NO PERMISSION)")

            # Command Log
            commandlog = self.bot.get_channel(1294458506099032164)
            
            embed = discord.Embed(
                title = f"{ctx.author}: /tipline",
                description = f'''Did not execute command due to: `No Permission/Role`''',
                color = discord.Color.red()
            )
            await commandlog.send(embed=embed)
            return
        
        # Embed

        title = "Submit a anonymous tip"
        desc = "Submit a tip to Roblox's United States Marshals Service to help fight our violent crime! Your data will not be given unless you want."
        color = discord.Color.green()

        # Log Command
        commandlog = self.bot.get_channel(1294458506099032164)
            
        embed2 = discord.Embed(
            title = f"{ctx.author}: /tipline",
            description = f'''Command Successfully Executed''',
            color = discord.Color.green()
        )

        # Log Message
        await commandlog.send(embed=embed2)
        
        # Embed
        embed = discord.Embed(title=title, description=desc, color=color)
        await ctx.send(embed=embed, view=tiplineView(self.bot))
        await ctx.respond("Done", ephemeral=True)

# SETUP
def setup(bot):
    bot.add_cog(tipline(bot))
import discord
from discord.ext import commands
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# =========================

# CHANGE PREFIX
bot = commands.Bot(command_prefix="$", intents=intents)

# CHANGE TOKEN
token = "YOUR TOKEN HERE"

# CHANGE ROLE MAPPING
# old_server_id: The ID of the server where the old role is located
# old_role_id: The ID of the old role
# new_role_id: The ID of the new role

# You will need a new mapping for each role you want to transfer.

rolemap = [
    {
        'old_server_id': '1246241632441991259',
        'old_role_id': '1246241727732518964',
        'new_role_id': '1246241790059876404'
    }
]

# =========================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}") # Print the bot's username when the bot is ready
    bot.add_view(MyView()) # Forces the bot to start listening for button events at startup

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Forces the bot to continue listening for button events for as long as it is running

    # Create a button that will transfer the roles
    @discord.ui.button(label="Transfer Now", custom_id="transferbutton", style=discord.ButtonStyle.primary) 
    async def button_callback(self, interaction, button):
        # Checks if the button pressed is the transfer button
        if button.custom_id == "transferbutton":
            # Creates an empty list to store what roles were transferred, if any
            transferredroles = []
            # Loops through each role mapping
            for mapping in rolemap:
                # Fetches the new server, new role, old server, and old role
                new_server = interaction.guild
                new_role = new_server.get_role(int(mapping['new_role_id']))
                old_server = bot.get_guild(int(mapping['old_server_id']))
                old_role = old_server.get_role(int(mapping['old_role_id']))
                # Fetches the guild-specific member object from the old server and new server
                old_server_member = await old_server.fetch_member(interaction.user.id)
                new_server_member = await new_server.fetch_member(interaction.user.id)
                # Checks to see if the user has the given role in the old server
                if old_role in old_server_member.roles:
                    # If so, check if the role was already transferred
                    if new_role not in new_server_member.roles:
                        # If so, transfer the role
                        await new_server_member.add_roles(new_role)
                        # Add that role to the list of transferred roles
                        transferredroles.append(f"{old_role.name} from {old_server.name}")
            # Once all roles have been checked...
            # If the list of transferred roles has anything in it
            if len(transferredroles) != 0:
                # Draft an embed to show what roles were transferred
                successembed = discord.Embed(title="Role Transfer Successful", description=f"Roles transferred:")
                # Add each transferred role to the embed
                for role in transferredroles:
                    successembed.add_field(name="Role", value=role)
                # Send the embed to the user
                await interaction.response.send_message(embed=successembed, ephemeral=True)
            # If the list of transferred roles is empty
            else:
                # Send a message to the user that no roles were transferred
                await interaction.response.send_message("You do not have any roles to transfer", ephemeral=True)

@bot.command()
async def display(ctx):
    # If the user has the manage_guild permission, send the embed with the button
    if ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(title="Transfer your roles!", description="Press the button below to transfer your roles from the old servers to the new server.")
        await ctx.send(embed=embed, view=MyView())

# Run the bot
bot.run(token)

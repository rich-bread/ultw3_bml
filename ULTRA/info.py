import json
import discord
from discord.ext import commands
from discord import app_commands

class Info(commands.Cog):
    def __init__(self, client:discord.Client):
        self.client = client

    @app_commands.command(name='info')
    async def info(self, interaction:discord.Interaction):
        pass


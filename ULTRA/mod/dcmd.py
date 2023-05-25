import discord

class CustomEmbed():
    def __init__(self) -> None:
        pass

    #通常
    def default(self, title:str, description:str, color=0x0067C0) -> discord.Embed:
        embed=discord.Embed(title=title,description=description, color=color)
        return embed

    #完了
    def success(self, description:str) -> discord.Embed:
        embed=discord.Embed(description=description,color=0x2CA02C)
        embed.set_author(name='完了', icon_url='https://icons.veryicon.com/png/o/miscellaneous/8atour/success-35.png')
        return embed

    #エラー
    def error(self, description:str) -> discord.Embed:
        embed=discord.Embed(description=description,color=0xEC1A2E)
        embed.set_author(name='エラー', icon_url='https://icon-library.com/images/error-icon-4_19035.png')
        return embed
    
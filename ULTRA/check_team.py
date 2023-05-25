import json
import discord
from discord.ext import commands
from discord import app_commands

from ULTRA.ercl.myerror import MyError
from ULTRA.func.tmfn import TeamFunc
from ULTRA.func.dbfn import DatabaseFunc
from ULTRA.mod.dcmd import CustomEmbed

j = open('ULTRA/data/cmds_team.json','r',encoding='utf-8')
cmdj = json.load(j)
cmd_info = cmdj['commands']['check_team']
cmd_name = cmd_info['name']
cmd_description = cmd_info['description']

class CheckTeam(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.teamfunc = TeamFunc()
        self.dbfunc = DatabaseFunc()
        self.dcembed = CustomEmbed()

    @app_commands.command(name=cmd_name, description=cmd_description)
    @app_commands.guild_only()
    async def check_team(self, interaction:discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)

            author = interaction.user #コマンド実行者

            #--チーム情報確認処理--
            raw_teamdata = await self.dbfunc.get_teamdata(leader_id=author.id)
            teamdata = raw_teamdata[0]
            #[ERROR] チーム情報が存在しない場合
            if not teamdata:
                error = "いずれかのチームのリーダーであることが確認できませんでした。チーム情報登録を行ってから再度実行してください"
                raise MyError(error)

            #--平均XP計算処理--
            members = teamdata[4:8]
            xps = []
            for mid in members:
                raw_userdata = await self.dbfunc.get_userdata(user_id=mid)
                userdata = raw_userdata[0]
                if not userdata: continue
                xps.append(userdata[9])
            xpavg = self.teamfunc.cal_averagexp(*xps)
            
            #--閲覧用チーム情報作成処理--
            viewdata = f"チーム名: {teamdata[1]}\n"+\
                        f"リーグ: {teamdata[3]}\n"+\
                        f"平均XP: {xpavg}\n"+\
                        f"リーダー: <@{teamdata[4]}>\n"+\
                        f"メンバー①: <@{teamdata[5]}>\n"+\
                        f"メンバー②: <@{teamdata[6]}>\n"+\
                        f"メンバー③: <@{teamdata[7]}>\n"
            if teamdata[8] != '': viewdata+"\nメンバー④: <@"+teamdata[8]+">"

        except MyError as e:
            await interaction.followup.send(content=author.mention, embed=self.dcembed.error(str(e)))

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"+str(e)
            print(error)
            await interaction.followup.send(content=author.mention, embed=self.dcembed.error(error))

        else:
            title = f"{teamdata[1]}のチーム情報"
            await interaction.followup.send(content=author.mention, embed=self.dcembed.default(title=title,description=viewdata))
        

async def setup(client: commands.Bot):
    await client.add_cog(CheckTeam(client))
    
import json
import discord
from discord.ext import commands
from discord import app_commands

from ULTRA.ercl.myerror import MyError
from ULTRA.func.cmfn import CommonFunc
from ULTRA.func.dbfn import DatabaseFunc
from ULTRA.mod.dcmd import CustomEmbed
from ULTRA.mod.tmmd import TimeModule

j = open('ULTRA/data/cmds_team.json','r',encoding='utf-8')
cmdj = json.load(j)
cmd_info = cmdj['commands']['update_team']
cmd_name = cmd_info['name']
cmd_description = cmd_info['description']
cmd_describe = cmdj['describe']
cmd_choices_league = [app_commands.Choice(name=c["name"],value=c["value"]) for c in cmdj['choices']['league']]

class UpdateTeam(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cmnfunc = CommonFunc()
        self.dbfunc = DatabaseFunc()
        self.tmmod = TimeModule()
        self.dcembed = CustomEmbed()

    @app_commands.command(name=cmd_name, description=cmd_description)
    @app_commands.describe(team_name=cmd_describe['team_name'], league=cmd_describe['league'])
    @app_commands.choices(league=cmd_choices_league)
    async def apply_team(self, interaction:discord.Interaction, team_name:str=None, league:app_commands.Choice[int]=None):
        try:
            await interaction.response.defer(thinking=True)

            author = interaction.user #コマンド実行者
            now = self.tmmod.dt2str(self.tmmod.change_timezone(interaction.created_at)) #現在日時

            #--チーム情報確認処理--
            raw_team_data = await self.dbfunc.get_teamdata(author.id)
            team_data = raw_team_data[0]
            #[ERROR] チーム情報が存在しない場合
            if not team_data:
                error = "いずれかのチームのリーダーであることが確認できませんでした。チーム情報登録を行ってから再度実行してください"
                raise MyError(error)
            
            #--リーグ確定処理--
            if league != None: league = league.name

            #--チーム情報作成処理--
            post_data = self.cmnfunc.create_postdata(name='team', org_data=team_data, team_name=team_name, league=league, updated_at=now)
            
            #--POST--
            await self.dbfunc.post_teamdata(author.id, post_data, is_update=True)
            await self.dbfunc.log_teamdata(author.id, post_data, is_update=True)
        
        except MyError as e:
            await interaction.followup.send(content=author.mention, embed=self.dcembed.error(str(e)))

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"+str(e)
            print(error)
            await interaction.followup.send(content=author.mention,embed=self.dcembed.error(error))

        else:
            success = f"リーダー{author.mention}のチーム情報更新を受け付けました。データベースからの完了通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.dcembed.success(success))


async def setup(client:commands.Bot):
    await client.add_cog(UpdateTeam(client))

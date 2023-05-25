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
cmd_info = cmdj['commands']['apply_team']
cmd_name = cmd_info['name']
cmd_description = cmd_info['description']
cmd_describe = cmdj['describe']
cmd_choices_league = [app_commands.Choice(name=c["name"],value=c["value"]) for c in cmdj['choices']['league']]

class ApplyTeam(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cmnfunc = CommonFunc()
        self.dbfunc = DatabaseFunc()
        self.tmmod = TimeModule()
        self.dcembed = CustomEmbed()

    @app_commands.command(name=cmd_name, description=cmd_description)
    @app_commands.describe(team_name=cmd_describe['team_name'], league=cmd_describe['league'],
                           member1=cmd_describe['member1'], member2=cmd_describe['member2'], member3=cmd_describe['member3'], member4=cmd_describe['member4'])
    @app_commands.choices(league=cmd_choices_league)
    async def apply_team(self, interaction:discord.Interaction, team_name:str, league:app_commands.Choice[int], 
                         member1:discord.Member, member2:discord.Member, member3:discord.Member, member4:discord.Member=None):
        try:
            await interaction.response.defer(thinking=True)

            author = interaction.user #コマンド実行者
            now = self.tmmod.dt2str(self.tmmod.change_timezone(interaction.created_at)) #現在日時

            #--チーム情報確認処理--
            raw_teamdata = await self.dbfunc.get_teamdata(author.id)
            teamdata = raw_teamdata[0]
            if not teamdata: 
                apptype = 0
                apptype_str = "登録"
                season_id = ""
                created_at = now
            else:
                apptype = 1
                apptype_str = "更新"
                season_id = None
                created_at = None

            #--ユーザ情報確認処理--
            members = [author,member1,member2,member3,member4]
            for member in members:
                if member != None:
                    userdata = (await self.dbfunc.get_userdata(str(member.id)))[0]
                    #[ERROR] 指定ユーザの情報がデータベースに登録されていない場合
                    if not userdata:
                        error = f"指定ユーザ{member.mention}の情報がデータベースに登録されていません。ユーザ情報を登録行ってからチーム情報登録・更新を行ってください"
                        raise MyError(error)
                    
            if member4 != None: member4id = str(member4.id)
            else: member4id = ''
                    
            #--チーム情報作成処理--
            post_data = self.cmnfunc.create_postdata(name='team', org_data=teamdata, team_name=team_name, season_id=season_id, league=league.name, 
                                                    leader=str(author.id), member1=str(member1.id), member2=str(member2.id), member3=str(member3.id), member4=member4id,
                                                    created_at=created_at, updated_at=now)
            
            #--POST--
            await self.dbfunc.post_teamdata(author.id, post_data, apptype)
            await self.dbfunc.log_teamdata(author.id, post_data)
        
        except MyError as e:
            await interaction.followup.send(content=author.mention, embed=self.dcembed.error(str(e)))

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"+str(e)
            print(error)
            await interaction.followup.send(content=author.mention,embed=self.dcembed.error(error))

        else:
            success = f"リーダー{author.mention}のチーム情報{apptype_str}を受け付けました。データベースからの完了通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.dcembed.success(success))


async def setup(client:commands.Bot):
    await client.add_cog(ApplyTeam(client))

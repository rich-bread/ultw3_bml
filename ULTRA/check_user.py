import json
import discord
from discord.ext import commands
from discord import app_commands

from ULTRA.ercl.myerror import MyError
from ULTRA.func.dbfn import DatabaseFunc
from ULTRA.func.uefn import UserFunc
from ULTRA.mod.dcmd import CustomEmbed
from ULTRA.mod.tmmd import TimeModule

j = open('ULTRA/data/cmds_user.json','r',encoding='utf-8')
cmdj = json.load(j)
cmd_info = cmdj['commands']['check_user']
cmd_name = cmd_info['name']
cmd_description = cmd_info['description']
cmd_describe = cmdj['describe']

class CheckUser(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.userfunc = UserFunc()
        self.dbfunc = DatabaseFunc()
        self.tmmod = TimeModule()
        self.dcembed = CustomEmbed()

    @app_commands.command(name=cmd_name, description=cmd_description)
    @app_commands.describe(user=cmd_describe['user'])
    @app_commands.guild_only()
    async def check_user(self, interaction:discord.Interaction, user:discord.User):
        try:
            await interaction.response.defer(ephemeral=True,thinking=True)

            author = interaction.user #コマンド実行者
            
            #--ユーザ情報確認処理--
            raw_userdata = await self.dbfunc.get_userdata(user_id=user.id)
            userdata = raw_userdata[0]
            #[ERROR] 指定ユーザの情報が存在しない場合
            if not userdata:
                error = f"指定ユーザ:{user.mention}の情報がデータベースに登録されていません。ユーザ情報登録を行ってから再度実行してください"
                raise MyError(error)

            #--ユーザ情報閲覧資格確認処理(他ユーザ指定時)-- ※指定ユーザとコマンド実行者が同じ場合はskip
            if author != user:
                raw_teamdata = await self.dbfunc.get_teamdata(leader_id=author.id)
                teamdata = raw_teamdata[0]
                #[ERROR] リーダーではない場合
                if not teamdata:
                    error = "いずれかのチームのリーダーであることが確認できませんでした。本人以外のユーザ情報を確認する場合は指定ユーザが所属するチームのリーダーである必要があります"
                    raise MyError(error)

                match_ids = [d for d in teamdata if str(user.id) == d]
                #[ERROR] 指定ユーザがリーダーのチームに所属していない場合
                if len(match_ids) < 1:
                    error = f"指定ユーザ{user.mention}はリーダー{author.mention}のチームに所属していません。本人以外のユーザ情報を閲覧する場合は指定ユーザが所属するチームのリーダーである必要があります"
                    raise MyError(error)

            #--閲覧用ユーザ情報作成処理--
            viewdata =  f"名前: {userdata[1]}\n"+\
                        f"フレンドコード: {userdata[2]}\n"+\
                        f"TwitterID: {userdata[3]}\n"+\
                        f"ポジション: {userdata[6]}\n"+\
                        f"持ちブキ: {userdata[7]}\n"+\
                        f"最高XP(エリア): {userdata[8]}\n"+\
                        f"最高XP(全ルール): {userdata[9]}\n"+\
                        f"ウデマエ画像1: {userdata[10]}\n"+\
                        f"ウデマエ画像2: {userdata[11]}\n"
            
        except MyError as e:
            await interaction.followup.send(content=author.mention, embed=self.dcembed.error(str(e)))

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"+str(e)
            print(error)
            await interaction.followup.send(content=author.mention, embed=self.dcembed.error(error))

        else:
            title = f"{str(user)}のユーザ情報"
            await interaction.followup.send(content=author.mention, embed=self.dcembed.default(title=title,description=viewdata))


async def setup(client: commands.Bot):
    await client.add_cog(CheckUser(client))
    
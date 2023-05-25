import json
import discord
from discord.ext import commands
from discord import app_commands

from ULTRA.ercl.myerror import MyError
from ULTRA.func.dbfn import DatabaseFunc
from ULTRA.mod.dcmd import CustomEmbed
from ULTRA.mod.tmmd import TimeModule

j = open('ULTRA/data/cmds_entry.json','r',encoding='utf-8')
cmdj = json.load(j)
cmd_info = cmdj['commands']['entry_draft']
cmd_name = cmd_info['name']
cmd_description = cmd_info['description']

##非常設コマンド##
class EntryDraft(commands.Cog):
    def __init__(self, client:discord.Client):
        self.client = client
        self.dbfunc = DatabaseFunc()
        self.tmmod = TimeModule()
        self.dcembed = CustomEmbed()

    @app_commands.command(name=cmd_name, description=cmd_description)
    @app_commands.guild_only()
    async def entry_draft(self, interaction:discord.Interaction):
        try:
            await interaction.response.defer(thinking=True)

            author = interaction.user #コマンド実行者
            now = self.tmmod.dt2str(self.tmmod.change_timezone(interaction.created_at)) #現在日時

            #--大会情報確認処理--
            tournament_data = await self.dbfunc.get_valid_tournament_data()
            #[ERROR] 受付中の大会が存在しない場合
            if not tournament_data:
                error = "現在参加申請を行える大会がありません。受付期間が開始し次第、参加申請を行ってください"
                raise MyError(error)
            
            #--ユーザ情報確認処理--
            raw_user_data = await self.dbfunc.get_userdata(user_id=author.id)
            user_data = raw_user_data[0]
            #[ERROR] 指定ユーザの情報が存在しない場合
            if not user_data: 
                error = "このコマンドはユーザ情報登録済みのユーザのみが使用できます。ユーザ情報登録を行ってから、このコマンドを実行してください"
                raise MyError(error)
            #[ERROR] 指定ユーザの情報にウデマエ画像がない場合
            if user_data[10] == '':
                error = f"指定ユーザ:<@{author.id}>のウデマエ画像が登録されていません。ウデマエ確認機能追加の為、ウデマエ画像を提出する必要があります"
                raise MyError(error)
            #[ERROR] 指定ユーザの最終更新日時が受付期間よりも前の場合
            updated_at = self.tmmod.str2dt(user_data[13])
            open_at = self.tmmod.str2dt(tournament_data[3])
            if updated_at < open_at:
                error = f"指定ユーザ:<@{author.id}>のウデマエ画像更新が確認できませんでした。ウデマエ確認機能追加の為、大会参加期間中に最新の最高XP及びウデマエ画像を提出する必要があります ※有効なウデマエ画像についてはルールブックを確認してください"
                raise MyError(error)
            
            #--POST処理--
            await self.dbfunc.log_entry_draft(entered_at=now, tournament_name=tournament_data[1], tournament_id=tournament_data[2], user_name=user_data[1], author_id=author.id)
        
        except MyError as e:
            await interaction.followup.send(content=author.mention, embed=self.dcembed.error(description=str(e)))

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"+str(e)
            print(error)
            await interaction.followup.send(content=author.mention, embed=self.dcembed.error(error))

        else:
            #--完了送信処理--
            success = f"大会:`{tournament_data[1]}`への参加申請を受け付けました。データベースからの参加受付通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.dcembed.success(success))


async def setup(client: commands.Bot):
    await client.add_cog(EntryDraft(client))

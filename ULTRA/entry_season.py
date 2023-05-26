import json
import discord
from discord.ext import commands
from discord import app_commands

from ULTRA.ercl.myerror import MyError
from ULTRA.func.cmfn import CommonFunc
from ULTRA.func.dbfn import DatabaseFunc
from ULTRA.func.uefn import UserFunc
from ULTRA.func.tmfn import TeamFunc
from ULTRA.mod.dcmd import CustomEmbed
from ULTRA.mod.tmmd import TimeModule

j = open('ULTRA/data/cmds_entry.json','r',encoding='utf-8')
cmdj = json.load(j)
cmd_info = cmdj['commands']['entry_season']
cmd_name = cmd_info['name']
cmd_description = cmd_info['description']

class EntrySeason(commands.Cog):
    def __init__(self, client:discord.Client):
        self.client = client
        self.cmnfunc = CommonFunc()
        self.userfunc = UserFunc()
        self.dbfunc = DatabaseFunc()
        self.teamfunc = TeamFunc()
        self.tmmod = TimeModule()
        self.dcembed = CustomEmbed()

    @app_commands.command(name=cmd_name, description=cmd_description)
    @app_commands.guild_only()
    async def entry_season(self, interaction:discord.Interaction):
        try:
            await interaction.response.defer(thinking=True)

            author = interaction.user #コマンド実行者
            now = self.tmmod.dt2str(self.tmmod.change_timezone(interaction.created_at)) #現在日時

            #--シーズン情報確認処理--
            seasondata = await self.dbfunc.get_valid_season_data()
            #[ERROR] 受付中のシーズンが存在しない場合
            if not seasondata:
                error = "現在参加申請を行えるシーズンがありません。受付期間が開始し次第、参加申請を行ってください"
                raise MyError(error)
            
            #--チーム情報確認処理--
            raw_teamdata = await self.dbfunc.get_teamdata(leader_id=author.id)
            teamdata = raw_teamdata[0]
            #[ERROR] コマンド実行者がリーダーのチームの情報が存在しない場合
            if not teamdata:
                error = "いずれかのチームのリーダーであることが確認できませんでした。参加申請を行う為には、コマンド実行者がリーダーとして登録されているチームの情報が必要です。チーム情報登録後、再度参加申請を行ってください"
                raise MyError(error)
            
            #--平均XP確認処理--
            members = teamdata[4:8]
            xps = []
            for mid in members:
                raw_userdata = await self.dbfunc.get_userdata(user_id=mid)
                userdata = raw_userdata[0]
                if not userdata: continue
                xps.append(userdata[9])
            xpavg = self.teamfunc.cal_averagexp(*xps)
            xpb = self.teamfunc.check_league_entry(teamdata[3], xpavg)
            #[ERROR] 指定リーグのXP上限より平均XPが上回った場合
            if xpb == False:
                error = "チームの平均XPが参加希望リーグのXP上限を超過しています。チーム平均XPを確認の上、参加希望リーグを変更し改めて参加申請を行ってください"
                raise MyError(error)
            
            #--ユーザ情報確認処理--
            for mid in members:
                raw_userdata = await self.dbfunc.get_userdata(user_id=mid)
                userdata = raw_userdata[0]
                if not userdata: continue
                #[ERROR] 指定ユーザの情報にウデマエ画像がない場合
                if userdata[10] == '':
                    error = f"指定ユーザ:<@{mid}>のウデマエ画像が登録されていません。ウデマエ確認機能追加の為、ウデマエ画像を提出する必要があります"
                    raise MyError(error)
                
                #[ERROR] 指定ユーザの最終更新日時が受付期間よりも前の場合
                updated_at = self.tmmod.str2dt(userdata[13])
                open_at = self.tmmod.str2dt(seasondata[3])
                if updated_at < open_at:
                    error = f"指定ユーザ:<@{mid}>のウデマエ画像更新が確認できませんでした。ウデマエ確認機能追加の為、シーズン毎に最新の最高XP及びウデマエ画像を提出する必要があります ※有効なウデマエ画像についてはルールブックを確認してください"
                    raise MyError(error)
            
            #--チーム情報作成処理--
            post_data = self.cmnfunc.create_postdata(name='team', org_data=teamdata, season_id=seasondata[2], updated_at=now)
            
            #--POST処理--
            await self.dbfunc.post_teamdata(leader_id=author.id, post_data=post_data, is_update=True)
            await self.dbfunc.log_entry_season(entered_at=now, author_id=author.id, season_name=seasondata[1], season_id=seasondata[2], team_name=teamdata[1])
        
        except MyError as e:
            await interaction.followup.send(content=author.mention, embed=self.dcembed.error(description=str(e)))

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"+str(e)
            print(error)
            await interaction.followup.send(content=author.mention, embed=self.dcembed.error(error))

        else:
            #--完了送信処理--
            success = f"シーズン:`{seasondata[1]}`への参加申請を受け付けました。データベースからの参加受付通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.dcembed.success(success))

async def setup(client: commands.Bot):
    await client.add_cog(EntrySeason(client))

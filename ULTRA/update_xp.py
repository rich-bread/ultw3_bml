import json
import discord
from discord.ext import commands
from discord import app_commands

from ULTRA.ercl.myerror import MyError
from ULTRA.func.cmfn import CommonFunc
from ULTRA.func.dbfn import DatabaseFunc
from ULTRA.func.uefn import UserFunc
from ULTRA.mod.dcmd import CustomEmbed
from ULTRA.mod.tmmd import TimeModule

j = open('ULTRA/data/cmds_user.json','r',encoding='utf-8')
cmdj = json.load(j)
cmd_info = cmdj['commands']['update_xp']
cmd_name = cmd_info['name']
cmd_description = cmd_info['description']
cmd_describe = cmdj['describe']
cmd_config = cmdj['config']

class UpdateXP(commands.Cog):
    def __init__(self, client:discord.Client):
        self.client = client
        self.cmnfunc = CommonFunc()
        self.userfunc = UserFunc()
        self.dbfunc = DatabaseFunc()
        self.tmmod = TimeModule()
        self.dcembed = CustomEmbed()

    @app_commands.command(name=cmd_name, description=cmd_description)
    @app_commands.describe(user=cmd_describe['user'], splatzone_xp=cmd_describe['splatzone_xp'], allmode_xp=cmd_describe['allmode_xp'],
                           image1=cmd_describe["image1"], image2=cmd_describe["image2"])
    @app_commands.guild_only
    async def update_xp(self, interaction:discord.Interaction, user:discord.Member, splatzone_xp:int, allmode_xp:int, image1:discord.Attachment, image2:discord.Attachment=None) -> None:
        try:
            await interaction.response.defer(thinking=True)

            author = interaction.user #コマンド実行者
            now = self.tmmod.dt2str(self.tmmod.change_timezone(interaction.created_at)) #現在日時

            raw_userdata = await self.dbfunc.get_userdata(user.id)
            userdata = raw_userdata[0]
            if not userdata: 
                error = "このコマンドはユーザ情報登録済みのユーザのみが使用できます。ユーザ情報登録を行ってから、このコマンドを実行してください"
                raise MyError(error)
            
            #--ウデマエ画像確認処理--
            imgl = [image1, image2]
            ciwhl = [[img.width, img.height] for img in imgl if img != None]
            for ciwh in ciwhl:
                #[ERROR] 添付ファイルが画像ではなかった場合
                if None in ciwh:
                    raise MyError("添付されたファイルは画像ではありません。ウデマエ画像は画像形式のファイルで、BomuLeagueの提出規格に沿った画像を提出してください")
                #[ERROR] 添付画像が1920×1080のゲーム内画像であった場合
                if ciwh[0]==1920 and ciwh[1]==1080:
                    raise MyError("添付されたウデマエ画像がゲーム内画像であると判定されました。ウデマエ画像はBomuLeagueの提出規格に沿った画像を提出してください")
                
            #--ウデマエ画像投稿処理--
            dbchannel = await self.client.fetch_channel(cmd_config['xp_image'])
            img_urll = [await self.dbfunc.post_xpimage(dbchannel, user, img) if img != None else '' for img in imgl]

            #--ユーザ情報作成処理--
            post_data = self.cmnfunc.create_postdata(name='user', org_data=userdata, splatzone_xp=splatzone_xp, allmode_xp=allmode_xp, image1=img_urll[0], image2=img_urll[1], updated_at=now)
            
            #--POST--
            await self.dbfunc.post_userdata(user.id, post_data, is_update=True)
            await self.dbfunc.log_userdata(author.id, post_data)

        except MyError as e:
            await interaction.followup.send(content=author.mention, embed=self.dcembed.error(str(e)))

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"+str(e)
            print(error)
            await interaction.followup.send(content=author.mention,embed=self.dcembed.error(error))

        else:
            success = f"{author.mention}から{user.mention}のXP更新を受け付けました。データベースからの完了通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.dcembed.success(success))


async def setup(client:commands.Bot):
    await client.add_cog(UpdateXP(client))

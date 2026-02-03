import discord
from discord import app_commands
from discord.ext import commands
import service.AudioService as AudioService
from exception.Exception import *
from manager.GuildManager import GuildManager

class leaveCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()

    @app_commands.command(name = "leave", description = "イントロクイズを終了します")
    async def leave(self, interaction: discord.Interaction):

        try:
            await AudioService.leave(interaction)
        except(
            UserNotJoinedException
        ) as e:
            embed = discord.Embed(title="エラー",description=e,color=0xff1100)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        except(
            AlreadyJoinedException
        ) as e:
            pass

        qm = GuildManager.get_instance().get_quiz_manager(interaction.guild.id)
        qm.end_quiz()
        GuildManager.get_instance().delete_quiz_manager(interaction.guild.id)

            
async def setup(bot: commands.Bot):
    await bot.add_cog(leaveCommand(bot))
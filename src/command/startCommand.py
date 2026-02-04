import discord
from discord import app_commands
from discord.ext import commands
import service.AudioService as AudioService
from exception.Exception import *
from manager.GuildManager import GuildManager

class startCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()

    @app_commands.command(name = "start", description = "イントロクイズを開始します")
    @app_commands.describe(length="問題数を入力してください")
    async def start(self, interaction: discord.Interaction, length:int):

        if(length <= 0):
            embed = discord.Embed(title="エラー",description="問題数は1以上を指定してください。",color=0xff1100)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if(length > len(AudioService.SONG_LIST)):
            embed = discord.Embed(title="エラー",description=f"問題数は最大{len(AudioService.SONG_LIST)}です。",color=0xff1100)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await AudioService.join(interaction, length)
        except(
            UserNotJoinedException
        ) as e:
            embed = discord.Embed(title="エラー",description=e,color=0xff1100)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        quiz_manager = GuildManager.get_instance().get_quiz_manager(interaction.guild.id)
        if(quiz_manager.is_quiz_active):
            embed = discord.Embed(title="エラー",description="すでにクイズが開始されています。",color=0xff1100)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(title="イントロクイズ開始",description=f"イントロクイズを開始しました！問題数: {length}問\n答えは{interaction.channel.mention}に入力してください！",color=0x00ff00)
        await interaction.response.send_message(embed=embed)

        quiz_manager.start_quiz()
        await AudioService.play(interaction.guild, quiz_manager.start_quiz_song()[0], self.bot)

            
async def setup(bot: commands.Bot):
    await bot.add_cog(startCommand(bot))
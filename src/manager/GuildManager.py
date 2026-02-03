# サーバーごとにクイズ中か/クイズを構成するyoutubeURLたち/今何問目/参加者のポイントなどを管理するクラス
from .QuizManager import QuizManager
from exception.Exception import *

class GuildManager:
    __instance = None

    @staticmethod
    def get_instance():
        if GuildManager.__instance is None:
            GuildManager()
        return GuildManager.__instance
    
    def __init__(self):
        if GuildManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            GuildManager.__instance = self
        
        self.guild_quiz_managers = {}

    def get_quiz_manager(self, guild_id):
        if not self.exists_quiz_manager(guild_id):
            raise QuizManagerNotExistException()
        return self.guild_quiz_managers[guild_id]
    
    def exists_quiz_manager(self, guild_id):
        return guild_id in self.guild_quiz_managers
    
    def create_quiz_manager(self, guild_id, youtube_urls, target_channel_id=None):
        if self.exists_quiz_manager(guild_id):
            return self.guild_quiz_managers[guild_id]
        quiz_manager = QuizManager(youtube_urls, target_channel_id)
        self.guild_quiz_managers[guild_id] = quiz_manager
        return quiz_manager
    
    def delete_quiz_manager(self, guild_id):
        if self.exists_quiz_manager(guild_id):
            del self.guild_quiz_managers[guild_id]



# クイズ中か/問題を再生中か/クイズを構成するyoutubeURLたち/今何問目/参加者のポイントなどを管理するクラス
from collections import defaultdict
import discord

class QuizManager:

    def __init__(self, youtube_urls, target_channel=None):
        self.is_quiz_active = False
        self.is_question_playing = False
        self.youtube_urls = youtube_urls
        self.current_question_index = 0
        self.target_channel = target_channel
        self.participant_points = defaultdict(int)

    def start_quiz(self):
        self.is_quiz_active = True
        self.current_question_index = 0
        self.participant_points.clear()

    def start_quiz_song(self):
        if(self.is_question_playing):
            return None
        self.is_question_playing = True
        return self.youtube_urls[self.current_question_index]
    
    def add_participant_point(self, user_id):
        self.participant_points[user_id] += 1

    async def end_quiz_song(self):
        self.is_question_playing = False
        self.current_question_index += 1
        if self.current_question_index >= len(self.youtube_urls):
            await self.end_quiz()

    async def end_quiz(self):
        self.is_quiz_active = False
        self.is_question_playing = False
        self.current_question_index = 0
        points = dict(self.participant_points)
        # 上位3名を取得
        sorted_points = sorted(points.items(), key=lambda x: x[1], reverse=True)
        title = "クイズ終了！結果発表！"
        embed = ""
        if(len(sorted_points) == 0):
            embed += "参加者がいませんでした。"
        else:
            for i, (user_id, point) in enumerate(sorted_points[:3], start=1):
                embed += f"{i}位: <@{user_id}> - {point}ポイント\n"
        if self.target_channel is not None:
            await self.target_channel.send(embed=discord.Embed(title=title, description=embed))
        self.participant_points.clear()
        

# configファイルのSONG_LISTから、指定された数の曲をランダムに選びシャッフルして返す
import random
from config.Config import SONG_LIST

def get_random_songs(num_songs):
    selected_songs = random.sample(SONG_LIST, min(num_songs, len(SONG_LIST)))
    random.shuffle(selected_songs)
    return selected_songs
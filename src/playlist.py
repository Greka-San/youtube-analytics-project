from googleapiclient.discovery import build
import datetime
import isodate
import os


api_key: str = os.getenv('API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)
channel_id = 'UCwHL6WHUarjGfUM_586me8w'


class PlayList:
    def __init__(self, playlist_id):
        self.playlist_id = playlist_id
        self.playlist_info = youtube.playlists().list(id=self.playlist_id,
                                                      part='snippet',
                                                      ).execute()
        self.title = self.playlist_info['items'][0]['snippet']['title']
        self.url = f'https://www.youtube.com/playlist?list={playlist_id}'

        self.playlist_videos = youtube.playlistItems().list(playlistId=self.playlist_id,
                                                            part='contentDetails',
                                                            maxResults=50,
                                                            ).execute()
        # получить все id видеороликов из плейлиста
        video_ids: list[str] = [video['contentDetails']['videoId'] for video in self.playlist_videos['items']]

        self.video_response = youtube.videos().list(part='contentDetails,statistics',
                                                    id=','.join(video_ids)
                                                    ).execute()

    @property
    def total_duration(self):
        '''возвращает объект класса datetime.timedelta с суммарной длительность плейлиста'''

        total_duration = datetime.timedelta()

        for video in self.video_response['items']:
            # YouTube video duration is in ISO 8601 format
            iso_8601_duration = video['contentDetails']['duration']
            duration = isodate.parse_duration(iso_8601_duration)
            total_duration += duration

        return total_duration

    def show_best_video(self):
        '''Возвращает ссылку на самое популярное видео из плейлиста (по количеству лайков)'''
        max_likes = 0
        video_id = ''
        for video in self.video_response['items']:
            like_count = int(video['statistics']['likeCount'])
            if like_count > max_likes:
                max_likes = like_count
                video_id = video['id']

        return f'https://youtu.be/{video_id}'

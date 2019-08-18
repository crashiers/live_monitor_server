import asyncio
import logging

from bilibili_api.bilibili_api import BilibiliAPI
from config import config
from daemon import VideoDaemon


class Bilibili(VideoDaemon):
    def __init__(self, user_config):
        super().__init__(user_config)
        self.API = BilibiliAPI()
        self.logger = logging.getLogger('run.bilibili')
        self.old_video_num = None
        self.old_article_num = None

    async def check(self):
        try:
            self.old_video_num = await self.API.get_video_num(self.target_id)
            while True:
                video_num = await self.API.get_video_num(self.target_id)
                if video_num > self.old_video_num:
                    self.logger.info('Found A new video')
                    await asyncio.sleep(10)  # 需要增加延迟，反正B站API未即时更新，防止返回上一个视频
                    video_info = await self.API.get_video(self.target_id)
                    video_info['User'] = 'bilibili'
                    video_info['Provide'] = 'Bilibili'
                    self.send_to_sub(video_info, False)
                    self.old_video_num = video_num
                else:
                    self.logger.info(f'{self.target_id}:{video_num} Not found new videos')
                await asyncio.sleep(config['sec'])
        except Exception:
            self.logger.exception('Check failed')


class BilibiliArticle(VideoDaemon):
    def __init__(self, user_config):
        super(BilibiliArticle, self).__init__(user_config)
        self.API = BilibiliAPI()
        self.logger = logging.getLogger('run.bilibili.article')
        self.old_article_num = None

    async def check(self):
        try:
            self.old_article_num = await self.API.get_article_num(self.target_id)
            while True:
                article_num = await self.API.get_article_num(self.target_id)
                if article_num > self.old_article_num:
                    self.logger.warning('Found A new article')
                    await asyncio.sleep(10)
                    article_info = await self.API.get_article(self.target_id)
                    article_info['User'] = 'bilibili'
                    article_info['Provide'] = 'Bilibili'
                    self.send_to_sub(article_info, False)
                    self.old_article_num = article_num
                else:
                    self.logger.info(f'{self.target_id}:{article_num} Not found new videos')
                await asyncio.sleep(config['sec'])
        except Exception:
            self.logger.exception('Check failed')


class BilibiliLive(VideoDaemon):
    def __init__(self, user_config):
        super(BilibiliLive, self).__init__(user_config)
        self.API = BilibiliAPI()
        self.logger = logging.getLogger('run.bilibili.live')

    async def check(self):
        while True:
            try:
                live_dict = await self.API.get_live_status(self.target_id)
                if live_dict.get('Is_live'):
                    live_dict['User'] = 'bilibili'
                    live_dict['Provide'] = 'Bilibili'
                    self.send_to_sub(live_dict, True)
                else:
                    self.logger.info(f'{self.target_id} Not found live')
                    await asyncio.sleep(config['sec'])
            except Exception:
                self.logger.exception('Check failed')

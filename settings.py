import pygame


class Settings:
    """ 存储游戏《外星人入侵》中所有设置的类 """

    FIRE_EVENT = pygame.USEREVENT

    def __init__(self):
        """ 初始化游戏的静态设置 """
        # 屏幕设置
        self.screen_width = 1500
        self.screen_height = 800
        self.bg_color = (0, 0, 0)

        # 飞船设置
        self.ship_speed = 1.5  # 速度：每次循环将移动1.5像素
        self.ship_limit = 3  # 飞船数量限制

        """音效设置"""
        # 音频文件路径

        # 音量设置
        self.load = 0.5     #0~1


        # 子弹设置
        self.bullet_speed = 3.0
        self.bullet_width = 4
        self.bullet_height = 15
        self.bullet_color = (160, 17, 33)  # 子弹颜色
        self.bullets_allowed = 10  # 允许在屏幕中的子弹数量

        # 外星人设置
        # self.alien_speed = 1.0
        self.fleet_drop_speed = 10
        # # fleet_direction为1表示右移，为-1表示左移
        # self.fleet_direction = 1

        # 加快游戏节奏的速度
        self.speedup_scale = 1.07

        # 外星人分数的提高速度
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """ 初始化随游戏进行而变化的设置 """
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 1.0

        # fleet_direction为1表示向右，为-1表示向左
        self.fleet_direction = 1

        # 记分
        self.alien_points = 50

    def increase_speed(self):
        """ 提高速度设置和外星人击杀分数 """
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)
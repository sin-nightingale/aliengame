import sys
import pygame
from time import sleep

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_starts import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
    """ 管理游戏资源和行为的类 """
    # 播放音乐
    pygame.mixer.init()
    pygame.mixer.music.load("music/bg_music2.mp3")
    pygame.mixer.music.set_volume(15)  # 设置音量
    pygame.mixer.music.play(-1)

    def __init__(self):
        """ 初始化游戏并创建游戏资源 """

        pygame.init()
        self.settings = Settings()
        pygame.time.set_timer(Settings.FIRE_EVENT, 50)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")


        # 创建一个用于存储游戏统计信息的实例
        # 并创建记分牌
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)

        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # 创建Play按钮
        self.play_button = Button(self, "Play")

    def run_game(self):
        """ 开始游戏的主循环 """
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _update_bullets(self):
        """ 更新子弹的位置并删除消失的子弹 """
        # 更新子弹的位置
        self.bullets.update()
        # 删除消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                # ######## 此处有改动
                # if bullet.rect.right >= self.ship.screen_rect.right:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """ 响应子弹和外星人碰撞 """
        # 删除发生碰撞的子弹和外星人
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, False, True)
        '''
        函数sprite.groupcollide()将一个编组中每个元素的rect同另一个编组中每个元素的rect及进行比较。
        '''
        if collisions:
            # 将消灭的每个外星人都计入得分
            pygame.mixer.Sound("music/boom.wav").play()
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.sb.prep_score()
                self.sb.check_high_score()

        if not self.aliens:
            # 删除现有的所有子弹并新建一群外星人
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # 提高等级
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """
        检查是否有外星人位于屏幕边缘，并更新外星人群中所有外星人的位置
        """
        self._check_fleet_edges()
        self.aliens.update()

        # 检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            print("Ship hit!!!")
            self._ship_hit()

        # 检查是否有外星人到达了屏幕底端
        self._check_aliens_bottom()

    def _ship_hit(self):
        """ 响应飞船被外星人撞到 """
        if self.stats.ships_left > 0:
            # 将ships_left减1并更新记分牌
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # 清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()

            # 创建一群新的外星人，并将飞船放到屏幕底端的中央
            self._create_fleet()
            self.ship.center_ship()

            # 暂停
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_events(self):
        """ 响应按键和鼠标事件 """
        for event in pygame.event.get():
            key_press = pygame.key.get_pressed()
            if key_press[pygame.K_SPACE]:
                """创建一颗子弹，并将其加入编组bullets中"""
                if len(self.bullets) < self.settings.bullets_allowed and event.type == Settings.FIRE_EVENT:
                    pygame.mixer.Sound("music/bullet.wav").play()
                    pygame.mixer.music.set_volume(20)
                    new_bullet = Bullet(self)  # 引用Bullet类创建子弹赋值给new_bullet
                    self.bullets.add(new_bullet)  # 在sprite中添加子弹

            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            elif event.type == pygame.KEYDOWN:  # 按下键
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:  # 松开键
                self._check_keyup_events(event)

    def _check_play_button(self, mouse_pos):
        """ 在玩家单击Play按钮时开始新游戏 """
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # 重置游戏设置
            self.settings.initialize_dynamic_settings()
            self._start_game()

    def _start_game(self):
        """ 响应单击Play按钮或按键P时开始游戏 """
        # 重置游戏统计信息
        self.stats.reset_stats()
        self.stats.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        # 清空余下的外星人和子弹
        self.aliens.empty()
        self.bullets.empty()

        # 创建一群新的外星人并让飞船居中
        self._create_fleet()
        self.ship.center_ship()

        # 隐藏鼠标光标
        pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """ 响应按键 """
        if event.key == pygame.K_RIGHT:  # 按下的键是右箭头键
            # 向右移动飞船
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:  # 按下的键是左箭头键
            # 向左移动飞船
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            # 向上移动飞船
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            # 向下移动飞船
            self.ship.moving_down = True
        elif event.key == pygame.K_q:
            # 按键Q以退出游戏
            sys.exit()
        elif event.key == pygame.K_p:
            # 按键P以开始游戏
            if not self.stats.game_active:
                self._start_game()


    def _check_keyup_events(self, event):
        """ 响应松开 """
        if event.key == pygame.K_RIGHT:  # 松开的键是右箭头键
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:  # 松开的键是左箭头键
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:  # 松开的键是上箭头键
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:  # 松开的键是下箭头键
            self.ship.moving_down = False
        elif event.key == pygame.K_SPACE:
            self.ship.space = False

    def _fire_bullet(self):
        """ 创建一颗子弹，并将其加入编组bullets中 """
        if len(self.bullets) < self.settings.bullets_allowed and self.ship.space and self.ship.bullets_fire:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _create_fleet(self):
        """ 创建外星人群 """
        # 创建一个外星人并计算一行可容纳多少个外星人
        # 外星人的间距为外星人宽度
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        availiable_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = availiable_space_x // (2 * alien_width) + 1

        # 计算屏幕可容纳多少行外星人
        ship_height = self.ship.rect.height
        availiable_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = availiable_space_y // (2 * alien_height)

        # 创建外星人群
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """ 创建一个外星人并将其加入到当前行 """
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        # 这里很重要！！！
        # 如果写作：
        # alien.rect.x = alien_width + 2 * alien_width * alien_number
        # 屏幕只会出现一列外星人
        # 原因是（alien_width + 2 * alien_width * alien_number）
        # 是计算当前外星人在当前行的位置，然后使用外星人的属性x来设置其rect的位置，这是创建外星人行列的过程，并不能展示外星人移动过程
        # alien是类Alien()的实例，在Alien()中alien.x在一直变化，利用函数_update_aliens()更新，以此来展示外星人左右移动

        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """ 外星人到达边缘时采取相应的措施 """
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_firection()
                break

    def _check_aliens_bottom(self):
        """ 检查是否有外星人到达了屏幕底端 """
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # 像飞船被撞到一样处理
                self._ship_hit()
                break

    def _change_fleet_firection(self):
        """ 将整群外星人下移，并改变它们方向 """
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """ 更新屏幕上的图像，并切换到新屏幕 """
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.aliens.draw(self.screen)

        # 显示得分
        self.sb.show_score()

        # 如果游戏处于非活动状态，就绘制Play按钮
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()


if __name__ == '__main__':
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()
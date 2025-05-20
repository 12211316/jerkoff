#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pygame.locals import *

from config.settings import *
from src.plane import OurPlane  # 导入我们的飞机
from src.enemy import SmallEnemy
from src.bullet import Bullet

# 初始化字体
pygame.font.init()
try:
    # 尝试使用系统中文字体
    font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 36)
except:
    try:
        # 备选方案：使用其他常见中文字体
        font = pygame.font.SysFont(['simsunnsimsun', 'microsoftyahei', 'simhei'], 36)
    except:
        # 如果都失败了，使用系统默认字体
        font = pygame.font.Font(None, 36)

bg_size = 480, 852  # 初始化游戏背景大小(宽, 高)
screen = pygame.display.set_mode(bg_size)  # 设置背景对话框
pygame.display.set_caption("飞机大战")  # 设置标题

background = pygame.image.load(os.path.join(BASE_DIR, "material/image/background.png"))  # 加载背景图片,并设置为不透明

# 创建退出按钮
exit_button = pygame.Rect(bg_size[0] - 100, 10, 80, 30)
exit_text = font.render("Exit", True, (255, 255, 255))
exit_text_rect = exit_text.get_rect(center=exit_button.center)

# 结束对话框
game_over_dialog = pygame.Surface((300, 200))
game_over_dialog.fill((0, 0, 0))
game_over_dialog.set_alpha(200)
game_over_rect = game_over_dialog.get_rect(center=(bg_size[0]//2, bg_size[1]//2))

# 失败对话框
game_fail_dialog = pygame.Surface((300, 200))
game_fail_dialog.fill((0, 0, 0))
game_fail_dialog.set_alpha(200)
game_fail_rect = game_fail_dialog.get_rect(center=(bg_size[0]//2, bg_size[1]//2))

#退出确定键
confirm_button = pygame.Rect(game_over_rect.width//2 - 40, 120, 80, 30)
confirm_text = font.render("ensure", True, (255, 255, 255))
confirm_text_rect = confirm_text.get_rect(center=confirm_button.center)

# 血槽颜色绘制
color_black = (0, 0, 0)
color_green = (0, 255, 0)
color_red = (255, 0, 0)
color_white = (255, 255, 255)

# 获取我方飞机
our_plane = OurPlane(bg_size)


def add_small_enemies(group1, group2, num):
    """
    添加小型敌机
    指定个敌机对象添加到精灵组（sprite.group）
    参数group1、group2是两个精灵组类型的形参，用以存储多个精灵对象（敌机）。
    需要注意的一点是group既然是特定的精灵组结构体，在向其内部添加精灵对象时需要调用其对应的成员函数add()
    :return:
    """
    for i in range(num):
        small_enemy = SmallEnemy(bg_size)
        group1.add(small_enemy)
        group2.add(small_enemy)


def main():
    # 响应音乐
    pygame.mixer.music.play(-1)  # loops 接收该参数, -1 表示无限循环(默认循环播放一次)
    running = True
    game_over = False
    switch_image = False  # 切换飞机的标识位(使飞机具有喷气式效果)
    delay = 60  # 对一些效果进行延迟, 效果更好一些

    enemies = pygame.sprite.Group()  # 生成敌方飞机组(一种精灵组用以存储所有敌机精灵)
    small_enemies = pygame.sprite.Group()  # 敌方小型飞机组(不同型号敌机创建不同的精灵组来存储)

    add_small_enemies(small_enemies, enemies, 6)  # 生成若干敌方小型飞机

    # 定义子弹, 各种敌机和我方敌机的毁坏图像索引
    bullet_index = 0
    e1_destroy_index = 0
    me_destroy_index = 0

    score = 0  # 初始化得分
    final_score = 0

    # 定义子弹实例化个数
    bullet1 = []
    bullet_num = 6
    for i in range(bullet_num):
        bullet1.append(Bullet(our_plane.rect.midtop))

    while running:
        # 绘制背景图
        screen.blit(background, (0, 0))



        # 微信的飞机貌似是喷气式的, 那么这个就涉及到一个帧数的问题
        clock = pygame.time.Clock()
        clock.tick(60)

        if not game_over:
            # 绘制我方飞机的两种不同的形式
            if not delay % 3:
                switch_image = not switch_image

            for each in small_enemies:
                if each.active:
                    # 随机循环输出小飞机敌机
                    each.move()
                    if each.rect.top >= bg_size[1]:
                        score -= 50  # 扣50分
                        each.active = False
                        each.reset()

                    screen.blit(each.image, each.rect)

                    pygame.draw.line(screen, color_black,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.right, each.rect.top - 5),
                                     2)
                    energy_remain = each.energy / SmallEnemy.energy
                    if energy_remain > 0.2:  # 如果血量大约百分之二十则为绿色，否则为红色
                        energy_color = color_green
                    else:
                        energy_color = color_red
                    pygame.draw.line(screen, energy_color,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5),
                                     2)
                else:
                    if e1_destroy_index == 0:
                        enemy1_down_sound.play()
                    screen.blit(each.destroy_images[e1_destroy_index], each.rect)
                    e1_destroy_index = (e1_destroy_index + 1) % 4
                    if e1_destroy_index == 0:
                        each.reset()

            # 当我方飞机存活状态, 正常展示
            if our_plane.active:
                if switch_image:
                    screen.blit(our_plane.image_one, our_plane.rect)
                else:
                    screen.blit(our_plane.image_two, our_plane.rect)

                # 飞机存活的状态下才可以发射子弹
                if not (delay % 10):  # 每十帧发射一颗移动的子弹
                    bullet_sound.play()
                    bullets = bullet1
                    bullets[bullet_index].reset(our_plane.rect.midtop)
                    bullet_index = (bullet_index + 1) % bullet_num

                for b in bullets:
                    if b.active:  # 只有激活的子弹才可能击中敌机
                        b.move()
                        screen.blit(b.image, b.rect)
                        enemies_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                        if enemies_hit:  # 如果子弹击中飞机
                            b.active = False
                            for e in enemies_hit:
                                e.active = False
                                score += 10  # 击中加分

                if score < 0 or not our_plane.active:
                    game_over = True
                    final_score = score

            # 毁坏状态绘制爆炸的场面
            else:
                if not (delay % 3):
                    screen.blit(our_plane.destroy_images[me_destroy_index], our_plane.rect)
                    me_destroy_index = (me_destroy_index + 1) % 4
                    if me_destroy_index == 0:
                        me_down_sound.play()
                        our_plane.reset()

            # 调用 pygame 实现的碰撞方法 spritecollide (我方飞机如果和敌机碰撞, 更改飞机的存活属性)
            enemies_down = pygame.sprite.spritecollide(our_plane, enemies, False, pygame.sprite.collide_mask)
            if enemies_down:
                our_plane.active = False
                game_over = True
                final_score = score
                for row in enemies:
                    row.active = False

            # 获得用户所有的键盘输入序列(如果用户通过键盘发出"向上"的指令,其他类似)
            key_pressed = pygame.key.get_pressed()
            if key_pressed[K_w] or key_pressed[K_UP]:
                our_plane.move_up()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                our_plane.move_down()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                our_plane.move_left()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                our_plane.move_right()

        # 响应用户的操作
        for event in pygame.event.get():
            if event.type == QUIT:  # 如果用户按下屏幕上的关闭按钮，触发QUIT事件，程序退出
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if exit_button.collidepoint(mouse_pos):
                    game_over = True
                elif game_over and confirm_button.collidepoint(mouse_pos[0] - game_over_rect.left, mouse_pos[1] - game_over_rect.top):
                    pygame.quit()
                    sys.exit()

        if delay == 0:
            delay = 60
        delay -= 1

        # 绘制退出按钮
        pygame.draw.rect(screen, (100, 100, 100), exit_button)
        screen.blit(exit_text, exit_text_rect)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        # 如果游戏结束，显示游戏结束对话框
        if game_over:
            # 游戏失败界面
            if score < 0 or not our_plane.active:
                # 绘制失败对话框
                screen.blit(game_fail_dialog, game_fail_rect)

                # 显示游戏结束文本
                fail_text = font.render("Game Over!", True, (255, 255, 255))
                screen.blit(fail_text, (game_fail_rect.centerx - 70, game_fail_rect.centery - 50))

                # 显示最终得分
                final_text = font.render(f"Final Score: {final_score}", True, (255, 255, 255))
                screen.blit(final_text, (game_fail_rect.centerx - 90, game_fail_rect.centery - 10))

                # 退出按钮
                quit_btn = pygame.Rect(game_fail_rect.centerx - 40, game_fail_rect.centery + 30, 80, 30)
                pygame.draw.rect(screen, (100, 100, 100), quit_btn)
                quit_text = font.render("Quit", True, (255, 255, 255))
                screen.blit(quit_text, (quit_btn.x + 15, quit_btn.y + 5))
            else:
                screen.blit(game_over_dialog, game_over_rect)
                screen.blit(confirm_text, (game_over_rect.left + confirm_text_rect.left, game_over_rect.top + confirm_text_rect.top))
                pygame.draw.rect(screen, (100, 100, 100), (game_over_rect.left + confirm_button.left, game_over_rect.top + confirm_button.top, confirm_button.width, confirm_button.height))
                screen.blit(confirm_text, (game_over_rect.left + confirm_text_rect.left, game_over_rect.top + confirm_text_rect.top))
                #退出界面文本
                quit_text = font.render("Make ture to exit?", True, (255, 255, 255))
                screen.blit(quit_text, (game_over_rect.centerx - 100, game_over_rect.centery - 50))
        # 绘制图像并输出到屏幕上面
        pygame.display.flip()





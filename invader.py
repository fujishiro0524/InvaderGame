import pygame
from pygame.locals import *
import os
import random
import sys

START, PLAY, GAMEOVER = (0, 1, 2)  # ゲーム状態
SCR_RECT = Rect(0, 0, 640, 480)

class Invader:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption(u"InvaderGame")
        # 素材のロード
        self.load_images()
        self.load_sounds()
        # ゲームオブジェクトを初期化
        self.init_game()
        # メインループ開始
        clock = pygame.time.Clock()
        
        
        while True:
            clock.tick(60)
            self.update()
            self.draw(screen)
            pygame.display.update()
            self.key_handler()
    def init_game(self):
        """ゲームオブジェクトを初期化"""
        # ゲーム状態
        self.game_state = START
        # スプライトグループを作成して登録
        self.all = pygame.sprite.RenderUpdates()
        self.aliens = pygame.sprite.Group()  # エイリアングループ
        self.shots = pygame.sprite.Group()   # ミサイルグループ
        # デフォルトスプライトグループを登録
        Player.containers = self.all
        Shot.containers = self.all, self.shots
        Alien.containers = self.all, self.aliens
        # Explosion.containers = self.all
        # 自機を作成
        self.player = Player()
        alienX = 20
        alienY = 20
        Alien((alienX,alienY))
        global score_board
        score_board = ScoreBoard()
        
    
    def update(self):
        
        """ゲーム状態の更新"""
        if self.game_state == PLAY:
            self.all.update()
            # ミサイルとエイリアンの衝突判定
            self.collision_detection(score_board)

    def draw(self, screen):
        """描画"""
        screen.fill((255, 255, 255))
        if self.game_state == START:  # スタート画面
            # タイトルを描画
            title_font = pygame.font.SysFont(None, 80)
            title = title_font.render("INVADER GAME", False, (255,0,0))
            screen.blit(title, ((SCR_RECT.width-title.get_width())/2, 100))
            # PUSH STARTを描画
            push_font = pygame.font.SysFont(None, 40)
            push_space = push_font.render("PUSH SPACE KEY", False, (0,0,0))
            screen.blit(push_space, ((SCR_RECT.width-push_space.get_width())/2, 300))
            # 名前を描画
            credit_font = pygame.font.SysFont(None,25)
            credit = credit_font.render("Akio Fujishiro", False, (0,0,0))
            screen.blit(credit, (500, 440))
        elif self.game_state == PLAY:  # ゲームプレイ画面
            self.all.draw(screen)
            score_board.draw(screen)
        elif self.game_state == GAMEOVER:  # ゲームオーバー画面
            # GAME OVERを描画
            gameover_font = pygame.font.SysFont(None, 80)
            gameover = gameover_font.render("GAME OVER", False, (255,0,0))
            screen.blit(gameover, ((SCR_RECT.width-gameover.get_width())/2, 100))
            # 結果スコアを描画
            result_font = pygame.font.SysFont(None, 60)
            result = result_font.render(f"Result Score : {str(score_board.score)}", False, (0,0,0))
            screen.blit(result, ((SCR_RECT.width-result.get_width())/2, 200))
            # PUSH STARTを描画
            push_font = pygame.font.SysFont(None, 40)
            push_space = push_font.render("PUSH SPACE KEY", False, (0,0,0))
            screen.blit(push_space, ((SCR_RECT.width-push_space.get_width())/2, 300))
    def key_handler(self):
        """キーハンドラー"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if self.game_state == START:  # スタート画面でスペースを押したとき
                    self.game_state = PLAY
                elif self.game_state == GAMEOVER:  # ゲームオーバー画面でスペースを押したとき
                    self.init_game()  # ゲームを初期化して再開
                    self.game_state = PLAY
    def collision_detection(self, score_board):
        """衝突判定"""
        # エイリアンとミサイルの衝突判定
        alien_collided = pygame.sprite.groupcollide(self.aliens, self.shots, True, True)
        for alien in alien_collided.keys():
            Alien.kill_sound.play()
            alienX = 20
            alienY = 20
            Alien((alienX,alienY))
            score_board.add_score(10)
        player_collided = pygame.sprite.spritecollide(self.player, self.aliens, True)
        if player_collided:  # プレイヤーとエイリアンの衝突
            Player.kill_sound.play()
            self.game_state = GAMEOVER
    def load_images(self):
        """イメージのロード"""
        # スプライトの画像を登録
        Player.image = load_image("player.png")
        Shot.image = load_image("bullet.png")
        Alien.image = load_image("enemy.png")
        # Explosion.images = split_image(load_image("explosion.png"), 16)
    def load_sounds(self):
        """サウンドのロード"""
        Alien.kill_sound = load_sound("bomb.wav")
        Player.shot_sound = load_sound("laser.wav")
        Player.kill_sound = load_sound("gameover.wav")

class Player(pygame.sprite.Sprite):
    """自機"""
    speed = 5  # 移動速度
    reload_time = 10  # リロード時間
    def __init__(self):
        # imageとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = SCR_RECT.center
        self.rect.bottom = SCR_RECT.bottom  # プレイヤーが画面の一番下
        self.reload_timer = 0
    def update(self):
        # 押されているキーをチェック
        pressed_keys = pygame.key.get_pressed()
        # 押されているキーに応じてプレイヤーを移動
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        elif pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
        self.rect.clamp_ip(SCR_RECT)
        # ミサイルの発射
        if pressed_keys[K_SPACE]:
            # リロード時間が0になるまで再発射できない
            if self.reload_timer > 0:
                # リロード中
                self.reload_timer -= 1
            else:
                # 発射！！！
                Player.shot_sound.play()
                Shot(self.rect.center)  # 作成すると同時にallに追加される
                self.reload_timer = self.reload_time

class Alien(pygame.sprite.Sprite):
    speed = 10  # 移動速度
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos
    def update(self):
        self.rect.move_ip(self.speed, 0)
        if self.rect.left < SCR_RECT.left:
            self.speed = 10
            self.rect.centery += 40
        if self.rect.right > SCR_RECT.right:
            self.speed = -10
            self.rect.centery += 40

class Shot(pygame.sprite.Sprite):
    """プレイヤーが発射するミサイル"""
    speed = 9  # 移動速度
    def __init__(self, pos):
        # imageとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos  # 中心座標をposに
    def update(self):
        self.rect.move_ip(0, -self.speed)  # 上へ移動
        if self.rect.top < 0:  # 上端に達したら除去
            self.kill()

class ScoreBoard():
    """スコアボード"""
    def __init__(self):
        self.sysfont = pygame.font.SysFont(None, 40)
        self.score = 0
    def draw(self, screen):
        score_img = self.sysfont.render(f"Score : {str(self.score)}", True, (0, 0, 0))
        screen.blit(score_img, (10, 10))
    def add_score(self, x):
        self.score += x
        return self.score

def load_image(filename, colorkey=None):
    # 透過処理
    filename = os.path.join("data", filename)
    image = pygame.image.load(filename)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def split_image(image, n):
    image_list = []
    w = image.get_width()
    h = image.get_height()
    w1 = w // n
    for i in range(0, w, w1):
        surface = pygame.Surface((w1,h))
        surface.blit(image, (0,0), (i,0,w1,h))
        surface.set_colorkey(surface.get_at((0,0)), RLEACCEL)
        surface.convert()
        image_list.append(surface)
    return image_list

def load_sound(filename):
    filename = os.path.join("data", filename)
    return pygame.mixer.Sound(filename)

if __name__ == "__main__":
    Invader()
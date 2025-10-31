import pygame
from pygame.locals import *
import random
import os

pygame.init()
pygame.mixer.init()

width = 500
height = 500
screen_size = width, height
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Vrom Vrom")

gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)
blue = (0, 100, 255)

gameover = False
speed = 2
max_speed = 8
score = 0
high_score = 0

marker_width = 10
marker_height = 50

road = (100, 0, 300, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

lane_marker_move_y = 0

if not os.path.exists('sounds'):
    os.makedirs('sounds')
if not os.path.exists('images'):
    os.makedirs('images')

try:
    pygame.mixer.music.load('sounds/music.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.03)
except:
    pass

try:
    crash_sound = pygame.mixer.Sound('sounds/crash.wav')
    engine_sound = pygame.mixer.Sound('sounds/engine.wav')
    has_audio = True
except:
    has_audio = False


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Les autres véhicules sont plus grands
        target_width = 60
        target_height = 50

        self.image = pygame.transform.scale(image, (target_width, target_height))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        try:
            image = pygame.image.load('images/car.png')
        except:
            image = pygame.Surface((50, 30))
            image.fill(red)
        super().__init__(image, x, y)


player_x = 250
player_y = 400
player_group = pygame.sprite.Group()
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

image_filenames = ['Police.png', 'Mini_truck.png', 'taxi.png', 'Ambulance.png', 'Audi.png', 'Mini_van.png']
vehicle_images = []
for image_filename in image_filenames:
    try:
        image = pygame.image.load('images/' + image_filename)
        vehicle_images.append(image)
    except:
        placeholder = pygame.Surface((50, 30))
        placeholder.fill((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
        vehicle_images.append(placeholder)

vehicle_group = pygame.sprite.Group()

try:
    crash = pygame.image.load('images/crash.png')
except:
    crash = pygame.Surface((40, 40))
    crash.fill((255, 165, 0))
crash_rect = crash.get_rect()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, power_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.power_type = power_type

        if power_type == 'shield':
            color = blue
        elif power_type == 'slow':
            color = yellow
        else:
            color = green

        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (15, 15), 15)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


powerup_group = pygame.sprite.Group()
shield_active = False
shield_timer = 0

clock = pygame.time.Clock()
fps = 120
running = True

while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == KEYDOWN:
            if event.key == K_LEFT and player.rect.center[0] > left_lane:
                player.rect.x -= 100
                if has_audio:
                    engine_sound.play()
            elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                player.rect.x += 100
                if has_audio:
                    engine_sound.play()

            if not shield_active:
                for vehicle in vehicle_group:
                    if pygame.sprite.collide_rect(player, vehicle):
                        gameover = True
                        if has_audio:
                            crash_sound.play()
                        if event.key == K_LEFT:
                            player.rect.left = vehicle.rect.right
                            crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                        elif event.key == K_RIGHT:
                            player.rect.right = vehicle.rect.left
                            crash_rect.center = [player.rect.right,
                                                 (player.rect.center[1] + vehicle.rect.center[1]) / 2]

    screen.fill(green)
    pygame.draw.rect(screen, gray, road)
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)

    lane_marker_move_y += speed * 2
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

    if shield_active:
        shield_rect = pygame.Rect(0, 0, 70, 70)
        shield_rect.center = player.rect.center
        pygame.draw.ellipse(screen, blue, shield_rect, 3)

    player_group.draw(screen)

    if len(vehicle_group) < 5:
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.2:
                add_vehicle = False
        if add_vehicle:
            lane = random.choice(lanes)
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, height / -2)
            vehicle_group.add(vehicle)

    if random.random() < 0.008 and len(powerup_group) == 0:
        empty_lanes = []
        for lane in lanes:
            lane_empty = True
            for vehicle in vehicle_group:
                if vehicle.rect.center[0] == lane and vehicle.rect.top < height / 1.5:
                    lane_empty = False
                    break
            if lane_empty:
                empty_lanes.append(lane)

        if empty_lanes:
            lane = random.choice(empty_lanes)
            power_type = random.choice(['shield', 'slow', 'points'])
            powerup = PowerUp(power_type, lane, -50)
            powerup_group.add(powerup)

    for vehicle in vehicle_group:
        vehicle.rect.y += speed + random.uniform(-0.2, 0.2)
        if vehicle.rect.top >= height:
            vehicle.kill()
            score += 1
            if score > 0 and score % 4 == 0 and speed < max_speed:
                speed += 0.3

    for powerup in powerup_group:
        powerup.rect.y += speed
        if powerup.rect.top >= height:
            powerup.kill()

    powerup_collisions = pygame.sprite.spritecollide(player, powerup_group, True)
    for powerup in powerup_collisions:
        if powerup.power_type == 'shield':
            shield_active = True
            shield_timer = 450
        elif powerup.power_type == 'slow':
            speed = max(2, speed - 0.8)
        elif powerup.power_type == 'points':
            score += 8

    if shield_active:
        shield_timer -= 1
        if shield_timer <= 0:
            shield_active = False

    vehicle_group.draw(screen)
    powerup_group.draw(screen)

    font = pygame.font.Font(None, 28)
    text = font.render(f'Score: {score}  High: {high_score}', True, white)
    screen.blit(text, (width // 2 - text.get_width() // 2, 450))

    speed_text = font.render(f'Speed: {speed:.1f}', True, white)
    screen.blit(speed_text, (width // 2 - speed_text.get_width() // 2, 470))

    if shield_active:
        shield_font = pygame.font.Font(None, 24)
        shield_text = shield_font.render('SHIELD ACTIVE', True, blue)
        screen.blit(shield_text, (width // 2 - shield_text.get_width() // 2, 430))

    if not shield_active and pygame.sprite.spritecollide(player, vehicle_group, False):
        gameover = True
        if has_audio:
            crash_sound.play()
        crash_rect.center = [player.rect.center[0], player.rect.top]
        if score > high_score:
            high_score = score

    if gameover:
        screen.blit(crash, crash_rect)
        pygame.draw.rect(screen, red, (0, 50, width, 120))

        game_over_font = pygame.font.Font(None, 48)
        text1 = game_over_font.render('GAME OVER', True, white)
        screen.blit(text1, (width // 2 - text1.get_width() // 2, 70))

        font = pygame.font.Font(None, 32)
        text2 = font.render('Press Y to retry, N to exit', True, white)
        screen.blit(text2, (width // 2 - text2.get_width() // 2, 120))

        final_score_text = font.render(f'Final Score: {score}', True, white)
        screen.blit(final_score_text, (width // 2 - final_score_text.get_width() // 2, 150))

    pygame.display.update()

    while gameover:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == QUIT:
                gameover = False
                running = False
            if event.type == KEYDOWN:
                if event.key == K_y:
                    gameover = False
                    speed = 2
                    score = 0
                    vehicle_group.empty()
                    powerup_group.empty()
                    shield_active = False
                    player.rect.center = [player_x, player_y]
                elif event.key == K_n:
                    gameover = False
                    running = False

pygame.quit()
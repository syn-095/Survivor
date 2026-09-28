import pygame
from pygame.math import Vector2
import sys
import shapes, between_levels

W, H = 800, 600
pygame.init()

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Survivor")
pygame.display.set_icon(pygame.image.load('assets/icon.png'))

class Main:
    def __init__(self):
        self.game_states = {
            "intro": self.intro_screen,
            "main_game": self.main_game
        }

        self.conveyor_middims = [50, H - 50]
        self.shape_size = Vector2(40, 40)
        self.shape_speed = 1

        # gap used to space shapes so they arrive in series
        gap = int(self.shape_size.x * 2)
        # level 1: single socket & plug; level 2: five of each (compact comprehensions)
        self.level_shapes = {
            1: [
                shapes.socketShape(Vector2(W, self.conveyor_middims[0]), Vector2(-self.shape_speed, 0), self.shape_size),
                shapes.plugShape(Vector2(0, self.conveyor_middims[1]), Vector2(self.shape_speed, 0), self.shape_size),
            ],
            2: [
                *[shapes.socketShape(Vector2(W + gap * i, self.conveyor_middims[0]), Vector2(-self.shape_speed, 0), self.shape_size) for i in range(5)],
                *[shapes.plugShape(Vector2(-gap * i, self.conveyor_middims[1]), Vector2(self.shape_speed, 0), self.shape_size) for i in range(5)],
            ],
        }
        self.current_state = "intro"

        self.level = 1
        self.score = 0
        self.information_level = 0
        self.between_levels = False
        # store the table rect so event loop can forward mouse events
        self.table_rect = pygame.Rect(0, 0, 0, 0)
        # list to hold completed/merged shapes placed on the table
        self.completed_shapes = []

    def main_game(self):
        self.screen_colour = (240, 240, 240)
        screen.fill(self.screen_colour)

        level_font = pygame.font.SysFont('New Times Roman', 20)
        level_surf = level_font.render(f"Level: {self.level}", True, "black")
        level_rect = level_surf.get_rect(topleft=(10, 10))
        screen.blit(level_surf, level_rect)

        score_font = pygame.font.SysFont('New Times Roman', 20)
        score_surf = score_font.render(f"Score: {self.score}", True, "black")
        score_rect = score_surf.get_rect(topright=(W - 10, 10))
        screen.blit(score_surf, score_rect)


        table_dimensions = Vector2(11, 9)
        square_size = 10
        table_rect = pygame.Rect(W // 2 - (table_dimensions.x * square_size) // 2,
                                 H // 2 - (table_dimensions.y * square_size) // 2,
                                 table_dimensions.x * square_size,
                                 table_dimensions.y * square_size)
        # expose table_rect for event handling
        self.table_rect = table_rect
        pygame.draw.rect(screen, (110, 110, 110), table_rect)

        # Draw conveyors
        top_conveyor = []
        bottom_conveyor = []
        for i in range(W//20):
            top_conveyor.append(pygame.Rect(i*20, self.conveyor_middims[0] - (45//2), 15, 45))
            pygame.draw.rect(screen, (200, 200, 200), top_conveyor[i])
            bottom_conveyor.append(pygame.Rect(i*20, self.conveyor_middims[1] - (45//2), 15, 45))
            pygame.draw.rect(screen, (200, 200, 200), bottom_conveyor[i])
        # -----------------------------------------------

        self.level_shaped_points = {
            1: 1,
            2: 1,
        }

        if self.between_levels:
            self.score, self.information_level, next_level = between_levels.between_levels(screen, self.score, self.information_level, self.level - 1)
            if next_level:
                self.between_levels = False

        elif self.level == 1:
            self.level_1()
        elif self.level == 2:
            self.level_2()

        # draw any completed shapes already on the table
        if not self.between_levels:
            for cs in self.completed_shapes:
                cs.draw(screen)

    def level_2(self):
        shapes_for_level = list(self.level_shapes[self.level])
        for shape in shapes_for_level:
            shape.update(screen)
        
        placed = [s for s in self.level_shapes[self.level] if getattr(s, 'on_table', False) and not getattr(s, 'merged', False)]
        # If two placed shapes are the same type, return them to conveyor (no merge)
        if len(placed) >= 2 and placed[0].shape_type == placed[1].shape_type:
            for i in range(2):
                if placed[i].shape_type == 'socket':
                    right = 0
                    for shape in shapes_for_level:
                        if shape.rect.y == placed[i].start_pos.y:
                            if right < shape.rect.right:
                                right = shape.rect.right
                    placed[i].enqueue_return(W + right + self.shape_size.x*1.5)

                elif placed[i].shape_type == 'plug':
                    left = 0
                    for shape in shapes_for_level:
                        if shape.rect.y == placed[i].start_pos.y:
                            if left > shape.rect.left:
                                left = shape.rect.left
                    placed[i].enqueue_return(-(left + self.shape_size.x*1.5))
        # Otherwise, merging happens
        elif len(placed) >= 2 and placed[0].shape_type != placed[1].shape_type:
            # take first two and merge
            a = placed[0]
            b = placed[1]
            a.set_merged()
            b.set_merged()
            # remove merged pieces from level shapes
            try:
                self.level_shapes[self.level].remove(a)
            except ValueError:
                pass
            try:
                self.level_shapes[self.level].remove(b)
            except ValueError:
                pass
            # create completed shape at table center
            comp_size = Vector2(max(self.shape_size.x, 40), max(self.shape_size.y, 40))
            completed = shapes.CompletedShape(Vector2(self.table_rect.center), comp_size)
            self.completed_shapes.append(completed)
            pygame.time.set_timer(completed_timer, 1000)

            shapes_for_level = list(self.level_shapes[self.level])

            self.score += self.level_shaped_points[2]
            if len(self.level_shapes[self.level]) == 0:
                self.level += 1
                self.between_levels = True

        # see if two same shapes are colliding on the conveyor
        moved_shapes = []
        for shape in shapes_for_level:
            for other_shape in shapes_for_level:
                if shape != other_shape and shape.shape_type == other_shape.shape_type and shape.rect.y == other_shape.rect.y and shape not in moved_shapes and other_shape not in moved_shapes and shape.dragging == False and other_shape.dragging == False:
                    if shape.rect.colliderect(other_shape.rect):
                        shape.enqueue_return(shape.start_pos.x + self.shape_size.x*1.5)
                        moved_shapes.append(shape)

    def level_1(self):
        # Update and draw shapes
        shapes_for_level = list(self.level_shapes[self.level])
        for shape in shapes_for_level:
            shape.update(screen)

        # Check for merging: if two shapes are on the table and not yet merged, merge them
        placed = [s for s in self.level_shapes[self.level] if getattr(s, 'on_table', False) and not getattr(s, 'merged', False)]
        if len(placed) >= 2 and placed[0].shape_type == placed[1].shape_type:
            for i in range(2):
                placed[i].on_table = False
                placed[i].rect.center = (round(placed[i].start_pos.x), round(placed[i].start_pos.y))
        elif len(placed) >= 2 and placed[0].shape_type != placed[1].shape_type:
            # take first two and merge
            a = placed[0]
            b = placed[1]
            a.set_merged()
            b.set_merged()
            # remove merged pieces from level shapes
            try:
                self.level_shapes[self.level].remove(a)
            except ValueError:
                pass
            try:
                self.level_shapes[self.level].remove(b)
            except ValueError:
                pass
            # create completed shape at table center
            comp_size = Vector2(max(self.shape_size.x, 40), max(self.shape_size.y, 40))
            completed = shapes.CompletedShape(Vector2(self.table_rect.center), comp_size)
            self.completed_shapes.append(completed)
            pygame.time.set_timer(completed_timer, 1000)

            shapes_for_level = list(self.level_shapes[self.level])

            self.score += self.level_shaped_points[1]
            if len(self.level_shapes[self.level]) == 0:
                self.level += 1
                self.between_levels = True

    def intro_screen(self):
        mouse_pos = pygame.mouse.get_pos()
        self.play_click = False
        self.settings_click = False

        title_font = pygame.font.SysFont('New Times Roman', 74)
        title_surf = title_font.render("Survivor", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(W // 2, H // 2 - 100))
        screen.blit(title_surf, title_rect)

        slogan_font = pygame.font.SysFont('New Times Roman', 20) 
        slogan_surf = slogan_font.render("Tomorrow, Tomorrow, and Tomorrow", True, (255, 255, 255))
        slogan_rect = slogan_surf.get_rect(center=(W // 2, H // 2 - 50))
        screen.blit(slogan_surf, slogan_rect)

        play_font = pygame.font.SysFont('New Times Roman', 50) 
        play_text = "PLAY [ENTER]"
        play_surf = play_font.render(play_text, True, (255, 255, 255))
        play_rect = play_surf.get_rect(center=(W // 2 , H // 2 + 100))
        if play_rect.collidepoint(mouse_pos):
            play_surf = play_font.render(play_text, True, (100, 100, 100))
            self.play_click = True
        screen.blit(play_surf, play_rect)

        settings_font = pygame.font.SysFont('New Times Roman', 40) 
        settings_text = "SETTINGS [SPACE]"
        settings_surf = settings_font.render(settings_text, True, (255, 255, 255))
        settings_rect = settings_surf.get_rect(center=(W // 2, H // 2 + 150))
        if settings_rect.collidepoint(mouse_pos):
            settings_surf = settings_font.render(settings_text, True, (100, 100, 100))
            self.settings_click = True
        screen.blit(settings_surf, settings_rect)

game = Main()

clock = pygame.time.Clock()
fps = 60

completed_timer = pygame.USEREVENT + 1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle input for intro screen
        if game.current_state == "intro":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game.current_state = "main_game"
                    game.score = 0
                if event.key == pygame.K_SPACE:
                    print("Open Settings")
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.play_click:
                    game.current_state = "main_game"
                    game.score = 0
                if game.settings_click:
                    print("Open Settings")
        # -----------------------------------------------
        # Forward mouse events to shapes when in main_game so they can be dragged
        if game.current_state == "main_game":
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                for shape in game.level_shapes.get(game.level, []):
                    # forward the event and the current table rect
                    try:
                        shape.handle_event(event, game.table_rect)
                    except Exception:
                        # ignore shapes that don't implement handle_event
                        pass
                # (no post-event enqueueing — shapes reset themselves on release)
            # -----------------------------------------------
            # Handle completed shape timer
            if event.type == completed_timer:
                pygame.time.set_timer(completed_timer, 0)
                game.completed_shapes.remove(game.completed_shapes[0])
            #-----------------------------------------------
    
    screen.fill((10,10,10))

    game.game_states[game.current_state]()

    pygame.display.update()
    clock.tick(fps)
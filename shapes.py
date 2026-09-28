import pygame
from pygame.math import Vector2


class socketShape:
    def __init__(self, midPos : Vector2, speed : Vector2, size, screen_dimensions = Vector2(800, 600)):
        self.img = pygame.image.load('assets/1st_shape_socket.png')
        self.img = pygame.transform.scale(self.img, size)
        self.rect = self.img.get_rect(center=midPos)
        self.shape_type = 'socket'
        self.speed = speed
        self.screen_dimensions = screen_dimensions
        # Drag & drop state
        self.dragging = False
        self.drag_offset = Vector2(0, 0)
        self.on_table = False
        self.merged = False
        # remember starting conveyor center so we can return here if user drops off-table
        self.start_pos = Vector2(self.rect.center)

    def update(self, screen):
        # Move along conveyor only if not placed on the table and not being dragged or merged
        if not self.on_table and not self.dragging and not self.merged:
            self.rect.x += self.speed.x
            self.rect.y += self.speed.y
            if self.rect.right < 0:
                self.rect.left = self.screen_dimensions.x
        if not self.merged:
            screen.blit(self.img, self.rect)

    def handle_event(self, event, table_rect: pygame.Rect):
        # Accept pygame mouse events and update dragging / on_table
        if self.merged:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                mouse_v = Vector2(event.pos)
                self.drag_offset = mouse_v - Vector2(self.rect.topleft)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                # On release, mark as on_table if it overlaps the table at all
                if self.rect.colliderect(table_rect):
                    self.on_table = True
                    # snap to left side of table so sockets sit nicely
                    self.rect.midleft = (table_rect.left + 5, table_rect.centery)
                else:
                    # return to starting conveyor position and resume movement
                    self.on_table = False
                    self.dragging = False
                    self.rect.center = (round(self.start_pos.x), round(self.start_pos.y))
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_v = Vector2(event.pos)
                new_topleft = mouse_v - self.drag_offset
                self.rect.topleft = (round(new_topleft.x), round(new_topleft.y))

    def enqueue_return(self, right : int):
        self.on_table = False
        self.dragging = False
        if self.start_pos.x > right:
            self.rect.center = (round(self.start_pos.x), round(self.start_pos.y))
        else:
            self.rect.center = (round(right), round(self.start_pos.y))

    def set_merged(self):
        self.merged = True
        

class plugShape(socketShape):
    def __init__(self, midPos : Vector2, speed : Vector2, size, screen_dimensions = Vector2(800, 600)):
        self.img = pygame.image.load('assets/2nd_shape_plug.png')
        self.img = pygame.transform.scale(self.img, size)
        self.rect = self.img.get_rect(center=midPos)
        self.shape_type = 'plug'
        self.speed = speed
        self.screen_dimensions = screen_dimensions
        # Drag & drop state
        self.dragging = False
        self.drag_offset = Vector2(0, 0)
        self.on_table = False
        self.merged = False
        # remember starting conveyor center so we can return here if user drops off-table
        self.start_pos = Vector2(self.rect.center)

    def update(self, screen):
        # Move along conveyor only if not placed on the table and not being dragged or merged
        if not self.on_table and not self.dragging and not self.merged:
            self.rect.centerx += self.speed.x
            self.rect.centery += self.speed.y
            if self.rect.left > self.screen_dimensions.x:
                self.rect.right = 0
        if not self.merged:
            screen.blit(self.img, self.rect)

    def handle_event(self, event, table_rect: pygame.Rect):
        # Accept pygame mouse events and update dragging / on_table
        if self.merged:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                mouse_v = Vector2(event.pos)
                self.drag_offset = mouse_v - Vector2(self.rect.topleft)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                # On release, snap/mark if on table
                # On release, mark as on_table if it overlaps the table at all
                if self.rect.colliderect(table_rect):
                    self.on_table = True
                    # snap to right side of table so plugs sit nicely
                    self.rect.midright = (table_rect.right - 5, table_rect.centery)
                else:
                    # return to starting conveyor position and resume movement
                    self.on_table = False
                    self.dragging = False
                    self.rect.center = (round(self.start_pos.x), round(self.start_pos.y))
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_v = Vector2(event.pos)
                new_topleft = mouse_v - self.drag_offset
                self.rect.topleft = (round(new_topleft.x), round(new_topleft.y))

    def enqueue_return(self, left : int):
        self.on_table = False
        self.dragging = False
        if self.start_pos.x < left:
            self.rect.center = (round(self.start_pos.x), round(self.start_pos.y))
        else:
            self.rect.center = (round(left), round(self.start_pos.y))

    def set_merged(self):
        self.merged = True


class CompletedShape:
    def __init__(self, center_pos: Vector2, size: Vector2):
        # Attempt to load an explicit completed image. If missing, default to socket image.
        self.img = pygame.image.load('assets/level1 - completed_shape.png')

        self.img = pygame.transform.scale(self.img, (int(size.x), int(size.y)))
        self.rect = self.img.get_rect(center=center_pos)

    def draw(self, surface):
        surface.blit(self.img, self.rect)
    
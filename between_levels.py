import pygame
from pygame.math import Vector2

def between_levels(screen, score, information, level):
    mouse_pos = pygame.mouse.get_pos()

    screen.fill((50, 50, 50))
    title_font = pygame.font.SysFont('New Times Roman', 30)
    subtitle_font = pygame.font.SysFont('New Times Roman', 24)
    button_font = pygame.font.SysFont('New Times Roman', 20)

    title_surf = title_font.render(f'Level {level} Complete!', True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 100))

    score_surf = subtitle_font.render(f'Score: {score}', True, (255, 255, 255))
    score_rect = score_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))

    information_surf = subtitle_font.render(f'Promotion: {information}', True, (255, 255, 255))
    information_rect = information_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    score_button_surf = button_font.render('Get paid', True, (0, 0, 0))
    score_button_rect = score_button_surf.get_rect(center=(screen.get_width() // 2 - 100, screen.get_height()//2 + 100))
    
    info_button_surf = button_font.render('Get promoted', True, (0, 0, 0))
    info_button_rect = info_button_surf.get_rect(center=(screen.get_width() // 2 + 100, screen.get_height()//2 + 100))

    screen.blit(title_surf, title_rect)
    screen.blit(score_surf, score_rect)
    screen.blit(information_surf, information_rect)
    if score_button_rect.collidepoint(mouse_pos):
        score_button_surf = button_font.render('Get paid', True, (100, 100, 100))
    if info_button_rect.collidepoint(mouse_pos):
        info_button_surf = button_font.render('Get promoted', True, (100, 100, 100))
    screen.blit(score_button_surf, score_button_rect)
    screen.blit(info_button_surf, info_button_rect)

    keys = pygame.key.get_pressed()
    if pygame.mouse.get_pressed()[0]:
        if score_button_rect.collidepoint(mouse_pos):
            score += 20
            return score, information, True
        elif info_button_rect.collidepoint(mouse_pos):
            information += 1
            return score, information, True
    
    else:
        return score, information, False


if __name__ == '__main__':
    print('test')

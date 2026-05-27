import pygame
from Engine import engine as e
from Entities.Player import Player
from Entities.World import World
from Entities.Map import Map

e.init(200, 200, title="Game", fps=60, display_scale=4)
e.resources.image(0, "./assests/images/feuille1.png")
e.resources.image(1, "./assests/images/stuff.png")
img = e.resources.images[0]
img2 = e.resources.images[1]
world = World()

player = Player(10, 10, 8, 8, img, world=world)
player.speed = 1
world.add(player)

frames_dict = {
    "image_x":4, "image_y":0, "shadow": (-4, 0),
    "idle_up": (0, 6), "idle_down": (0, 7),
    "idle_left": (0, 5), "idle_right": (0, 4),
    "walk_up": (0, 2), "walk_down": (0, 3),
    "walk_left": (0, 1), "walk_right": (0, 0),
    "bank":img2,
}
frames_dict2 = {
    "image_x":8, "image_y":0, "shadow": (-8, 0),
    "idle_up": (0, 6), "idle_down": (0, 7),
    "idle_left": (0, 5), "idle_right": (0, 4),
    "walk_up": (0, 2), "walk_down": (0, 3),
    "walk_left": (0, 1), "walk_right": (0, 0),
    "bank":img2,
}

game_map = Map(world)
game_map.generate_island(
    ["plains", "hills", "forest", "desert", "rocky_plains", "mountains"],
    50, 50,
    npc_count=8, player=player,
    frames_dicts=[frames_dict, frames_dict2], img2=img2,
)
bg_color = game_map.bg_color

cam = e.Camera(player, e.width(), e.height(), mouse_influence=0.2, mouse_limit=10)
e.active_camera = cam

BOX_W, BOX_H = 50, 44
SLOT_SIZE = 10
GAP = 2
COLS = 3
ROWS = 2
GRID_W = COLS * SLOT_SIZE + (COLS - 1) * GAP
GRID_H = ROWS * SLOT_SIZE + GAP

inventory_open = False
drag_slot = -1
drag_item = None


def _box_pos():
    return (
        player.x + e.graphics._camera_x + 10,
        player.y + e.graphics._camera_y - 26,
    )


def _slot_rects(bx, by):
    gx = bx + (BOX_W - GRID_W) // 2
    gy = by + (BOX_H - GRID_H) // 2 - 2
    rects = []
    for i in range(6):
        col = i % COLS
        row = i // COLS
        sx = gx + col * (SLOT_SIZE + GAP)
        sy = gy + row * (SLOT_SIZE + GAP)
        rects.append((sx, sy, SLOT_SIZE, SLOT_SIZE))
    return rects, gx, gy


def _section_rects(gx, gy):
    rw = GRID_W + 4
    rh = SLOT_SIZE + 4
    return (
        (gx - 2, gy - 2, rw, rh),
        (gx - 2, gy + SLOT_SIZE + GAP - 2, rw, rh),
    )


def update():
    global inventory_open, drag_slot, drag_item

    if not inventory_open:
        world.update()
        cam.update()
    cam.apply()

    if e.btnp(e.KEY_I):
        inventory_open = not inventory_open
        if not inventory_open:
            drag_slot = -1
            drag_item = None

    if not inventory_open:
        if e.btn(e.KEY_ESCAPE):
            e.quit()
        return

    mx, my = e.mouse_x(), e.mouse_y()
    bx, by = _box_pos()
    slot_rects, gx, gy = _slot_rects(bx, by)

    if e.mouse_btnp(e.MOUSE_BUTTON_LEFT) and drag_slot < 0:
        for i, (sx, sy, sw, sh) in enumerate(slot_rects):
            if sx <= mx <= sx + sw and sy <= my <= sy + sh:
                if player.items[i] is not None:
                    drag_slot = i
                    drag_item = player.items[i]
                break

    if e.mouse_btnr(e.MOUSE_BUTTON_LEFT) and drag_slot >= 0:
        target = -1
        for i, (sx, sy, sw, sh) in enumerate(slot_rects):
            if sx <= mx <= sx + sw and sy <= my <= sy + sh:
                target = i
                break

        if 0 <= target < 6 and target != drag_slot:
            other = player.items[target]
            player.items[target] = player.items[drag_slot]
            player.items[drag_slot] = other
            if player.current_item is drag_item:
                player.current_item = other
            elif player.current_item is other:
                player.current_item = drag_item
        elif target == -1:
            item = drag_item
            item.picked_up = False
            item.parent = None
            item.x = player.x
            item.y = player.y
            world.add(item)
            player.items[drag_slot] = None
            if player.current_item is item:
                player.current_item = next(
                    (it for it in player.items if it is not None), None
                )

        drag_slot = -1
        drag_item = None


def draw():
    global inventory_open, drag_slot, drag_item
    e.cls(bg_color)
    world.draw()

    if inventory_open:
        inv_sx, inv_sy = _box_pos()

    if cam.flash_alpha > 0:
        surf = pygame.Surface((e.width(), e.height()), pygame.SRCALPHA)
        surf.fill((*cam.flash_color, cam.flash_alpha))
        e.graphics.screen.blit(surf, (0, 0))

    e.camera()

    if inventory_open:
        _draw_inventory_box(inv_sx, inv_sy)

    if drag_item and drag_slot >= 0:
        mx, my = e.mouse_x(), e.mouse_y()
        e.blt(mx - 4, my - 4, drag_item.bank,
              drag_item.w * drag_item.dropped_pos[0],
              drag_item.h * drag_item.dropped_pos[1],
              drag_item.w, drag_item.h)
    else:
        e.circb(e.mouse_x(), e.mouse_y(), 4, (255, 255, 255, 50))


def _draw_inventory_box(bx, by):
    slot_rects, gx, gy = _slot_rects(bx, by)
    sec_a, sec_b = _section_rects(gx, gy)
    sections = [sec_a, sec_b]

    e.rect(bx - 1, by - 1, BOX_W + 2, BOX_H + 2, (40, 40, 50))
    e.rect(bx, by, BOX_W, BOX_H, (15, 15, 22))

    for s in (0, 1):
        sr = sections[s]
        col = (30, 40, 55) if s == player.current_section else (20, 22, 30)
        e.rect(sr[0], sr[1], sr[2], sr[3], col)

    for i, (sx, sy, sw, sh) in enumerate(slot_rects):
        item = player.items[i]
        if item is not None and (drag_slot < 0 or drag_slot != i):
            is_active = (item is player.current_item)
            e.rect(sx, sy, sw, sh, (55, 55, 65))
            e.blt(sx + 1, sy + 1, item.bank,
                  item.w * item.dropped_pos[0],
                  item.h * item.dropped_pos[1],
                  item.w, item.h)
            if is_active:
                e.rectb(sx - 1, sy - 1, sw + 2, sh + 2, (255, 210, 60))
        elif drag_slot == i:
            e.rect(sx, sy, sw, sh, (25, 35, 50))
        else:
            e.rect(sx, sy, sw, sh, (30, 30, 35))


if __name__ == "__main__":
    e.run(update, draw)

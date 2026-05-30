from PIL import Image
from Engine import engine as e
from Entities.Item import Item


class Consumable(Item):
    def __init__(self, x, y, w, h, bank, parent=None, speed=1,
                 name="Potion", heal_amount=10, dropped_pos=(0, 0)):
        if bank is not None:
            if isinstance(bank, int) and bank < len(e.resources.images):
                bank = e.resources.images[bank]
            _spr = bank
            _w, _h = w, h
        else:
            _spr = Image.new('RGBA', (4, 4), (0, 0, 0, 0))
            _spr.putpixel((1, 0), (180, 60, 60))
            _spr.putpixel((2, 0), (180, 60, 60))
            for xx in range(4):
                _spr.putpixel((xx, 1), (220, 80, 80))
            for xx in range(4):
                _spr.putpixel((xx, 2), (200, 60, 60))
            _spr.putpixel((1, 3), (180, 40, 40))
            _spr.putpixel((2, 3), (180, 40, 40))
            _w, _h = 4, 4

        super().__init__(x, y, _w, _h, _spr, parent, speed,
                         name=name, stackable=True, max_stack=16)
        self.heal_amount = heal_amount
        self.dropped_pos = dropped_pos

    def draw(self):
        if not self.picked_up:
            self.draw_image(self.dropped_pos[0], self.dropped_pos[1])
        elif self.parent and self.parent.current_item == self:
            pass

    def use(self, player, inventory):
        if self.quantity <= 0:
            return
        heal = min(self.heal_amount, player.max_health - player.health)
        if heal <= 0:
            return
        player.health += heal
        self.quantity -= 1
        inventory.open = False

        w = getattr(player, 'world', None)
        if w:
            w.add_floating_text(
                player.x + player.w / 2,
                player.y - 2,
                f"+{heal} HP",
                (100, 255, 100),
                30
            )
            from Entities.Particle import spawn_heal
            spawn_heal(player.x + player.w / 2, player.y + player.h / 2, w)

        if hasattr(e, 'active_camera'):
            e.active_camera.flash((100, 255, 100), 20, 6)

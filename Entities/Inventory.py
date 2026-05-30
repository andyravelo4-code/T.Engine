from PIL import Image, ImageDraw
from Engine import engine as e


class Inventory:
    SLOT = 10
    GAP = 1
    PANEL_PAD = 4
    INNER_PAD = 3
    EQUIP_COLS = 2
    CRAFT_COLS = 2
    CRAFT_ROWS = 2
    STORAGE_COLS = 5
    STORAGE_ROWS = 5

    STORE_W = STORAGE_COLS * SLOT + (STORAGE_COLS - 1) * GAP
    STORE_H = STORAGE_ROWS * SLOT + (STORAGE_ROWS - 1) * GAP
    CRAFT_W = CRAFT_COLS * SLOT + (CRAFT_COLS - 1) * GAP
    CRAFT_H = CRAFT_ROWS * SLOT + (CRAFT_ROWS - 1) * GAP
    OUT_W = SLOT + 2
    OUT_H = SLOT
    PW = STORE_W + PANEL_PAD * 2

    EQ_SEC_H = PANEL_PAD + SLOT + PANEL_PAD
    CR_SEC_H = PANEL_PAD + CRAFT_H + PANEL_PAD
    ST_SEC_H = PANEL_PAD + STORE_H + PANEL_PAD
    PH = EQ_SEC_H + INNER_PAD + CR_SEC_H + INNER_PAD + ST_SEC_H

    BG_C = (50, 50, 55)
    BG_S = (35, 35, 40)
    BG_EQ = (40, 40, 50)
    SLOT_C = (70, 70, 78)
    SLOT_E = (42, 42, 48)
    SLOT_EQ = (55, 50, 60)
    SLOT_H = (90, 90, 100)
    BORDER = (25, 25, 30)
    TT_BG = (20, 20, 25, 230)
    EQ_BORDER = (120, 100, 80)

    def __init__(self, player):
        self.player = player
        self.open = False
        self.drag_item = None
        self.drag_qty = 0
        self.hovered = -1
        self._prev_btn = False
        self._prev_rbtn = False
        self._prev_key_e = False
        self._prev_key_r = False

    def toggle(self):
        self.open = not self.open
        if not self.open:
            self._drop_drag()
            self.drag_item = None
            self.drag_qty = 0

    # ── index helpers ──────────────────────────────────────────
    @property
    def _eq_start(self):
        return 0

    @property
    def _eq_end(self):
        return 2

    @property
    def _cr_start(self):
        return 2

    @property
    def _cr_end(self):
        return 6

    @property
    def _out_idx(self):
        return 6

    @property
    def _st_start(self):
        return 7

    @property
    def _st_end(self):
        return 32

    @property
    def _crafting_count(self):
        return self._cr_end

    # ── update ─────────────────────────────────────────────────
    def update(self):
        if not self.open:
            return

        mx, my = e.mouse_x(), e.mouse_y()
        px, py = self._panel_pos()
        eqr, cr, ox, oy, sr = self._slot_rects(px, py)

        btn = e.mouse_btn(e.MOUSE_BUTTON_LEFT)
        rbtn = e.mouse_btn(e.MOUSE_BUTTON_RIGHT)
        btnp = btn and not self._prev_btn
        rbtnp = rbtn and not self._prev_rbtn
        btnr = not btn and self._prev_btn

        shiftp = e.btn(e.KEY_LSHIFT) or e.btn(e.KEY_RSHIFT)
        ep = e.btnp(e.KEY_E) and not self._prev_key_e
        rp = e.btnp(e.KEY_R) and not self._prev_rbtn

        all_rects = eqr + cr + [(ox, oy, self.OUT_W, self.OUT_H)] + sr
        self.hovered = -1
        for i, (rx, ry, rw, rh) in enumerate(all_rects):
            if rx <= mx < rx + rw and ry <= my < ry + rh:
                self.hovered = i
                break

        cc = self._crafting_count

        # Left-click press
        if btnp:
            if self.hovered >= 0 and self.drag_qty == 0:
                slot_item, slot_qty = self._slot_get(self.hovered)
                if slot_item is not None and slot_qty > 0:
                    self.drag_item = slot_item
                    if rbtn:
                        self.drag_qty = (slot_qty + 1) // 2
                    else:
                        self.drag_qty = slot_qty
                    self._slot_set(self.hovered, None, 0)

            elif self.hovered >= 0 and self.drag_qty > 0:
                self._place_drag(self.hovered, shiftp)

            elif self.hovered < 0 and self.drag_qty > 0:
                self._drop_drag()

        # Left-click release over slot with drag
        elif btnr and self.hovered >= 0 and self.drag_qty > 0:
            self._place_drag(self.hovered, shiftp)

        # Right-click consumable use
        if rbtnp and self.drag_qty == 0 and self.hovered >= 0:
            slot_item, slot_qty = self._slot_get(self.hovered)
            from Items.Consumable import Consumable
            if isinstance(slot_item, Consumable):
                self._use_consumable(slot_item, self.hovered)
            elif slot_item is not None and slot_qty > 1:
                half = slot_qty // 2
                self.drag_item = slot_item
                self.drag_qty = half
                self._slot_set(self.hovered, slot_item, slot_qty - half)

        # Shift-click quick move
        if shiftp and btnp and self.hovered >= 0 and self.drag_qty == 0:
            self._shift_move(self.hovered)

        # E key pickup
        if ep and self.drag_qty == 0 and self.hovered >= 0:
            slot_item, slot_qty = self._slot_get(self.hovered)
            if slot_item is not None:
                self.drag_item = slot_item
                self.drag_qty = slot_qty
                self._slot_set(self.hovered, None, 0)

        # R key drop
        if rp and self.drag_qty == 0 and self.hovered >= 0:
            slot_item, slot_qty = self._slot_get(self.hovered)
            if slot_item is not None:
                self._drop_item_at_world(slot_item, slot_qty)
                self._slot_set(self.hovered, None, 0)

        self._update_current()
        self._prev_btn = btn
        self._prev_rbtn = rbtn
        self._prev_key_e = ep
        self._prev_key_r = rp

    def _place_drag(self, target_idx, shiftp):
        target_item, target_qty = self._slot_get(target_idx)
        if target_item is None:
            if self._can_equip(self.drag_item, target_idx):
                self._slot_set(target_idx, self.drag_item, self.drag_qty)
                self.drag_item = None
                self.drag_qty = 0
            else:
                self._drop_drag()
        elif self.drag_item is target_item and self.drag_item.stackable:
            space = target_item.max_stack - target_qty
            put = min(self.drag_qty, space)
            self._slot_set(target_idx, target_item, target_qty + put)
            self.drag_qty -= put
            if self.drag_qty <= 0:
                self.drag_item = None
        else:
            if shiftp:
                pass
            else:
                self._slot_set(target_idx, self.drag_item, self.drag_qty)
                self.drag_item = target_item
                self.drag_qty = target_qty

    def _shift_move(self, idx):
        item, qty = self._slot_get(idx)
        if item is None:
            return
        if self._st_start <= idx < self._st_end:
            dest = self._find_storage_empty()
            if dest >= 0:
                self._slot_set(dest, item, qty)
                self._slot_set(idx, None, 0)
        elif self._cr_start <= idx < self._cr_end or self._eq_start <= idx < self._eq_end:
            dest = self._find_storage_empty_for(item)
            if dest >= 0:
                self._slot_set(dest, item, qty)
                self._slot_set(idx, None, 0)

    # ── can equip ──────────────────────────────────────────────
    def _can_equip(self, item, idx):
        from Items.Sword import Sword
        from Items.Crossbow import Crossbow
        if idx == 0:
            return isinstance(item, Sword)
        if idx == 1:
            return isinstance(item, Crossbow)
        return True

    # ── draw ───────────────────────────────────────────────────
    def draw(self):
        if not self.open:
            return

        mx, my = e.mouse_x(), e.mouse_y()
        px, py = self._panel_pos()
        eqr, cr, ox, oy, sr = self._slot_rects(px, py)

        # Outer border
        e.rect(px - 1, py - 1, self.PW + 2, self.PH + 2, self.BORDER)

        # Equipment section
        ey = py
        e.rect(px, ey, self.PW, self.EQ_SEC_H, self.BG_EQ)
        e.rectb(px, ey, self.PW, self.EQ_SEC_H, self.EQ_BORDER)
        for i, (rx, ry, rw, rh) in enumerate(eqr):
            gi = self._eq_start + i
            item, qty = self._slot_get(gi)
            hv = gi == self.hovered
            ac = (item is self.player.current_item)
            self._draw_slot(rx, ry, rw, rh, item, qty, hv, ac, is_equip=True)

        # Crafting section
        cy = py + self.EQ_SEC_H + self.INNER_PAD
        e.rect(px, cy, self.PW, self.CR_SEC_H, self.BG_C)
        for i, (rx, ry, rw, rh) in enumerate(cr):
            gi = self._cr_start + i
            item, qty = self._slot_get(gi)
            hv = gi == self.hovered
            self._draw_slot(rx, ry, rw, rh, item, qty, hv, False)

        e.rect(ox, oy, self.OUT_W, self.OUT_H, self.SLOT_E)
        if self.hovered == self._out_idx:
            e.rectb(ox - 1, oy - 1, self.OUT_W + 2, self.OUT_H + 2, self.SLOT_H)

        # Storage section
        ssy = py + self.EQ_SEC_H + self.INNER_PAD + self.CR_SEC_H + self.INNER_PAD
        e.rect(px, ssy, self.PW, self.ST_SEC_H, self.BG_S)
        for i, (rx, ry, rw, rh) in enumerate(sr):
            gi = self._st_start + i
            item, qty = self._slot_get(gi)
            hv = gi == self.hovered
            ac = (item is self.player.current_item)
            self._draw_slot(rx, ry, rw, rh, item, qty, hv, ac)

        self._draw_drag()
        self._draw_tooltip(mx, my)

    def _draw_slot(self, x, y, w, h, item, qty, hovered, active, is_equip=False):
        if item is not None and qty > 0:
            bg = self.SLOT_C
            e.rect(x, y, w, h, bg)
            e.blt(
                x + 1, y + 1, item.bank,
                item.w * item.dropped_pos[0],
                item.h * item.dropped_pos[1],
                item.w, item.h,
            )
            if qty > 1:
                ts = e.default_font(6)
                tsurf = ts.render(str(qty), False, (255, 255, 255))
                e.graphics.screen.blit(tsurf, (x + w - tsurf.get_width() - 1, y + 1))
        else:
            bg = self.SLOT_EQ if is_equip else self.SLOT_E
            e.rect(x, y, w, h, bg)
            if is_equip:
                # small indicator dot
                e.pset(x + w // 2, y + h // 2, (90, 80, 70))

        if active:
            e.rectb(x - 1, y - 1, w + 2, h + 2, (255, 210, 60))
        elif hovered:
            e.rectb(x - 1, y - 1, w + 2, h + 2, self.SLOT_H)
        elif is_equip:
            e.rectb(x - 1, y - 1, w + 2, h + 2, (80, 70, 60))

    def _draw_drag(self):
        if self.drag_item is None or self.drag_qty <= 0:
            return
        mx, my = e.mouse_x(), e.mouse_y()
        e.blt(
            mx - 4, my - 4, self.drag_item.bank,
            self.drag_item.w * self.drag_item.dropped_pos[0],
            self.drag_item.h * self.drag_item.dropped_pos[1],
            self.drag_item.w, self.drag_item.h,
        )
        if self.drag_qty > 1:
            ts = e.default_font(6)
            tsurf = ts.render(str(self.drag_qty), False, (255, 255, 255))
            e.graphics.screen.blit(tsurf, (mx + 2, my - 6))

    def _draw_tooltip(self, mx, my):
        if self.hovered < 0 or self.drag_qty > 0:
            return
        item, qty = self._slot_get(self.hovered)
        if item is None:
            return
        font = e.default_font(6)
        label = item.name
        if self._eq_start <= self.hovered < self._eq_end:
            label += " (équipé)"
        if qty > 1:
            label += f" x{qty}"
        ts = font.render(label, False, (255, 255, 255))
        tw, th = ts.get_size()
        tx = min(mx + 8, e.width() - tw - 4)
        ty = max(my - th - 4, 0)
        bg = Image.new('RGBA', (tw + 6, th + 4), self.TT_BG)
        e.graphics.screen.blit(bg, (tx - 3, ty - 2))
        e.graphics.screen.blit(ts, (tx, ty))

    # ── panel / rects ──────────────────────────────────────────
    def _panel_pos(self):
        sw = e.width()
        sh = e.height()
        return (sw - self.PW) // 2, (sh - self.PH) // 2

    def _slot_rects(self, px, py):
        # Equipment row
        eq_w = self.EQUIP_COLS * self.SLOT + (self.EQUIP_COLS - 1) * self.GAP
        eqx = px + (self.PW - eq_w) // 2
        eqy = py + self.PANEL_PAD
        eqr = []
        for c in range(self.EQUIP_COLS):
            eqr.append((
                eqx + c * (self.SLOT + self.GAP),
                eqy, self.SLOT, self.SLOT,
            ))

        # Crafting grid
        cx = px + (self.PW - self.CRAFT_W - self.GAP - self.OUT_W) // 2
        cy = py + self.EQ_SEC_H + self.INNER_PAD + self.PANEL_PAD
        cr = []
        for r in range(self.CRAFT_ROWS):
            for c in range(self.CRAFT_COLS):
                cr.append((
                    cx + c * (self.SLOT + self.GAP),
                    cy + r * (self.SLOT + self.GAP),
                    self.SLOT, self.SLOT,
                ))

        # Output slot
        ox = cx + self.CRAFT_W + self.GAP + 2
        oy = cy + (self.CRAFT_H - self.OUT_H) // 2

        # Storage grid
        ssy = py + self.EQ_SEC_H + self.INNER_PAD + self.CR_SEC_H + self.INNER_PAD + self.PANEL_PAD
        sx = px + (self.PW - self.STORE_W) // 2
        sr = []
        for r in range(self.STORAGE_ROWS):
            for c in range(self.STORAGE_COLS):
                sr.append((
                    sx + c * (self.SLOT + self.GAP),
                    ssy + r * (self.SLOT + self.GAP),
                    self.SLOT, self.SLOT,
                ))

        return eqr, cr, ox, oy, sr

    # ── slot get/set ──────────────────────────────────────────
    def _slot_get(self, idx):
        if self._eq_start <= idx < self._eq_end:
            item = self.player.equipment[idx]
            return (item, item.quantity if item else 0) if item else (None, 0)
        if self._cr_start <= idx < self._cr_end:
            i = idx - self._cr_start
            item = self.player.crafting[i]
            return (item, item.quantity if item else 0) if item else (None, 0)
        if idx == self._out_idx:
            return (None, 0)
        if self._st_start <= idx < self._st_end:
            i = idx - self._st_start
            item = self.player.items[i]
            return (item, item.quantity if item else 0) if item else (None, 0)
        return (None, 0)

    def _slot_set(self, idx, item, qty=None):
        if self._eq_start <= idx < self._eq_end:
            self.player.equipment[idx] = item
            if item:
                item.quantity = qty if qty is not None else item.quantity
            return
        if self._cr_start <= idx < self._cr_end:
            i = idx - self._cr_start
            self.player.crafting[i] = item
            if item:
                item.quantity = qty if qty is not None else item.quantity
            return
        if idx == self._out_idx:
            return
        if self._st_start <= idx < self._st_end:
            i = idx - self._st_start
            self.player.items[i] = item
            if item:
                item.quantity = qty if qty is not None else item.quantity
            return

    # ── helpers ────────────────────────────────────────────────
    def _find_storage_empty(self):
        for i in range(self.player.MAX_STORAGE):
            if self.player.items[i] is None:
                return self._st_start + i
        return -1

    def _find_storage_empty_for(self, item):
        if item and item.stackable:
            for i, slot in enumerate(self.player.items):
                if slot is not None and slot is not item and slot.can_stack_with(item):
                    space = slot.stack_space()
                    if space > 0:
                        return self._st_start + i
        return self._find_storage_empty()

    def _use_consumable(self, item, slot_idx):
        old_qty = item.quantity
        item.use(self.player, self)
        if item.quantity <= 0 < old_qty:
            self._slot_set(slot_idx, None, 0)

    def _drop_drag(self):
        if self.drag_item and self.drag_qty > 0:
            self.drag_item.quantity = self.drag_qty
            self.drag_item.picked_up = False
            self.drag_item.parent = None
            self.drag_item.x = self.player.x
            self.drag_item.y = self.player.y
            world = getattr(self.drag_item, 'world', None) or getattr(self.player, 'world', None)
            if world:
                world.add(self.drag_item)
            self.drag_item = None
            self.drag_qty = 0

    def _drop_item_at_world(self, item, qty):
        item.quantity = qty
        item.picked_up = False
        item.parent = None
        item.x = self.player.x
        item.y = self.player.y
        world = getattr(item, 'world', None) or getattr(self.player, 'world', None)
        if world:
            world.add(item)

    def _update_current(self):
        self.player._sync_current_item()

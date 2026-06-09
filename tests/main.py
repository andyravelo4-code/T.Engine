
import pyxel
import math
import time
import random as rnd
from classes import *
from particules import *
import pygame as pg
import os
import sys
os.system("clear")
nombre_adv = 5
#initialisation
pyxel.init(120,120,title= 'game',fps = 60)
pg.mixer.init(11025)
pyxel.images[0].load(0,0,'feuille1.png')
old = pyxel.colors.to_list()
new = [0x000000,0x3a4466,0x833789,0x63c64d,0x743f39,0x124f88,0x0095e9,0xffffff,0xe53b44,0xb86f50,0xffad34,0x3d8947,0x596886,0x8c9bb3,0xf7767a,0xedc7b0,0xffffff]
pyxel.colors.from_list(old)
#pyxel.fullscreen(True)
#variables
#sons
main_dir = os.path.split(os.path.abspath(__file__))[0]
attack_s = pg.mixer.Sound(os.path.join(main_dir, "sounddata", "07_human_atk_sword_1.wav"))
attack_s2 = pg.mixer.Sound(os.path.join(main_dir, "sounddata", "07_human_atk_sword_2.wav"))
damage_s = pg.mixer.Sound(os.path.join(main_dir, "sounddata", "23_orc_jump_land.wav"))
cross_s = pg.mixer.Sound(os.path.join(main_dir, "sounddata", "07_human_atk_sword_3.wav"))
walk_s = pg.mixer.Sound(os.path.join(main_dir, "sounddata", "16_human_walk_stone_2.wav"))
damage_s.set_volume(0.5)
cross_s.set_volume(0.3)
walk_s.set_volume(0.5)
attack_s.set_volume(0.7)
attack_s2.set_volume(0.5)
#fin sons
traces = []
sang = []
n = -1
p=1
w = 8
h = 8
it = 0
x = 0
encours = False
fleches = []
magies = []
fleches_en = []
droped = []
duree = 3
debut = 0
r = 0
angle_f = 0
#enemies var
ais = []
animals = []
conso = ['potion','viande']
arms = ['sword','objet']
nowover = 0
gameover = False
score = 0
on_time = 0
CAMERA_X = 0
CAMERA_Y = 0
CURSOR_X = 0
CURSOR_Y = 0
#fin enemy var
#fin variables
#sons
pyxel.sounds[1].set("c1","n","3","f",3)
pyxel.sounds[2].set("e2c2","ss","57","nn",5)
pyxel.sounds[3].set("c3g1","ss","57","nn",5)
pyxel.sounds[4].set("b2b2","nn","55","ff",2)
pyxel.sounds[5].set("a2c3","nnn","457","nns",6)
#fin sons
player = mob(0,0,8,8)
player.speed = 1
player.hp = 101
fire = mob(40,30,8,8)
cam_offsetx = 0
cam_offsety = 0
shake_dur = 20
shake_int = 4
for i in range(nombre_adv):
    animals.append(AI('marcher',rnd.randint(0,100),rnd.randint(0,100),8,8,player,nom = 'poulet'))
    ais.append(AI('suivre',rnd.randint(-100,100),rnd.randint(-100,100),8,8,player,nom = rnd.choice(['fantome','sauvage',"momie","demon"])))

objet = ArcObject(player.x+8,player.y+11, 7,math.degrees(angle(player.x,player.y,pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y)),player)

droped.append(item(rnd.randint(0,50),rnd.randint(0,50),"potion",1))
droped.append(item(rnd.randint(0,50),rnd.randint(0,50),"cross",1))
droped.append(item(rnd.randint(0,50),rnd.randint(0,50),"viande",1))
droped.append(item(rnd.randint(0,50),rnd.randint(0,50),"septre",1))
def shake(dur,inte):
    global shake_dur,shake_int
    shake_dur = dur
    shake_int = inte
    pass
def draw_game():
    global CAMERA_X,CAMERA_Y
    global n,p,w,h,x,encours,fleches,r,armes,ais,traces,sang,droped,animals,fleches_en,magies,gameover,score,shake_dur,shake_int,cam_offsetx,cam_offsety
    if gameover:
        pyxel.cls(0)
    else :
        pyxel.cls(3)
    #pyxel.circ(fire.x+4,fire.y+4,10,6 + pyxel.frame_count // 6 % 2)
    for f in fleches:
        pyxel.blt(f['x']-4,f['y']-4,0,4*8,6*8,8,8,0,rotate = r)
    for m in magies:
        dist(m['x']+4,m['y']+4,[8,2,12],sang,t = 1)
    if not gameover:  
        pyxel.blt( player.x, player.y+1, 0, 3*8, 6*8, player.w, player.h,0)  
      
    fire.animate(0,6,0,6,2)
    
    # dessisnateur de particule
    for _ in traces:
        _.draw() 
    for a in animals:
        if a.coll(objet.x,objet.y,8,8)[0] and player.att:
            #damage_s.play()
            pass
        pyxel.blt( a.x+1, a.y+1, 0, 3*8, 6*8, 8,8,0)
        a.animate(0,a.image,a.xtile,6,4) 
    for i in range(len(ais)): 
        for f in ais[i].fleche:
            pyxel.blt(f['x']-4,f['y']-4,0,4*8,6*8,8,8,0,rotate =ais[i].rot)  
        for _ in ais[i].p:
            _.draw()
        if ais[i].hp > 0:
            pyxel.blt( ais[i].x, ais[i].y+1, 0, 3*8, 6*8, 8,8,0)
            pyxel.blt(int(ais[i].armes.x), int(ais[i].armes.y),0,5*8 if ais[i].nom == "momie" else (4 if ais[i].arm_type == "mellee" else (1 if ais[i].att_r else 0))*8,8*7,ais[i].w_en,ais[i].h_en,0,rotate = ais[i].armes.rt)
            if pyxel.frame_count - ais[i].now < 12:
                pyxel.pal(11,7)
                pyxel.pal(1,7)
                pyxel.pal(9,7)
            ais[i].animate(0,ais[i].image,ais[i].xtile,8,4)
            pyxel.pal()
    if pyxel.frame_count - player.dmg < 2:
        shake(20,3)
    if pyxel.frame_count - player.dmg < 12:
        pyxel.pal(15,7)
        pyxel.pal(1,7)
    if player.hp > 0:
        player.animate(0,player.state,0,6,4)  
    pyxel.pal()
    if player.s_item == 'sword':
        pyxel.blt(int(objet.x), int(objet.y),0,3*8,8*7,w,h,0,rotate = objet.rt)
    elif player.s_item == 'cross':
        pyxel.blt(int(objet.x), int(objet.y),0,1*8 if encours else 0,7*8,8,8,0,rotate = objet.rt)
    elif player.s_item == 'septre':
        book_x = player.x + 5 * -math.cos(objet.angle)
        book_y = player.y + 5 * -math.sin(objet.angle)
        if pyxel.frame_count % 7 == 0:
            fumee(book_x+4,book_y+4,[8,2,6,5,10],sang,t = 2,p = rnd.randint(-3,3),speed = 1.3)
        if player.coll(player.x,player.y,8,8)[1] == "left":
            pyxel.blt(book_x,book_y,0,7*8,7*8,8,8,0,rotate = (math.degrees((math.pi/2)+angle(player.x+8,player.y+8,pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y))+90))
            #pyxel.blt(int(objet.x), int(objet.y),0,6*8,7*8,8,8,0,rotate = objet.rt)
        else :   
            pyxel.blt(book_x,book_y,0,7*8,7*8,-8,8,0,rotate = -(math.degrees((math.pi/2)+angle(player.x+8,player.y+8,pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y))+90))
            #pyxel.blt(int(objet.x), int(objet.y),0,6*8,7*8,-8,8,0,rotate = -objet.rt)

    elif player.s_item in conso:
        match player.s_item:
            case 'potion':
                pyxel.blt(int(objet.x), int(objet.y),0,5*8,6*8,8,8,0)
            case 'viande':
                pyxel.blt(int(objet.x), int(objet.y),0,6*8,6*8,8,8,0)
    for _ in sang:
        _.draw()
    for f in fleches:
        for i in range(len(ais)):
            if ais[i].coll(f['x'],f['y'],8,8)[0]:
                #damage_s.play()
                ais[i].now = pyxel.frame_count
    for f in magies:
        for i in range(len(ais)):
            if ais[i].coll(f['x'],f['y'],8,8)[0]:
                damage_s.play()
                ais[i].now = pyxel.frame_count
    for i in range(len(ais)):  
        if ais[i].coll(objet.x,objet.y,8,8)[0] and player.att:
            damage_s.play()
            ais[i].now = pyxel.frame_count
        for f in ais[i].fleche:
            if player.coll(f['x'],f['y'],8,8)[0]:
                damage_s.play()
                player.dmg = pyxel.frame_count
        if player.coll(ais[i].x,ais[i].y,8,8)[0] and ais[i].att:
            damage_s.play()
            player.dmg = pyxel.frame_count
        
        
    #for i in range(len(player.item)):
     #   pyxel.rect(CAMERA_X+i*8+(pyxel.width/2-len(player.item)*8/2),CAMERA_Y+pyxel.height-8,8,8,7)
      #  pyxel.rectb(CAMERA_X+i*8+(pyxel.width/2-len(player.item)*8/2),CAMERA_Y+pyxel.height-8,8,8,5)
    #pyxel.rectb(objet.x-2,objet.y-2,12,12,7)
    for item in droped:
        item.draw()
        if player.coll(item.x,item.y,8,8)[0]:
            pyxel.text(player.x+3,player.y-5,'f',7)
            pyxel.circb(item.x+4,item.y+4,4,7)
            if pyxel.btnp(pyxel.KEY_F):
                pyxel.play(0,3)
                player.item.append(item.name)
                item.pris = True
    cx = (CURSOR_X-player.x) / 5
    cy = (CURSOR_Y-player.y) / 5
    cx = limit(cx,-10,10)
    cy = limit(cy,-10,10)
    pyxel.circb(pyxel.mouse_x+CAMERA_X +cx,pyxel.mouse_y+CAMERA_Y+cy,4 if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) else 2,7)
    pyxel.pset(pyxel.mouse_x+CAMERA_X +cx,pyxel.mouse_y+CAMERA_Y+cy,4 if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) else 7)
    pyxel.rect(CAMERA_X+cx+20,CAMERA_Y+cy+9,player.hp*19//40,3,7 if pyxel.frame_count - player.dmg < 15 else 5)
    pyxel.circb(CAMERA_X+cx+10,CAMERA_Y+cy+10,7,1)
    pyxel.rectb(CAMERA_X+cx+19,CAMERA_Y+cy+8,20,5,5)
    pyxel.rectb(CAMERA_X+cx+8,CAMERA_Y+cy+19,5,20,5)
    pyxel.circb(CAMERA_X+cx+(pyxel.width-10-len(str(int(score)))*3)+(len(str(int(score)))*2),CAMERA_Y+cy+10,8,10)
    pyxel.text(CAMERA_X+cx+(pyxel.width-9-len(str(int(score)))*3),CAMERA_Y+cy+8,str(int(score)),10)
    match player.s_item:
        case 'sword':
            pyxel.blt(CAMERA_X+cx+7,CAMERA_Y+cy+7,0,3*8,8*7,8,8,0,rotate = -40)
        case 'cross':
            pyxel.blt(CAMERA_X+cx+7,CAMERA_Y+cy+7,0,0*8,8*7,8,8,0,rotate = -40)
        case 'septre':
            pyxel.blt(CAMERA_X+cx+6,CAMERA_Y+cy+7,0,6*8,8*7,8,8,0)
        case _ :
            pyxel.fill(CAMERA_X+cx+10,CAMERA_Y+cy+10,1)
    
def update_game():
    global CAMERA_X,CAMERA_Y,CURSOR_X,CURSOR_Y
    CAMERA_X = player.x-(pyxel.width/2-player.w/2)
    CAMERA_Y = player.y-(pyxel.height/2-player.h/2)
    CURSOR_X = pyxel.mouse_x+CAMERA_X
    CURSOR_Y = pyxel.mouse_y+CAMERA_Y
    
    global score,gameover,magies,r_,fleches_en,animals,droped,n,p,w,h,it,duree,debut,encours,x,fleches,angle_f,r,now,p_en,n_en,h_en,w_en,on_time,armes,ais,traces,sang,shake_dur,shake_int,cam_offsetx,cam_offsety
    #joueur principal
    if shake_dur > 0:
        shake_dur -= 1
        if shake_dur % 5 == 0:
            shake_int = max(0, shake_int - 1)
    else:
        shake_int = 0
    cam_offsetx = 0
    cam_offsety = 0
    if shake_int > 0:
        cam_offsetx = rnd.randint(-shake_int,shake_int)
        cam_offsety = rnd.randint(-shake_int,shake_int)
    if player.hp > 0:
        gameover = False
    if player.hp > 40:
        player.hp = 40
    player.push_back(fire.x,fire.y+4,8,4,1)
    if pyxel.btnp(pyxel.KEY_R):
        if player.s_item != '':
            pyxel.play(0,2)
            i = player.item.index(player.s_item)
            droped.append(item(player.x+5,player.y+5,player.s_item,1))
            del player.item[i]
            if len(player.item) != 0:
                player.s_item = player.item[it % len(player.item) - 1]
            else :
                player.s_item = ''
    player.vx = 0
    player.vy = 0
    if pyxel.btnp(pyxel.KEY_SPACE):
        shake(20,4)
    if player.hp <= 0 and not gameover:
        for i in range(len(player.item)): 
            player.s_item = ''   
            #droped.append(item(player.x + rnd.randint(-10,10),player.y + rnd.randint(-10,10),player.item[i],1))
            #player.item.remove(player.item[i])
        dist(player.x+4,player.y+4,[7,13],sang,t = 1)
        if pyxel.frame_count % 2 == 0:
            player.hp -= 1
    if player.hp <= -15:
        gameover = True
    else:
        gameover = False
    if pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_Z):
        player.lasty = 1
        player.state = 2
        player.vy=-player.speed
        player.y+=player.vy
        foot(player.x+3,player.y+7,traces)
    if pyxel.btn(pyxel.KEY_S) :
        player.lasty = 1
        player.state = 3
        player.vy=player.speed
        player.y+= player.vy
        foot(player.x+3,player.y+7,traces)
    if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_Q) :
        player.lastx = -1
        if player.coll(pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y,8,8)[1] == 'right' and player.att:
            player.state = 1
        elif player.coll(pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y,8,8)[1] == 'left' and player.att:
            player.state = 0
        else :
            player.state = 1
        player.vx=-player.speed
        player.x+= player.vx
        foot(player.x+3,player.y+7,traces)
    if pyxel.btn(pyxel.KEY_D) :
        player.lastx = 1
        if player.coll(pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y,8,8)[1] == 'right' and player.att:
            player.state = 1
        elif player.coll(pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y,8,8)[1] == 'left' and player.att:
            player.state = 0
        else :
            player.state = 0
        player.vx=player.speed
        player.x+= player.vx
        foot(player.x+3,player.y+7,traces)
    #if player.vx != 0 or player.vy != 0:
     #   if pyxel.frame_count % 17 == 0:
            #walk_s.play()
    if not (pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_Q) or pyxel.btn(pyxel.KEY_Z)):
        if player.coll(pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y,8,8)[1] == 'right':
            player.state = 5
        elif player.coll(pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y,8,8)[1] == 'left':
            player.state = 4

    if len(player.item) != 0:
        player.s_item = player.item[it % len(player.item) - 1]

    if pyxel.btnp(pyxel.KEY_E):
        it+=1
        if len(player.item) != 0:
            pyxel.play(0,3)
            player.s_item = player.item[it % len(player.item) - 1]

    if player.s_item == 'sword':
        objet.duree_animation = rnd.randint(2,6)
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and not objet.animation_en_cours:
            attack_s.play()
            p*=-1
            n*=-1
            objet.demarrer_animation(objet.angle+(math.pi)*p)
        if  objet.animation_en_cours == False:
            objet.radius = objet.init_radius
            objet.angle = angle(player.x,player.y,pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y)+(math.pi/2)*-n
            objet.rt = math.degrees(angle(player.x,player.y,pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y))
            w = 8*n
            h = 8*n
        elif objet.animation_en_cours: 
            objet.radius += 0.4
            objet.rt+=15*p
        if player.att:
            foot(objet.x+4,objet.y+4,sang,g = [8,2],fr = 1,t = 2) 
        objet.act()
        objet.x = player.x + objet.radius * math.cos(objet.angle)
        objet.y = player.y + objet.radius * math.sin(objet.angle)
        objet.center_x = player.x
        objet.center_y = player.y
        objet.x = objet.x
        objet.y = objet.y
    elif player.s_item == 'cross':
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and not encours:
            cross_s.play(fade_ms = 100)
            r = objet.rt
            angle_f = angle(player.x,player.y,pyxel.mouse_x-8+CAMERA_X,pyxel.mouse_y-8+CAMERA_Y)
            #cible = cible2
            encours = True
            debut = pyxel.frame_count
            fleches.append({"x": player.x+4, "y": player.y+4, "angle": angle_f, "speed" : 3})
            
        if encours:
            objet.radius -= 0.1
            passe = pyxel.frame_count - debut
            if  not passe < duree+rnd.randint(10,20):
                encours = False 
                objet.radius = objet.init_radius+1  
        fleches = [f for f in fleches if player.x-100 <= f["x"] <= player.x+100 and player.y-100 <= f["y"] <= player.y+100 and f['speed'] == 3]
        objet.x = player.x + objet.radius * math.cos(objet.angle)
        objet.y = player.y + objet.radius * math.sin(objet.angle)   
        objet.center_x = player.x
        objet.center_y = player.y+2
        objet.angle = angle(player.x+8,player.y+8,pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y)
        objet.rt = math.degrees(angle(player.x+8,player.y+8,pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y))+90
    elif player.s_item == "septre":
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and not encours:
            cross_s.play(fade_ms = 100)
            r = objet.rt
            angle_f = angle(player.x,player.y,pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y)
            #cible = cible2
            encours = True
            debut = pyxel.frame_count
            magies.append({"x": objet.x, "y": objet.y, "angle": angle_f, "speed" : 3})
            
        if encours:
            if player.coll(objet.x,objet.y,8,8)[1] == "left":
                objet.radius += 0.5
                objet.rt += 20
            else:
                objet.radius += 0.5
                objet.rt -= 20
            passe = pyxel.frame_count - debut
            if  not passe < duree+rnd.randint(10,20):
                encours = False 
                objet.radius = objet.init_radius+1  
        else :
            objet.rt = math.degrees((math.pi/4)+angle(player.x+8,player.y+8,pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y))+90
        magies = [f for f in magies if player.x-100 <= f["x"] <= player.x+100 and player.y-100 <= f["y"] <= player.y+100 and f['speed'] == 3]
        objet.x = objet.x
        objet.y = objet.y
        objet.x = player.x + objet.radius * math.cos(objet.angle)
        objet.y = player.y + objet.radius * math.sin(objet.angle)
        objet.center_x = player.x
        objet.center_y = player.y+2
        objet.angle = (math.pi/2)+angle(player.x+8,player.y+8,pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y)
        
    if player.s_item in conso:
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and not encours:
            match player.s_item:
                case 'potion':
                    player.hp += 20
                case 'viande':
                    player.hp += 10
                case _ :
                    player.hp += 0
            
            encours = True
            debut = pyxel.frame_count
        if encours:
            objet.radius -= 0.5
            fumee(player.x+4,player.y+4,[8,2],sang,t = 2,p = rnd.randint(-3,3))
            passe = pyxel.frame_count - debut
            if  not passe < duree+3:
                objet.radius = objet.init_radius
                encours = False 
                del player.item[player.item.index(player.s_item)]
                if len(player.item) != 0:
                    player.s_item = player.item[it % len(player.item) - 1]
                else :
                    player.s_item = ''
        objet.x = objet.center_x + objet.radius * math.cos(objet.angle)
        objet.y = objet.center_y + objet.radius * math.sin(objet.angle)
        objet.center_x = player.x
        objet.center_y = player.y
        objet.angle = angle(player.x+8,player.y+8,pyxel.mouse_x+CAMERA_X,pyxel.mouse_y+CAMERA_Y)
    for f in fleches:
        f["x"] += math.cos(f["angle"]) * f["speed"] 
        f["y"] += math.sin(f["angle"]) * f["speed"]
    for f in magies:
        f["x"] += math.cos(f["angle"]) * f["speed"] 
        f["y"] += math.sin(f["angle"]) * f["speed"]

    droped = [d for d in droped if not d.pris]
    cx = (CURSOR_X-player.x) / 5
    cy = (CURSOR_Y-player.y) / 5
    cx = limit(cx,-10,10)
    cy = limit(cy,-10,10)

    pyxel.camera(CAMERA_X+cx+cam_offsetx,CAMERA_Y+cy+cam_offsety)

    #fin joueur principal
    #particule 
    traces = [p for p in traces if p.lifetime > 0]
    if pyxel.frame_count % 9 == 0:
        fumee(fire.x+4,fire.y-2,[7,13],sang,t = 1)
    for t in traces:
        t.update()
    sang = [s for s in sang if s.lifetime > 0]
    for s in sang:
        s.update()    
    #fin particules 
    #point de vie 
    
    for i in range(len(animals)):
        c = rnd.randint(1,2)
        if animals[i].hp == -9 and c == 2:
            droped.append(item(animals[i].x,animals[i].y,'viande',1))
        if animals[i].hp <= 0:
            animals[i].etat = 'stop'
            dist(animals[i].x+rnd.randint(0,8),animals[i].y+rnd.randint(0,8),[7,13],sang,t = 1)
           # dist(ai.x+4,ai.y+4,[8,2,15],sang,speed = 2.3,life = rnd.randint(5,6))
            animals[i].hp -= 0.5
    # fin   
    #boucles des autres mobs
    for o in ais:
        o.update()
    animals = [a for a in animals if a.hp > -10]
    for a in animals:
        if a.coll(objet.x,objet.y,8,8)[0] and player.att:
            dist(a.x+4,a.y+rnd.randint(3,5),[8,2],sang)
            dist(objet.x+4,objet.y+rnd.randint(3,5),[8,2],sang)
            a.push_back(objet.x,objet.y,8,8,4)
            if pyxel.frame_count - on_time > 3:
                a.hp -= rnd.randint(3,4)               
                on_time = pyxel.frame_count 
        for f in fleches:
            if a.coll(f['x'],f['y'],8,8)[0]:
                f['speed'] = 2
                for _ in range(10):
                    dist(a.x+4,a.y+rnd.randint(3,5),[8,2],sang)
                a.hp -= rnd.randint(3,5)  
    #boucles des enemie
    for o in animals:
        o.update()
    ais = [ai for ai in ais if ai.hp > -10]
    for ai in ais:
        if ai.hp <= 0:
            ai.etat = 'stop'
            dist(ai.x+4,ai.y+4,[7,13],sang,t = 1)
            #dist(ai.x+4,ai.y+4,[8,2,15],sang,speed = 2.3,life = rnd.randint(5,6))
            if pyxel.frame_count % 2 == 0:
                ai.hp -= 1
                score += 0.4
    for e in ais:
        e.push_back(fire.x,fire.y,8,8,1)
    for a in ais:
        if a.coll(fire.x,fire.y,8,8)[0]:
            a.etat = 'marcher'
        else :
            a.etat = a.p_etat
        if a.coll(objet.x,objet.y,8,8)[0] and player.att:
            foot(objet.x+4,objet.y+4,traces,g= [8])
            for i in range(rnd.randint(2,5)):
                dist(objet.x+4,objet.y+rnd.randint(3,5),[8,2],traces,t = 1)
            a.push_back(objet.x,objet.y,8,8,4)
            if pyxel.frame_count - on_time > 3:
                shake(20,3)
                a.hp -= rnd.randint(3,4)               
                on_time = pyxel.frame_count              
    for i in range(len(ais)):
        if ais[i].target.hp < 0:
            ais[i].etat = "marcher"
        if ais[i].target == player:
            for j in range(len(ais)): 
                if i is not j:
                    princ = ais[i]
                    other = ais[j]
                    dx = ais[i].x - ais[j].x
                    dy = ais[i].y - ais[j].y
                    if dx * dx + dy * dy <= 400:
                        other.etat = 'marcher'
                    elif (princ.dist < other.dist):
                        if princ.hp > 6:
                            princ.etat = princ.p_etat
                            other.etat = 'stop'
                        else :
                            princ.etat = 'fuire'
                            other.etat = 'stop'
                if len(ais) == 1:
                    ais[0].etat = ais[i].p_etat
    #collisions
        if ais[i].target.coll(ais[i].armes.x,ais[i].armes.y,8,8)[0] and ais[i].att:
            dist(ais[i].target.x+4,ais[i].target.y+rnd.randint(3,5),[8,2],sang,life = rnd.randint(60,150))
            ais[i].target.push_back(ais[i].armes.x,ais[i].armes.y,8,8,4)
            ais[i].target.hp -= rnd.uniform(1,3)
            on_time = pyxel.frame_count
            shake(20,3)
           
        for f in fleches:
            if ais[i].coll(f['x'],f['y'],8,8)[0]:
                shake(10,3)
                f['speed'] = 2
                for _ in range(10):
                    dist(ais[i].x+4,ais[i].y+rnd.randint(3,5),[8,2],traces,t = 1)
                if pyxel.frame_count - on_time > 5:
                    ais[i].hp -= rnd.randint(3,4)               
                    on_time = pyxel.frame_count
        for f in magies:
            if ais[i].coll(f['x'],f['y'],8,8)[0]:
                f['speed'] = 2
                for _ in range(10):
                    dist(ais[i].x+4,ais[i].y+rnd.randint(3,5),[8,2],sang)
                if pyxel.frame_count - on_time > 5:
                    ais[i].hp -= rnd.randint(3,4)               
                    on_time = pyxel.frame_count
        for f in ais[i].fleche :
            if objet.coll(f['x'],f['y'],8,8)[0] and player.att:
                f["angle"] = rnd.uniform(0,math.pi*2)
                ais[i].rot = math.degrees(f["angle"])
            if ais[i].target.coll(f['x'],f['y'],8,8)[0]:
                f["speed"] = 2
                ais[i].target.hp -= rnd.uniform(0.5,1.5)
                for _ in range(10):
                    dist(ais[i].target.x+4,ais[i].target.y+rnd.randint(3,5),[8,2],sang,life = rnd.randint(60,150))
    ## enemy arme
        for f in ais[i].fleche:
            f["x"] += math.cos(f["angle"]) * f["speed"] 
            f["y"] += math.sin(f["angle"]) * f["speed"]
        ais[i].armes.x = ais[i].armes.center_x + ais[i].armes.radius * math.cos(ais[i].armes.angle)
        ais[i].armes.y = ais[i].armes.center_y + ais[i].armes.radius * math.sin(ais[i].armes.angle)
        ais[i].armes.center_x = ais[i].x
        ais[i].armes.center_y = ais[i].y
        if ais[i].arm_type == "mellee":
            ais[i].armes.act()
            ais[i].armes.duree_animation = rnd.randint(3,5)
            if (ais[i].dist <= 16 and ais[i].target.hp >= 0) and ((ais[i].etat == 'suivre') or (ais[i].etat == 'stop')):
                if pyxel.frame_count % 60 == 0 and not ais[i].armes.animation_en_cours :
                    ais[i].p_en*= -1
                    ais[i].n_en*= -1 
                    attack_s2.play()
                    ais[i].armes.demarrer_animation(ais[i].armes.angle + math.pi*ais[i].p_en)
            if not ais[i].armes.animation_en_cours:
                ais[i].att = False
                ais[i].armes.angle = angle(ais[i].x,ais[i].y,ais[i].target.x,ais[i].target.y)+math.pi/2*-ais[i].n_en
                ais[i].armes.rt = math.degrees(angle(ais[i].x,ais[i].y,ais[i].target.x,ais[i].target.y))
            
                ais[i].w_en = 8*ais[i].n_en

                ais[i].h_en = 8*ais[i].n_en 
            elif ais[i].armes.animation_en_cours:
                ais[i].armes.rt+=15*ais[i].p_en
                ais[i].att = True
        elif ais[i].arm_type == "range":
            if (ais[i].dist <= 70 and ais[i].target.hp >= 0) and ((ais[i].etat == 'fuire') or (ais[i].etat == 'marcher')) and pyxel.frame_count % 70 == 0:
                ais[i].rot = ais[i].armes.rt
                angle_f = angle(ais[i].x,ais[i].y,ais[i].target.x,ais[i].target.y)
                ais[i].att_r = True
                ais[i].att_t = pyxel.frame_count
                ais[i].fleche.append({"x": ais[i].x+4, "y": ais[i].y+4, "angle": angle_f, "speed" : 3})
            
            if ais[i].att_r:
                passe = pyxel.frame_count - ais[i].att_t
                if  not passe < duree+20:
                    ais[i].att_r = False    
            ais[i].fleche = [f for f in ais[i].fleche if ais[i].x-80 <= f["x"] <= ais[i].x+80 and ais[i].y-80 <= f["y"] <= ais[i].y+80 and f["speed"] == 3]
            ais[i].armes.x = ais[i].armes.center_x + ais[i].armes.radius * math.cos(ais[i].armes.angle)
            ais[i].armes.y = ais[i].armes.center_y + ais[i].armes.radius * math.sin(ais[i].armes.angle)
            ais[i].armes.center_x = ais[i].x
            ais[i].armes.center_y = ais[i].y+2
            ais[i].armes.angle = angle(ais[i].x,ais[i].y,ais[i].target.x,ais[i].target.y)
            ais[i].armes.rt = math.degrees(angle(ais[i].x,ais[i].y,ais[i].target.x,ais[i].target.y))+90 
    ## fin enemy arme

playg = btn(pyxel.width/2-20,20,40,12)
quitg = btn(pyxel.width/2-20,40,40,12)
menug = btn(pyxel.width/2-20,60,40,12)
paramg = btn(pyxel.width/2-20,70,40,12)
fullscreen = btn(pyxel.width/2-20,20,40,12)
score_style = 0
def game_over():
    global score_style,score
    pyxel.cls(8)
    playg.set_clicker(pyxel.mouse_x,pyxel.mouse_y,8,8)
    quitg.set_clicker(pyxel.mouse_x,pyxel.mouse_y,8,8)
    menug.set_clicker(pyxel.mouse_x,pyxel.mouse_y,8,8)
    pyxel.text(43,10,"GAME OVER",7)
    if pyxel.frame_count % 2 == 0:
        if score_style < score:
            score_style += 0.1
    pyxel.circb(pyxel.width/2-(len(str(int(score_style)))*2),92.5,score_style,7)
    pyxel.text(pyxel.width/2-(len(str(int(score_style)))*4)/2,90,str(int(score_style)),7)
    playg.draw('r',7 if playg.hover() else 2)
    playg.setcaption('RESTART',2)
    quitg.draw('r',8 if quitg.hover() else 2)
    quitg.setcaption('QUIT',2)
    menug.draw('r',8 if menug.hover() else 2)
    menug.setcaption('MENU',2)
    pyxel.circ(pyxel.mouse_x,pyxel.mouse_y,3,7)
def game_over_u():
    global gameover,ais,score
    pyxel.camera(0,0)
    if playg.onclick():
        player.x = 0
        player.y = 0
        score = 0
        ais.clear()
        for i in range(nombre_adv):
            animals.append(AI('marcher',rnd.randint(0,100),rnd.randint(0,100),8,8,player,nom = 'poulet'))
            ais.append(AI('suivre',rnd.randint(-100,100),rnd.randint(-100,100),8,8,player,nom = rnd.choice(['fantome','sauvage',"momie","demon"])))

        print('played')
        player.hp = 40
    elif menug.onclick():
        player.hp = 101
        gameover = False
    elif quitg.onclick():
        pyxel.quit()
def menu_draw():
    pyxel.cls(1)
    paramg.set_clicker(pyxel.mouse_x,pyxel.mouse_y,2,2)
    playg.set_clicker(pyxel.mouse_x,pyxel.mouse_y,2,2)
    quitg.set_clicker(pyxel.mouse_x,pyxel.mouse_y,2,2)
    playg.draw('r',7 if playg.hover() else 2)
    playg.setcaption('PLAY',2)
    quitg.draw('r',8 if quitg.hover() else 2)
    quitg.setcaption('QUIT',8)
    paramg.draw('r', 3 if paramg.hover() else 2)
    paramg.setcaption('SETTINGS',2)
    pyxel.circ(pyxel.mouse_x,pyxel.mouse_y,3,7)

    pass
def menu_u():
    global score
    if playg.onclick():
        print('played')
        player.x = 0 
        player.y = 0
        score = 0
        player.hp = 40
    elif quitg.onclick():
        os.system("clear")
        print("bye(*o*)!")
        pyxel.quit()
def draw():
    if player.hp <= -15:
        game_over()
    elif player.hp > 100:
        menu_draw()
    else:
        draw_game()
def update():
    if player.hp <= -15:
        game_over_u()
    elif player.hp > 100:
        menu_u()
    else :
        update_game()
pyxel.run(draw,update)

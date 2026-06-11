# Wall Tile Mapping Reference

## Spritesheet walls.png
![Spritesheet reference](wall_spritesheet_reference.png)

## Nouveau Mapping (utilisateur)

| Tile # | Name | Sheet Pos | Description |
|--------|------|-----------|-------------|
| 20 | horiz_n | (1,0) | mur E-W, face S (room au S) |
| 21 | horiz_s | (1,2) | mur E-W, face N (room au N) |
| 22 | vert_e | (2,0) | mur N-S, face E (room a l'W) |
| 23 | vert_w | (0,0) | mur N-S, face W (room a l'E) |
| 24 | limite_NW | (0,0) | coin ext NW (partage avec vert_w) |
| 25 | limite_NE | (2,0) | coin ext NE (partage avec vert_e) |
| 26 | limite_SW | (0,2) | coin ext SW |
| 27 | limite_SE | (2,2) | coin ext SE |
| 28 | deviation_nw | (0,3) | coin int NW |
| 29 | deviation_ne | (1,3) | coin int NE |
| 30 | deviation_sw | (0,1) | coin int SW |
| 31 | deviation_se | (2,1) | coin int SE |

## Room Example
![Room example with sprites](room_example.png)

## Sprite positions libres
- **(2,3)**: 64px opaque, couleur claire — **toujours libre**

## Corrections appliquees
1. `_enclose_with_walls`: detection des coins par diagonales
2. `_classify_walls`: T-junctions (wc=3) → murs droits
3. `_build_blocks`: plus de doublons de sol
4. `World.draw()`: frustum culling

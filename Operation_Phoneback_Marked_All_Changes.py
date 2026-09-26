# ================================================================
# OPERATION PHONEBACK - MARKED VERSION
# Final Lab 3 compliant version with every changed area marked.
# Search for: >>> CHANGED
# Any gameplay code without a CHANGED marker stayed the same.
# ================================================================

# MAIN CHANGES
# 1. Removed keys[] + keyboardUp system and changed W/S/A/D to Lab 3 style.
# 2. Added player_move_timer only for short RUN animation after a movement key.
# 3. Added quadric + gluNewQuadric() and replaced GLUT solid spheres with gluSphere().
# 4. Replaced glutWireSphere() with a custom line-loop sphere.
# 5. Removed glLineWidth(), glVertex2f(), glDisable(), glClearColor(), glutKeyboardUpFunc().
# 6. Added cube-made sky because glClearColor() was removed.
# 7. HUD now uses glVertex3f(...,0) and depth-buffer clearing.
# 8. Added glViewport() like the Lab 3 template.
# ================================================================

# Checkpoint 1 - Game Data and World Setup
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

window_W = 1200
window_H = 800
world_limit = 1300
player = {"x":0.0,"y":-80.0,"z":0.0,"angle":90.0,"vz":0.0,"speed":190.0,"jump":290.0,"radius":18.0}
selected_character = 0
character_names = ["Investigator","Runner","Tracker"]
character_stats = [(190.0,290.0),(235.0,350.0),(195.0,295.0)]
# >>> CHANGED 1 - GLOBAL INPUT/SPHERE DATA
# Old code had keys = []. New code uses a short movement-animation timer, and quadric is needed for Lab 3 gluSphere().
player_move_timer = 0.0
quadric = None
paused = False
game_state = "SELECT"
last_time = time.time()
game_time = 0.0
mission_time = 120.0
score = 0
wrong_capture = 0
phone_stolen = False
phone_owner = -1
thief_id = -1
accomplice_id = -1
npcs = []
projectiles = []
stun_ammo = 8
evidence = []
last_message = "Choose a character: 1 Investigator, 2 Runner, 3 Tracker"
message_timer = 999.0
remote_cooldown = 0.0
ring_timer = 0.0
ring_holder = -1
handoff_planned = False
handoff_done = False
handoff_detected = False
cctv_mode = False
cctv_index = 0
cctv_watch = 0.0
cctv_scored = []
shortcut_timer = 0.0
shortcut_armed = False
last_collision_penalty = 0.0

shirt_colors = [
    (0.15,0.35,0.95,"Blue"),(0.90,0.18,0.18,"Red"),(0.18,0.70,0.25,"Green"),
    (0.95,0.75,0.12,"Yellow"),(0.70,0.25,0.80,"Purple"),(0.95,0.45,0.10,"Orange")
]
size_values = [(0.88,"Small"),(1.0,"Medium"),(1.14,"Tall")]

routes = [
    {"dir":"East","points":[(250,90),(520,110),(790,90),(1060,120),(1240,130)]},
    {"dir":"West","points":[(-240,100),(-500,180),(-780,150),(-1050,110),(-1240,90)]},
    {"dir":"North","points":[(90,250),(120,520),(60,790),(150,1040),(120,1240)]},
    {"dir":"South","points":[(-80,-260),(-130,-520),(-30,-800),(-150,-1060),(-110,-1240)]},
    {"dir":"North-East","points":[(230,210),(360,430),(420,690),(520,980),(860,1120),(1240,1180)]},
    {"dir":"South-West","points":[(-230,-220),(-360,-430),(-420,-690),(-520,-980),(-860,-1120),(-1240,-1180)]}
]

cameras = [
    {"name":"Central Market","eye":(-190,-760,500),"target":(0,110,30),"center":(-190,100)},
    {"name":"East Alley","eye":(1020,-180,420),"target":(620,140,20),"center":(670,140)},
    {"name":"North Street","eye":(190,790,450),"target":(40,560,20),"center":(190,760)},
    {"name":"West Market","eye":(-1030,120,420),"target":(-560,140,20),"center":(-650,140)}
]

obstacles = [
    (-210,-82,120,42,52),(215,-82,140,40,56),(-215,455,130,42,50),(215,455,140,46,54),
    (-215,-395,120,40,56),(215,-395,125,42,58),(760,-82,130,42,52),(-760,-82,130,42,52)
]

buildings = [
    (-1060,1040,420,400,500),(-650,1130,360,340,560),(660,1160,390,360,520),(1080,1050,430,420,610),
    (-1080,-820,450,400,560),(-640,-1130,360,340,460),(660,-1150,390,360,580),(1090,-820,430,400,500),
    (-760,960,280,250,320),(780,950,290,260,340)
]
stalls = [(-420,110),(420,120),(-430,-78),(440,-78),(-760,40),(760,30)]

gaps = [(250,470,180,40),(560,-430,40,180),(-580,430,40,180)]
shortcut_zones = [(300,430,160,340),(-300,-470,160,340),(760,760,180,280),(-760,-760,180,280)]
terminal = (-190,-760)

cars = [
    {"x":-1180.0,"y":-205.0,"dir":1,"speed":175.0,"axis":"x"},{"x":1040.0,"y":-255.0,"dir":-1,"speed":195.0,"axis":"x"},
    {"x":-1120.0,"y":585.0,"dir":1,"speed":165.0,"axis":"x"},{"x":1180.0,"y":635.0,"dir":-1,"speed":185.0,"axis":"x"},
    {"x":-38.0,"y":-1180.0,"dir":1,"speed":170.0,"axis":"y"},{"x":38.0,"y":1180.0,"dir":-1,"speed":185.0,"axis":"y"}
]


# Checkpoint 2 - Basic Helper Functions

def clamp(v,a,b):
    return max(a,min(b,v))

def dist(x1,y1,x2,y2):
    return math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))

def angle_to(x1,y1,x2,y2):
    return math.degrees(math.atan2(y2-y1,x2-x1))

def set_message(text,duration=3.0):
    global last_message,message_timer
    last_message = text
    message_timer = duration

def darker(color,factor):
    return (color[0]*factor,color[1]*factor,color[2]*factor)

def lighter(color,amount):
    return (min(1,color[0]+amount),min(1,color[1]+amount),min(1,color[2]+amount))

def key_name(key):
    if isinstance(key,bytes):
        return key.decode("utf-8").lower()
    return str(key).lower()


# Checkpoint 3 - Character Selection and Game Reset

def set_character(index):
    global selected_character
    selected_character = index
    player["speed"],player["jump"] = character_stats[index]

def reset_game():
    global game_state,paused,game_time,mission_time,score,wrong_capture,phone_stolen,phone_owner
    global thief_id,accomplice_id,npcs,projectiles,stun_ammo,evidence,last_time,remote_cooldown,ring_timer,ring_holder
    global handoff_planned,handoff_done,handoff_detected,cctv_mode,cctv_index,cctv_watch,cctv_scored
    # >>> CHANGED 2A - RESET GLOBAL
    # player_move_timer was added to reset_game() because the old keys[] movement state no longer exists.
    global shortcut_timer,shortcut_armed,last_collision_penalty,player_move_timer
    player["x"],player["y"],player["z"],player["angle"],player["vz"] = 0.0,-80.0,0.0,90.0,0.0
    set_character(selected_character)
    game_state = "PLAY"
    paused = False
    game_time = 0.0
    mission_time = 120.0
    score = 0
    wrong_capture = 0
    phone_stolen = False
    phone_owner = -1
    projectiles = []
    stun_ammo = 8
    evidence = []
    remote_cooldown = 0.0
    ring_timer = 0.0
    ring_holder = -1
    handoff_planned = random.random() < 0.7
    handoff_done = False
    handoff_detected = False
    cctv_mode = False
    cctv_index = 0
    cctv_watch = 0.0
    cctv_scored = []
    shortcut_timer = 0.0
    shortcut_armed = False
    last_collision_penalty = 0.0
    # >>> CHANGED 2B - RESET MOVEMENT TIMER
    # Reset the new movement-animation timer when starting a fresh round.
    player_move_timer = 0.0
    npcs = []
    for i in range(14):
        while True:
            a = random.uniform(0,math.pi*2)
            r = random.uniform(260,980)
            sx,sy = math.cos(a)*r,math.sin(a)*r
            if not obstacle_hit(sx,sy,0,16):
                break
        c = random.randrange(len(shirt_colors))
        s = random.randrange(len(size_values))
        npcs.append({
            "x":sx,"y":sy,"z":0.0,"vz":0.0,"angle":random.uniform(0,360),
            "speed":random.uniform(55,90),"role":"CIVILIAN","state":"WALK","color":c,"size":s,
            "hat":random.random()<0.35,"target":(random.uniform(-1080,1080),random.uniform(-1080,1080)),
            "route":-1,"wp":0,"stun":0.0,"dodge_cd":0.0,"asked":False,"clue":None,
            "state_time":0.0,"blend_cd":0.0
        })
    thief_id = random.randrange(len(npcs))
    accomplice_id = random.randrange(len(npcs))
    while accomplice_id == thief_id:
        accomplice_id = random.randrange(len(npcs))
    npcs[thief_id]["role"] = "THIEF"
    npcs[thief_id]["state"] = "BLEND"
    npcs[accomplice_id]["role"] = "ACCOMPLICE"
    npcs[accomplice_id]["state"] = "WALK"
    last_time = time.time()
    set_message("Stay alert. Someone in this crowd is watching you.",4.0)


# Checkpoint 4 - Collision and Walkable Surfaces

def point_in_rect(x,y,rect):
    rx,ry,rw,rh = rect
    return abs(x-rx) <= rw/2 and abs(y-ry) <= rh/2

def walkable_surface_height(x,y,radius=16):
    top = None
    for ox,oy,ow,oh,oz in obstacles:
        if abs(x-ox) <= max(4,ow/2-radius*0.25) and abs(y-oy) <= max(4,oh/2-radius*0.25):
            top = oz if top is None else max(top,oz)
    for sx,sy in stalls:
        if abs(x-sx) <= max(4,60-radius*0.25) and abs(y-sy) <= max(4,35-radius*0.25):
            top = 65 if top is None else max(top,65)
    if abs(x-terminal[0]) <= max(4,31-radius*0.25) and abs(y-terminal[1]) <= max(4,20-radius*0.25):
        top = 92 if top is None else max(top,92)
    return top

def obstacle_hit(x,y,z,radius=16):
    for ox,oy,ow,oh,oz in obstacles:
        if abs(x-ox) <= ow/2+radius and abs(y-oy) <= oh/2+radius and z < oz-6:
            return True
    for bx,by,bw,bh,bz in buildings:
        if abs(x-bx) <= bw/2+radius and abs(y-by) <= bh/2+radius and z < bz+4:
            return True
    for sx,sy in stalls:
        if abs(x-sx) <= 60+radius and abs(y-sy) <= 35+radius and z < 65-6:
            return True
    if abs(x-terminal[0]) <= 31+radius and abs(y-terminal[1]) <= 20+radius and z < 92-6:
        return True
    return False


# Checkpoint 5 - Player Movement, Gravity and Shortcuts

# >>> CHANGED 3 - LAB 3 PLAYER MOVEMENT
# Old move_player(dt) read held keys every frame. New move_player(val) moves one step when keyboardDown() receives W or S, like Assignment 3.
def move_player(val):
    global mission_time,last_collision_penalty,score,player_move_timer
    if cctv_mode:
        return
    rad = math.radians(player["angle"])
    nx = player["x"] + math.cos(rad)*val
    ny = player["y"] + math.sin(rad)*val
    nx = clamp(nx,-world_limit+25,world_limit-25)
    ny = clamp(ny,-world_limit+25,world_limit-25)
    if not obstacle_hit(nx,ny,player["z"],player["radius"]):
        player["x"],player["y"] = nx,ny
        player_move_timer = 0.16
    elif last_collision_penalty <= 0:
        score -= 10
        mission_time = max(0,mission_time-1.0)
        last_collision_penalty = 1.0
        set_message("Obstacle collision: time and score penalty.",1.5)

# >>> CHANGED 4 - CONTINUOUS PLAYER PHYSICS
# Gravity, landing, gap penalties and shortcut logic were separated from key movement so they still update every frame.
def update_player(dt):
    global mission_time,last_collision_penalty,score,shortcut_armed,shortcut_timer,player_move_timer
    if player_move_timer > 0:
        player_move_timer = max(0,player_move_timer-dt)
    if cctv_mode:
        return

    prev_z = player["z"]
    support = walkable_surface_height(player["x"],player["y"],player["radius"])
    if support is not None and player["vz"] == 0 and abs(player["z"]-support) <= 8:
        player["z"] = support

    if player["z"] > 0 or player["vz"] != 0:
        player["vz"] -= 620.0*dt
        player["z"] += player["vz"]*dt
        landing_z = 0
        support = walkable_surface_height(player["x"],player["y"],player["radius"])
        if support is not None and player["vz"] <= 0 and player["z"] <= support <= prev_z + 45:
            landing_z = max(landing_z,support)
        if player["z"] <= landing_z:
            player["z"] = landing_z
            player["vz"] = 0

    if player["z"] < 22:
        for g in gaps:
            if point_in_rect(player["x"],player["y"],g) and last_collision_penalty <= 0:
                mission_time = max(0,mission_time-2.0)
                score -= 10
                last_collision_penalty = 1.2
                set_message("Bad landing: 2 second penalty.",1.5)
                break

    if phone_stolen:
        for z in shortcut_zones:
            if point_in_rect(player["x"],player["y"],z):
                owner = npcs[phone_owner]
                d = dist(player["x"],player["y"],owner["x"],owner["y"])
                if 140 < d < 520:
                    shortcut_armed = True
                    shortcut_timer = 6.0
                    break
        if shortcut_armed and shortcut_timer > 0:
            owner = npcs[phone_owner]
            if dist(player["x"],player["y"],owner["x"],owner["y"]) < 85:
                score += 100
                shortcut_armed = False
                shortcut_timer = 0
                set_message("Shortcut interception! +100",2.0)


# Checkpoint 6 - NPC Movement and Escape Routes

def route_for_escape():
    best = 0
    best_value = -1
    for i,r in enumerate(routes):
        ex,ey = r["points"][-1]
        value = dist(player["x"],player["y"],ex,ey) + random.uniform(-120,120)
        if value > best_value:
            best_value = value
            best = i
    return best

def move_toward(n,tx,ty,speed,dt):
    a = angle_to(n["x"],n["y"],tx,ty)
    n["angle"] = a
    for turn in [0,40,-40,80,-80]:
        rad = math.radians(a+turn)
        nx = clamp(n["x"]+math.cos(rad)*speed*dt,-world_limit+25,world_limit-25)
        ny = clamp(n["y"]+math.sin(rad)*speed*dt,-world_limit+25,world_limit-25)
        if not obstacle_hit(nx,ny,n["z"],14):
            n["x"],n["y"] = nx,ny
            return True
    return False

def update_civilian(n,dt):
    tx,ty = n["target"]
    if dist(n["x"],n["y"],tx,ty) < 35:
        n["target"] = (random.uniform(-1100,1100),random.uniform(-1100,1100))
        tx,ty = n["target"]
    a = angle_to(n["x"],n["y"],tx,ty)
    n["angle"] = a
    rad = math.radians(a)
    nx = n["x"] + math.cos(rad)*n["speed"]*dt
    ny = n["y"] + math.sin(rad)*n["speed"]*dt
    if not obstacle_hit(nx,ny,n["z"],14):
        n["x"],n["y"] = nx,ny
    else:
        n["target"] = (random.uniform(-1100,1100),random.uniform(-1100,1100))

def auto_jump(n):
    if n["z"] == 0 and n["vz"] == 0:
        n["vz"] = 300.0

def move_route(n,dt,speed):
    if n["route"] < 0:
        n["route"] = route_for_escape()
        n["wp"] = 0
    pts = routes[n["route"]]["points"]
    if n["wp"] >= len(pts):
        return True
    tx,ty = pts[n["wp"]]
    if dist(n["x"],n["y"],tx,ty) < 35:
        n["wp"] += 1
        if n["wp"] >= len(pts):
            return True
        tx,ty = pts[n["wp"]]
    a = angle_to(n["x"],n["y"],tx,ty)
    n["angle"] = a
    rad = math.radians(a)
    nx = n["x"] + math.cos(rad)*speed*dt
    ny = n["y"] + math.sin(rad)*speed*dt
    if obstacle_hit(nx,ny,n["z"],14):
        auto_jump(n)
    else:
        n["x"],n["y"] = nx,ny
    return False

def update_vertical(n,dt):
    support = walkable_surface_height(n["x"],n["y"],14)
    if support is not None and n["vz"] == 0 and abs(n["z"]-support) <= 8:
        n["z"] = support
    prev_z = n["z"]
    if n["z"] > 0 or n["vz"] != 0:
        n["vz"] -= 620.0*dt
        n["z"] += n["vz"]*dt
        landing_z = 0
        support = walkable_surface_height(n["x"],n["y"],14)
        if support is not None and n["vz"] <= 0 and n["z"] <= support <= prev_z+45:
            landing_z = support
        if n["z"] <= landing_z:
            n["z"] = landing_z
            n["vz"] = 0


# Checkpoint 7 - Phone Theft and Witnesses

def assign_witnesses():
    candidates = []
    t = npcs[thief_id]
    for i,n in enumerate(npcs):
        if i != thief_id and i != accomplice_id:
            candidates.append((dist(t["x"],t["y"],n["x"],n["y"]),i))
    candidates.sort()
    chosen = [x[1] for x in candidates[:4]]
    tcolor = shirt_colors[t["color"]][3]
    tsize = size_values[t["size"]][1]
    route_dir = routes[t["route"]]["dir"]
    clues = [
        ("color",t["color"],"The person was wearing %s." % tcolor),
        ("size",t["size"],"The person looked %s-sized." % tsize),
        ("hat",t["hat"],"I %s a hat." % ("noticed" if t["hat"] else "did not notice")),
        ("direction",route_dir,"I saw them moving %s." % route_dir)
    ]
    random.shuffle(clues)
    for j,i in enumerate(chosen):
        npcs[i]["role"] = "WITNESS"
        npcs[i]["clue"] = clues[j]
        npcs[i]["asked"] = False

def steal_phone():
    global phone_stolen,phone_owner,mission_time
    t = npcs[thief_id]
    phone_stolen = True
    phone_owner = thief_id
    t["state"] = "STEAL"
    t["state_time"] = 0.0
    t["route"] = route_for_escape()
    t["wp"] = 0
    mission_time = 120.0
    assign_witnesses()
    set_message("Your phone was stolen! Investigate witnesses, CCTV and the tracker.",5.0)


# Checkpoint 8 - Thief AI, Dodge and Handoff

def attempt_handoff(dt):
    global phone_owner,handoff_done,score,handoff_detected
    if not handoff_planned or handoff_done or not phone_stolen or phone_owner != thief_id or game_time < 12:
        return
    t = npcs[thief_id]
    a = npcs[accomplice_id]
    if t["state"] != "HANDOFF":
        if dist(player["x"],player["y"],t["x"],t["y"]) < 360 or game_time > 24:
            t["state"] = "HANDOFF"
            t["state_time"] = 0.0
            a["state"] = "WAIT_HANDOFF"
    if t["state"] == "HANDOFF":
        a["target"] = (t["x"],t["y"])
        move_toward(t,a["x"],a["y"],175,dt)
        if dist(t["x"],t["y"],a["x"],a["y"]) < 45:
            phone_owner = accomplice_id
            handoff_done = True
            a["state"] = "ESCAPE"
            a["state_time"] = 0.0
            a["route"] = route_for_escape()
            a["wp"] = 0
            t["state"] = "DISTRACT"
            t["state_time"] = 0.0
            t["route"] = route_for_escape()
            t["wp"] = 0
            if dist(player["x"],player["y"],t["x"],t["y"]) < 260:
                score += 150
                handoff_detected = True
                set_message("You witnessed a phone handoff! +150",4.0)
            else:
                set_message("The tracker changed suddenly. Did the phone change hands?",4.0)

def dodge_projectile(n):
    if n["dodge_cd"] > 0 or n["stun"] > 0:
        return
    for p in projectiles:
        if dist(n["x"],n["y"],p["x"],p["y"]) < 145:
            toward = (n["x"]-p["x"])*p["dx"] + (n["y"]-p["y"])*p["dy"]
            if toward > 0 and random.random() < 0.28:
                side = random.choice([-1,1])
                for direction in [side,-side]:
                    nx = clamp(n["x"]-p["dy"]*55*direction,-world_limit+25,world_limit-25)
                    ny = clamp(n["y"]+p["dx"]*55*direction,-world_limit+25,world_limit-25)
                    if not obstacle_hit(nx,ny,n["z"],14):
                        n["x"],n["y"] = nx,ny
                        n["dodge_cd"] = 2.5
                        return

def update_npcs(dt):
    global game_state
    for i,n in enumerate(npcs):
        if n["blend_cd"] > 0:n["blend_cd"] = max(0,n["blend_cd"]-dt)
        if n["stun"] > 0:
            n["stun"] -= dt
            if n["stun"] <= 0 and i == phone_owner:
                n["state"] = "ESCAPE"
                n["state_time"] = 0.0
            update_vertical(n,dt)
            continue
        if n["dodge_cd"] > 0:n["dodge_cd"] -= dt

        if i == thief_id and not phone_stolen:
            if game_time < 2.0:
                update_civilian(n,dt)
            else:
                n["state"] = "APPROACH"
                move_toward(n,player["x"],player["y"],player["speed"]+55,dt)
                if dist(n["x"],n["y"],player["x"],player["y"]) < 35:steal_phone()
            update_vertical(n,dt)
            continue

        if n["state"] == "HANDOFF":
            update_vertical(n,dt)
            continue
        if n["state"] == "WAIT_HANDOFF":
            move_toward(n,n["target"][0],n["target"][1],105,dt)
            update_vertical(n,dt)
            continue

        if i == phone_owner and phone_stolen:
            dodge_projectile(n)
            n["state_time"] += dt

            if n["state"] == "STEAL":
                if n["state_time"] >= 0.35:
                    n["state"] = "WALK_AWAY"
                    n["state_time"] = 0.0
                update_vertical(n,dt)
                continue

            if n["state"] == "WALK_AWAY":
                dx,dy = n["x"]-player["x"],n["y"]-player["y"]
                length = max(1.0,math.sqrt(dx*dx+dy*dy))
                move_toward(n,n["x"]+dx/length*180,n["y"]+dy/length*180,105,dt)
                if n["state_time"] >= 1.6:
                    n["state"] = "ESCAPE"
                    n["state_time"] = 0.0
                update_vertical(n,dt)
                continue

            d = dist(player["x"],player["y"],n["x"],n["y"])
            if ring_timer > 0 and ring_holder == i:
                if n["state"] != "PANIC":n["state_time"] = 0.0
                n["state"] = "PANIC"
            elif d < 180:
                if n["state"] != "DESPERATION":n["state_time"] = 0.0
                n["state"] = "DESPERATION"
            elif n["state"] in ["PANIC","DESPERATION"]:
                n["state"] = "ESCAPE"
                n["state_time"] = 0.0
            elif n["state"] == "BLEND":
                if d < 340 or n["state_time"] >= 3.5:
                    n["state"] = "ESCAPE"
                    n["state_time"] = 0.0
                    n["blend_cd"] = 6.0
            elif d > 520 and n["blend_cd"] <= 0 and n["state"] == "ESCAPE":
                n["state"] = "BLEND"
                n["state_time"] = 0.0

            if n["state"] == "BLEND":
                update_civilian(n,dt)
            else:
                speed = 220.0 if n["state"] in ["DESPERATION","PANIC"] else 175.0
                if n["state"] in ["DESPERATION","PANIC"] and random.random() < 0.008:
                    n["route"] = route_for_escape()
                    n["wp"] = 0
                if move_route(n,dt,speed):
                    game_state = "LOSE"
                    set_message("The phone holder reached an escape point.",999)
            update_vertical(n,dt)
            continue

        if i == thief_id and handoff_done and n["state"] == "DISTRACT":
            move_route(n,dt,180.0)
            update_vertical(n,dt)
            continue
        update_civilian(n,dt)
        update_vertical(n,dt)
    attempt_handoff(dt)


# Checkpoint 9 - Stun Projectile System

def fire_stun():
    global stun_ammo
    if game_state != "PLAY" or paused or cctv_mode or not phone_stolen:
        return
    if stun_ammo <= 0:
        set_message("No stun ammunition left.",1.5)
        return
    if len(projectiles) >= 3:
        set_message("Only 3 stun projectiles can be active.",1.5)
        return
    rad = math.radians(player["angle"])
    projectiles.append({
        "x":player["x"]+math.cos(rad)*24,"y":player["y"]+math.sin(rad)*24,
        "z":player["z"]+38,"dx":math.cos(rad),"dy":math.sin(rad),"life":2.0
    })
    stun_ammo -= 1

def update_projectiles(dt):
    global projectiles,score
    alive = []
    for p in projectiles:
        p["x"] += p["dx"]*520*dt
        p["y"] += p["dy"]*520*dt
        p["life"] -= dt
        hit = False
        if abs(p["x"]) > world_limit or abs(p["y"]) > world_limit or p["life"] <= 0:
            score -= 20
            set_message("Wasted stun projectile. -20",1.5)
            continue
        if obstacle_hit(p["x"],p["y"],p["z"],2):
            score -= 20
            set_message("Stun projectile hit an obstacle. -20",1.5)
            continue
        for i,n in enumerate(npcs):
            if dist(p["x"],p["y"],n["x"],n["y"]) < 24 and abs(p["z"]-(n["z"]+32)) < 40:
                hit = True
                if i == phone_owner:
                    n["stun"] = 2.2
                    n["state"] = "STUNNED"
                    score += 50
                    set_message("Accurate stun hit! +50",2.0)
                else:
                    score -= 20
                    set_message("Wrong stun target. -20",2.0)
                break
        if not hit:
            alive.append(p)
    projectiles = alive


# Checkpoint 10 - Investigation, Tracker, CCTV and Capture

def tracker_strength():
    if not phone_stolen or phone_owner < 0:
        return "PHONE SAFE"
    o = npcs[phone_owner]
    d = dist(player["x"],player["y"],o["x"],o["y"])
    if selected_character == 2:
        if d < 90:return "EXTREME"
        if d < 170:return "VERY STRONG"
        if d < 280:return "STRONG"
        if d < 420:return "MEDIUM"
        if d < 600:return "WEAK"
        return "VERY WEAK"
    if d < 120:return "VERY STRONG"
    if d < 260:return "STRONG"
    if d < 430:return "MEDIUM"
    if d < 620:return "WEAK"
    return "VERY WEAK"

def suspect_count():
    if not phone_stolen:
        return len(npcs)
    count = 0
    for n in npcs:
        ok = True
        for e in evidence:
            if e[0] == "color" and n["color"] != e[1]:ok = False
            if e[0] == "size" and n["size"] != e[1]:ok = False
            if e[0] == "hat" and n["hat"] != e[1]:ok = False
        if ok:
            count += 1
    return count

def collect_witness(n):
    global score
    if n["asked"] or n["clue"] is None:
        set_message("This witness has nothing more to add.",2.0)
        return
    n["asked"] = True
    clue = n["clue"]
    evidence.append(clue)
    score += 30
    text = clue[2]
    if selected_character == 0:
        extra = None
        t = npcs[thief_id]
        if clue[0] != "color":
            extra = ("color",t["color"],"Investigator detail: %s shirt." % shirt_colors[t["color"]][3])
        elif clue[0] != "size":
            extra = ("size",t["size"],"Investigator detail: %s build." % size_values[t["size"]][1])
        if extra and not any(x[0] == extra[0] for x in evidence):
            evidence.append(extra)
            text += " " + extra[2]
    set_message("Witness: " + text + "  +30",4.0)

def interact():
    global cctv_mode,wrong_capture,score,game_state,mission_time
    if game_state != "PLAY" or paused:
        return
    if cctv_mode:
        cctv_mode = False
        set_message("Exited CCTV.",1.5)
        return
    if dist(player["x"],player["y"],terminal[0],terminal[1]) < 90:
        cctv_mode = True
        set_message("CCTV active. Press Q to switch cameras, E to exit.",3.0)
        return
    if phone_stolen and phone_owner >= 0:
        o = npcs[phone_owner]
        if dist(player["x"],player["y"],o["x"],o["y"]) < 58:
            score += 650
            time_bonus = int(max(0,mission_time)/120.0*200)
            score += time_bonus
            game_state = "WIN"
            set_message("Phone recovered! Capture +650, time bonus +%d" % time_bonus,999)
            return
    nearest_w = -1
    nearest_d = 999
    for i,n in enumerate(npcs):
        if n["role"] == "WITNESS" and not n["asked"]:
            d = dist(player["x"],player["y"],n["x"],n["y"])
            if d < nearest_d:
                nearest_d,nearest_w = d,i
    if nearest_w >= 0 and nearest_d < 80:
        collect_witness(npcs[nearest_w])
        return
    if phone_stolen:
        nearest = -1
        nearest_d = 999
        for i,n in enumerate(npcs):
            d = dist(player["x"],player["y"],n["x"],n["y"])
            if d < nearest_d:
                nearest_d,nearest = d,i
        if nearest >= 0 and nearest_d < 58:
            wrong_capture += 1
            score -= 150
            mission_time = max(0,mission_time-7.0)
            set_message("Wrong suspect! -150 and 7 second penalty.",3.0)
            if wrong_capture >= 3:
                game_state = "LOSE"
                set_message("Too many wrong captures. Investigation failed.",999)
            return
    set_message("Nothing to interact with here.",1.5)

def remote_ring():
    global remote_cooldown,ring_timer,ring_holder
    if not phone_stolen or game_state != "PLAY" or paused:
        return
    if remote_cooldown > 0:
        set_message("Remote pulse cooling down: %.1fs" % remote_cooldown,1.5)
        return
    o = npcs[phone_owner]
    d = dist(player["x"],player["y"],o["x"],o["y"])
    remote_cooldown = 5.0 if selected_character == 2 else 8.0
    if d <= 620:
        ring_timer = 3.0
        ring_holder = phone_owner
        set_message("Remote pulse activated. Watch the crowd!",2.5)
    else:
        ring_timer = 0.0
        ring_holder = -1
        set_message("Phone is too far away for a visible pulse.",2.5)

def update_cctv(dt):
    global cctv_watch,score
    if not cctv_mode or not phone_stolen:
        cctv_watch = 0.0
        return
    cam = cameras[cctv_index]
    o = npcs[phone_owner]
    if dist(cam["center"][0],cam["center"][1],o["x"],o["y"]) < 430:
        cctv_watch += dt
        watch_needed = 0.7 if selected_character == 0 else 1.2
        if cctv_watch > watch_needed and cctv_index not in cctv_scored:
            cctv_scored.append(cctv_index)
            score += 50
            evidence.append(("area",cam["name"],"CCTV last saw movement near %s." % cam["name"]))
            set_message("Useful CCTV observation: %s. +50" % cam["name"],3.0)
    else:
        cctv_watch = 0.0


# Checkpoint 11 - Cars, Timer and Main Game Update

def check_car_collision():
    global mission_time,score,last_collision_penalty
    if last_collision_penalty > 0 or player["z"] > 25:
        return
    for c in cars:
        if c["axis"] == "x":
            hit = abs(player["x"]-c["x"]) < 55 and abs(player["y"]-c["y"]) < 30
        else:
            hit = abs(player["x"]-c["x"]) < 30 and abs(player["y"]-c["y"]) < 55
        if hit:
            mission_time = max(0,mission_time-3.0)
            score -= 20
            last_collision_penalty = 1.5
            set_message("Traffic collision: -20 and 3 second penalty.",2.0)
            break

def update_cars(dt):
    for c in cars:
        if c["axis"] == "x":
            c["x"] += c["dir"]*c["speed"]*dt
            if c["x"] > 1320:c["x"] = -1320
            if c["x"] < -1320:c["x"] = 1320
        else:
            c["y"] += c["dir"]*c["speed"]*dt
            if c["y"] > 1320:c["y"] = -1320
            if c["y"] < -1320:c["y"] = 1320

def update_game(dt):
    global game_time,mission_time,remote_cooldown,ring_timer,ring_holder,message_timer
    global shortcut_timer,shortcut_armed,last_collision_penalty,game_state,handoff_detected,score
    if game_state != "PLAY" or paused:
        return
    game_time += dt
    if phone_stolen:
        mission_time -= dt
        if mission_time <= 0:
            mission_time = 0
            game_state = "LOSE"
            set_message("Time ran out. The phone escaped.",999)
    if remote_cooldown > 0:
        remote_cooldown = max(0,remote_cooldown-dt)
    if ring_timer > 0:
        ring_timer = max(0,ring_timer-dt)
        if ring_timer == 0:ring_holder = -1
    if message_timer > 0:message_timer -= dt
    if shortcut_timer > 0:
        shortcut_timer -= dt
        if shortcut_timer <= 0:shortcut_armed = False
    if last_collision_penalty > 0:last_collision_penalty -= dt
    # >>> CHANGED 5 - MASTER UPDATE CALL
    # Old update_game() called move_player(dt). It now calls update_player(dt); actual W/S movement happens in keyboardDown().
    update_player(dt)
    update_npcs(dt)
    update_projectiles(dt)
    update_cars(dt)
    update_cctv(dt)
    check_car_collision()
    if handoff_done and not handoff_detected and phone_stolen:
        o = npcs[phone_owner]
        if dist(player["x"],player["y"],o["x"],o["y"]) < 220:
            handoff_detected = True
            score += 150
            set_message("You identified the new phone holder after the handoff! +150",3.0)


# Checkpoint 12 - 3D World Drawing

def draw_box(x,y,z,sx,sy,sz,color):
    glPushMatrix()
    glTranslatef(x,y,z+sz/2)
    glScalef(sx,sy,sz)
    glColor3f(*color)
    glutSolidCube(1)
    glPopMatrix()

def draw_disc(x,y,z,r,color,segments=20):
    glColor3f(*color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(x,y,z)
    for i in range(segments+1):
        a = 2*math.pi*i/segments
        glVertex3f(x+math.cos(a)*r,y+math.sin(a)*r,z)
    glEnd()

# >>> CHANGED 6 - SKY INSTEAD OF glClearColor
# glClearColor() is not in the Lab 3 template, so large cube surfaces now create the same blue-sky background.
def draw_sky():
    sky = (0.58,0.78,0.94)
    draw_box(0,3000,0,7000,20,3000,sky)
    draw_box(0,-3000,0,7000,20,3000,sky)
    draw_box(3000,0,0,20,7000,3000,sky)
    draw_box(-3000,0,0,20,7000,3000,sky)
    draw_box(0,0,2980,7000,7000,20,sky)

def draw_ground():
    city_ground = (0.44,0.43,0.40)
    concrete_1 = (0.50,0.50,0.47)
    concrete_2 = (0.47,0.48,0.46)
    concrete_3 = (0.54,0.53,0.49)
    pavement = (0.62,0.62,0.59)
    pavement_alt = (0.57,0.58,0.56)
    curb = (0.76,0.76,0.72)
    drain = (0.24,0.25,0.24)
    grass = (0.29,0.43,0.27)
    dry_grass = (0.39,0.43,0.27)
    dirt = (0.43,0.34,0.25)

    draw_box(0,0,-18,2600,2600,18,city_ground)

    concrete_zones = [
        (-690,245,1000,470,concrete_1),(690,245,1000,470,concrete_2),
        (-690,-760,1000,720,concrete_2),(690,-760,1000,720,concrete_1),
        (-690,1010,1000,420,concrete_3),(690,1010,1000,420,concrete_3)
    ]
    for x,y,w,h,color in concrete_zones:
        draw_box(x,y,-2,w,h,4,color)

    draw_box(-500,110,-1,350,340,5,(0.52,0.50,0.45))
    draw_box(500,105,-1,350,340,5,(0.52,0.50,0.45))
    for px in [-620,-500,-380,380,500,620]:
        draw_box(px,105,4,72,300,1.3,(0.48,0.47,0.43))

    for gx,gy,gw,gh,col in [
        (-1050,160,210,120,grass),(1040,150,220,120,dry_grass),
        (-1040,-1030,230,130,dry_grass),(1040,-1030,230,130,grass),
        (-840,790,150,95,dirt),(870,800,170,90,dirt)
    ]:
        draw_box(gx,gy,0,gw,gh,2,col)

    road = (0.0,0.0,0.0)
    white = (0.38,0.40,0.40)
    crossing_white = (0.68,0.70,0.70)
    yellow = (0.86,0.64,0.06)

    draw_box(0,-230,0,2600,225,6,road)
    draw_box(0,610,0,2600,205,6,road)
    draw_box(0,0,0,275,2600,6,road)

    sidewalks = [
        (0,-355,2600,34,pavement),(0,-105,2600,34,pavement_alt),
        (0,495,2600,30,pavement),(0,725,2600,30,pavement_alt),
        (-155,0,34,2600,pavement),(155,0,34,2600,pavement_alt)
    ]
    for x,y,w,h,color in sidewalks:
        draw_box(x,y,1,w,h,8,color)

    for x in range(-1160,1200,240):
        draw_box(x,-355,8.5,105,30,1.0,(0.66,0.66,0.63))
        draw_box(x,-105,8.5,105,30,1.0,(0.60,0.61,0.59))
        draw_box(x,495,8.5,105,26,1.0,(0.66,0.66,0.63))
        draw_box(x,725,8.5,105,26,1.0,(0.60,0.61,0.59))
    for y in range(-1160,1200,240):
        draw_box(-155,y,8.5,30,105,1.0,(0.66,0.66,0.63))
        draw_box(155,y,8.5,30,105,1.0,(0.60,0.61,0.59))

    curbs = [(0,-337,2600,4),(0,-123,2600,4),(0,512,2600,4),(0,708,2600,4),(-137,0,4,2600),(137,0,4,2600)]
    drains = [(0,-343,2600,5),(0,-117,2600,5),(0,518,2600,5),(0,702,2600,5),(-143,0,5,2600),(143,0,5,2600)]
    for x,y,w,h in curbs:draw_box(x,y,8,w,h,4,curb)
    for x,y,w,h in drains:draw_box(x,y,3,w,h,2,drain)

    for x in range(-1200,1260,280):
        draw_box(x,-280,6.05,82,4,1.0,white)
        draw_box(x,-180,6.05,82,4,1.0,white)
        draw_box(x,565,6.05,82,4,1.0,white)
        draw_box(x,655,6.05,82,4,1.0,white)
    for y in range(-1200,1260,280):
        draw_box(-58,y,6.05,4,82,1.0,white)
        draw_box(58,y,6.05,4,82,1.0,white)

    draw_box(0,-230,6.05,2600,1.6,1.0,yellow)
    draw_box(0,610,6.05,2600,1.6,1.0,yellow)
    draw_box(0,0,6.05,1.6,2600,1.0,yellow)

    for x in range(-95,100,22):
        draw_box(x,-125,6.1,12,55,1.2,crossing_white)
        draw_box(x,505,6.1,12,48,1.2,crossing_white)
    for y in range(-78,90,22):
        draw_box(-135,y,6.1,48,12,1.2,crossing_white)
        draw_box(135,y,6.1,48,12,1.2,crossing_white)

def draw_building(x,y,sx,sy,sz,index):
    palette = [
        (0.56,0.40,0.34),(0.46,0.50,0.52),(0.60,0.52,0.39),
        (0.46,0.42,0.50),(0.61,0.44,0.37),(0.43,0.50,0.45)
    ]
    wall = palette[index%len(palette)]
    side_wall = darker(wall,0.88)
    back_wall = darker(wall,0.80)
    trim = lighter(wall,0.10)
    glass = (0.30,0.57,0.68)
    dark_glass = (0.20,0.40,0.50)
    door = (0.12,0.16,0.18)

    draw_box(x,y,0,sx,sy,sz,wall)

    draw_box(x-sx/2-2,y,2,4,sy-10,sz-4,side_wall)
    draw_box(x+sx/2+2,y,2,4,sy-10,sz-4,side_wall)
    draw_box(x,y+sy/2+2,2,sx-10,4,sz-4,back_wall)

    draw_box(x,y-sy/2-4,0,sx*0.72,8,58,darker(wall,0.72))
    draw_box(x,y-sy/2-9,0,34,5,50,door)
    draw_box(x-38,y-sy/2-8,12,36,5,32,dark_glass)
    draw_box(x+38,y-sy/2-8,12,36,5,32,dark_glass)
    draw_box(x,y-sy/2-11,55,min(150,sx*0.58),4,16,shirt_colors[index%len(shirt_colors)][:3])

    floors = max(3,min(7,int(sz/68)))
    front_cols = 4 if sx > 300 else 3 if sx > 220 else 2
    side_cols = 4 if sy > 330 else 3 if sy > 240 else 2

    for f in range(1,floors):
        wz = 58 + f*58
        if wz > sz-34:
            break
        for c in range(front_cols):
            wx = x-sx*0.34 + c*(sx*0.68/max(1,front_cols-1))
            draw_box(wx,y-sy/2-3,wz,30,5,32,glass)
            draw_box(wx,y-sy/2-6,wz-5,34,4,4,trim)
            draw_box(wx,y+sy/2+3,wz,30,5,32,dark_glass)
            draw_box(wx,y+sy/2+6,wz-5,34,4,4,trim)

        draw_box(x,y-sy/2-2,wz+38,sx,3,4,trim)
        draw_box(x,y+sy/2+2,wz+38,sx,3,4,trim)
        draw_box(x-sx/2-2,y,wz+38,3,sy,4,trim)
        draw_box(x+sx/2+2,y,wz+38,3,sy,4,trim)

    for f in range(1,floors):
        wz = 58 + f*58
        if wz > sz-34:
            break
        for c in range(side_cols):
            wy = y-sy*0.34 + c*(sy*0.68/max(1,side_cols-1))
            draw_box(x-sx/2-3,wy,wz,5,30,32,dark_glass)
            draw_box(x+sx/2+3,wy,wz,5,30,32,glass)

    if sy > 300:
        draw_box(x+sx/2+4,y-sy*0.22,0,6,34,48,door)
        draw_box(x+sx/2+7,y-sy*0.22,48,5,42,7,trim)

    parapet_h = 15
    draw_box(x,y-sy/2+6,sz,sx,10,parapet_h,trim)
    draw_box(x,y+sy/2-6,sz,sx,10,parapet_h,trim)
    draw_box(x-sx/2+6,y,sz,10,sy,parapet_h,trim)
    draw_box(x+sx/2-6,y,sz,10,sy,parapet_h,trim)

    if index%2 == 0:
        draw_box(x+sx*0.20,y,sz+parapet_h,48,48,38,(0.20,0.24,0.25))
        draw_box(x+sx*0.20,y,sz+parapet_h+38,54,54,6,(0.10,0.12,0.13))
    else:
        draw_box(x-sx*0.18,y,sz+parapet_h,58,44,32,(0.25,0.27,0.27))
        draw_box(x-sx*0.18,y,sz+parapet_h+32,64,50,6,(0.12,0.14,0.15))

def draw_market_stall(x,y,index):
    cloth = shirt_colors[index%len(shirt_colors)][:3]
    draw_box(x,y,0,118,68,8,(0.30,0.20,0.12))
    draw_box(x,y-15,20,110,18,25,(0.46,0.27,0.15))
    for px in [-50,50]:
        for py in [-28,28]:
            draw_box(x+px,y+py,0,5,5,76,(0.20,0.16,0.12))
    draw_box(x,y,72,135,82,9,cloth)
    draw_box(x,y-43,63,135,7,18,lighter(cloth,0.12))
    for j in range(4):
        draw_box(x-36+j*24,y-19,45,16,14,10,shirt_colors[(index+j+1)%len(shirt_colors)][:3])

def draw_streetlight(x,y,rotation=0):
    glPushMatrix()
    glTranslatef(x,y,0)
    glRotatef(rotation,0,0,1)
    draw_box(0,0,0,7,7,150,(0.14,0.15,0.16))
    draw_box(0,0,145,42,7,7,(0.14,0.15,0.16))
    draw_box(18,0,139,22,15,9,(0.92,0.80,0.42))
    glPopMatrix()

def draw_utility_pole(x,y):
    draw_box(x,y,0,8,8,175,(0.20,0.16,0.12))
    draw_box(x,y,158,62,7,7,(0.20,0.16,0.12))
    # >>> CHANGED 7A - glLineWidth REMOVED
    # Utility wires still use GL_LINES; only glLineWidth() was removed because it was outside the Lab 3 template.
    glColor3f(0.09,0.09,0.10)
    glBegin(GL_LINES)
    glVertex3f(x-30,y,162);glVertex3f(x+130,y+55,155)
    glVertex3f(x+30,y,162);glVertex3f(x+150,y-45,150)
    glEnd()

def draw_barricade(x,y,w,h,z):
    draw_box(x,y,0,w,h,z,(0.62,0.37,0.12))
    draw_box(x,y,z*0.50,w+4,h+3,8,(0.88,0.70,0.20))
    draw_box(x,y,z*0.72,w+4,h+3,8,(0.18,0.18,0.18))
    draw_box(x-w*0.32,y,0,10,h+18,16,(0.16,0.16,0.17))
    draw_box(x+w*0.32,y,0,10,h+18,16,(0.16,0.16,0.17))

def draw_city():
    for i,(x,y,sx,sy,sz) in enumerate(buildings):
        draw_building(x,y,sx,sy,sz,i)

    for i,(x,y) in enumerate(stalls):
        draw_market_stall(x,y,i)

    for i,(ox,oy,ow,oh,oz) in enumerate(obstacles):
        if i%3 == 0:
            draw_barricade(ox,oy,ow,oh,oz)
        elif i%3 == 1:
            draw_box(ox,oy,0,ow,oh,oz,(0.44,0.28,0.14))
        else:
            draw_box(ox,oy,0,ow,oh,oz,(0.32,0.34,0.34))
            draw_box(ox,oy,oz,ow+8,oh+8,7,(0.80,0.52,0.16))

    for gx,gy,gw,gh in gaps:
        draw_box(gx,gy,0.5,gw,gh,2,(0.035,0.04,0.045))
    # >>> CHANGED 7B - glLineWidth REMOVED
    # Shortcut outlines are unchanged except the old glLineWidth() calls were removed.
    for zx,zy,zw,zh in shortcut_zones:
        glColor3f(0.40,0.46,0.35)
        glBegin(GL_LINE_LOOP)
        glVertex3f(zx-zw/2,zy-zh/2,3);glVertex3f(zx+zw/2,zy-zh/2,3)
        glVertex3f(zx+zw/2,zy+zh/2,3);glVertex3f(zx-zw/2,zy+zh/2,3)
        glEnd()

    draw_box(terminal[0],terminal[1],0,62,40,92,(0.10,0.13,0.15))
    draw_box(terminal[0],terminal[1]-22,58,50,5,34,(0.08,0.60,0.67))
    draw_box(terminal[0],terminal[1]-25,61,40,3,24,(0.18,0.88,0.92))
    draw_box(terminal[0]-20,terminal[1],92,8,8,16,(0.80,0.20,0.15))

    for i,cam in enumerate(cameras):
        x,y = cam["center"]
        draw_box(x,y,0,10,10,230,(0.13,0.14,0.15))
        glPushMatrix()
        glTranslatef(x,y,230)
        glRotatef((i*90+35)%360,0,0,1)
        draw_box(0,0,0,48,22,25,(0.22,0.24,0.25))
        draw_box(21,-1,8,12,17,14,(0.08,0.09,0.10))
        glPopMatrix()

    for x in [-900,-300,300,900]:
        draw_streetlight(x,-375,0)
        draw_streetlight(x,745,180)
    for y in [-900,-420,170,960]:
        draw_streetlight(-175,y,90)
    draw_utility_pole(-610,-75)
    draw_utility_pole(600,340)
    draw_utility_pole(-520,745)

    for x,y in [(-380,-10),(-350,180),(390,-5),(360,180),(-620,120),(620,110)]:
        draw_box(x,y,0,52,18,12,(0.34,0.20,0.11))
        draw_box(x-20,y,12,6,20,22,(0.20,0.17,0.13))
        draw_box(x+20,y,12,6,20,22,(0.20,0.17,0.13))

def draw_car(c):
    x,y = c["x"],c["y"]
    axis = c["axis"]
    body_colors = [(0.76,0.16,0.12),(0.12,0.48,0.68),(0.82,0.58,0.12),(0.26,0.60,0.34),(0.70,0.70,0.74),(0.48,0.24,0.68)]
    col = body_colors[cars.index(c)%len(body_colors)]
    glPushMatrix()
    glTranslatef(x,y,0)
    if axis == "y":
        glRotatef(90,0,0,1)
    draw_box(0,0,7,100,48,24,col)
    draw_box(0,0,31,56,40,22,darker(col,0.75))
    draw_box(-10,-20,30,25,3,14,(0.20,0.34,0.42))
    draw_box(13,-20,30,20,3,14,(0.20,0.34,0.42))
    for wx in [-29,29]:
        for wy in [-22,22]:
            draw_box(wx,wy,2,14,7,15,(0.06,0.06,0.065))
    front_x = 43*c["dir"]
    draw_box(front_x,0,14,4,24,6,(0.95,0.90,0.70))
    draw_box(-front_x,0,14,4,24,6,(0.80,0.18,0.14))
    glPopMatrix()


# Checkpoint 13 - Characters, Camera, HUD, Controls and Main Loop

# >>> CHANGED 8A - WIRE SPHERE REPLACEMENT
# glutWireSphere() was replaced by three GL_LINE_LOOP circles using glBegin(), glVertex3f() and glEnd().
def draw_wire_sphere(radius,color,segments=20):
    glColor3f(*color)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        a = 2*math.pi*i/segments
        glVertex3f(math.cos(a)*radius,math.sin(a)*radius,0)
    glEnd()
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        a = 2*math.pi*i/segments
        glVertex3f(math.cos(a)*radius,0,math.sin(a)*radius)
    glEnd()
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        a = 2*math.pi*i/segments
        glVertex3f(0,math.cos(a)*radius,math.sin(a)*radius)
    glEnd()

def draw_limb(px,py,pz,sx,sy,sz,color,angle):
    glPushMatrix()
    glTranslatef(px,py,pz)
    glRotatef(angle,1,0,0)
    draw_box(0,0,-sz, sx,sy,sz,color)
    glPopMatrix()

def draw_person(x,y,z,angle,color,size,hat=False,is_player=False,state="WALK",seed=0):
    base_scale = 0.82 if not is_player else 0.88
    scale = size_values[size][0]*base_scale if not is_player else base_scale
    moving = state not in ["STUNNED","WAIT_HANDOFF"]
    run = state in ["ESCAPE","DESPERATION","PANIC","DISTRACT","HANDOFF","APPROACH"]
    stride_speed = 10.5 if run else 6.0
    stride_size = 28.0 if run else 17.0
    if not moving:
        stride_size = 4.0
    phase = game_time*stride_speed + seed*0.9
    swing = math.sin(phase)*stride_size
    bounce = abs(math.sin(phase))*1.5 if moving else 0

    skin_options = [(0.83,0.64,0.48),(0.67,0.47,0.33),(0.52,0.34,0.24),(0.76,0.55,0.40)]
    skin = skin_options[seed%len(skin_options)]
    pants = (0.10,0.12,0.15)
    hair = (0.08,0.055,0.035)
    cap_colors = [(0.08,0.20,0.55),(0.65,0.16,0.12),(0.10,0.42,0.20),(0.30,0.20,0.48)]
    cap_color = cap_colors[seed%len(cap_colors)]

    glPushMatrix()
    glTranslatef(x,y,z+bounce)
    glRotatef(angle-90,0,0,1)

    draw_limb(-7,0,31*scale,8*scale,9*scale,27*scale,pants,swing)
    draw_limb(7,0,31*scale,8*scale,9*scale,27*scale,pants,-swing)

    draw_box(0,0,30*scale,29*scale,19*scale,39*scale,color)

    draw_limb(-18*scale,0,65*scale,7*scale,7*scale,30*scale,skin,-swing*0.72)
    draw_limb(18*scale,0,65*scale,7*scale,7*scale,30*scale,skin,swing*0.72)

    draw_box(0,0,68*scale,8*scale,8*scale,6*scale,skin)
    glPushMatrix()
    glTranslatef(0,0,84*scale)
    glColor3f(*skin)
    # >>> CHANGED 8B - HEAD SPHERE
    # Old glutSolidSphere() -> Lab 3 gluSphere().
    gluSphere(quadric,12*scale,10,8)
    glPopMatrix()

    if hat:
        glPushMatrix()
        glTranslatef(0,1*scale,94*scale)
        glScalef(1.06,0.98,0.38)
        glColor3f(*cap_color)
        # >>> CHANGED 8C - HAT SPHERE
        # Old glutSolidSphere() -> Lab 3 gluSphere().
        gluSphere(quadric,11.5*scale,9,7)
        glPopMatrix()
        draw_box(0,9*scale,92.5*scale,25*scale,10*scale,2.5*scale,cap_color)
        draw_box(8*scale,14*scale,92.5*scale,13*scale,7*scale,2.5*scale,cap_color)
    else:
        glPushMatrix()
        glTranslatef(0,1*scale,93*scale)
        glScalef(1.0,1.0,0.42)
        glColor3f(*hair)
        # >>> CHANGED 8D - HAIR SPHERE
        # Old glutSolidSphere() -> Lab 3 gluSphere().
        gluSphere(quadric,11*scale,9,7)
        glPopMatrix()
    glPopMatrix()

def draw_world_marker(x,y,z,color):
    bob = 4*math.sin(game_time*4)
    glPushMatrix()
    glTranslatef(x,y,z+bob)
    glColor3f(*color)
    # >>> CHANGED 8E - WITNESS MARKER
    # Old glutWireSphere() -> custom Lab 3-function wire sphere.
    draw_wire_sphere(9,color,18)
    draw_box(0,0,11,3,3,18,color)
    glPopMatrix()

def draw_npcs():
    pulse = 1.0 + 0.18*math.sin(game_time*10)
    for i,n in enumerate(npcs):
        c = shirt_colors[n["color"]][:3]
        draw_person(n["x"],n["y"],n["z"],n["angle"],c,n["size"],n["hat"],False,n["state"],i)
        if n["role"] == "WITNESS" and not n["asked"] and phone_stolen:
            if dist(player["x"],player["y"],n["x"],n["y"]) < 260:
                draw_world_marker(n["x"],n["y"],n["z"]+112,(1.0,0.82,0.16))
        if ring_timer > 0 and ring_holder == i:
            for r_add in [0,22,44]:
                glPushMatrix()
                glTranslatef(n["x"],n["y"],n["z"]+42)
                s = pulse + r_add/70.0
                glScalef(s,s,s)
                glColor3f(1.0,0.20+0.003*r_add,0.16)
                # >>> CHANGED 8F - PHONE PULSE
                # Old glutWireSphere() -> custom Lab 3-function wire sphere.
                draw_wire_sphere(30,(1.0,0.20+0.003*r_add,0.16),24)
                glPopMatrix()
        if n["stun"] > 0:
            glPushMatrix()
            glTranslatef(n["x"],n["y"],n["z"]+108)
            glScalef(1.4,1.4,0.25)
            glColor3f(0.18,0.88,1.0)
            # >>> CHANGED 8G - STUN EFFECT
            # Old glutWireSphere() -> custom Lab 3-function wire sphere.
            draw_wire_sphere(14,(0.18,0.88,1.0),20)
            glPopMatrix()

def draw_player():
    colors = [(0.18,0.62,0.96),(0.96,0.52,0.10),(0.12,0.82,0.55)]
    # >>> CHANGED 8H - PLAYER RUN ANIMATION
    # Old code checked W/S inside keys[]. Since keys[] is gone, player_move_timer now controls RUN/IDLE visually.
    state = "RUN" if player_move_timer > 0 and not paused else "IDLE"
    draw_person(player["x"],player["y"],player["z"],player["angle"],colors[selected_character],1,False,True,state,30+selected_character)

def draw_projectiles():
    for p in projectiles:
        # >>> CHANGED 7C - PROJECTILE LINE WIDTH
        # Projectile trail still uses GL_LINES; forbidden glLineWidth() was removed.
        glColor3f(0.18,0.72,0.96)
        glBegin(GL_LINES)
        glVertex3f(p["x"],p["y"],p["z"])
        glVertex3f(p["x"]-p["dx"]*26,p["y"]-p["dy"]*26,p["z"])
        glEnd()
        glPushMatrix()
        glTranslatef(p["x"],p["y"],p["z"])
        glColor3f(0.35,0.92,1.0)
        # >>> CHANGED 8I - PROJECTILE SPHERE
        # Old glutSolidSphere() -> Lab 3 gluSphere().
        gluSphere(quadric,5,8,6)
        glPopMatrix()

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(72.0,window_W/window_H,1.0,6000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if cctv_mode:
        c = cameras[cctv_index]
        sway = math.sin(game_time*0.7)*18
        gluLookAt(c["eye"][0],c["eye"][1],c["eye"][2],c["target"][0]+sway,c["target"][1],c["target"][2],0,0,1)
    else:
        rad = math.radians(player["angle"])
        cx = player["x"]-math.cos(rad)*270
        cy = player["y"]-math.sin(rad)*270
        cz = player["z"]+165
        tx = player["x"]+math.cos(rad)*70
        ty = player["y"]+math.sin(rad)*55
        gluLookAt(cx,cy,cz,tx,ty,player["z"]+56,0,0,1)

# >>> CHANGED 9A - HUD DEPTH METHOD
# The old HUD used glDisable(GL_DEPTH_TEST). New HUD clears only GL_DEPTH_BUFFER_BIT before drawing text/shapes.
def draw_text(x,y,text,font=GLUT_BITMAP_HELVETICA_18):
    glClear(GL_DEPTH_BUFFER_BIT)
    glRasterPos2f(x,y)
    for ch in str(text):
        glutBitmapCharacter(font,ord(ch))

# >>> CHANGED 9B - glDisable REMOVED
# Old hud_mode() called glDisable(GL_DEPTH_TEST). That non-template function was removed.
def hud_mode():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,window_W,0,window_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

# >>> CHANGED 9C - EXTRA glEnable REMOVED
# Old world_mode() re-enabled depth because HUD disabled it. That call is no longer needed.
def world_mode():
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# >>> CHANGED 9D - glVertex2f REPLACED
# Old rectangle used glVertex2f(). New code uses Lab 3 glVertex3f(x,y,0).
def draw_rect_2d(x,y,w,h,color):
    glClear(GL_DEPTH_BUFFER_BIT)
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex3f(x,y,0);glVertex3f(x+w,y,0);glVertex3f(x+w,y+h,0);glVertex3f(x,y+h,0)
    glEnd()

# >>> CHANGED 9E - 2D LINE REWORK
# Old line helper used glVertex2f() and glLineWidth(). New code uses glVertex3f(...,0) and default width.
def draw_line_2d(x1,y1,x2,y2,color,width=1):
    glClear(GL_DEPTH_BUFFER_BIT)
    glColor3f(*color)
    glBegin(GL_LINES)
    glVertex3f(x1,y1,0);glVertex3f(x2,y2,0)
    glEnd()

def draw_panel(x,y,w,h,accent=(0.12,0.72,0.78)):
    draw_rect_2d(x,y,w,h,(0.055,0.065,0.075))
    draw_rect_2d(x,y+h-4,w,4,accent)
    draw_rect_2d(x,y,4,h,(0.10,0.12,0.14))

def draw_signal_meter(x,y,strength):
    levels = {"VERY WEAK":1,"WEAK":2,"MEDIUM":3,"STRONG":4,"VERY STRONG":5,"EXTREME":5}
    active = levels.get(strength,0)
    for i in range(5):
        h = 7+i*5
        col = (0.14,0.78,0.72) if i < active else (0.18,0.20,0.22)
        draw_rect_2d(x+i*13,y,9,h,col)

def nearby_prompt():
    if game_state != "PLAY" or paused:return ""
    if cctv_mode:return "E  EXIT CCTV     Q  NEXT CAMERA"
    if dist(player["x"],player["y"],terminal[0],terminal[1]) < 90:return "E  ACCESS CCTV NETWORK"
    if phone_stolen and phone_owner >= 0:
        o = npcs[phone_owner]
        if dist(player["x"],player["y"],o["x"],o["y"]) < 58:return "E  CAPTURE / VERIFY TARGET"
    for n in npcs:
        if n["role"] == "WITNESS" and not n["asked"] and dist(player["x"],player["y"],n["x"],n["y"]) < 80:
            return "E  QUESTION WITNESS"
    if phone_stolen:
        for n in npcs:
            if dist(player["x"],player["y"],n["x"],n["y"]) < 58:return "E  CAPTURE / VERIFY SUSPECT"
    return ""

def mission_phase():
    if not phone_stolen:return "CROWD PHASE"
    if len(evidence) < 2:return "INVESTIGATE"
    if tracker_strength() in ["VERY STRONG","EXTREME"]:return "INTERCEPT"
    return "TRACK & CHASE"

def draw_select_hud():
    draw_rect_2d(0,0,window_W,window_H,(0.045,0.055,0.065))
    draw_rect_2d(0,650,window_W,150,(0.035,0.045,0.055))
    glColor3f(0.95,0.96,0.93)
    draw_text(38,752,"OPERATION PHONEBACK",GLUT_BITMAP_TIMES_ROMAN_24)
    glColor3f(0.18,0.80,0.83)
    draw_text(40,720,"3D INVESTIGATION  /  PARKOUR  /  CHASE")
    glColor3f(0.78,0.80,0.80)
    draw_text(40,686,"Choose the specialist you want to bring into the chase.",GLUT_BITMAP_HELVETICA_12)

    card_x = [115,455,795]
    names = ["1  INVESTIGATOR","2  RUNNER","3  TRACKER"]
    desc1 = ["Sharper witness clues","Higher movement speed","More precise phone signal"]
    desc2 = ["Faster CCTV confirmation","Stronger jump ability","Shorter pulse cooldown"]
    for i,x in enumerate(card_x):
        accent = [(0.18,0.62,0.96),(0.96,0.52,0.10),(0.12,0.82,0.55)][i]
        selected = i == selected_character
        draw_panel(x,72,290,170,accent if selected else (0.20,0.22,0.23))
        if selected:draw_rect_2d(x+10,221,270,4,accent)
        glColor3f(*(accent if selected else (0.82,0.83,0.81)))
        draw_text(x+18,190,names[i])
        glColor3f(0.72,0.74,0.74)
        draw_text(x+18,150,desc1[i],GLUT_BITMAP_HELVETICA_12)
        draw_text(x+18,126,desc2[i],GLUT_BITMAP_HELVETICA_12)
        draw_text(x+18,93,"SELECTED" if selected else "Press %d"%(i+1),GLUT_BITMAP_HELVETICA_12)
    glColor3f(0.94,0.86,0.34)
    draw_text(455,32,"PRESS ENTER TO START",GLUT_BITMAP_HELVETICA_18)

def draw_cctv_overlay():
    draw_line_2d(22,22,1178,22,(0.15,0.85,0.88),2)
    draw_line_2d(22,778,1178,778,(0.15,0.85,0.88),2)
    draw_line_2d(22,22,22,778,(0.15,0.85,0.88),2)
    draw_line_2d(1178,22,1178,778,(0.15,0.85,0.88),2)
    glColor3f(1.0,0.25,0.20)
    draw_text(52,742,"REC")
    draw_rect_2d(28,742,12,12,(1.0,0.22,0.18))
    glColor3f(0.68,0.90,0.90)
    draw_text(920,742,"CAM %02d  %s"%(cctv_index+1,cameras[cctv_index]["name"]),GLUT_BITMAP_HELVETICA_12)
    for y in range(70,730,42):
        draw_line_2d(35,y,1165,y,(0.11,0.18,0.18),1)
    draw_line_2d(570,400,630,400,(0.16,0.88,0.88),1)
    draw_line_2d(600,370,600,430,(0.16,0.88,0.88),1)

def draw_hud():
    hud_mode()
    if game_state == "SELECT":
        draw_select_hud()
        world_mode()
        return

    accent = (0.14,0.78,0.76)
    draw_panel(18,655,310,126,accent)
    glColor3f(0.62,0.94,0.91)
    draw_text(34,750,"OPERATION PHONEBACK",GLUT_BITMAP_HELVETICA_12)
    glColor3f(0.96,0.96,0.92)
    draw_text(34,720,mission_phase(),GLUT_BITMAP_HELVETICA_18)
    glColor3f(0.72,0.75,0.75)
    draw_text(34,692,"%s   SCORE %d"%(character_names[selected_character].upper(),score),GLUT_BITMAP_HELVETICA_12)
    if phone_stolen:
        glColor3f(0.94,0.84,0.33)
        draw_text(34,668,"TIME  %05.1f"%mission_time,GLUT_BITMAP_HELVETICA_12)
    else:
        glColor3f(0.38,0.90,0.55)
        draw_text(34,668,"PHONE SECURE",GLUT_BITMAP_HELVETICA_12)

    if phone_stolen:
        draw_panel(930,655,252,126,(0.18,0.65,0.92))
        strength = tracker_strength()
        glColor3f(0.70,0.89,0.98)
        draw_text(948,749,"PHONE TRACKER",GLUT_BITMAP_HELVETICA_12)
        glColor3f(0.96,0.96,0.92)
        draw_text(948,720,strength,GLUT_BITMAP_HELVETICA_18)
        draw_signal_meter(948,677,strength)
        glColor3f(0.72,0.75,0.76)
        draw_text(1020,680,"SUSPECTS %d"%suspect_count(),GLUT_BITMAP_HELVETICA_12)
        draw_text(1020,660,"AMMO %d  PULSE %.1f"%(stun_ammo,remote_cooldown),GLUT_BITMAP_HELVETICA_12)

    if evidence:
        draw_panel(18,548,310,92,(0.76,0.63,0.22))
        glColor3f(0.95,0.86,0.42)
        draw_text(34,614,"EVIDENCE",GLUT_BITMAP_HELVETICA_12)
        y = 588
        shown = []
        for e in reversed(evidence):
            if e[2] not in shown:
                shown.append(e[2])
                glColor3f(0.78,0.80,0.79)
                draw_text(34,y,("- "+e[2])[:44],GLUT_BITMAP_HELVETICA_12)
                y -= 19
                if y < 555:break

    if cctv_mode:
        draw_cctv_overlay()

    prompt = nearby_prompt()
    if prompt:
        w = 360
        draw_panel((window_W-w)/2,76,w,48,(0.94,0.76,0.24))
        glColor3f(0.96,0.94,0.82)
        draw_text((window_W-w)/2+24,94,prompt,GLUT_BITMAP_HELVETICA_12)

    if message_timer > 0 or game_state in ["WIN","LOSE"]:
        draw_panel(245,18,710,44,(0.90,0.68,0.20))
        glColor3f(0.96,0.93,0.82)
        draw_text(266,34,last_message[:90],GLUT_BITMAP_HELVETICA_12)

    glColor3f(0.52,0.55,0.55)
    draw_text(365,780,"W/S MOVE   A/D TURN   SPACE JUMP   E INTERACT   R PULSE   F STUN   P PAUSE",GLUT_BITMAP_HELVETICA_12)

    if paused:
        draw_panel(440,338,320,105,(0.94,0.75,0.20))
        glColor3f(0.98,0.92,0.55)
        draw_text(548,398,"PAUSED",GLUT_BITMAP_TIMES_ROMAN_24)
        glColor3f(0.75,0.77,0.76)
        draw_text(505,366,"Press P to continue",GLUT_BITMAP_HELVETICA_12)

    if game_state in ["WIN","LOSE"]:
        draw_rect_2d(330,245,540,295,(0.045,0.055,0.065))
        accent2 = (0.20,0.90,0.45) if game_state == "WIN" else (0.94,0.25,0.18)
        draw_rect_2d(330,528,540,12,accent2)
        glColor3f(*accent2)
        title = "PHONE RECOVERED" if game_state == "WIN" else "MISSION FAILED"
        draw_text(450 if game_state=="WIN" else 475,452,title,GLUT_BITMAP_TIMES_ROMAN_24)
        glColor3f(0.95,0.95,0.90)
        draw_text(510,405,"FINAL SCORE  %d"%score,GLUT_BITMAP_HELVETICA_18)
        glColor3f(0.72,0.74,0.74)
        draw_text(485,360,"Wrong captures  %d / 3"%wrong_capture,GLUT_BITMAP_HELVETICA_12)
        draw_text(475,320,"Press ENTER to run another case",GLUT_BITMAP_HELVETICA_12)
    world_mode()

def draw_selection_scene():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(58.0,window_W/window_H,1.0,3200.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0,-760,240,0,0,78,0,0,1)
    draw_box(0,70,-5,1100,560,10,(0.12,0.15,0.15))
    draw_box(0,160,0,1100,180,5,(0.17,0.18,0.20))
    for x in [-250,0,250]:
        draw_box(x,10,0,120,90,12,(0.20,0.22,0.23))
    cols = [(0.18,0.62,0.96),(0.96,0.52,0.10),(0.12,0.82,0.55)]
    for i,x in enumerate([-250,0,250]):
        if i == selected_character:
            draw_disc(x,0,14,58,cols[i],28)
            glPushMatrix()
            glTranslatef(x,0,17)
            glScalef(1.0,1.0,0.08)
            glColor3f(*cols[i])
            # >>> CHANGED 8J - SELECTION HIGHLIGHT
            # Old glutWireSphere() -> custom Lab 3-function wire sphere.
            draw_wire_sphere(68,cols[i],28)
            glPopMatrix()
        draw_person(x,0,15,90,cols[i],1,False,True,"IDLE",50+i)
    for i,x in enumerate(range(-520,600,130)):
        h = 120+(i%4)*35
        draw_box(x,245,0,115,80,h,(0.22+0.02*(i%3),0.24,0.25))
        draw_box(x,202,h*0.45,24,3,30,(0.26,0.50,0.58))

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    # >>> CHANGED 10A - VIEWPORT ADDED
    # Added the same glViewport() style used in Lab 3 to explicitly use the full window.
    glViewport(0,0,window_W,window_H)
    if game_state == "SELECT":
        draw_selection_scene()
    else:
        setup_camera()
        # >>> CHANGED 10B - SKY DRAW CALL
        # The cube-made sky is drawn before the city because glClearColor() was removed.
        draw_sky()
        draw_ground()
        draw_city()
        for c in cars:draw_car(c)
        draw_npcs()
        draw_player()
        draw_projectiles()
    draw_hud()
    glutSwapBuffers()

def keyboardDown(key,x,y):
    global paused,cctv_index,cctv_watch,game_state,cctv_mode
    k = key_name(key)
    if k in ['1','2','3'] and game_state == "SELECT":
        set_character(int(k)-1)
        return
    if k == '\r':
        if game_state in ["SELECT","WIN","LOSE"]:
            reset_game()
        return
    if k == 'p' and game_state == "PLAY":
        paused = not paused
        return
    if k == 'e':
        interact()
        return
    if k == 'r':
        remote_ring()
        return
    if k == 'f':
        fire_stun()
        return
    if k == 'q' and cctv_mode:
        cctv_index = (cctv_index+1)%len(cameras)
        cctv_watch = 0.0
        return
    if k == ' ' and game_state == "PLAY" and not paused and not cctv_mode:
        support = walkable_surface_height(player["x"],player["y"],player["radius"])
        on_surface = player["z"] == 0 or (support is not None and abs(player["z"]-support) <= 8)
        if on_surface and player["vz"] == 0:
            player["vz"] = player["jump"]
        return
    # >>> CHANGED 11A - ESC CLEANUP
    # Old ESC block also called keys.clear(). keys[] no longer exists, so that line was removed.
    if k == '\x1b':
        if game_state != "SELECT":
            game_state = "SELECT"
            paused = False
            cctv_mode = False
            set_message("Choose a character: 1 Investigator, 2 Runner, 3 Tracker",999.0)
        return
    if game_state != "PLAY" or paused or cctv_mode:
        return

    # >>> CHANGED 11B - W/S/A/D NOW MATCH LAB 3
    # W/S call move_player() directly and A/D directly change angle inside glutKeyboardFunc(), just like Assignment 3. Holding works through normal GLUT key repeat.
    move_step = 20.0*(player["speed"]/190.0)
    if k == 'w':
        move_player(move_step)
    elif k == 's':
        move_player(-move_step*0.70)
    elif k == 'd':
        player["angle"] = (player["angle"]-5.0)%360
    elif k == 'a':
        player["angle"] = (player["angle"]+5.0)%360
    glutPostRedisplay()

def animate():
    global last_time
    now = time.time()
    dt = now-last_time
    last_time = now
    if dt > 0.05:dt = 0.05
    update_game(dt)
    glutPostRedisplay()

# >>> CHANGED 12A - glClearColor REMOVED
# Old init() used glClearColor(). It was removed; the allowed GL depth setup remains.
def init():
    glEnable(GL_DEPTH_TEST)

def main():
    # >>> CHANGED 12B - QUADRIC GLOBAL
    # main() now accesses the global quadric so the project can use Lab 3 gluSphere().
    global quadric
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
    glutInitWindowSize(window_W,window_H)
    glutInitWindowPosition(80,40)
    glutCreateWindow(b"Operation Phoneback - CSE423 Project")
    init()
    # >>> CHANGED 12C - LAB 3 SPHERE SETUP
    # Same pattern as Assignment 3: create one reusable GLU quadric for all gluSphere() calls.
    quadric = gluNewQuadric()
    set_character(0)
    glutDisplayFunc(showScreen)
    # >>> CHANGED 12D - glutKeyboardUpFunc REMOVED
    # Old main() registered glutKeyboardUpFunc(keyboardUp). Both that callback and keyboardUp() were removed for strict Lab 3 compliance.
    glutKeyboardFunc(keyboardDown)
    glutIdleFunc(animate)
    glutMainLoop()


# Start the program
if __name__ == "__main__":
    main()

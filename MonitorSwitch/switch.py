from json import loads
import os
from subprocess import run
import sys
import pygame as pg

pg.init()

WIDTH, HEIGHT = 1080, 640
root = pg.display.set_mode((WIDTH, HEIGHT))
bgColor = (20, 20, 20)

pg.display.set_caption("Monitor Switcher Utility")

font = pg.font.SysFont(None, 24)
font_large = pg.font.SysFont(None, 32, bold=True)

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

ZOOM = 1080 / HEIGHT

MARGIN = 30

# --------------------------------------------------
# PATHS
# --------------------------------------------------

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

wallpaper_path = os.path.join(
    script_directory,
    "../background/ready.jpg"
)

if not os.path.exists(wallpaper_path):
    print(
        f"Wallpaper not found at {wallpaper_path}. "
        "Triggering image_blur.py..."
    )

    try:
        blur_script = os.path.join(
            script_directory,
            "image_blur.py"
        )

        run([sys.executable, blur_script], check=True)

    except Exception as e:
        print(f"Error running image_blur.py: {e}")


# --------------------------------------------------
# LOAD WALLPAPER
# --------------------------------------------------

wallpaper = None

if os.path.exists(wallpaper_path):
    try:
        wallpaper = pg.image.load(wallpaper_path).convert()

        print(
            f"Loaded wallpaper: "
            f"{wallpaper.get_width()}x{wallpaper.get_height()}"
        )

    except Exception as e:
        print(f"Failed to load wallpaper image: {e}")


# --------------------------------------------------
# COMMAND EXECUTION
# --------------------------------------------------

def command(com):

    try:
        result = run(
            com,
            shell=True,
            capture_output=True
        )

        if result.returncode != 0:
            return None

        return loads(
            result.stdout.decode("utf-8").strip()
        )

    except Exception:
        return None


# --------------------------------------------------
# MONITOR CLASS
# --------------------------------------------------

class Monitor:

    def __init__(
        self,
        id,
        name,
        x,
        y,
        width,
        height,
        refresh_rate,
        scale,
        focused,
        active_ws,
        disabled=False,
    ):

        self.id = id
        self.name = name

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.refresh_rate = refresh_rate
        self.scale = scale

        self.focused = focused
        self.active_ws = active_ws

        self.disabled = disabled


# --------------------------------------------------
# APPLY MONITOR POSITIONS
# --------------------------------------------------

def apply_hyprland_positions(monitors):

    for m in monitors:

        disabled_str = str(m.disabled).lower()

        eval_str = (
            f"hl.monitor({{"
            f'output="{m.name}",'
            f"disabled={disabled_str},"
            f"scale={m.scale},"
            f"position='{m.x}x{m.y}',"
            f"mode='{m.width}x{m.height}@{m.refresh_rate}'"
            f"}})"
        )

        run(["hyprctl", "eval", eval_str])


# --------------------------------------------------
# TOGGLE MONITOR
# --------------------------------------------------

def toggle_monitor(mon_id, monitors):

    m = next(
        (mon for mon in monitors if mon.id == mon_id),
        None
    )

    if not m:
        return

    active_count = sum(
        1 for mon in monitors if not mon.disabled
    )

    if not m.disabled and active_count <= 1:

        print(
            f"Safety check: Cannot disable {m.name} "
            "because it is the only active monitor!"
        )

        return

    m.disabled = not m.disabled

    disabled_str = str(m.disabled).lower()

    eval_str = (
        f"hl.monitor({{"
        f'output="{m.name}",'
        f"disabled={disabled_str},"
        f"scale={m.scale},"
        f"position='{m.x}x{m.y}',"
        f"mode='{m.width}x{m.height}@{m.refresh_rate}'"
        f"}})"
    )

    run(["hyprctl", "eval", eval_str])

    print(
        f"Monitor {m.name} "
        f"(ID: {m.id}) disabled = {m.disabled}"
    )


# --------------------------------------------------
# MOVE MONITOR
# --------------------------------------------------

def execute_move(src_id, direction, tgt_id, monitors):

    src = next(
        (m for m in monitors if m.id == src_id),
        None
    )

    tgt = next(
        (m for m in monitors if m.id == tgt_id),
        None
    )

    if not src or not tgt or src == tgt:
        return

    if direction == "RIGHT":

        src.x = tgt.x + tgt.width
        src.y = tgt.y

    elif direction == "LEFT":

        src.x = tgt.x - src.width
        src.y = tgt.y

    elif direction == "DOWN":

        src.x = tgt.x
        src.y = tgt.y + tgt.height

    elif direction == "UP":

        src.x = tgt.x
        src.y = tgt.y - src.height

    others = [
        m for m in monitors
        if m.id != src.id and m.id != tgt.id
    ]

    if direction == "RIGHT":

        others.sort(key=lambda m: m.x)

        current_bound = src.x + src.width

        for m in others:

            if (
                m.x < current_bound
                and (m.x + m.width) > src.x
            ):

                m.x = current_bound
                current_bound = m.x + m.width

    elif direction == "LEFT":

        others.sort(
            key=lambda m: m.x,
            reverse=True
        )

        current_bound = src.x

        for m in others:

            if (
                (m.x + m.width) > current_bound
                and m.x < (src.x + src.width)
            ):

                m.x = current_bound - m.width
                current_bound = m.x

    elif direction == "DOWN":

        others.sort(key=lambda m: m.y)

        current_bound = src.y + src.height

        for m in others:

            if (
                m.y < current_bound
                and (m.y + m.height) > src.y
            ):

                m.y = current_bound
                current_bound = m.y + m.height

    elif direction == "UP":

        others.sort(
            key=lambda m: m.y,
            reverse=True
        )

        current_bound = src.y

        for m in others:

            if (
                (m.y + m.height) > current_bound
                and m.y < (src.y + src.height)
            ):

                m.y = current_bound - m.height
                current_bound = m.y

    apply_hyprland_positions(monitors)


# --------------------------------------------------
# PREPARE VIRTUAL DESKTOP IMAGE
# --------------------------------------------------

def prepare_virtual_desktop(monitors):

    if not monitors or not wallpaper:
        return None, 0, 0, 1, 1

    min_x = min(m.x for m in monitors)
    min_y = min(m.y for m in monitors)

    max_x = max(
        m.x + m.width for m in monitors
    )

    max_y = max(
        m.y + m.height for m in monitors
    )

    virtual_width = max(max_x - min_x, 1)
    virtual_height = max(max_y - min_y, 1)

    # ------------------------------------------
    # WALLPAPER ZOOM
    # ------------------------------------------

    image_scale = max(
        virtual_width / wallpaper.get_width(),
        virtual_height / wallpaper.get_height()
    ) * ZOOM

    scaled_width = max(
        1,
        int(wallpaper.get_width() * image_scale)
    )

    scaled_height = max(
        1,
        int(wallpaper.get_height() * image_scale)
    )

    virtual_image = pg.transform.smoothscale(
        wallpaper,
        (scaled_width, scaled_height)
    )

    # ------------------------------------------
    # CENTER CROP
    # ------------------------------------------

    crop_x = (scaled_width - virtual_width) // 2
    crop_y = (scaled_height - virtual_height) // 2

    virtual_image = virtual_image.subsurface(
        pg.Rect(
            crop_x,
            crop_y,
            virtual_width,
            virtual_height
        )
    ).copy()

    return (
        virtual_image,
        min_x,
        min_y,
        virtual_width,
        virtual_height
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    render = True
    seq_buffer = []

    clock = pg.time.Clock()

    num_keys = {
        pg.K_0: 0,
        pg.K_1: 1,
        pg.K_2: 2,
        pg.K_3: 3,
        pg.K_4: 4,
        pg.K_5: 5,
        pg.K_6: 6,
        pg.K_7: 7,
        pg.K_8: 8,
        pg.K_9: 9,
    }

    dir_keys = {
        pg.K_RIGHT: "RIGHT",
        pg.K_LEFT: "LEFT",
        pg.K_UP: "UP",
        pg.K_DOWN: "DOWN",
    }

    while render:

        # ------------------------------------------
        # FETCH MONITOR DATA
        # ------------------------------------------

        raw_monitors = command(
            "hyprctl monitors all -j"
        ) or []

        monitors = []
        active_monitor = None

        for m in raw_monitors:

            mon = Monitor(
                id=m.get("id", 0),
                name=m.get("name", ""),

                x=m.get("x", 0),
                y=m.get("y", 0),

                width=m.get("width", 1920),
                height=m.get("height", 1080),

                refresh_rate=m.get("refreshRate", 60),
                scale=m.get("scale", 1.0),

                focused=m.get("focused", False),

                active_ws=m.get(
                    "activeWorkspace", {}
                ).get("id", 1),

                disabled=m.get("disabled", False),
            )

            monitors.append(mon)

            if mon.focused:
                active_monitor = mon

        if not active_monitor and monitors:

            active_monitor = next(
                (
                    m for m in monitors
                    if not m.disabled
                ),
                monitors[0]
            )

        # ------------------------------------------
        # BUILD VIRTUAL DESKTOP
        # ------------------------------------------

        (
            virtual_image,
            min_x,
            min_y,
            virtual_width,
            virtual_height
        ) = prepare_virtual_desktop(monitors)

        # ------------------------------------------
        # DISPLAY SCALE
        # ------------------------------------------

        if virtual_image:

            scale_factor = min(
                (WIDTH - MARGIN * 2) / virtual_width,
                (HEIGHT - MARGIN * 2) / virtual_height
            )

            desktop_draw_width = (
                virtual_width * scale_factor
            )

            desktop_draw_height = (
                virtual_height * scale_factor
            )

            desktop_offset_x = (
                WIDTH - desktop_draw_width
            ) / 2

            desktop_offset_y = (
                HEIGHT - desktop_draw_height
            ) / 2

        else:

            scale_factor = 0.12

            desktop_offset_x = 0
            desktop_offset_y = 0

        # ------------------------------------------
        # BACKGROUND
        # ------------------------------------------

        root.fill(bgColor)

        if wallpaper:

            full_bg = pg.transform.smoothscale(
                wallpaper,
                (WIDTH, HEIGHT)
            )

            root.blit(full_bg, (0, 0))

            tint = pg.Surface(
                (WIDTH, HEIGHT),
                pg.SRCALPHA
            )

            tint.fill((0, 0, 0, 170))

            root.blit(tint, (0, 0))

        # ------------------------------------------
        # INPUT EVENTS
        # ------------------------------------------

        for event in pg.event.get():

            if event.type == pg.QUIT:

                render = False

            elif event.type == pg.KEYDOWN:

                if event.key == pg.K_ESCAPE:

                    seq_buffer.clear()

                elif event.key in num_keys:

                    num = num_keys[event.key]

                    if (
                        len(seq_buffer) == 1
                        and seq_buffer[0] == num
                    ):

                        toggle_monitor(
                            num,
                            monitors
                        )

                        seq_buffer.clear()

                    elif len(seq_buffer) in (0, 2):

                        seq_buffer.append(num)

                    elif len(seq_buffer) == 1:

                        seq_buffer = [num]

                elif event.key in dir_keys:

                    if len(seq_buffer) == 1:

                        seq_buffer.append(
                            dir_keys[event.key]
                        )

                if len(seq_buffer) == 3:

                    execute_move(
                        seq_buffer[0],
                        seq_buffer[1],
                        seq_buffer[2],
                        monitors
                    )

                    seq_buffer.clear()

        # ------------------------------------------
        # RENDER MONITORS
        # ------------------------------------------

        if active_monitor and virtual_image:

            for m in monitors:

                draw_x = (
                    desktop_offset_x
                    + (m.x - min_x) * scale_factor
                )

                draw_y = (
                    desktop_offset_y
                    + (m.y - min_y) * scale_factor
                )

                draw_w = max(
                    1,
                    int(m.width * scale_factor)
                )

                draw_h = max(
                    1,
                    int(m.height * scale_factor)
                )

                draw_x = int(draw_x)
                draw_y = int(draw_y)

                # ----------------------------------
                # X-RAY PORTAL
                # ----------------------------------

                src_rect = pg.Rect(
                    m.x - min_x,
                    m.y - min_y,
                    m.width,
                    m.height
                )

                clipped_rect = src_rect.clip(
                    virtual_image.get_rect()
                )

                if (
                    clipped_rect.width > 0
                    and clipped_rect.height > 0
                ):

                    slice_surf = virtual_image.subsurface(
                        clipped_rect
                    )

                    preview_slice = pg.transform.smoothscale(
                        slice_surf,
                        (draw_w, draw_h)
                    )

                    root.blit(
                        preview_slice,
                        (draw_x, draw_y)
                    )

                else:

                    pg.draw.rect(
                        root,
                        (40, 40, 40),
                        (draw_x, draw_y, draw_w, draw_h)
                    )

                # ----------------------------------
                # MONITOR TINT
                # ----------------------------------

                tint_box = pg.Surface(
                    (draw_w, draw_h),
                    pg.SRCALPHA
                )

                if m.disabled:

                    tint_box.fill(
                        (20, 20, 20, 190)
                    )

                elif m.focused:

                    tint_box.fill(
                        (0, 60, 40, 80)
                    )

                else:

                    tint_box.fill(
                        (0, 0, 0, 90)
                    )

                root.blit(
                    tint_box,
                    (draw_x, draw_y)
                )

                # ----------------------------------
                # BORDER
                # ----------------------------------

                if m.disabled:

                    border_color = (120, 40, 40)

                elif m.focused:

                    border_color = (0, 255, 128)

                else:

                    border_color = (100, 100, 100)

                pg.draw.rect(
                    root,
                    border_color,
                    (
                        draw_x,
                        draw_y,
                        draw_w,
                        draw_h
                    ),
                    2
                )

                # ----------------------------------
                # MONITOR LABELS
                # ----------------------------------

                id_surf = font_large.render(
                    f"ID: {m.id}",
                    True,
                    (255, 255, 255)
                )

                root.blit(
                    id_surf,
                    (draw_x + 10, draw_y + 10)
                )

                status_text = (
                    "DISABLED"
                    if m.disabled
                    else f"WS: {m.active_ws} ({m.name})"
                )

                ws_surf = font.render(
                    status_text,
                    True,
                    (
                        (255, 100, 100)
                        if m.disabled
                        else (220, 220, 220)
                    )
                )

                root.blit(
                    ws_surf,
                    (draw_x + 10, draw_y + 40)
                )

        # ------------------------------------------
        # KEY SEQUENCE DISPLAY
        # ------------------------------------------

        seq_str = (
            " -> ".join(str(s) for s in seq_buffer)
            or "None (Press ESC to clear)"
        )

        seq_text = font.render(
            f"Key Sequence: {seq_str} "
            "(Press number twice to toggle enable/disable)",
            True,
            (255, 255, 0)
        )

        root.blit(
            seq_text,
            (20, HEIGHT - 40)
        )

        # ------------------------------------------
        # UPDATE DISPLAY
        # ------------------------------------------

        pg.display.flip()

        clock.tick(20)

    pg.quit()


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
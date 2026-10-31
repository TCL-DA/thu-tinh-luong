"""Do do muot cua trang: dem tac vu luong chinh > 8,33 ms (120 Hz) va > 16,7 ms (60 Hz).
Dung Chrome tracing qua CDP. Chay: python -I -X utf8 do_muot.py [url]"""
import json, sys, pathlib, time
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else pathlib.Path("F:/Project/tinh-luong-otl/index.html").as_uri()
BUDGET_120 = 8330      # micro giay
BUDGET_60 = 16700


def do(pg, cdp, ten, thaotac):
    events = []
    done = {"v": False}
    cdp.on("Tracing.dataCollected", lambda p: events.extend(p.get("value", [])))
    cdp.on("Tracing.tracingComplete", lambda p: done.update(v=True))
    cdp.send("Tracing.start", {
        "traceConfig": {"includedCategories": ["devtools.timeline", "disabled-by-default-devtools.timeline"]},
        "transferMode": "ReportEvents",
    })
    thaotac()
    cdp.send("Tracing.end")
    t0 = time.time()
    while not done["v"] and time.time() - t0 < 10:
        pg.wait_for_timeout(100)
    tasks = [e for e in events if e.get("name") == "RunTask" and e.get("ph") == "X"]
    durs = sorted((e.get("dur", 0) for e in tasks), reverse=True)
    over120 = [d for d in durs if d > BUDGET_120]
    over60 = [d for d in durs if d > BUDGET_60]
    worst = durs[0] / 1000 if durs else 0
    print("%-26s tac vu:%4d | >8,33ms:%3d | >16,7ms:%3d | nang nhat:%6.1f ms  %s"
          % (ten, len(tasks), len(over120), len(over60), worst,
             "DAT 120Hz" if not over120 else ("dat 60Hz" if not over60 else "CHUA DAT")))
    cdp.remove_listener("Tracing.dataCollected", None) if False else None
    return len(over120), len(over60), worst


with sync_playwright() as p:
    b = p.chromium.launch(args=["--enable-gpu-rasterization"])
    pg = b.new_page(viewport={"width": 390, "height": 844})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(1500)

    res = []

    def luot():
        for _ in range(60):
            pg.mouse.wheel(0, 60)
            pg.wait_for_timeout(16)
    cdp = pg.context.new_cdp_session(pg)
    res.append(do(pg, cdp, "Luot trang xuong", luot))

    def luot_len():
        for _ in range(60):
            pg.mouse.wheel(0, -60)
            pg.wait_for_timeout(16)
    res.append(do(pg, cdp, "Luot trang len", luot_len))

    def go_so():
        pg.click("#diem")
        for ch in "187":
            pg.keyboard.press("Backspace")
        for ch in "203":
            pg.keyboard.type(ch)
            pg.wait_for_timeout(60)
        for ch in "456":
            pg.keyboard.press("Backspace")
            pg.wait_for_timeout(60)
        pg.keyboard.type("145")
    res.append(do(pg, cdp, "Go so vao o diem", go_so))

    def bam_nut():
        for i in [1, 3, 5, 2, 4]:
            pg.click("#segNgach button:nth-child(%d)" % i)
            pg.wait_for_timeout(110)
        for i in [5, 1, 3]:
            pg.click("#segBac button:nth-child(%d)" % i)
            pg.wait_for_timeout(110)
    res.append(do(pg, cdp, "Bam nut chon ngach/bac", bam_nut))

    def doi_tab():
        for _ in range(3):
            pg.click("#t2"); pg.wait_for_timeout(420)
            pg.click("#t1"); pg.wait_for_timeout(420)
    res.append(do(pg, cdp, "Doi qua lai 2 tab", doi_tab))

    def luot_tab2():
        pg.click("#t2"); pg.wait_for_timeout(400)
        for _ in range(70):
            pg.mouse.wheel(0, 70)
            pg.wait_for_timeout(16)
        pg.click("#t1")
    res.append(do(pg, cdp, "Luot bang tham chieu", luot_tab2))

    print()
    print("TONG: tac vu >8,33ms =", sum(r[0] for r in res), "| >16,7ms =", sum(r[1] for r in res))
    print("LOI JS:", errs if errs else "khong co")
    b.close()

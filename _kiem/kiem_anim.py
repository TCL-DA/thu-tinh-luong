from playwright.sync_api import sync_playwright
import pathlib

url = pathlib.Path("F:/Project/tinh-luong-otl/index.html").as_uri()
errs = []

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 390, "height": 844})
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    pg.on("console", lambda m: errs.append(m.type + ": " + m.text) if m.type == "error" else None)
    pg.goto(url)
    pg.wait_for_timeout(1400)

    print("tran ngang:", pg.evaluate("document.documentElement.scrollWidth-window.innerWidth"))

    # 1. co bao nhieu quy tac @keyframes + transition trong CSS
    print("so @keyframes:", pg.evaluate("""
      [...document.styleSheets[0].cssRules].filter(r=>r.type===7).length"""))

    # 2. moi .rv phai duoc mo ra khi cuon toi (khong duoc an vinh vien)
    pg.evaluate("window.scrollTo(0,document.body.scrollHeight)")
    pg.wait_for_timeout(1200)
    pg.evaluate("window.scrollTo(0,0)")
    pg.wait_for_timeout(600)
    an = pg.evaluate("""[...document.querySelectorAll('#s1 .rv')].filter(e=>!e.classList.contains('in')).length""")
    print("tab1 - khoi con an:", an)

    # 3. tab 2
    pg.click("#t2"); pg.wait_for_timeout(400)
    pg.evaluate("window.scrollTo(0,document.body.scrollHeight)")
    pg.wait_for_timeout(2000)
    an2 = pg.evaluate("""[...document.querySelectorAll('#s2 .rv')].filter(e=>{
        const r=e.getBoundingClientRect();return !e.classList.contains('in')&&r.top<window.innerHeight*3}).length""")
    vis = pg.evaluate("""getComputedStyle(document.querySelector('#s2 .tb tr')).opacity""")
    ind = pg.evaluate("""getComputedStyle(document.getElementById('tabInd')).transform""")
    print("tab2 - khoi con an gan man hinh:", an2, "| opacity hang bang:", vis, "| con truot tab:", ind)
    pg.click("#t1"); pg.wait_for_timeout(400)

    # 4. so chay dan khi doi gia tri
    pg.evaluate("window.scrollTo(0,0)")
    before = pg.inner_text("#barTot")
    pg.fill("#diem", "200")
    pg.wait_for_timeout(90)
    mid = pg.inner_text("#barTot")
    pg.wait_for_timeout(600)
    after = pg.inner_text("#barTot")
    print("so chay dan:", before, "->", mid, "->", after, "| co chay dan:", mid != after and mid != before)

    # 5. lop hieu ung co duoc gan khi doi so
    cls = pg.evaluate("""[...document.querySelectorAll('#lines .line')].map(e=>e.className).join(' ')""")
    print("co lop hit/vu/vd:", "hit" in cls, "| mix bar:", pg.inner_text("#mixL").replace("\\n", " / "))

    # 6. ro chuot
    pg.click("#segNgach button:nth-child(4)")
    rip = pg.evaluate("document.querySelectorAll('.rip').length")
    pg.wait_for_timeout(700)
    rip2 = pg.evaluate("document.querySelectorAll('.rip').length")
    print("ro chuot tao ra:", rip, "-> don sach:", rip2)

    # 7. thanh day an khi cuon xuong
    pg.evaluate("window.scrollTo(0,900)"); pg.wait_for_timeout(350)
    hid = pg.evaluate("document.querySelector('.bar').classList.contains('hid')")
    pg.evaluate("window.scrollTo(0,300)"); pg.wait_for_timeout(350)
    sho = pg.evaluate("!document.querySelector('.bar').classList.contains('hid')")
    pr = pg.evaluate("document.getElementById('prog').style.transform")
    print("thanh day an khi cuon xuong:", hid, "| hien lai khi cuon len:", sho, "| tien do:", pr)

    # 8. do muot: dem khung hinh trong 1,2 s khi dang cuon
    fps = pg.evaluate("""() => new Promise(res=>{
        let n=0,t0=performance.now();
        function f(t){n++; if(t-t0<1200){window.scrollBy(0,6);requestAnimationFrame(f)} else res(Math.round(n/((t-t0)/1000)))}
        requestAnimationFrame(f);
    })""")
    print("fps khi cuon:", fps)

    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
    pg.screenshot(path="a_top.png")
    pg.evaluate("document.querySelector('#res').scrollIntoView()"); pg.wait_for_timeout(700)
    pg.screenshot(path="a_res.png")
    pg.close()

    # 9. che do giam chuyen dong
    pg2 = b.new_page(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
    pg2.on("pageerror", lambda e: errs.append("rm pageerror: " + str(e)))
    pg2.goto(url); pg2.wait_for_timeout(800)
    op = pg2.evaluate("getComputedStyle(document.querySelector('.vd')).opacity")
    print("giam chuyen dong - the vi du van hien:", op)
    pg2.close()

    # 10. may tinh ban
    pg3 = b.new_page(viewport={"width": 1280, "height": 900})
    pg3.on("pageerror", lambda e: errs.append("desktop pageerror: " + str(e)))
    pg3.goto(url); pg3.wait_for_timeout(1200)
    print("desktop tran ngang:", pg3.evaluate("document.documentElement.scrollWidth-window.innerWidth"))
    pg3.screenshot(path="a_desk.png")
    pg3.close()
    b.close()

print("LOI JS:", errs if errs else "khong co")

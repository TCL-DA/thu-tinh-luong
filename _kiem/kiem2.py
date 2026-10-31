from playwright.sync_api import sync_playwright
import pathlib
url = pathlib.Path("F:/Project/tinh-luong-otl/index.html").as_uri()
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror", lambda e: errs.append("pageerror: "+str(e)))
    pg.on("console", lambda m: errs.append(m.type+": "+m.text) if m.type=="error" else None)
    pg.goto(url); pg.wait_for_timeout(200)
    print("tran ngang:", pg.evaluate("document.documentElement.scrollWidth-window.innerWidth"))
    print("ngach chon:", pg.inner_text("#capNgach"))
    print("bac chon:", pg.inner_text("#capBac"))
    for sel in [".line:nth-child(1)",".line:nth-child(2)",".line:nth-child(3)",".line:nth-child(5)",".line:nth-child(6)",".line:nth-child(8)",".line.sub",".line.tot"]:
        try: print(" ", pg.inner_text(sel).replace("\n"," | "))
        except Exception as e: print("  !",sel,e)
    print("BAR:", pg.inner_text("#barTot"))
    pg.screenshot(path="v1.png")
    # thu nut "Dien lai vi du mau" sau khi doi lung tung
    pg.click("#segNgach button:nth-child(5)"); pg.fill("#diem","3"); pg.wait_for_timeout(100)
    pg.click("button:has-text('Điền lại ví dụ mẫu')"); pg.wait_for_timeout(200)
    print("sau khi bam dien lai:", pg.inner_text("#capNgach"), "|", pg.input_value("#diem"), "| BAR", pg.inner_text("#barTot"))
    b.close()
print("LOI JS:", errs if errs else "khong co")

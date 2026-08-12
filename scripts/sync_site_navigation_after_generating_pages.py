from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PUB=ROOT/"publications"
NAV=[("Home","index.html"),("About","about.html"),("Publications","publications.html"),("Books","books.html"),("Teaching","teaching.html"),("CV","cv.html"),("Updates","updates.html"),("Reflections","quotes.html"),("Rankings","south-south-rankings.html"),("Contact","contact.html")]

def patch(p):
    s=p.read_text(encoding="utf-8")
    a=s.find('<header class="site-header">')
    if a>=0:
        b=s.find("</header>",a)
        links=''.join(f'<a class="nav-link{" active" if href=="publications.html" else ""}" href="../{href}">{label}</a>' for label,href in NAV)
        h='<header class="site-header"><div class="container header-inner"><div class="brand"><a href="../index.html" class="brand-name">Valentine Joseph Owan, PhD</a><div class="brand-tag">Research Evaluation • Scientometrics • Scholarly Communication</div></div><button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button><nav id="site-nav" class="site-nav" aria-label="Primary">'+links+'</nav></div></header>'
        s=s[:a]+h+s[b+9:]
    a=s.find('<footer class="site-footer">')
    if a>=0:
        b=s.find("</footer>",a)
        links=''.join(f'<a href="../{href}">{label}</a>' for label,href in NAV)
        f='<footer class="site-footer"><div class="container"><div class="footer-top"><div class="footer-copy">© <span id="year"></span> Valentine Joseph Owan <span class="footer-sep">•</span> Department of Educational Psychology, University of Calabar</div><nav class="footer-links" aria-label="Footer Navigation">'+links+'</nav></div><div class="footer-note">Academic website featuring research, publications, teaching, and professional activities in <strong>Research Evaluation</strong>, <strong>Scientometrics</strong>, <strong>Scholarly Communication</strong>, <strong>Educational Measurement</strong>, and <strong>Research Analytics</strong>.</div><div class="footer-logos"><img class="footer-logo" src="../assets/img/logos/unical-logo.png" alt="University of Calabar"><img class="footer-logo" src="../assets/img/logos/vinkwell-logo.png" alt="Vinkwell Publishing"><img class="footer-logo" src="../assets/img/logos/ultimate-research-network-logo.png" alt="Ultimate Research Network"></div></div></footer>'
        s=s[:a]+f+s[b+9:]
    p.write_text(s,encoding="utf-8")

n=0
for p in PUB.glob("*.html"):
    patch(p); n+=1
print(f"Navigation synchronised: {n} publication pages")

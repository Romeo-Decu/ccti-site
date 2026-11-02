# ccti-site

Site-ul public ccti.ro: o pagină statică (index.html + logo.png), găzduită pe Azure Static Web Apps (Free).

## Conținut și generare (2.11.2026)
Site-ul se generează din `content.py` (textele EN/RO) cu `python build.py`. Scriptul produce paginile HTML, `sitemap.xml` și `robots.txt`. Pentru orice schimbare de text se modifică `content.py`, se rulează `python build.py` și se urcă fișierele generate.

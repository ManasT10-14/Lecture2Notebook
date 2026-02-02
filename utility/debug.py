import requests, re, json
from http.cookiejar import MozillaCookieJar

COURSE_SLUG = "neural-networks-deep-learning"
TEST_SLUG = "gradient-descent"   # <-- any REAL lecture

cookies = MozillaCookieJar("cookies.txt")
cookies.load()

s = requests.Session()
s.cookies.update({c.name: c.value for c in cookies})

print("✔ Logged in")

url = f"https://www.coursera.org/learn/{COURSE_SLUG}/lecture/{TEST_SLUG}"
r = s.get(url)

m = re.search(
    r'window\.__APOLLO_STATE__\s*=\s*(\{.*?\});',
    r.text,
    re.DOTALL
)

if not m:
    print("❌ Could not extract JSON")
    quit()

data = json.loads(m.group(1))

print("Top-level keys:", len(data.keys()))
print(list(data.keys())[:25])

with open("apollo_dump.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("\n📁 Saved full JSON to apollo_dump.json")
print("Please send me:")
print("1️⃣ First 20 keys printed")
print("2️⃣ Search inside file for:")
print('   "videoId" or "video" or "asset"')

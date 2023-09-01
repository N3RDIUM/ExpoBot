from speaker import Speaker
s = Speaker()
s.initialize()

import inflect
import time
from selenium import webdriver

# Start a new browser
browser = webdriver.Chrome()

# Create a new tab with custom html
browser.get("https://n3rdium.dev")
# Now remove all tags from body 
browser.execute_script("""
var body = document.getElementsByTagName("body")[0];
while (body.firstChild) {
    body.removeChild(body.firstChild);
}
""")
# Now add custom html
def gen_html(number):
    return f"""
<div style="width: 100vh; height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center;">
    <h1 style="font-family: Arial, helvetica, sans-serif; font-size: 32vw; text-align: center;text-shadow: 0 0 32px white;">{number}</h1>
</div>
    """
# Now add the html
browser.execute_script(f"""
var body = document.getElementsByTagName("body")[0];
body.innerHTML = `{gen_html(10)}`;
""")

# Count down from 10
p = inflect.engine()
for i in range(10, 0, -1):
    t = time.time()
    browser.execute_script(f"""
    var body = document.getElementsByTagName("body")[0];
    body.innerHTML = `{gen_html(i)}`;
    """)
    s.speak_gtts(p.number_to_words(i))
    while time.time() - t < 1:
        pass

# Play rocket launch vid
browser.get("https://www.youtube.com/shorts/x67ku2zLgTs")
time.sleep(16)